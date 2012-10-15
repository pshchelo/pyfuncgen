# -*- coding: utf-8 -*-
"""
Created on Sat Oct 06 22:37:19 2012

@author: Pavlo Shchelokovskyy
"""

from serial.tools.list_ports import comports

def list_serial():
    """Return a list of available serial ports in the form suitable to pass to pyserial"""
    seriallist = []
    for item in comports():
        seriallist.append(item[0])
    return seriallist
