
import time
import includes
import os

def setVolume(value):
    os.system("amixer sset Master {}% > /dev/null".format(int(value)))

def getVolume():
    import subprocess
    p = subprocess.Popen(["amixer", "sget", "Master"], stdout=subprocess.PIPE)
    out = str(p.stdout.read())

    out = out.split("\\n")
    line = out[-2].split(" ")

    for item in line:
        if "%" in item:
            item = item.replace("[", "")
            item = item.replace("]", "")
            item = item.replace("%", "")
            return int(item)


def audioFadeout(t0, t1, t2, v0, v1, incVal):
    '''
    Audio fade out happens in 3 sections to allow for non linearity of volume
    All time values are given in seconds

    T0 = 0 to t0 --> in this time volume drops down to v0
    T1 = t0 to t1  -> in this time volime drops down to v1
    T2 = t1 to t2 -> in this time volume drops down to 0

    y = mx + b
    '''
    volume = getVolume()
    v0 = includes.clipInt(v0, 0, volume)
    v1 = includes.clipInt(v1, 0, v0)

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

        os.system("amixer sset Master {}% > /dev/null".format(int(tmpVol)))
        cnt = cnt + incVal

        time.sleep(incVal)


if __name__ == "__main__":
    #getVolume()
    audioFadeout(10, 12, 15, 60, 40, 0.1)
