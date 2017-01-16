
DEBUG = False

import os
import sys

class Beacon(object):

    def __init__(self, macAddr, udid, major, minor, txPower, rssi):
        self.macAddr=macAddr
        self.udid=udid
        self.major=major
        self.minor=minor
        self.txPower=txPower
        self.rssi=rssi
