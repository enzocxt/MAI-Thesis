#import numpy as np
#import operator
#import matplotlib.pyplot as plt
import pylab as pl
#import time

'''
x = [25,28,30,32,34,35,36,38,40]        # support
#x = [14853,8329,5243,3490,2338,1638,1328,873,526]      # number of frequent itemsets

y = [2520.7,474.7,113.5,50.3,18.17,8.1,5.09,2.76,1.63]     # time cost

#pl.plot(x, y)
pl.semilogy(x, y, 'bx-', linewidth=2.0)
pl.xlabel('Mininum supports')
#pl.xlabel('The number of frequent itemsets.')
pl.ylabel('Time cost (s)')
pl.grid(True)
pl.show()
'''

'''
x = [526,1638,5243,14853,29258,56368,133165,219869]
y = [0.02,0.078,0.308,1.1,2.4,4.7,12.2,31.1]
pl.plot(x,y,'bo-', linewidth=1.5)
pl.xlabel('The number of frequent itemsets.')
pl.ylabel('File size (MB)')
pl.grid(True)
pl.show()
'''

'''
x = [0.15,0.2,0.25,0.3,0.35,0.4]
y1 = [578,223,96,32,22,18]
y2 = [4.6,0.5,0.25,0.12,0.08,0.06]
y3 = [0.021,0.019,0.017,0.018,0.015,0.019]
y = [0.02,0.078,0.308,1.1,2.4,4.7,12.2,31.1]
pl.semilogy(x,y1,'bo-', linewidth=1.5, label='eclat+IDP')
pl.semilogy(x,y2,'rx-', linewidth=1.5, label='python-postprocess')
pl.semilogy(x,y3,'g+-', linewidth=1.5, label='pure eclat')
pl.xlabel('Minimum support.')
pl.ylabel('Time cost (s)')
pl.xlim(0.15,0.4)
pl.ylim(0,10000)
pl.legend(loc='upper left')
pl.grid(True)
pl.show()
'''

'''
x = [526,1638,5243,14853,29258,56368]
y = [18,22,32,96,223,578]
pl.plot(x,y,'bo-', linewidth=1.5)
pl.xlabel('The number of frequent itemsets.')
pl.ylabel('Time cost (s)')
pl.grid(True)
pl.show()
'''

'''
x = [0.1,0.15,0.2,0.25,0.3,0.35,0.4]
zoo = [1532,578,223,96,32,22,18]
vote = [230,80,71,48,39,27,16]
soybean = [258,169,146,116,129,87,61]
primary_tumor = [384,160,116,105,84,75,69]
pl.plot(x,zoo,'bo-', linewidth=1.5, label='zoo-1')
pl.plot(x,vote,'rx-', linewidth=1.5, label='vote')
pl.plot(x,soybean,'g+-', linewidth=1.5, label='soybean')
pl.plot(x,primary_tumor,'y*-', linewidth=1.5, label='primary-tumor')
pl.xlabel('Mininum support')
pl.ylabel('Time cost (s)')
pl.legend(loc='upper right')
pl.grid(True)
pl.show()
'''

x = [0.25,0.3,0.35,0.4]
fifa = [233.1,57.7,29.5,8.4]
prefixSpan = [98.4,27.5,17.2,6.3]
pl.plot(x,fifa,'bo-', linewidth=1.5, label='total')
pl.plot(x,prefixSpan,'rx-', linewidth=1.5, label='prefixSpan')
pl.xlabel('Mininum support')
pl.ylabel('Time cost (s)')
pl.legend(loc='upper right')
pl.grid(True)
pl.show()
