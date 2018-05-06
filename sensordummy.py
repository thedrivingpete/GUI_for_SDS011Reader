# -*- coding: utf-8 -*-
"""
Created on Thu May  3 21:17:45 2018

@author: Peter
"""

import random

class SensorDummy:
    """Dummy des Sensors zum Testen"""
    
    def __init__(self):
        pass

    def readValue( self ):
        value1  = float(int(random.random()*50))/10
        value2  = float(50+int(random.random()*50))/10
        return [value1, value2]