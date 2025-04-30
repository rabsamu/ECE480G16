import matplotlib.pyplot as plt
import numpy as np

# pass xdata and ydata as lists; pass title, xlabel, and ylabel as strings 

def plotData(xdata, ydata, title, xlabel, ylabel):
    plt.plot(xdata, ydata, 'ro')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(-20, 20)
    plt.ylim(-20, 20)
    plt.show()

testVoltages = [-10., -4.5, -1.7, 2., 4.9, ]
testCurrents = [0.75, 4.3, 7.6, 8.1, 12.2]
testTitle = 'Measurement'
testxlabel = 'voltages'
testylabel = 'currents'
plotData(testVoltages, testCurrents, testTitle, testxlabel, testylabel)