import time
import includes
import os
import logging
import subprocess

from helper import clipInt

class AudioController():
    def _setVolume(self, value):
        tmp = includes.config["amixer"]["set"]
        tmp.append(f"{int(value)}% > /dev/null")
        subprocess.Popen(tmp, stdout=subprocess.PIPE)

    def _getVolume(self):

        p = subprocess.Popen(includes.config["amixer"]["get"], stdout=subprocess.PIPE)
        out = str(p.stdout.read())

        out = out.split("\\n")
        line = out[-2].split(" ")

        for item in line:
            if "%" in item:
                item = item.replace("[", "")
                item = item.replace("]", "")
                item = item.replace("%", "")
                return int(item)

    def volumeUp(self, *args, **kwargs):
        if self.isMuted:
            self.volume = self.lastVolume
            self.isMuted  = False

        self.volume = clipInt(self.volume + self.incVal, 0, 100)
        self._setVolume(self.volume)
        self.indicator.value = self.volume


    def volumeDown(self, *args, **kwargs):
        if self.isMuted:
            self.volume = self.lastVolume
            self.isMuted  = False

        self.volume = clipInt(self.volume - self.incVal, 0, 100)
        self._setVolume(self.volume)
        self.indicator.value = self.volume


    def setVolume(self, volume):
        self.volume = clipInt(volume, 0, 100)
        self._setVolume(volume)
        self.indicator.value = self.volume

    def _audioFadeout(self, t0, t1, t2, v0, v1, incVal):
        '''
        Audio fade out happens in 3 sections to allow for non linearity of volume
        All time values are given in seconds

        T0 = 0 to t0 --> in this time volume drops down to v0
        T1 = t0 to t1  -> in this time volime drops down to v1
        T2 = t1 to t2 -> in this time volume drops down to 0

        y = mx + b
        '''
        volume = self.getVolume()
        v0 = clipInt(v0, 0, volume)
        v1 = clipInt(v1, 0, v0)

        m0 = (v0-volume) / (t0)
        m1 = (v1-v0) / (t1-t0)
        m2 = (0-v1) / (t2-t1)

        b0 = volume
        b1 = v0 - m1 * t0
        b2 = v1 - m2 * t1


        cnt = 0
        last = False

        while not last:

            if cnt >= 0 and cnt < t0:
                tmpVol = cnt * m0 + b0
            elif cnt >= t0 and cnt < t1:
                tmpVol = cnt * m1 + b1
            elif cnt >= t1 and cnt < t2:
                tmpVol = cnt * m2 + b2
            elif cnt >= t2:
                tmpVol = 0
                last = True

            self.setVolume(tmpVol)
            cnt = cnt + incVal

            time.sleep(incVal)

    def mute(self):

        if not self.isMuted:
            if self.indicator.value != 0:
                self.lastVolume = self.volume
                self.volume = 0
                self.isMuted = True
            else:
                self.volumeUp()
        else:
            self.volume = self.lastVolume
            self.isMuted = False

        self.indicator.value = self.volume
        self.setVolume(self.volume)

    def getVolume(self, *args, **kwargs):
        tmp =  clipInt(self._getVolume(), 0, 100)
        self.indicator.value = tmp
        return tmp

    def fadeOut(self, *args, **kwargs):
        self._audioFadeout(10,12,15,60,40,0.1)
        return True

    def __init__(self, incVal, indicator, dryRun):
        self.incVal = incVal
        self.volume = self._getVolume()


        self.lastVolume = self.volume
        self.isMuted = False
        self.indicator = indicator

        self.indicator.value = self.volume
