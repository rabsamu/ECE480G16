# tutorial using matplotlib 

import matplotlib.pyplot as plt 
import numpy as np

xdata = [2, 4, 5, 7, 9, 10]
ydata = [1, 5, 8, 13, 16, 18]
t = np.arange(0. , 5.2 , 0.2)    # evenly sampled time at 200ms intervals
plt.plot(xdata, ydata, 'ro')    #plot two arrays with "red circle" 
# plt.plot(t, t, 'r--', t, t**2, 'bs', t, t**3, 'g^') # red dashes, blue squares and green triangles; multiple lines on one plot 
plt.title('this is the title')
plt.xlabel('this is the x stuff')
plt.ylabel('this is the y stuff')
plt.axis([0, 10, 0, 20])          #axis w (x1, x2, y1, y2) 
plt.show()                      #produces plot 