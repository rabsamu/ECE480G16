from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

import matplotlib.pyplot as plt
import numpy as np


class ResultsScreen(Screen):
    data_x = []
    data_y = []

    INSTANCE = None

    def start_process(self):
        self.data_x = []
        self.data_y = []
        self.event = Clock.schedule_interval(self.process, 0.02)

    def process(self, dt):
        data_string = self.INSTANCE.bluetooth.BluetoothReceive()
        self.layout.topBar.mytext.text = data_string
        if data_string == "END":
            self.stop_process()
        else:
            try:
                self.data_x.append(float(data_string.split(",")[0]))
                self.data_y.append(float(data_string.split(",")[1]))
            except Exception as e:
                print("whoops")
        self.update_graph(self.data_x, self.data_y, "graph of victory", "x", "y")
        self.layout.mainContent.graph.reload()
    
    def update_graph(self, xdata, ydata, title, xlabel, ylabel):
        plt.plot(xdata, ydata, 'ro')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # plt.xlim(-20, 20)
        # plt.ylim(-20, 20)
        plt.savefig("graph.png")

    def stop_process(self):
        self.event.cancel()