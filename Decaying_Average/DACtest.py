import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


path1 = 'F:\\work\\2020Correct\\data\\nihe.txt'
df1 = pd.read_csv(path1,sep=',')
print(df1)
x = np.array(df1['rate'])
y = np.array(df1['TMIN'])

f1 = np.polyfit(x, y, 3)
print('f1 is :\n',f1)
p1 = np.poly1d(f1)
print('p1 is :\n',p1)
yvals = p1(x)  #拟合y值
print('yvals is :\n',yvals)
#绘图
plot1 = plt.plot(x, y, 's',label='original values')
plot2 = plt.plot(x, yvals, 'r',label='polyfit values')
plt.xlabel('x')
plt.ylabel('y')
plt.legend(loc=4) #指定legend的位置右下角
plt.title('polyfitting')
plt.show()