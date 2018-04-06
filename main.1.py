import numpy as np
import matplotlib.pyplot as plt
import sys, time, os
import random
from optparse import OptionParser

def func (x, tilt=0.1, offset=1.0):
    tilt   += random.uniform(0, 0.1)/10
    offset += random.uniform(0, 1)/10
    a = np.tan(np.deg2rad(tilt))
    b = offset
    return a*x + b 

if __name__ == "__main__":
    argvs = sys.argv  
    parser = OptionParser()
    parser.add_option("--tilt"  , dest="tilt"  , default=0.1)
    parser.add_option("--offset", dest="offset", default=1.0)
    opt, argc = parser.parse_args(argvs)

    dt = []
    px = np.linspace (0, 1000, 11)
    for x in px:
        dt.append ([x, func(x, opt.tilt, opt.offset)])
    dt = np.array(dt)
    a, b = np.polyfit(dt[:,0], dt[:,1], 1)
    print (np.rad2deg(np.arctan(a)), b)

    plt.figure()
    plt.scatter (dt[:,0], dt[:,1])
    plt.plot (px, a*px+b)
    #plt.show()
