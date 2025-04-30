from appData import AppData

import json
import pickle
import datetime
import matplotlib.pyplot as plt

sam = []
sam2 = []

def func(my_list, num):
    my_list.append(num)

def update_graph(xdata, ydata, title, xlabel, ylabel):
        plt.clf()
        plt.plot(xdata, ydata, 'ro')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # plt.
        # plt.xlim(-20, 20)
        # plt.ylim(-20, 20)
        
ct = datetime.datetime.now()
ts = str(ct.month) + "_" + str(ct.day) + "_" + str(ct.hour) + "_" + str(ct.minute) + "_" + str(ct.second)
print(ts)