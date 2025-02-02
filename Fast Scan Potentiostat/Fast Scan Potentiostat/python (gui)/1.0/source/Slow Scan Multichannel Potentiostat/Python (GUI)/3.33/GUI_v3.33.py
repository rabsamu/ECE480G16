import sys
import serial
import serial.tools.list_ports
import pyqtgraph as pg
import time
import numpy as np
import datetime
import csv
from PyQt6 import QtWidgets, uic, QtCore, QtGui
from PyQt6.QtGui import QIcon
from serial import SerialException
from threading import Thread
import queue
import pandas as pd
import random
import tkinter as tk
from tkinter import filedialog
import os
import json

import ctypes


import configparser

def find_USB_device():
    '''
    Finds the USB port that the Teensy is connected to 
    '''
    myPorts = [tuple(p) for p in list(serial.tools.list_ports.comports()) if p[1].startswith('USB')]
    usb_port_list = [p[0] for p in myPorts]
    return usb_port_list

class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        # Base case for recursion
        if isinstance(obj, dict):
            items = []
            for key, value in obj.items():
                item = f'"{key}": {json.dumps(value, indent=4)}'
                items.append(item)
            return '{\n  ' + ',\n  '.join(items) + '\n}'
        else:
            return super().encode(obj)

class MainUI(QtWidgets.QMainWindow):


    ##### INITIALIZATIONS #####


    def __init__(self, *args, **kwargs):
        super(MainUI, self).__init__(*args, **kwargs)
        uic.loadUi('GUI_v3.33.ui', self)


        '''###### DATA PARAMETERS ######'''


        # data storage lists
        self.calibration_data_gather_list = []
        self.asv_data_response = []
        self.asv_data_potential = []
        self.data_points = [] #for save file

        # dpv data storage lists by Nathan
        self.dpv_data_potential = []
        self.dpv_data_response = []
        self.dpv_data_item_list = []
        self.dpv_color_list = []
        self.dpv_parameter_values = {}

        # dpasv data storage lists by Nathan
        self.dpasv_data_potential = []
        self.dpasv_data_response = []
        self.dpasv_data_item_list = []
        self.dpasv_color_list = []
        self.dpasv_parameter_values = {}

        # cv data storage lists by Nathan
        self.cv_data_potential = []
        self.cv_data_response = []
        self.cv_data_item_list = []
        self.cv_color_list = []
        self.cv_parameter_values = {}

        # asv data storage lists by Nathan
        self.asv_data_potential = []
        self.asv_data_response = []
        self.asv_data_item_list = []
        self.asv_color_list = []
        self.asv_parameter_values = {}

        # experiment indexes by Nathan (for open_file)
        self.dpv_index = 0
        self.dpasv_index = 0
        self.cv_index = 0
        self.asv_index = 0

        # Create thread-safe queues (data storage)
        self.calibration_data_queue = queue.Queue()
        self.cv_data_queue = queue.Queue()
        self.asv_data_queue = queue.Queue()
        self.dpv_data_queue = queue.Queue()
        self.dpasv_data_queue = queue.Queue()

        # current calibration coefficients attribute
        self.calibration_coefficients = [None, None, None]
        self.selected_calibration_coefficients = [None, None, None]


        '''###### CONFIG ######'''

        self.config_values = {}
        try:
            # read data values from .json
            self.read_json()
            if self.check_date(): #if new date
                self.update_experiment_counter()
                self.update_date()
        except:
            # create .json if it does not exist
            # or add in missing entries
            self.initialize_json()

        #cv
        self.cv_config_values = {}
        try:
            # read data values from .json
            self.read_cv_config()
        except:
            self.initialize_cv_config()


        #self.config = self.read_config("failsaveconfig.txt")


        '''###### UNCATEGORIZED INITIALIZATIONS ######'''


        # set window icon
        self.setWindowIcon(QIcon('./icons/ssmc.png'))

        # current console log in focus attribute
        self.current_console_log = self.main_screen_console_log

        # Random initial settings
        self.main_screen_console_log.setReadOnly(True)
        self.cv_console_log.setReadOnly(True)
        self.asv_console_log.setReadOnly(True)
        self.dpv_console_log.setReadOnly(True)
        self.dpasv_console_log.setReadOnly(True)
        self.eis_console_log.setReadOnly(True)
        self.extras_console_log.setReadOnly(True)
        self.noise_console_log.setReadOnly(True)
        self.calibration_console_log.setReadOnly(True)
        pg.setConfigOptions(antialias=True)

        # communication attributes and initialization
        self.selected_COM = None
        self.baud_rate = 115200
        
        # experiment running attribute and initialization
        self.cv_running = False
        self.asv_running = False
        self.eis_running = False
        self.noise_running = False
        self.dpasv_running = False
        self.dpv_running = False

        # initial ports list update
        self.ports_list = find_USB_device()
        for p in self.ports_list:
            self.main_port_combo_box.addItem(p)

        # timer to update combobox. Add more connects here if you want to have other events happen on a 1 second basis.
        self.port_timer = QtCore.QTimer(self)
        self.port_timer.setInterval(1000)  # in milliseconds
        self.port_timer.start()
        self.port_timer.timeout.connect(self.handle_1s_timeout)
        
        # timer to update current calibraton gather data plot item
        self.calibration_plot_timer = QtCore.QTimer(self)
        self.calibration_plot_timer.setInterval(30)  # in milliseconds
        self.calibration_plot_timer.start()
        self.calibration_plot_timer.timeout.connect(self.handle_30ms_timeout)

        # timer to update current calibraton gather data plot item
        self.data_timer = QtCore.QTimer(self)
        self.data_timer.setInterval(1)  # in milliseconds
        self.data_timer.start()
        self.data_timer.timeout.connect(self.handle_1ms_timeout)

        # instantiate plots
        self.instantiate_calibration_plot()
        self.instantiate_cv_plot()
        self.instantiate_asv_plot()
        self.instantiate_dpv_plot()
        self.instantiate_dpasv_plot()


        '''###### BUTTONS ######'''

            # main (0)<--Index
        self.main_connect_button.clicked.connect(self.connect_clicked)
        self.main_to_cv_button.clicked.connect(self.show_cv_window)
        self.main_to_asv_button.clicked.connect(self.show_asv_window)
        self.main_to_dpv_button.clicked.connect(self.show_dpv_window)
        self.main_to_dpasv_button.clicked.connect(self.show_dpasv_window)
        self.main_to_eis_button.clicked.connect(self.show_eis_window)
        self.main_to_extras_button.clicked.connect(self.show_extras_window)
            #  calibration (1)
        self.calibration_load_current_fit_button.clicked.connect(self.plot_current_fit_data)
        self.calibration_collect_calibration_data_button.clicked.connect(self.collect_calibration_data_worker)
        self.calibration_apply_current_fit_button.clicked.connect(self.apply_coefficients)
        self.calibration_check_current_calibration_button.clicked.connect(self.calibration_test_worker)
        self.calibration_open_file_button.clicked.connect(self.open_file)
        self.calibration_save_file_button.clicked.connect(self.save_file)
            # CV (2)
        self.run_cv_button.clicked.connect(self.cv_worker)
        self.cv_open_file_button.clicked.connect(self.open_file)
        self.cv_save_file_button.clicked.connect(self.save_file)
        self.cv_remove_data_button.clicked.connect(self.remove_data_cv)
            # ASV (3)
        self.run_asv_button.clicked.connect(self.asv_worker)
        self.asv_open_file_button.clicked.connect(self.open_file)
        self.asv_save_file_button.clicked.connect(self.save_file)
        self.asv_remove_data_button.clicked.connect(self.remove_data_asv)
            # eis (4)
        self.run_eis_button.clicked.connect(self.eis_worker)
        self.eis_open_file_button.clicked.connect(self.open_file)
        self.eis_save_file_button.clicked.connect(self.save_file)
            # extras (5)
        self.extras_to_noise_button.clicked.connect(self.show_noise_window)
        self.extras_to_calibration_button.clicked.connect(self.show_calibration_window)
            # noise (6)
        self.run_noise_button.clicked.connect(self.noise_worker)
        self.noise_open_file_button.clicked.connect(self.open_file)
        self.noise_save_file_button.clicked.connect(self.save_file)
            # dpv (7)
        self.run_dpv_button.clicked.connect(self.dpv_worker)
        self.dpv_open_file_button.clicked.connect(self.open_file)
        self.dpv_save_file_button.clicked.connect(self.save_file)
        self.dpv_remove_data_button.clicked.connect(self.remove_data_dpv)
            # dpasv (8)
        self.run_dpasv_button.clicked.connect(self.dpasv_worker)
        self.dpasv_open_file_button.clicked.connect(self.open_file)
        self.dpasv_save_file_button.clicked.connect(self.save_file)
        self.dpasv_remove_data_button.clicked.connect(self.remove_data_dpasv)
        #self.dpasv_stop_button.clicked.connect(self.stop_dpasv)
      
            # back-to-main buttons (NA)
        self.calibration_to_main_button.clicked.connect(self.show_main_window) #1
        self.cv_to_main_button.clicked.connect(self.show_main_window) #2
        self.asv_to_main_button.clicked.connect(self.show_main_window) #3
        self.eis_to_main_button.clicked.connect(self.show_main_window) #4
        self.extras_to_main_button.clicked.connect(self.show_main_window) #5
        self.noise_to_main_button.clicked.connect(self.show_main_window) #6
        self.dpv_to_main_button.clicked.connect(self.show_main_window) #7
        self.dpasv_to_main_button.clicked.connect(self.show_main_window) #8


    ##### TIMEOUT HANDLERS #####  
          

    def handle_1ms_timeout(self):
        # Get data first in queue, append to data list. If empty, don't do anything
        try:
            data = self.cv_data_queue.get(block=False)
            self.cv_data_potential.append(data[0])
            self.cv_data_response.append(data[1])
        except queue.Empty:
            pass
        try:
            data = self.asv_data_queue.get(block=False)
            self.asv_data_potential.append(data[0])
            self.asv_data_response.append(data[1])
        except queue.Empty:
            pass
        try:
            data = self.dpv_data_queue.get(block=False)
            self.dpv_data_potential.append(data[0])
            self.dpv_data_response.append(data[1])
        except queue.Empty:
            pass
        try:
            data = self.dpasv_data_queue.get(block=False)
            self.dpasv_data_potential.append(data[0])
            self.dpasv_data_response.append(data[1])
        except queue.Empty:
            pass
        try:
            data = self.asv_data_queue.get(block=False)
            self.asv_data_potential.append(data[0])
            self.asv_data_response.append(data[1])
        except queue.Empty:
            pass

    def handle_1s_timeout(self):
        # function to update combo box, update console log scrollbar, update buttons etc
        self.scroll_to_bottom()

        temp = find_USB_device()
        if self.ports_list != temp:
            self.main_port_combo_box.clear()
            self.selected_COM = None
            self.ports_list = find_USB_device()
            for p in self.ports_list:
                self.main_port_combo_box.addItem(p)
        
        if not self.cv_running:
            if self.cv_data_queue.qsize() == 0:
                if not self.run_cv_button.isEnabled():
                    self.run_cv_button.setEnabled(True)
                if not self.cv_open_file_button.isEnabled():
                    self.cv_open_file_button.setEnabled(True)
                if not self.cv_save_file_button.isEnabled():
                    self.cv_save_file_button.setEnabled(True)
                if not self.cv_to_main_button.isEnabled():
                    self.cv_to_main_button.setEnabled(True)
        if not self.asv_running:
            if self.asv_data_queue.qsize() == 0:
                if not self.run_asv_button.isEnabled():
                    self.run_asv_button.setEnabled(True)
                if not self.asv_open_file_button.isEnabled():
                    self.asv_open_file_button.setEnabled(True)
                if not self.asv_save_file_button.isEnabled():
                    self.asv_save_file_button.setEnabled(True)
        if not self.dpv_running:
            if self.dpv_data_queue.qsize() == 0:
                if not self.run_dpv_button.isEnabled():
                    self.run_dpv_button.setEnabled(True)
                if not self.dpv_open_file_button.isEnabled():
                    self.dpv_open_file_button.setEnabled(True)
                if not self.dpv_save_file_button.isEnabled():
                    self.dpv_save_file_button.setEnabled(True)
                if not self.dpv_to_main_button.isEnabled():
                    self.dpv_to_main_button.setEnabled(True)
        if not self.dpasv_running:
            if self.dpasv_data_queue.qsize() == 0:
                if not self.run_dpasv_button.isEnabled():
                    self.run_dpasv_button.setEnabled(True)
                if not self.dpasv_open_file_button.isEnabled():
                    self.dpasv_open_file_button.setEnabled(True)
                if not self.dpasv_save_file_button.isEnabled():
                    self.dpasv_save_file_button.setEnabled(True)
            
    def handle_30ms_timeout(self):
        # 10ms timer events - update plots
        self.update_calibration_gather_plot_item()
        self.update_cv_plot_item()
        self.update_asv_plot_item()
        self.update_dpv_plot_item()
        self.update_dpasv_plot_item()


    ##### DPV PAGE CODE **DONE #####


    def instantiate_dpv_plot(self):
        # # helper function to instantiate calibration plot
        
        # self.plot_widget_dpv = pg.PlotWidget(background='#CCCCCC')
        # self.dpv_data_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311',width=3))

        # # add the data item to the plot widget
        # self.plot_widget_dpv.addItem(self.dpv_data_item)

        # # create and add the legend to the plot widget
        # self.dpv_legend = pg.LegendItem(offset=(70, 30))
        # # set legend font size and color
        # self.dpv_legend.setLabelTextColor('#1E3D59')
        # self.dpv_legend.setParentItem(self.plot_widget_cv.graphicsItem())
        # # set legends to data items
        # #self.cv_legend.addItem(self.cv_data_item, 'Measured CV data')
        # # label and layout setup and adding plotWidget to layout
        # label_style = {"font-size": "18pt"}
        # self.plot_widget_dpv.setLabel('left', 'Current',units='A', **label_style)
        # self.plot_widget_dpv.setLabel('bottom', 'Potential', units='V', **label_style)


        # # Customize the tick labels
        # tick_font = QtGui.QFont()
        # tick_font.setPointSize(14)  # Set the desired font size for the tick labels

        # # Apply the tick font to both axes
        # for axis in ['left', 'bottom']:
        #     ax = self.plot_widget_dpv.getAxis(axis)
        #     ax.setTickFont(tick_font)


        # self.plot_layout_dpv = QtWidgets.QGridLayout(self.dpv_plot_widget_container)
        # self.plot_layout_dpv.setContentsMargins(20, 30, 30, 20)
        # self.plot_layout_dpv.addWidget(self.plot_widget_dpv)
        # self.plot_widget_dpv.getAxis('left').setTextPen('#1E3D59')
        # self.plot_widget_dpv.getAxis('left').setPen('#1E3D59')
        # self.plot_widget_dpv.getAxis('bottom').setTextPen('#1E3D59')
        # self.plot_widget_dpv.getAxis('bottom').setPen('#1E3D59')

        self.plot_widget_dpv = pg.PlotWidget(background='#CCCCCC')
        self.dpv_data_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311',width=3))

        # add the data item to the plot widget
        self.plot_widget_dpv.addItem(self.dpv_data_item)

        # create and add the legend to the plot widget
        self.dpv_legend = pg.LegendItem(offset=(70, 30))
        # set legend font size and color
        self.dpv_legend.setLabelTextColor('#1E3D59')
        self.dpv_legend.setParentItem(self.plot_widget_dpv.graphicsItem())
        # set legends to data items
        self.dpv_legend.addItem(self.dpv_data_item, 'Measured DPV data')
        # label and layout setup and adding plotWidget to layout
        label_style = {"font-size": "18pt"}
        self.plot_widget_dpv.setLabel('left', 'Current',units='A', **label_style)
        self.plot_widget_dpv.setLabel('bottom', 'Potential', units='V', **label_style)


        # Customize the tick labels
        tick_font = QtGui.QFont()
        tick_font.setPointSize(14)  # Set the desired font size for the tick labels

        # Apply the tick font to both axes
        for axis in ['left', 'bottom']:
            ax = self.plot_widget_dpv.getAxis(axis)
            ax.setTickFont(tick_font)


        self.plot_layout_dpv = QtWidgets.QGridLayout(self.dpv_plot_widget_container)
        self.plot_layout_dpv.setContentsMargins(20, 30, 30, 20)
        self.plot_layout_dpv.addWidget(self.plot_widget_dpv)
        self.plot_widget_dpv.getAxis('left').setTextPen('#1E3D59')
        self.plot_widget_dpv.getAxis('left').setPen('#1E3D59')
        self.plot_widget_dpv.getAxis('bottom').setTextPen('#1E3D59')
        self.plot_widget_dpv.getAxis('bottom').setPen('#1E3D59')

    def update_dpv_plot_item(self):
        self.dpv_data_item.setData(x=self.dpv_data_potential, y=self.dpv_data_response)

    # WILL NEED TO BE UPDATED
    def check_DPV(self):

        test = 1

        #inital E
        if float(self.dpv_initial_potential.text()) < float(self.config["dpv_initial_potential_min"]):
            self.write_to_console_log("Error. Entered inital E too low")
            test = 0
        elif float(self.dpv_initial_potential.text()) > float(self.config["dpv_initial_potential_max"]):
            self.write_to_console_log("Error. Entered initial E too high")
            test = 0

        #Final E
        if float(self.dpv_final_potential.text()) < float(self.config["dpv_final_potential_min"]):
            self.write_to_console_log("Error. Entered final E too low")
            test = 0
        elif float(self.dpv_final_potential.text()) > float(self.config["dpv_final_potential_max"]):
            self.write_to_console_log("Error. Entered final E too high")
            test = 0
        elif float(self.dpv_final_potential.text()) < float(self.dpv_initial_potential.text()):
            self.write_to_console_log("Error. Entered final E is less than inital E")
            test = 0

        #increment E
        if float(self.dpv_increment_potential.text()) < float(self.config["dpv_increment_potential_min"]):
            self.write_to_console_log("Error. Entered increment E too low")
            test = 0
        elif float(self.dpv_increment_potential.text()) > float(self.config["dpv_increment_potential_max"]):
            self.write_to_console_log("Error. Entered increment E too high")
            test = 0

        #pulse width
        if float(self.dpv_pulse_width.text()) < float(self.config["dpv_pulse_width_min"]):
            self.write_to_console_log("Error. Entered Pulse Width too small")
            test = 0
        elif float(self.dpv_pulse_width.text()) > float(self.config["dpv_pulse_width_max"]):
            self.write_to_console_log("Error. Entered Pulse Width too large")
            test = 0

        #pulse period
        if float(self.dpv_pulse_period.text()) < float(self.config["dpv_pulse_period_min"]):
            self.write_to_console_log("Error. Entered Pulse Period too short")
            test = 0
        elif float(self.dpv_pulse_period.text()) > float(self.config["dpv_pulse_period_max"]):
            self.write_to_console_log("Error. Entered Pulse Period too long")
            test = 0

        #pulse amplitude
        if float(self.dpv_amplitude.text()) < float(self.config["dpv_amplitude_min"]):
            self.write_to_console_log("Error. Entered Pulse Amplitude too large")
            test = 0
        elif float(self.dpv_amplitude.text()) > float(self.config["dpv_amplitude_max"]):
            self.write_to_console_log("Error. Entered Pulse Amplitude too small")
            test = 0

        #quiet time
        if float(self.dpv_quiet_time.text()) < float(self.config["dpv_quiet_time_min"]):
            self.write_to_console_log("Error. Entered quiet time too short")
            test = 0
        elif float(self.dpv_quiet_time.text()) > float(self.config["dpv_quiet_time_max"]):
            self.write_to_console_log("Error. Entered quiet time too long")
            test = 0

        #sample width
        if float(self.dpv_sample_width.text()) < float(self.config["dpv_sample_width_min"]):
            self.write_to_console_log("Error. Entered sample width too small")
            test = 0
        elif float(self.dpv_sample_width.text()) > float(self.config["dpv_sample_width_max"]):
            self.write_to_console_log("Error. Entered sample width too big")
            test = 0

        #oversampling
        if float(self.dpv_oversampling.text()) < float(self.config["dpv_oversampling_min"]):
            self.write_to_console_log("Error. Entered oversampling too small")
            test = 0
        elif float(self.dpv_oversampling.text()) > float(self.config["dpv_oversampling_max"]):
            self.write_to_console_log("Error. Entered oversampling too big")
            test = 0

        return test

    def run_dpv(self):
        
        #if self.check_DPV():

            channel = int(self.dpv_channel_selector.currentText().replace("Ch", ""))

            self.write_to_console_log("Running DPV experiment...")
            command = "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(channel, self.dpv_gain_combo_box.currentText(),
                                                                    self.dpv_initial_potential.text(),
                                                                    self.dpv_final_potential.text(),
                                                                    self.dpv_increment_potential.text(),
                                                                    self.dpv_pulse_width.text(), 4, 
                                                                    self.dpv_pulse_period.text(),
                                                                    self.dpv_amplitude.text(),
                                                                    self.dpv_quiet_time.text())
            
            if self.selected_calibration_coefficients == [None, None, None]:
                command += ", 2, 0, 0, 0"
            else:
                command += ",1"
                command += "," + str(self.selected_calibration_coefficients[0])
                command += "," + str(self.selected_calibration_coefficients[1])
                command += "," + str(self.selected_calibration_coefficients[2])


            command += ', ' + self.dpv_sample_width.text()
            command += ', ' + self.dpv_oversampling.text()

            print(command)
            
            with serial.Serial(self.selected_COM, baudrate=self.baud_rate) as ser:
                self.data_points = []
                time.sleep(0.1)
                ser.write(command.encode('UTF-8'))
                time.sleep(0.1)
                dpv_running = True
                while dpv_running:
                    line = ser.read(ser.in_waiting)  # binary string
                    if line != b'':
                        if line == b'Done!\r\n':
                            dpv_running = False
                            continue
                        try:
                            temp_line = line.decode('UTF-8')
                            temp_line = temp_line.strip()
                            dpv_applied_code,I1,I2 =  temp_line.split(',')
                            gain = float(self.dpv_gain_combo_box.currentText())
                            dpv_response = np.float64((float(I1)-float(I2)) / gain)

                            
                            #dpv_response = ((5 * dpv_response / (2**16-1)) - 2.5) * 2 / gain
                            #dpv_E_f = (float(dpv_applied_code) / 8192 -1) * 2.5
                            self.add_data(self.dpv_data_queue, [float(dpv_applied_code),dpv_response])
                        except UnicodeDecodeError:
                            print("Warning: UnicodeDecodeError")
                            continue
                        except ValueError:
                                print("ValueError")
                                #print(temp_line)
                                exit()


            self.dpv_parameter_values['Initial Potential (V)'] = self.dpv_initial_potential.text()
            self.dpv_parameter_values['Final Potential (V)'] = self.dpv_final_potential.text()
            self.dpv_parameter_values['Pulse Width (s)'] = self.dpv_pulse_width.text()
            self.dpv_parameter_values['Pulse Period (s)'] = self.dpv_pulse_period.text()
            self.dpv_parameter_values['Amplitude (V)'] = self.dpv_amplitude.text()
            self.dpv_parameter_values['Increment V (V)'] = self.dpv_increment_potential.text()
            self.dpv_parameter_values['Sample Width (s)'] = self.dpv_sample_width.text()
            self.dpv_parameter_values['Oversampling'] = self.dpv_oversampling.text()
            self.dpv_parameter_values['Channel used'] = str(channel)
            self.dpv_parameter_values['Additional comments'] = self.dpv_comments_textEdit.toPlainText()

            self.auto_save()
            self.write_to_console_log("DPV test complete.")
            self.dpv_running = False
        
    def dpv_worker(self):

        self.dpv_data_potential.clear(), self.dpv_data_response.clear()
        for item in self.plot_widget_dpv.items():
                if isinstance(item, pg.PlotDataItem):
                    item.setData(x=[], y=[], clear=True)
        
        #removes legend labels for opened files
        for item in self.dpv_data_item_list:
            self.dpv_legend.removeItem(item)

        if self.check_false_COM():
            return
        self.run_dpv_button.setEnabled(False)
        self.dpv_open_file_button.setEnabled(False)
        self.dpv_save_file_button.setEnabled(False)
        self.dpv_to_main_button.setEnabled(False)
        self.dpv_running = True
        t3 = Thread(target=self.run_dpv)
        t3.start()

    def open_dpv(self, file, df):
        # Helper function for self.open_file()
        
        #test to ensure file is in dpv format
        try:
            test = df["dpv"]
            failed = 0
        except KeyError:
            self.write_to_console_log("Please select a .txt file with dpv format")
            failed = 1

        if not failed:    
            #variables
            finished = 0
            index = 0
            voltage_l = []
            current_l = []
            file_name_l = file.name.split("/")
            for i in file_name_l: #get last value
                file_name = i

            #plot stuff
            color_str = self.get_random_color(self.dpv_color_list)
            self.dpv_data_item_list.append(pg.PlotDataItem(pen=pg.mkPen(color=color_str,width=3)))
            self.plot_widget_dpv.addItem(self.dpv_data_item_list[self.dpv_index])
            self.dpv_legend.addItem(self.dpv_data_item_list[self.dpv_index], file_name)

            while not finished:
                try:
                    voltage_l.append(df["voltage"][index])
                    current_l.append(df["current"][index])
                    index += 1
                except KeyError:
                    finished = 1
                    
            self.dpv_data_item_list[self.dpv_index].setData(x=voltage_l, y=current_l)
            self.dpv_index += 1
            self.dpv_remove_data_combo_box.addItem(file_name)

    def remove_data_dpv(self):

        #variable declarations
        file_name = self.dpv_remove_data_combo_box.currentText()
        index = self.dpv_remove_data_combo_box.findText(file_name)
        data_item = self.dpv_data_item_list[index]

        #legend item removal
        self.dpv_legend.removeItem(data_item)

        #plot data removal
        self.plot_widget_dpv.removeItem(data_item)

        #combo box data removal
        self.dpv_remove_data_combo_box.removeItem(index)
        
        #update lists
        self.dpv_data_item_list.remove(data_item)
        self.dpv_color_list.remove(self.dpv_color_list[index])
        self.dpv_index -= 1


    ##### DPASV PAGE CODE **DONE #####


    def open_dpasv(self, file, df):
        # Helper function for self.open_file()
        
        #test to ensure file is in dpasv format
        try:
            test = df["dpasv"]
            failed = 0
        except KeyError:
            self.write_to_console_log("Please select a .txt file with dpasv format")
            failed = 1

        if not failed:    
            #variables
            finished = 0
            index = 0
            voltage_l = []
            current_l = []
            file_name_l = file.name.split("/")
            for i in file_name_l: #get last value
                file_name = i

            #plot stuff
            color_str = self.get_random_color(self.dpasv_color_list)
            self.dpasv_data_item_list.append(pg.PlotDataItem(pen=pg.mkPen(color=color_str,width=3)))
            self.plot_widget_dpasv.addItem(self.dpasv_data_item_list[self.dpasv_index])
            self.dpasv_legend.addItem(self.dpasv_data_item_list[self.dpasv_index], file_name)

            while not finished:
                try:
                    voltage_l.append(df["voltage"][index])
                    current_l.append(df["current"][index])
                    index += 1
                except KeyError:
                    finished = 1
                    
            self.dpasv_data_item_list[self.dpasv_index].setData(x=voltage_l, y=current_l)
            self.dpasv_index += 1
            self.dpasv_remove_data_combo_box.addItem(file_name)

    def update_dpasv_plot_item(self):
        self.dpasv_data_item.setData(x=self.dpasv_data_potential, y=self.dpasv_data_response)

    def instantiate_dpasv_plot(self):
        # # helper function to instantiate dpasv plot
        
        # self.plot_widget_dpasv = pg.PlotWidget(background='#CCCCCC')
        # self.dpasv_data_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311'))

        # # add the data item to the plot widget
        # self.plot_widget_dpasv.addItem(self.dpasv_data_item)

        # # create and add the legend to the plot widget
        # self.dpasv_legend = pg.LegendItem(offset=(70, 30))
        # # set legend font size and color
        # self.dpasv_legend.setLabelTextColor('#1E3D59')
        # self.dpasv_legend.setParentItem(self.plot_widget_dpasv.graphicsItem())
        # # set legends to data items
        # self.dpasv_legend.addItem(self.dpasv_data_item, 'Measured DPASV data')
        # # label and layout setup and adding plotWidget to layout
        # label_style = {"font-size": "12pt"}
        # self.plot_widget_dpasv.setLabel('left', 'Current',units='A', **label_style)
        # self.plot_widget_dpasv.setLabel('bottom', 'Potential', units='V', **label_style)
        # self.plot_layout_dpasv = QtWidgets.QGridLayout(self.dpasv_plot_widget_container)
        # self.plot_layout_dpasv.setContentsMargins(20, 30, 30, 20)
        # self.plot_layout_dpasv.addWidget(self.plot_widget_dpasv)
        # self.plot_widget_dpasv.getAxis('left').setTextPen('#1E3D59')
        # self.plot_widget_dpasv.getAxis('left').setPen('#1E3D59')
        # self.plot_widget_dpasv.getAxis('bottom').setTextPen('#1E3D59')
        # self.plot_widget_dpasv.getAxis('bottom').setPen('#1E3D59')

        self.plot_widget_dpasv = pg.PlotWidget(background='#CCCCCC')
        self.dpasv_data_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311',width=3))

        # add the data item to the plot widget
        self.plot_widget_dpasv.addItem(self.dpasv_data_item)

        # create and add the legend to the plot widget
        self.dpasv_legend = pg.LegendItem(offset=(70, 30))
        # set legend font size and color
        self.dpasv_legend.setLabelTextColor('#1E3D59')
        self.dpasv_legend.setParentItem(self.plot_widget_dpasv.graphicsItem())
        # set legends to data items
        self.dpasv_legend.addItem(self.dpasv_data_item, 'Measured DPASV data')
        # label and layout setup and adding plotWidget to layout
        label_style = {"font-size": "18pt"}
        self.plot_widget_dpasv.setLabel('left', 'Current',units='A', **label_style)
        self.plot_widget_dpasv.setLabel('bottom', 'Potential', units='V', **label_style)


        # Customize the tick labels
        tick_font = QtGui.QFont()
        tick_font.setPointSize(14)  # Set the desired font size for the tick labels

        # Apply the tick font to both axes
        for axis in ['left', 'bottom']:
            ax = self.plot_widget_dpasv.getAxis(axis)
            ax.setTickFont(tick_font)


        self.plot_layout_dpasv = QtWidgets.QGridLayout(self.dpasv_plot_widget_container)
        self.plot_layout_dpasv.setContentsMargins(20, 30, 30, 20)
        self.plot_layout_dpasv.addWidget(self.plot_widget_dpasv)
        self.plot_widget_dpasv.getAxis('left').setTextPen('#1E3D59')
        self.plot_widget_dpasv.getAxis('left').setPen('#1E3D59')
        self.plot_widget_dpasv.getAxis('bottom').setTextPen('#1E3D59')
        self.plot_widget_dpasv.getAxis('bottom').setPen('#1E3D59')



    # WILL NEED TO BE UPDATED
    def check_DPASV(self):

        test = 1

        #inital E
        if float(self.dpasv_initial_potential.text()) < float(self.config["dpasv_initial_potential_min"]):
            self.write_to_console_log("Error. Entered inital E too low")
            test = 0
        elif float(self.dpasv_initial_potential.text()) > float(self.config["dpasv_initial_potential_max"]):
            self.write_to_console_log("Error. Entered initial E too high")
            test = 0

        #Final E
        if float(self.dpasv_final_potential.text()) < float(self.config["dpasv_final_potential_min"]):
            self.write_to_console_log("Error. Entered final E too low")
            test = 0
        elif float(self.dpasv_final_potential.text()) > float(self.config["dpasv_final_potential_max"]):
            self.write_to_console_log("Error. Entered final E too high")
            test = 0
        elif float(self.dpasv_final_potential.text()) < float(self.dpasv_initial_potential.text()):
            self.write_to_console_log("Error. Entered final E is less than inital E")
            test = 0

        #increment E
        if float(self.dpasv_increment_potential.text()) < float(self.config["dpasv_increment_potential_min"]):
            self.write_to_console_log("Error. Entered increment E too low")
            test = 0
        elif float(self.dpasv_increment_potential.text()) > float(self.config["dpasv_increment_potential_max"]):
            self.write_to_console_log("Error. Entered increment E too high")
            test = 0

        #pulse width
        if float(self.dpasv_pulse_width.text()) < float(self.config["dpasv_pulse_width_min"]):
            self.write_to_console_log("Error. Entered Pulse Width too small")
            test = 0
        elif float(self.dpasv_pulse_width.text()) > float(self.config["dpasv_pulse_width_max"]):
            self.write_to_console_log("Error. Entered Pulse Width too large")
            test = 0

        #pulse period
        if float(self.dpasv_pulse_period.text()) < float(self.config["dpasv_pulse_period_min"]):
            self.write_to_console_log("Error. Entered Pulse Period too short")
            test = 0
        elif float(self.dpasv_pulse_period.text()) > float(self.config["dpasv_pulse_period_max"]):
            self.write_to_console_log("Error. Entered Pulse Period too long")
            test = 0

        #pulse amplitude
        if float(self.dpasv_amplitude.text()) < float(self.config["dpasv_amplitude_min"]):
            self.write_to_console_log("Error. Entered Pulse Amplitude too large")
            test = 0
        elif float(self.dpasv_amplitude.text()) > float(self.config["dpasv_amplitude_max"]):
            self.write_to_console_log("Error. Entered Pulse Amplitude too small")
            test = 0

        #quiet time
        if float(self.dpasv_quiet_time.text()) < float(self.config["dpasv_quiet_time_min"]):
            self.write_to_console_log("Error. Entered quiet time too short")
            test = 0
        elif float(self.dpasv_quiet_time.text()) > float(self.config["dpasv_quiet_time_max"]):
            self.write_to_console_log("Error. Entered quiet time too long")
            test = 0

        #sample width
        if float(self.dpasv_sample_width.text()) < float(self.config["dpasv_sample_width_min"]):
            self.write_to_console_log("Error. Entered sample width too small")
            test = 0
        elif float(self.dpasv_sample_width.text()) > float(self.config["dpasv_sample_width_max"]):
            self.write_to_console_log("Error. Entered sample width too big")
            test = 0

        #oversampling
        if float(self.dpasv_oversampling.text()) < float(self.config["dpasv_oversampling_min"]):
            self.write_to_console_log("Error. Entered oversampling too small")
            test = 0
        elif float(self.dpasv_oversampling.text()) > float(self.config["dpasv_oversampling_max"]):
            self.write_to_console_log("Error. Entered oversampling too big")
            test = 0
        
        #hold time 1
        if float(self.dpasv_hold_time1.text()) < float(self.config["dpasv_hold_time1_min"]):
            self.write_to_console_log("Error. Entered 'hold time 1' too short")
            test = 0
        elif float(self.dpasv_hold_time1.text()) > float(self.config["dpasv_hold_time1_max"]):
            self.write_to_console_log("Error. Entered 'hold time 1' too long")
            test = 0

        #hold time 2
        if float(self.dpasv_hold_time2.text()) < float(self.config["dpasv_hold_time2_min"]):
            self.write_to_console_log("Error. Entered 'hold time 2' too short")
            test = 0
        elif float(self.dpasv_hold_time2.text()) > float(self.config["dpasv_hold_time2_max"]):
            self.write_to_console_log("Error. Entered 'hold time 2' too long")
            test = 0

        #hold voltage 1
        if float(self.dpasv_hold_voltage1.text()) < float(self.config["dpasv_hold_voltage1_min"]):
            self.write_to_console_log("Error. Entered 'hold voltage 1' too low")
            test = 0
        elif float(self.dpasv_hold_voltage1.text()) > float(self.config["dpasv_hold_voltage1_max"]):
            self.write_to_console_log("Error. Entered 'hold voltage 1' too high")
            test = 0
        
        #hold voltage 2
        if float(self.dpasv_hold_voltage2.text()) < float(self.config["dpasv_hold_voltage2_min"]):
            self.write_to_console_log("Error. Entered 'hold voltage 2' too low")
            test = 0
        elif float(self.dpasv_hold_voltage2.text()) > float(self.config["dpasv_hold_voltage2_max"]):
            self.write_to_console_log("Error. Entered 'hold voltage 2' too high")
            test = 0

        return test

    def dpasv_worker(self):

        self.dpasv_data_potential.clear(), self.dpasv_data_response.clear()
        for item in self.plot_widget_dpasv.items():
                if isinstance(item, pg.PlotDataItem):
                    item.setData(x=[], y=[], clear=True)
        
        #removes legend labels for opened files
        for item in self.dpasv_data_item_list:
            self.dpasv_legend.removeItem(item)

        if self.check_false_COM():
            return
        self.run_dpasv_button.setEnabled(False)
        self.dpasv_open_file_button.setEnabled(False)
        self.dpasv_save_file_button.setEnabled(False)
        self.dpasv_running = True
        t3 = Thread(target=self.run_dpasv)
        t3.start()

    def run_dpasv(self):

        # if self.check_DPASV():
            
            channel = int(self.dpv_channel_selector.currentText().replace("Ch", ""))

            self.write_to_console_log("Running DPASV experiment...")
            command = "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(channel, self.dpasv_gain_combo_box.currentText(),
                                                                    self.dpasv_initial_potential.text(),
                                                                    self.dpasv_final_potential.text(),
                                                                    self.dpasv_increment_potential.text(),
                                                                    self.dpasv_pulse_width.text(), 5, 
                                                                    self.dpasv_pulse_period.text(),
                                                                    self.dpasv_amplitude.text(),
                                                                    self.dpasv_quiet_time.text())

            if self.selected_calibration_coefficients == [None, None, None]:
                command += ", 2, 0, 0, 0"
            else:
                command += ",1"
                command += "," + str(self.selected_calibration_coefficients[0])
                command += "," + str(self.selected_calibration_coefficients[1])
                command += "," + str(self.selected_calibration_coefficients[2])

            command += ', ' + self.dpasv_sample_width.text()
            command += ', ' + self.dpasv_hold_time1.text()
            command += ', ' + self.dpasv_hold_voltage1.text()
            command += ', ' + self.dpasv_hold_time2.text()
            command += ', ' + self.dpasv_hold_voltage2.text()
            command += ', ' + self.dpasv_oversampling.text()

            print(command)
            
            
            with serial.Serial(self.selected_COM, baudrate=self.baud_rate) as ser:
                self.data_points = []
                time.sleep(0.1)
                ser.write(command.encode('UTF-8'))
                time.sleep(0.1)
                self.dpasv_running2 = True
                while self.dpasv_running2:
                    line = ser.read(ser.in_waiting)  # binary string
                    if line != b'':
                        if line == b'Done!\r\n':
                            self.dpasv_running2 = False
                            continue
                        if line == b'hold\r\n': #don't know why this is here (as in for the arduino code)
                            continue
                        try:
                            temp_line = line.decode('UTF-8')
                            temp_line = temp_line.strip()
                            dpasv_applied_code,I1,I2 =  temp_line.split(',')
                            dpasv_response = float(I1)-float(I2)
                            gain = float(self.dpasv_gain_combo_box.currentText())
                            dpasv_response = dpasv_response / gain
                            #dpasv_response = ((5 * dpasv_response / (2**16-1)) - 2.5) * 2 / gain
                            #dpasv_E_f = (float(dpasv_applied_code) / 8192 -1) * 2.5
                            self.add_data(self.dpasv_data_queue, [float(dpasv_applied_code),dpasv_response])
                        except UnicodeDecodeError:
                            print("Warning: UnicodeDecodeError")
                            continue
                        except ValueError:
                                print("ValueError")
                                print(temp_line)
                                exit()

            self.dpasv_parameter_values['Initial Potential (V)'] = self.dpasv_initial_potential.text()
            self.dpasv_parameter_values['Final Potential (V)'] = self.dpasv_final_potential.text()
            self.dpasv_parameter_values['Pulse Width (s)'] = self.dpasv_pulse_width.text()
            self.dpasv_parameter_values['Pulse Period (s)'] = self.dpasv_pulse_period.text()
            self.dpasv_parameter_values['Amplitude (V)'] = self.dpasv_amplitude.text()
            self.dpasv_parameter_values['Increment V (V)'] = self.dpasv_increment_potential.text()
            self.dpasv_parameter_values['Sample Width (s)'] = self.dpasv_sample_width.text()
            self.dpasv_parameter_values['Hold Time 1 (s)'] = self.dpasv_hold_time1.text()
            self.dpasv_parameter_values['Hold Voltage 1 (V)'] = self.dpasv_hold_voltage1.text()
            self.dpasv_parameter_values['Hold Time 2 (s)'] = self.dpasv_hold_time2.text()
            self.dpasv_parameter_values['Hold Voltage 2 (V)'] = self.dpasv_hold_voltage2.text()
            self.dpasv_parameter_values['Oversampling'] = self.dpasv_oversampling.text()
            self.dpasv_parameter_values['Channel used'] = str(channel)
            self.dpasv_parameter_values['Additional comments'] = self.dpasv_comments_textEdit.toPlainText()

            self.auto_save()
            self.write_to_console_log("DPASV test complete.")
            self.dpasv_running = False

    def stop_dpasv(self):
        self.dpasv_running2 = False

    def remove_data_dpasv(self):

        #variable declarations
        file_name = self.dpasv_remove_data_combo_box.currentText()
        index = self.dpasv_remove_data_combo_box.findText(file_name)
        data_item = self.dpasv_data_item_list[index]

        #legend item removal
        self.dpasv_legend.removeItem(data_item)

        #plot data removal
        self.plot_widget_dpasv.removeItem(data_item)

        #combo box data removal
        self.dpasv_remove_data_combo_box.removeItem(index)
        
        #update lists
        self.dpasv_data_item_list.remove(data_item)
        self.dpasv_color_list.remove(self.dpasv_color_list[index])
        self.dpasv_index -= 1


    ##### EIS PAGE CODE (UNCODED) #####
    

    def eis_worker(self):

       # self.cv_data_potential.clear(), self.cv_data_response.clear()
        #for item in self.plot_widget_cv.items():
        #        if isinstance(item, pg.PlotDataItem):
        #            item.setData(x=[], y=[], clear=True)

        # return, and do not start data gather thread if not a valid COM

        if self.check_false_COM():
            return
        self.run_eis_button.setEnabled(False)
        self.eis_open_file_button.setEnabled(False)
        self.eis_save_file_button.setEnabled(False)
        self.eis_running = True
        t3 = Thread(target=self.run_eis)
        t3.start()

    def run_eis(self):
        self.write_to_console_log("Uncoded lol")


    ##### NOISE PAGE CODE (Uncoded) #####


    def run_noise(self):
        self.write_to_console_log("Uncoded lol")

    def noise_worker(self):

       # self.cv_data_potential.clear(), self.cv_data_response.clear()
        #for item in self.plot_widget_cv.items():
        #        if isinstance(item, pg.PlotDataItem):
        #            item.setData(x=[], y=[], clear=True)

        # return, and do not start data gather thread if not a valid COM

        if self.check_false_COM():
            return
        self.run_noise_button.setEnabled(False)
        self.noise_running = True
        t3 = Thread(target=self.run_noise)
        t3.start()


    ##### CV PAGE CODE  ***DONE #####
        

    def open_cv(self, file, df):
        # Helper function for self.open_file()
        # How I figured out to plot it.  Probably very dumb
        # and inefficient.  Feel free to make it better and laugh at me
        
        #test to ensure file is in cv format
        try:
            test = df["cv"]
            failed = 0
        except KeyError:
            self.write_to_console_log("Please select a .txt file with cv format")
            failed = 1

        if not failed:    
            #variables
            finished = 0
            index = 0
            voltage_l = []
            current_l = []
            file_name_l = file.name.split("/")
            for i in file_name_l: #get last value
                file_name = i

            #plot stuff
            color_str = self.get_random_color(self.cv_color_list)
            self.cv_data_item_list.append(pg.PlotDataItem(pen=pg.mkPen(color=color_str,width=3)))
            #self.cv_data_item_list.append(pg.PlotDataItem(pen=pg.mkPen(color=color_str,width=3,style=QtCore.Qt.PenStyle.DotLine)))
            self.plot_widget_cv.addItem(self.cv_data_item_list[self.cv_index])
            self.cv_legend.addItem(self.cv_data_item_list[self.cv_index], file_name)

            while not finished:
                try:
                    voltage_l.append(df["voltage"][index])
                    current_l.append(df["current"][index])
                    index += 1
                except KeyError:
                    finished = 1
                    
            self.cv_data_item_list[self.cv_index].setData(x=voltage_l, y=current_l)
            self.cv_index += 1 
            self.cv_remove_data_combo_box.addItem(file_name) 
        
    def cv_worker(self):

        self.cv_data_potential.clear(), self.cv_data_response.clear()
        for item in self.plot_widget_cv.items():
                if isinstance(item, pg.PlotDataItem):
                    item.setData(x=[], y=[], clear=True)
        # return, and do not start data gather thread if not a valid COM
        if self.check_false_COM():
            return
        self.run_cv_button.setEnabled(False)
        self.cv_open_file_button.setEnabled(False)
        self.cv_save_file_button.setEnabled(False)
        self.cv_to_main_button.setEnabled(False)
        self.cv_running = True
        t3 = Thread(target=self.run_cv)
        t3.start()

    def remove_data_cv(self):

        #variable declarations
        file_name = self.cv_remove_data_combo_box.currentText()
        index = self.cv_remove_data_combo_box.findText(file_name)
        data_item = self.cv_data_item_list[index]

        #legend item removal
        self.cv_legend.removeItem(data_item)

        #plot data removal
        self.plot_widget_cv.removeItem(data_item)

        #combo box data removal
        self.cv_remove_data_combo_box.removeItem(index)
        
        #update lists
        self.cv_data_item_list.remove(data_item)
        self.cv_color_list.remove(self.cv_color_list[index])
        self.cv_index -= 1

    # WILL NEED TO BE UPDATED
    def check_cv(self):

        test = 1

        #lower voltage limit
        if float(self.cv_lower_voltage_limit.text()) < float(self.config["cv_lower_voltage_limit_min"]):
            self.write_to_console_log("Error. Entered lower voltage limit too low")
            test = 0
        elif float(self.cv_lower_voltage_limit.text()) > float(self.config["cv_lower_voltage_limit_max"]):
            self.write_to_console_log("Error. Entered lower voltage limit too high")
            test = 0

        #upper voltage limit
        if float(self.cv_upper_voltage_limit.text()) < float(self.config["cv_upper_voltage_limit_min"]):
            self.write_to_console_log("Error. Entered upper voltage limit too low")
            test = 0
        elif float(self.cv_upper_voltage_limit.text()) > float(self.config["cv_upper_voltage_limit_max"]):
            self.write_to_console_log("Error. Entered lower voltage limit too high")
            test = 0
        elif float(self.cv_upper_voltage_limit.text()) < float(self.cv_lower_voltage_limit.text()):
            self.write_to_console_log("Error. Entered upper voltage is less lower voltage")
            test = 0

        #number of segments
        if float(self.cv_number_of_segments.text()) < float(self.config["cv_number_of_segments_min"]):
            self.write_to_console_log("Error. Entered number of segments is too low")
            test = 0
        elif float(self.cv_number_of_segments.text()) > float(self.config["cv_number_of_segments_max"]):
            self.write_to_console_log("Error. Entered number of segments is too high")
            test = 0

        #sampling rate
        if float(self.cv_sampling_rate.text()) < float(self.config["cv_sampling_rate_min"]):
            self.write_to_console_log("Error. Entered sampling rate is too low")
            test = 0
        elif float(self.cv_sampling_rate.text()) > float(self.config["cv_sampling_rate_max"]):
            self.write_to_console_log("Error. Entered sampling rate is too high")
            test = 0

        #scan rate
        if float(self.cv_scan_rate.text()) < float(self.config["cv_scan_rate_min"]):
            self.write_to_console_log("Error. Entered scan rate is too low")
            test = 0
        elif float(self.cv_scan_rate.text()) > float(self.config["cv_scan_rate_max"]):
            self.write_to_console_log("Error. Entered scan rate is too high")
            test = 0

        return test

    def run_cv(self):
        self.write_to_console_log("Running CV experiment...")

        channel = int(self.cv_channel_selector.currentText().replace("Ch", ""))

        command = "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(channel,
                                                                self.cv_voltage_to_hold.text(), 
                                                                self.cv_lower_voltage_limit.text(),
                                                                self.cv_upper_voltage_limit.text(), 
                                                                self.cv_scan_rate.text(),
                                                                self.cv_number_of_segments.text(), 0,
                                                                self.cv_sensitivity_combo_box.currentText(),
                                                                self.cv_sampling_rate.text(), 0)
        if self.selected_calibration_coefficients == [None, None, None]:
            command += ", 2, 0, 0, 0"
        else:
            command += ",1"
            command += "," + str(self.selected_calibration_coefficients[0])
            command += "," + str(self.selected_calibration_coefficients[1])
            command += "," + str(self.selected_calibration_coefficients[2])

        print(command)
        
        with serial.Serial(self.selected_COM, baudrate=self.baud_rate) as ser:
            self.data_points = []
            ser.write(command.encode('UTF-8'))
            cv_running = True
            while cv_running:
                line = ser.read(ser.in_waiting)
                try:
                    lines = line.decode('UTF-8').strip()
                except UnicodeDecodeError:
                    lines = 'err'
                    self.write_to_console_log("UnicodeDecodeError")
                if lines != "":
                    lines = lines.replace('\r', '')
                    lines = lines.split('\n')
                    lines = lines[0].split(',')
                    if lines is not None:
                        try:
                            if lines[0] == 'End CV':
                                cv_running = False
                                continue
                            for i in range(0, len(lines)):
                                    float(lines[i])
                            for i in range(0, len(lines), 2):
                                self.add_data(self.cv_data_queue, [float(lines[i]), float(lines[i+1])])
                        except ValueError:
                            print("ValueError")
                            print(lines)
                        except IndexError:
                            print("IndexError")
                            print(lines)

        # for .json save file
        self.cv_parameter_values['Voltage to hold'] = self.cv_voltage_to_hold.text()
        self.cv_parameter_values['Lower voltage limit'] = self.cv_lower_voltage_limit.text()
        self.cv_parameter_values['Upper voltage limit'] = self.cv_upper_voltage_limit.text()
        self.cv_parameter_values['Scan rate'] = self.cv_scan_rate.text()
        self.cv_parameter_values['Number of segments'] = self.cv_number_of_segments.text()
        self.cv_parameter_values['Sensitivity'] = self.cv_sensitivity_combo_box.currentText()
        self.cv_parameter_values['Sampling rate'] = self.cv_sampling_rate.text()
        self.cv_parameter_values['Channel used'] = str(channel)
        self.cv_parameter_values['Additional comments'] = self.cv_comments_textEdit.toPlainText()

        self.auto_save()
        self.write_to_console_log("CV test complete.")
        self.cv_running = False
        
    def update_cv_plot_item(self):
        self.cv_data_item.setData(x=self.cv_data_potential, y=self.cv_data_response)

    def instantiate_cv_plot(self):
        # helper function to instantiate calibration plot
        
        self.plot_widget_cv = pg.PlotWidget(background='#CCCCCC')
        self.cv_data_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311',width=3))

        # add the data item to the plot widget
        self.plot_widget_cv.addItem(self.cv_data_item)

        # create and add the legend to the plot widget
        self.cv_legend = pg.LegendItem(offset=(70, 30))
        # set legend font size and color
        self.cv_legend.setLabelTextColor('#1E3D59')
        self.cv_legend.setParentItem(self.plot_widget_cv.graphicsItem())
        # set legends to data items
        self.cv_legend.addItem(self.cv_data_item, 'Measured CV data')
        # label and layout setup and adding plotWidget to layout
        label_style = {"font-size": "18pt"}
        self.plot_widget_cv.setLabel('left', 'Current',units='A', **label_style)
        self.plot_widget_cv.setLabel('bottom', 'Potential', units='V', **label_style)


        # Customize the tick labels
        tick_font = QtGui.QFont()
        tick_font.setPointSize(14)  # Set the desired font size for the tick labels

        # Apply the tick font to both axes
        for axis in ['left', 'bottom']:
            ax = self.plot_widget_cv.getAxis(axis)
            ax.setTickFont(tick_font)


        self.plot_layout_cv = QtWidgets.QGridLayout(self.cv_plot_widget_container)
        self.plot_layout_cv.setContentsMargins(20, 30, 30, 20)
        self.plot_layout_cv.addWidget(self.plot_widget_cv)
        self.plot_widget_cv.getAxis('left').setTextPen('#1E3D59')
        self.plot_widget_cv.getAxis('left').setPen('#1E3D59')
        self.plot_widget_cv.getAxis('bottom').setTextPen('#1E3D59')
        self.plot_widget_cv.getAxis('bottom').setPen('#1E3D59')


    ##### ASV PAGE CODE **DONE #####

    def open_asv(self, file, df):
        # Helper function for self.open_file()
        
        #test to ensure file is in asv format
        try:
            test = df["asv"]
            failed = 0
        except KeyError:
            self.write_to_console_log("Please select a .txt file with asv format")
            failed = 1

        if not failed:    
            #variables
            finished = 0
            index = 0
            voltage_l = []
            current_l = []
            file_name_l = file.name.split("/")
            for i in file_name_l: #get last value
                file_name = i

            #plot stuff
            color_str = self.get_random_color(self.asv_color_list)
            self.asv_data_item_list.append(pg.PlotDataItem(pen=pg.mkPen(color_str,width=3)))
            self.plot_widget_asv.addItem(self.asv_data_item_list[self.asv_index])
            self.asv_legend.addItem(self.asv_data_item_list[self.asv_index], file_name)

            while not finished:
                try:
                    voltage_l.append(df["voltage"][index])
                    current_l.append(df["current"][index])
                    index += 1
                except KeyError:
                    finished = 1
                    
            self.asv_data_item_list[self.asv_index].setData(x=voltage_l, y=current_l)
            self.asv_index += 1
            self.asv_remove_data_combo_box.addItem(file_name)

    def asv_worker(self):

        # TODO: Perhaps only capture linear sweep, and ignore first data points that is pre clean and concentration voltages

        self.asv_data_potential.clear(), self.asv_data_response.clear()
        for item in self.plot_widget_asv.items():
                if isinstance(item, pg.PlotDataItem):
                    item.setData(x=[], y=[], clear=True)
        # return, and do not start data gather thread if not a valid COM
        if self.check_false_COM():
            return
        self.run_asv_button.setEnabled(False)
        self.asv_open_file_button.setEnabled(False)
        self.asv_save_file_button.setEnabled(False)
        self.asv_running = True
        t4 = Thread(target=self.run_asv)
        t4.start()

    def update_asv_plot_item(self):
        self.asv_data_item.setData(x=self.asv_data_potential, y=self.asv_data_response)

    def run_asv(self):

        channel = int(self.asv_channel_selector.currentText().replace("Ch", ""))

        self.write_to_console_log("Running ASV experiment...")
        command = "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(channel,
                                                                self.asv_scan_rate.text(),
                                                                self.asv_sampling_rate.text(),
                                                                self.asv_concentration_voltage.text(),
                                                                self.asv_upper_stripping_voltage.text(),
                                                                self.asv_pre_clean_voltage.text(),
                                                                2,
                                                                self.asv_pre_clean_time.text(),
                                                                self.asv_concentration_voltage.text(),
                                                                self.asv_concentration_time.text())
        
        if self.selected_calibration_coefficients == [None, None, None]:
            command += ", 2, 0, 0, 0"
        else:
            command += ",1"
            command += "," + str(self.selected_calibration_coefficients[0])
            command += "," + str(self.selected_calibration_coefficients[1])
            command += "," + str(self.selected_calibration_coefficients[2])
        
        command += ", " + self.asv_sensitivity_combo_box.currentText()

        print(command)

        with serial.Serial(self.selected_COM, baudrate=self.baud_rate) as ser:
            self.data_points = []
            ser.write(command.encode('UTF-8'))
            asv_running = True
            while asv_running:
                line = ser.read(ser.in_waiting)
                try:
                    lines = line.decode('UTF-8').strip()
                except UnicodeDecodeError:
                    lines = 'err'
                    self.write_to_console_log("UnicodeDecodeError")
                if lines != "":
                    lines = lines.replace('\r', '')
                    lines = lines.split('\n')
                    lines = lines[0].split(',')
                    if lines is not None:
                        try:
                            if lines[0] == 'End ASV':
                                asv_running = False
                                continue
                            elif lines[0] == 'Applying pre-clean voltage':
                                self.write_to_console_log("Applying pre-clean voltage.")
                                continue
                            elif lines[0] == 'Applying concentration voltage':
                                self.write_to_console_log("Applying concentration voltage.")
                                continue
                            elif lines[0] == 'Starting linear sweep':
                                self.write_to_console_log("Starting linear sweep.")
                                continue
                            for i in range(0, len(lines)):
                                    float(lines[i])
                            for i in range(0, len(lines), 2):
                                self.add_data(self.asv_data_queue, [float(lines[i]), float(lines[i+1])])
                        except ValueError:
                            print("ValueError")
                            print(lines)
                        except IndexError:
                            print("IndexError")
                            print(lines)

        self.asv_parameter_values['Pre clean voltage (V)'] = self.asv_pre_clean_voltage.text()
        self.asv_parameter_values['Pre clean time (s)'] = self.asv_pre_clean_time.text()
        self.asv_parameter_values['Concentration voltage (V)'] = self.asv_concentration_voltage.text()
        self.asv_parameter_values['Concentration time (s)'] = self.asv_concentration_time.text()
        self.asv_parameter_values['Upper stripping voltage (V)'] = self.asv_upper_stripping_voltage.text()
        self.asv_parameter_values['asv_scan_rate'] = self.asv_scan_rate.text()
        self.asv_parameter_values['Sensitivity (ohms)'] = self.asv_sensitivity_combo_box.currentText()
        self.asv_parameter_values['Sampling rate (Samples/s)'] = self.asv_sampling_rate.text()
        self.asv_parameter_values['Channel used'] = str(channel)
        self.asv_parameter_values['Additional comments'] = self.asv_comments_textEdit.toPlainText()
        
        self.auto_save()
        self.write_to_console_log("ASV test complete.")
        self.asv_running = False

    def instantiate_asv_plot(self):
        # helper function to instantiate calibration plot
        
        # self.plot_widget_asv = pg.PlotWidget(background='#CCCCCC')
        # self.asv_data_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311', width=2))

        # # add the data item to the plot widget
        # self.plot_widget_asv.addItem(self.asv_data_item)

        # # create and add the legend to the plot widget
        # legend = pg.LegendItem(offset=(70, 30))
        # # set legend font size and color
        # legend.setLabelTextColor('#1E3D59')
        # legend.setParentItem(self.plot_widget_asv.graphicsItem())
        # # set legends to data items
        # legend.addItem(self.asv_data_item, 'Measured ASV data')
        # # label and layout setup and adding plotWidget to layout
        # label_style = {"font-size": "12pt"}
        # self.plot_widget_asv.setLabel('left', 'Current',units='A', **label_style)
        # self.plot_widget_asv.setLabel('bottom', 'Potential', units='V', **label_style)
        # self.plot_layout_asv = QtWidgets.QGridLayout(self.asv_plot_widget_container)
        # self.plot_layout_asv.setContentsMargins(20, 30, 30, 20)
        # self.plot_layout_asv.addWidget(self.plot_widget_asv)
        # self.plot_widget_asv.getAxis('left').setTextPen('#1E3D59')
        # self.plot_widget_asv.getAxis('left').setPen('#1E3D59')
        # self.plot_widget_asv.getAxis('bottom').setTextPen('#1E3D59')
        # self.plot_widget_asv.getAxis('bottom').setPen('#1E3D59')

        self.plot_widget_asv = pg.PlotWidget(background='#CCCCCC')
        self.asv_data_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311',width=3))

        # add the data item to the plot widget
        self.plot_widget_asv.addItem(self.asv_data_item)

        # create and add the legend to the plot widget
        self.asv_legend = pg.LegendItem(offset=(70, 30))
        # set legend font size and color
        self.asv_legend.setLabelTextColor('#1E3D59')
        self.asv_legend.setParentItem(self.plot_widget_asv.graphicsItem())
        # set legends to data items
        self.asv_legend.addItem(self.asv_data_item, 'Measured ASV data')
        # label and layout setup and adding plotWidget to layout
        label_style = {"font-size": "18pt"}
        self.plot_widget_asv.setLabel('left', 'Current',units='A', **label_style)
        self.plot_widget_asv.setLabel('bottom', 'Potential', units='V', **label_style)


        # Customize the tick labels
        tick_font = QtGui.QFont()
        tick_font.setPointSize(14)  # Set the desired font size for the tick labels

        # Apply the tick font to both axes
        for axis in ['left', 'bottom']:
            ax = self.plot_widget_asv.getAxis(axis)
            ax.setTickFont(tick_font)


        self.plot_layout_asv = QtWidgets.QGridLayout(self.asv_plot_widget_container)
        self.plot_layout_asv.setContentsMargins(20, 30, 30, 20)
        self.plot_layout_asv.addWidget(self.plot_widget_asv)
        self.plot_widget_asv.getAxis('left').setTextPen('#1E3D59')
        self.plot_widget_asv.getAxis('left').setPen('#1E3D59')
        self.plot_widget_asv.getAxis('bottom').setTextPen('#1E3D59')
        self.plot_widget_asv.getAxis('bottom').setPen('#1E3D59')


    def remove_data_asv(self):

        #variable declarations
        file_name = self.asv_remove_data_combo_box.currentText()
        index = self.asv_remove_data_combo_box.findText(file_name)
        data_item = self.asv_data_item_list[index]

        #legend item removal
        self.asv_legend.removeItem(data_item)

        #plot data removal
        self.plot_widget_asv.removeItem(data_item)

        #combo box data removal
        self.asv_remove_data_combo_box.removeItem(index)
        
        #update lists
        self.asv_data_item_list.remove(data_item)
        self.asv_color_list.remove(self.asv_color_list[index])
        self.asv_index -= 1

    ##### CALIBRATION PAGE CODE (maybe working idk) #####


    def run_calibration_test(self):
        self.write_to_console_log("Running calibration test...")
        use_coefficients = True
        if self.selected_calibration_coefficients == [None, None, None]:
            self.write_to_console_log("WARNING: calibration test running without calibration coefficients set")
            use_coefficients = False
        with serial.Serial(self.selected_COM, baudrate=self.baud_rate) as ser:
            if not use_coefficients:
                command = "0,0,0,0,0,-1,1000,0,0,2, 0, 0, 0"
            else:
                command = "0,0,0,0,0,-1,1000,0,0,1"
                command += "," + str(self.selected_calibration_coefficients[0])
                command += "," + str(self.selected_calibration_coefficients[1])
                command += "," + str(self.selected_calibration_coefficients[2])
            ser.write(command.encode('UTF-8'))
            calibration_test_running = True
            while calibration_test_running:
                line = ser.read(ser.in_waiting)
                try:
                    lines = line.decode('UTF-8').strip()
                except UnicodeDecodeError:
                    lines = 'err'
                    self.write_to_console_log("UnicodeDecodeError")
                if lines != "":
                    lines = lines.replace('\r', '')
                    lines = lines.split('\n')
                    if lines is not None:
                        try:
                            for i in range(0, len(lines)):
                                    float(lines[i])
                            for i in range(0, len(lines), 2):
                                self.add_data(self.calibration_data_queue, [float(lines[i]), float(lines[i+1])])
                            if float(lines[0]) >= 2.0:
                                calibration_test_running = False
                        except ValueError:
                            continue
                        except IndexError:
                            self.write_to_console_log("IndexError")
        self.write_to_console_log("Calibration test complete.") 

    def instantiate_calibration_plot(self):
        # helper function to instantiate calibration plot
        self.plot_widget_calibration = pg.PlotWidget(background='#CCCCCC')
        self.current_calibration_data_item = pg.PlotDataItem(pen=pg.mkPen(color='k', width=2))
        self.current_polyfit_data_item = pg.PlotDataItem(pen=pg.mkPen(color='red', width=2))
        self.current_data_gather_item = pg.PlotDataItem(pen=pg.mkPen(color='#FCA311', width=2))
        # add the data item to the plot widget
        self.plot_widget_calibration.addItem(self.current_polyfit_data_item)
        self.plot_widget_calibration.addItem(self.current_calibration_data_item)
        self.plot_widget_calibration.addItem(self.current_data_gather_item)
        # create and add the legend to the plot widget
        legend = pg.LegendItem(offset=(70, 30))
        # set legend font size and color
        legend.setLabelTextColor('#1E3D59')
        legend.setParentItem(self.plot_widget_calibration.graphicsItem())
        # set legends to data items
        legend.addItem(self.current_calibration_data_item, 'Gathered calibration data')
        legend.addItem(self.current_polyfit_data_item, 'Polynomial fit')
        legend.addItem(self.current_data_gather_item, 'Current calibration data gathered')
        # label and layout setup and adding plotWidget to layout
        label_style = {"font-size": "12pt"}
        self.plot_widget_calibration.setLabel('left', 'Applied Voltage',units='V', **label_style)
        self.plot_widget_calibration.setLabel('bottom', 'Measured Voltage', units='V', **label_style)
        self.plot_layout_calibration = QtWidgets.QGridLayout(self.calibration_plot_widget_container)
        self.plot_layout_calibration.setContentsMargins(20, 30, 30, 20)
        self.plot_layout_calibration.addWidget(self.plot_widget_calibration)
        self.plot_widget_calibration.getAxis('left').setTextPen('#1E3D59')
        self.plot_widget_calibration.getAxis('left').setPen('#1E3D59')
        self.plot_widget_calibration.getAxis('bottom').setTextPen('#1E3D59')
        self.plot_widget_calibration.getAxis('bottom').setPen('#1E3D59')

    def collect_calibration_data_worker(self):
        self.calibration_data_gather_list = []
        for item in self.plot_widget_calibration.items():
                if isinstance(item, pg.PlotDataItem):
                    item.setData(x=[], y=[], clear=True)

        # return, and do not start data gather thread if not a valid COM
        if self.check_false_COM():
            return
        t1 = Thread(target=self.collect_calibration_data)
        t1.start()
    
    def collect_calibration_data(self):
        # TODO: implement multiple iteration data collection. Right now, it only runs once.
        
        # code to gather and transmit calibration data, and write to file.
        try:
            with serial.Serial(self.selected_COM, baudrate=self.baud_rate) as ser:
                self.write_to_console_log("Collecting calibration data...")
                command = "0,0,0,0,0,-1,1000,0,0,2, 0, 0, 0"
                ser.write(command.encode('UTF-8'))
                gather_data_running = True
                with open('./calibration/calibration_data.txt', 'w') as f:
                    writer = csv.writer(f)
                    while gather_data_running:
                        line = ser.read(ser.in_waiting)
                        try:
                            lines = line.decode('UTF-8').strip()
                        except UnicodeDecodeError:
                            lines = 'err'
                            self.write_to_console_log("UnicodeDecodeError")
                        if lines != "":
                            lines = lines.replace('\r', '')
                            lines = lines.split('\n')
                            if lines is not None:
                                try:
                                    for i in range(0, len(lines)):
                                        float(lines[i])
                                    for i in range(0, len(lines), 2):
                                        self.add_data(self.calibration_data_queue, [float(lines[i]), float(lines[i+1])])
                                        writer.writerow([float(lines[i]), float(lines[i+1])])
                                    if float(lines[0]) >= 2.0:
                                        gather_data_running = False
                                except ValueError:
                                    self.write_to_console_log(lines)
                                    self.write_to_console_log("ValueError")
                                    continue
                                except IndexError:
                                    self.write_to_console_log("IndexError")
        except SerialException:
            self.write_to_console_log("SerialException")
    
        self.write_to_console_log("Calibration data collection complete.")

    def apply_coefficients(self):
        self.selected_calibration_coefficients = self.calibration_coefficients
        self.write_to_console_log("Selected calibration coefficients: " + str(self.selected_calibration_coefficients))

    def calibration_test_worker(self):
        self.calibration_data_gather_list = []
        for item in self.plot_widget_calibration.items():
                if isinstance(item, pg.PlotDataItem):
                    item.setData(x=[], y=[], clear=True)

        # return, and do not start data gather thread if not a valid COM
        if self.check_false_COM():
            return
        t2 = Thread(target=self.run_calibration_test)
        t2.start()

    def update_calibration_gather_plot_item(self):
        # Get data first in queue, if empty return and do not do any plotting
        try:
            data = self.calibration_data_queue.get(block=False)
        except queue.Empty:
            return
        
        self.calibration_data_gather_list.append(data)
        measured_vals = []
        applied_vals = []
        for val in self.calibration_data_gather_list:
            measured_vals.append(val[1]), applied_vals.append(val[0])
        self.current_data_gather_item.setData(x=measured_vals, y=applied_vals, clear=True)

    def plot_current_fit_data(self):
        measured_voltage_data = []
        applied_voltage_data = []
        try:
            file = open('./calibration/calibration_data.txt')
            csvreader = csv.reader(file)
            for row in csvreader:
                if len(row) > 1:
                    measured_voltage_data.append(float(row[1]))
                    applied_voltage_data.append(float(row[0]))
            file.close()

            coefficients = np.polyfit(measured_voltage_data, applied_voltage_data, 2)
            self.calibration_coefficients = [round(coefficients[0], 6), round(coefficients[1], 6), round(coefficients[2], 6)]
            poly = np.poly1d(coefficients)
            fit_x = np.linspace(-2.0, 2.0)
            fit_y = poly(fit_x)
            
            self.current_polyfit_data_item.setData(fit_x, fit_y)
            self.current_calibration_data_item.setData(measured_voltage_data, applied_voltage_data)
            self.plot_widget_calibration.autoRange()

        except FileNotFoundError:
            self.write_to_console_log("Calibration file not setup. Please collect calibration data!")
            self.calibration_coefficients = [None, None, None]
        except TypeError:
            self.write_to_console_log("TypeError") 
    

    ##### WINDOW SWITCH FUNCTIONS #####
        

    def show_asv_window(self):
         # set current console log
        self.current_console_log = self.asv_console_log
        # switch to asv window
        self.main_stacked_widget.setCurrentIndex(3)

    def show_extras_window(self):
         # set current console log
        self.current_console_log = self.extras_console_log
        # switch to extras window
        self.main_stacked_widget.setCurrentIndex(5)

    def show_noise_window(self):
        # set current console log
        self.current_console_log = self.noise_console_log
        # switch to noise window
        self.main_stacked_widget.setCurrentIndex(6)

    def show_eis_window(self):
         # set current console log
        self.current_console_log = self.eis_console_log
        # switch to eis window
        self.main_stacked_widget.setCurrentIndex(4)

    def show_dpasv_window(self):
         # set current console log
        self.current_console_log = self.dpasv_console_log
        # switch to dpasv window
        self.main_stacked_widget.setCurrentIndex(8)

    def show_dpv_window(self):
        # set current console log
        self.current_console_log = self.dpv_console_log
        # switch to dpv window
        self.main_stacked_widget.setCurrentIndex(7)

    def show_cv_window(self):
        # set current console log
        self.current_console_log = self.cv_console_log
        # switch to cv window
        self.main_stacked_widget.setCurrentIndex(2)

    def show_calibration_window(self):
        # set current console log
        self.current_console_log = self.calibration_console_log
        # switch to calibration window
        self.main_stacked_widget.setCurrentIndex(1)

    def show_main_window(self):
        # set current console log
        self.current_console_log = self.main_screen_console_log
        # switch to main window
        self.main_stacked_widget.setCurrentIndex(0)


    ##### MISC FUNCTIONS #####
        

    def connect_clicked(self):
        if self.main_port_combo_box.currentText() == "":
            self.selected_COM = None
            self.write_to_console_log("Please select a valid port!")
        else:
            self.selected_COM = self.main_port_combo_box.currentText()
            self.write_to_console_log("Port selected: " + self.selected_COM)
            self.plot_current_fit_data()
            self.apply_coefficients()

    def write_to_console_log(self, text):
        # get the current date and time
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # append the text with the current date and time to the console log widget
        log_entry = f"{now} - {text}"
        # append the text to the console log widget
        self.current_console_log.append(log_entry)
    
    def scroll_to_bottom(self):
        scrollbar = self.current_console_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def check_false_COM(self):
        # function that checks current COM, and returns True if current COM is None
        if self.selected_COM is None:
            self.write_to_console_log("Currently selected port: \'" + str(self.selected_COM) + 
                                "\'. Please select and connect to a valid port!")
            return True

    def add_data(self, queue, data):
        # function enqueues data to the selected queue
        #also handles data collection for self.save_file()
        queue.put(data)
        self.data_points.append(data)

    def get_current_date(self):
        # Get the current date and time
        now = datetime.datetime.now()

        # Format the date as a string
        current_date = now.strftime("%Y%m%d")

        return current_date
    
    def get_current_time(self):
        # Returns the current time formatted in military time.  So for instance
        # 8:30 AM will be 0830

        now = datetime.datetime.now()

        # Format the time as a string
        current_time = now.strftime("%H%M")

        return current_time


    ##### PLOT COLOR #####


    def get_random_color(self, color_list):
        # generates a random color to be used with the plotting of curves when self.open_file() is called
        # Could be refined more. This function still generates colors which are hard to see or too close to each other.
        # Alternatively having a list of preset colors might be preffered 

        error = 1
        color = "%06x" % random.randint(0, 0xFFFFFF)
        
        while error == 1:
            error = 0
            for item in color_list:
                if  not self.test_color_variance(color, item): #variance
                    error = 1
                    color = "%06x" % random.randint(0, 0xFFFFFF)
                elif not self.test_color_variance(color, "CCCCCC"): # not too close to background color
                    error = 1
                    color = "%06x" % random.randint(0, 0xFFFFFF)
                elif not self.test_color_variance(color, "FCA311"): # not too close to starting curve color
                    error = 1
                    color = "%06x" % random.randint(0, 0xFFFFFF)
                
        color_str = "#" + str(color)
        color_list.append(color)

        return color_str

    def test_color_variance(self, color_1_str, color_2_str):
        # helper function for self.get_random_color()
        # input colors as 6 hex-bit number formatted like "cccccc" (as a string)
        # returns a true or false for if variance is good enough
        # tests against existing colors already plotted and also against general
        # colors I want to avoid

        color_1_list = self.make_color_list(color_1_str) # will be red, green, blue
        color_2_list = self.make_color_list(color_2_str)

        #variance between compared to existing colors
        if abs(color_1_list[0] - color_2_list[0]) <= 85 and abs(color_1_list[1] - color_2_list[1]) <= 85 and abs(color_1_list[2] - color_2_list[2]) <= 85:
            good_variance = 0
        #no teal or lime green
        elif abs(color_1_list[1] + color_1_list[2] + color_1_list[0]) >= 280:
            good_variance = 0
        #not too bright
        elif abs(color_1_list[0]) > 230 or abs(color_1_list[1]) > 230 or abs(color_1_list[2]) > 230:
            good_variance = 0
        #no grey
        elif abs(color_1_list[0]) <= 65 and abs(color_1_list[0]) >= 35 and abs(color_1_list[1]) <= 65 and abs(color_1_list[1]) >= 35 and abs(color_1_list[2]) <= 65 and abs(color_1_list[2]) >= 35:
            good_variance = 0
        #elif
        else:
            good_variance = 1
        
        return good_variance  

    def make_color_list(self, color_str):
        #helper function for test_color_variance
        color_list = [] # will be red, green, blue
        red, green, blue = "","",""

        #making of list
        index = 0
        for i in color_str:
            if index == 0 or index == 1:
                red += i
            elif index == 2 or index == 3:
                green += i
            elif index == 4 or index == 5:
                blue += i
            index += 1
        
        color_list.append(int(red, 16))
        color_list.append(int(green, 16))
        color_list.append(int(blue, 16))
    
        return color_list


    ##### FILING ##### 
         

    def open_file(self):
        #by Nathan
        initial_dir = self.get_json_value('last_dir')
        mode = self.main_stacked_widget.currentIndex()
        root = tk.Tk()
        root.withdraw() # Hide the Tkinter root window
        file = filedialog.askopenfile(parent=root, initialdir=initial_dir,
                                    title='Please select a file', mode="r")
        if file:
            file_path = file.name
            last_dir = os.path.dirname(file_path)

        try:
            if file is None:
                raise AttributeError
            df = pd.read_csv(file)
            self.save_last_dir(last_dir)

            if mode == 1: #calibration
                print("hi")
            elif mode == 2: #cv
                self.open_cv(file, df)
            elif mode == 3: #asv
                self.open_asv(file, df)
            elif mode == 5: #extras
                print("hi")
            elif mode == 6: #noise
                print("hi")
            elif mode == 7: #dpv
                self.open_dpv(file, df)
            elif mode == 8: #dpasv
                self.open_dpasv(file, df)

        except(ValueError):
            self.write_to_console_log("Please select only valid file types (.txt)")
            self.save_last_dir(last_dir)
        except(AttributeError):
            self.write_to_console_log("No file selected")
            self.save_last_dir(initial_dir)
    
    def save_file(self):
        #by Nathan
        mode = self.main_stacked_widget.currentIndex()
        if self.data_points:
            root = tk.Tk()
            root.withdraw() # Hide the Tkinter root window
            file = filedialog.asksaveasfile(parent=root, initialdir="/",
                                        title='Select name and location', defaultextension = ".txt")
            
            file_path = file.name
            file_path_json = file_path.replace(".txt",".json")

            if mode == 1: #calibration
                file.write("calibration\n")
            elif mode == 2: #cv
                file.write("voltage,current,cv\n")
            elif mode == 3: #asv
                file.write("voltage,current,asv\n")
            elif mode == 5: #extras
                file.write("extras\n")
            elif mode == 6: #noise
                file.write("noise\n")
            elif mode == 7: #dpv
                file.write("voltage,current,dpv\n")
            elif mode == 8: #dpasv
                file.write("voltage,current,dpasv\n")

            for i in self.data_points:
                for j in i:
                    file.write(str(j))
                    file.write(",")
                file.write("\n")    
            file.close()

            self.save_file_json(file_path_json)
        else:
            self.write_to_console_log('No data to save')

    def save_file_json(self,file_path_json):
        mode = self.main_stacked_widget.currentIndex()
        # if mode == 1: #calibration
        #     experiment = 'calibration'
        if mode == 2: #cv
            with open(file_path_json, 'w') as f:
                formatted_json = json.dumps(self.cv_parameter_values, cls=CustomJSONEncoder)
                f.write(formatted_json)

        elif mode == 3: #asv
            with open(file_path_json, 'w') as f:
                formatted_json = json.dumps(self.asv_parameter_values, cls=CustomJSONEncoder)
                f.write(formatted_json)

        # elif mode == 5: #extras
        #     experiment = 'extras'
        # elif mode == 6: #noise
        #     experiment = 'noise'
        elif mode == 7: #dpv
            with open(file_path_json, 'w') as f:
                formatted_json = json.dumps(self.dpv_parameter_values, cls=CustomJSONEncoder)
                f.write(formatted_json)
        elif mode == 8: #dpasv
            with open(file_path_json, 'w') as f:
                formatted_json = json.dumps(self.dpasv_parameter_values, cls=CustomJSONEncoder)
                f.write(formatted_json)

    def auto_save(self):

        #for file name string
        current_date = self.get_current_date()
        documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        mode = self.main_stacked_widget.currentIndex()
        
        if mode == 1: #calibration
            experiment = 'calibration'
        elif mode == 2: #cv

            experiment = 'cv'
            parameter_values = self.cv_parameter_values
            experiment_name = self.cv_experiment_name.text()
            experiment_counter = 'cv_counter'

        elif mode == 3: #asv

            experiment = 'asv'
            parameter_values = self.asv_parameter_values
            experiment_name = self.asv_experiment_name.text()
            experiment_counter = 'asv_counter'

        elif mode == 5: #extras
            experiment = 'extras'
        elif mode == 6: #noise
            experiment = 'noise'
        elif mode == 7: #dpv

            experiment = 'dpv'
            parameter_values = self.dpv_parameter_values
            experiment_name = self.dpv_experiment_name.text()
            experiment_counter = 'dpv_counter'

        elif mode == 8: #dpasv

            experiment = 'dpasv'
            parameter_values = self.dpasv_parameter_values
            experiment_name = self.dpasv_experiment_name.text()
            experiment_counter = 'dpasv_counter'

        # Writing the file path
        if experiment_name:
            file_name = current_date + "_" + self.get_current_time() + '_' + experiment + self.get_json_value(experiment_counter) + '_' + experiment_name + '.txt'
            file_name_json = current_date + "_" + self.get_current_time() + '_' + experiment + self.get_json_value(experiment_counter) + '_' + experiment_name + '.json'
        else:
            file_name = current_date + "_" + self.get_current_time() + '_' + experiment + self.get_json_value(experiment_counter) + '.txt'
            file_name_json = current_date + "_" + self.get_current_time() + '_' + experiment + self.get_json_value(experiment_counter) + '.json'
        self.update_experiment_counter(experiment_counter)
        file_path = os.path.join(documents_path, 'Slow Scan Multi-channel Potentiostat', 'Auto Save', experiment, current_date, file_name)
        file_path_json = os.path.join(documents_path, 'Slow Scan Multi-channel Potentiostat', 'Auto Save', experiment, current_date, file_name_json)

        # Actually writing the data (.txt)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            file.write("voltage,current," + experiment + "\n")
            for i in self.data_points:
                for j in i:
                    file.write(str(j))
                    file.write(",")
                file.write("\n")    
            file.close()

        # Actually writing the data (.json)
        with open(file_path_json, 'w') as f:
            formatted_json = json.dumps(parameter_values, cls=CustomJSONEncoder)
            f.write(formatted_json)


    ##### CONFIGS #####


    ## (config_cv.json) ##
    
    def get_cv_value(self, key, config_file):
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get(key, '')
        else:
            raise LookupError #just a random error
        return ''

    def read_cv_config(self):
        # This function reads in values from the config.json file,
        # and loads them into the self.config_values dictionary that
        # is used to keep track of certain variables and counters that
        # we want to save after the program closes.

        #voltage_to_hold_min
        if self.get_cv_value('voltage_to_hold_min'):
            self.config_values['voltage_to_hold_min'] = self.get_cv_value('voltage_to_hold_min')
        else: 
            self.config_values['voltage_to_hold_min'] = '0'

        #voltage_to_hold_max
        if self.get_cv_value('voltage_to_hold_max'):
            self.config_values['voltage_to_hold_max'] = self.get_cv_value('voltage_to_hold_max')
        else: 
            self.config_values['voltage_to_hold_max'] = '5'

        #lower_voltage_limit_min
        if self.get_cv_value('lower_voltage_limit_min'):
            self.config_values['lower_voltage_limit_min'] = self.get_cv_value('lower_voltage_limit_min')
        else: 
            self.config_values['lower_voltage_limit_min'] = '-4'

        #lower_voltage_limit_max
        if self.get_cv_value('lower_voltage_limit_max'):
            self.config_values['lower_voltage_limit_max'] = self.get_cv_value('lower_voltage_limit_max')
        else: 
            self.config_values['lower_voltage_limit_max'] = '4'

        #upper_voltage_limit_min
        if self.get_cv_value('upper_voltage_limit_min'):
            self.config_values['upper_voltage_limit_min'] = self.get_cv_value('upper_voltage_limit_min')
        else: 
            self.config_values['upper_voltage_limit_min'] = '-4'

        #upper_voltage_limit_max
        if self.get_cv_value('upper_voltage_limit_max'):
            self.config_values['upper_voltage_limit_max'] = self.get_cv_value('upper_voltage_limit_max')
        else: 
            self.config_values['upper_voltage_limit_max'] = '4'

        #scan_rate_min
        if self.get_cv_value('scan_rate_min'):
            self.config_values['scan_rate_min'] = self.get_cv_value('scan_rate_min')
        else: 
            self.config_values['scan_rate_min'] = '0.01'

        #scan_rate_max
        if self.get_cv_value('scan_rate_max'):
            self.config_values['scan_rate_max'] = self.get_cv_value('scan_rate_max')
        else: 
            self.config_values['scan_rate_max'] = '1'

        #number_of_segments_min
        if self.get_cv_value('number_of_segments_min'):
            self.config_values['number_of_segments_min'] = self.get_cv_value('number_of_segments_min')
        else: 
            self.config_values['number_of_segments_min'] = '1'

        #number_of_segments_max
        if self.get_cv_value('number_of_segments_max'):
            self.config_values['number_of_segments_max'] = self.get_cv_value('number_of_segments_max')
        else: 
            self.config_values['number_of_segments_max'] = '100'

        #sampling_rate_min
        if self.get_cv_value('sampling_rate_min'):
            self.config_values['sampling_rate_min'] = self.get_cv_value('sampling_rate_min')
        else: 
            self.config_values['sampling_rate_min'] = '10'

        #sampling_rate_max
        if self.get_cv_value('sampling_rate_max'):
            self.config_values['sampling_rate_max'] = self.get_cv_value('sampling_rate_max')
        else: 
            self.config_values['sampling_rate_max'] = '100'

        self.update_cv_config()

    def update_cv_config(self, config_file="config_cv.json"):
        # Helper function for other .json config functions.
        # This function takes the values from the
        # self.config_values dictionary and puts them into
        # the config.json file.

        with open(config_file, 'w') as f:
            # json.dump(self.failsaveconfig_values, f)
            formatted_json = json.dumps(self.cv_config_values, cls=CustomJSONEncoder)
            f.write(formatted_json)
    
    def initialize_cv_config(self):
            #     This function is supposed to either create the config.json
            #     file if it does not exist yet, and/or fill in missing entries to
            #     prevent the program from crashing if there is an error with the
            #     .json file.

            #self.cv_voltage_to_hold
            self.cv_config_values['voltage_to_hold_min'] = '0'
            self.cv_config_values['voltage_to_hold_max'] = '5'
            
            #self.cv_lower_voltage_limit
            self.cv_config_values['lower_voltage_limit_min'] = '-4'
            self.cv_config_values['lower_voltage_limit_max'] = '4'

            #self.cv_upper_voltage_limit
            self.cv_config_values['upper_voltage_limit_min'] = '-4'
            self.cv_config_values['upper_voltage_limit_max'] = '4'

            #self.cv_scan_rate
            self.cv_config_values['scan_rate_min'] = '0.01'
            self.cv_config_values['scan_rate_max'] = '1'

            #self.cv_number_of_segments
            self.cv_config_values['number_of_segments_min'] = '1'
            self.cv_config_values['number_of_segments_max'] = '100'

            #self.cv_sampling_rate
            self.cv_config_values['sampling_rate_min'] = '10'
            self.cv_config_values['sampling_rate_max'] = '100'

            self.update_cv_config()


    ## (config.json) ##

    def update_experiment_counter(self, key):
        # Whenever this function is called, the value for 'cv_counter'
        # in both self.config_values and config.json will be incremented by 1

        count = self.get_json_value(key)
        count = str(int(count) + 1)
        self.config_values[key] = count
        self.update_json()

    def reset_experiment_counters(self):

        counter_keys = ['cv_counter', 'dpv_counter', 'dpasv_counter', 'asv_counter']

        for key in counter_keys:
            self.config_values[key] = '1'

    def update_date(self):
        
        self.config_values['date'] = self.get_current_date()
        self.update_json()

    def check_date(self):

        if self.config_values['date'] != self.get_current_date():
            return 1
        else:
            return 0
        
    def update_json(self, config_file='config.json'):
        # Helper function for other .json config functions.
        # This function takes the values from the
        # self.config_values dictionary and puts them into
        # the config.json file.

        # with open(config_file, 'w') as f:
        #     json.dump(self.config_values, f)

        with open(config_file, 'w') as f:
            # json.dump(self.failsaveconfig_values, f)
            formatted_json = json.dumps(self.config_values, cls=CustomJSONEncoder)
            f.write(formatted_json)
        
    def save_last_dir(self, dir_path):
        # This function will effectively update both the
        # self.config_values dictionary and the config.json file's
        # value for 'last_dir' to whatever the user inputs for dir_path

        self.config_values['last_dir'] = dir_path
        self.update_json()

    def get_json_value(self, key, config_file='config.json'):
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get(key, '')
        else:
            raise LookupError #just a random error
        return ''

    def initialize_json(self):
        #     This function is supposed to either create the config.json
        #     file if it does not exist yet, and/or fill in missing entries to
        #     prevent the program from crashing if there is an error with the
        #     .json file.

        self.config_values['cv_counter'] = '1'
        self.config_values['dpv_counter'] = '1'
        self.config_values['dpasv_counter'] = '1'
        self.config_values['asv_counter'] = '1'
        self.config_values['last_dir'] = ""
        self.config_values['date'] = self.get_current_date()
        self.update_json()

    def read_json(self):
        # This function reads in values from the config.json file,
        # and loads them into the self.config_values dictionary that
        # is used to keep track of certain variables and counters that
        # we want to save after the program closes.

        self.config_values['last_dir'] = self.get_json_value('last_dir')

        if self.get_json_value('date'):
            self.config_values['date'] = self.get_json_value('date')
        else: 
            self.config_values['date'] = self.get_current_date()

        if self.get_json_value('cv_counter'):
            self.config_values['cv_counter'] = self.get_json_value('cv_counter')
        else:
            self.config_values['cv_counter'] = '1'

        if self.get_json_value('dpv_counter'):
            self.config_values['dpv_counter'] = self.get_json_value('dpv_counter')
        else:
            self.config_values['dpv_counter'] = '1'
        
        if self.get_json_value('dpasv_counter'):
            self.config_values['dpasv_counter'] = self.get_json_value('dpasv_counter')
        else:
            self.config_values['dpasv_counter'] = '1'

        if self.get_json_value('asv_counter'):
            self.config_values['asv_counter'] = self.get_json_value('asv_counter')
        else:
            self.config_values['asv_counter'] = '1'

        self.update_json()


        # key_list = ['last_dir', 'cv_counter', 'date', 'dpv_counter']
        # for i in key_list:
        #     self.config_values[i] = self.get_json_value(i)
        #     if self.config_values[i] == '':

        # self.update_json()


    ##### MAIN ######
    
        
def main():
    app = QtWidgets.QApplication(sys.argv)

    # Windows-specific: Set the icon for the taskbar explicitly
    if sys.platform.startswith('win'):
        myappid = 'fraunhofer-usa.slow-scan-portable-potentiostat-multichannel.gui.3.28'  # Arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    window = MainUI()
    app.setStyle('Fusion')
    window.show()
    window.show_main_window()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()