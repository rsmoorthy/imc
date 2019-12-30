#from player import *
#from vlc_player import Player
from mpv_player import Player
from screensaver import *
import os
import logging
import json
from kivy.utils import get_color_from_hex as hexColor


#Merge default config with config file.
#Default config has all elements that can be defined in the application
#cfgFile can overrride these values but cannot add any new items which do not
#exist in defautlCfg. For example cfg gile cannot just change a songle key value
#pair to a nother dictionary with multiple key value pairs.
#
# So how to do this:
# Check if key of defaultCfg is also contained in cfgFile, if not we can skip to next
# if yes we have to merge defaultCfg and cfgFile.
# Config files do use nested dictionaries, but we allow only two levels
# This means a value of a key can be another dictionary but a key of the child
# can only have one value.
#
def mergeConfig(defaultConf, configFile):
    for key in defaultConf:
        if key in configFile:#Key exist in cfgFile so we need to merge:
            if type(defaultConf[key]) == dict:
                defaultConf[key].update(configFile[key])
            else:
                defaultConf[key] = configFile[key]

    return defaultConf


#Just make sure its not causing error redefininf build-in
defined = True

#Color definition
colors = {
    'gray': (0.4,0.4,0.4,1),
    'darkgray': (0.2,0.2,0.2,1),
    'darkestgray': (0.1,0.1,0.1,1),
    'defaultGray': hexColor('#303030'),
    'btngray': hexColor('#575757'),
    'red': (0.5,0.0,0.0,0.8),
    'lightred': (0.8,0.2,0.2,0.3),
    'black' : (0, 0, 0, 1),
    'darkblue': hexColor('#2c2c57'),
    'blue' : (0.5, 0.5, 1, 1),
    'oldblue': hexColor('#0f85a5'),
    'lightblue' : hexColor('#035972'),
    'orange' : (1,0.5,0.2,0.5),
    'ishaOrange' : hexColor('#F15B28'),
    #error message colors
    'errMsgHead' : hexColor('#6c5d53'),
    'errMsgText' : hexColor('#ffffff'),
    'errMsgSidebar' : hexColor('#483e37'),
    'errMsgContent' : hexColor('#917c6f'),
    #warning message colors
    'warnMsgHead' : hexColor('#536c5d'),
    'warnMsgText' : hexColor('#ffffff'),
    'warnMsgSidebar' : hexColor('#37483e'),
    'warnMsgContent' : hexColor('#6f917c'),
    #info message colors
    'infoMsgHead' : hexColor('#216778'),
    'infoMsgText' : hexColor('#ffffff'),
    'infoMsgSidebar' : hexColor('#164450'),
    'infoMsgContent' : hexColor('#2c89a0'),
    'msgBorder' : hexColor('#303030'),
    # #error message colors
    # 'errMsgHead' : hexColor('#ffc8be'),
    # 'errMsgText' : hexColor('#000000'),
    # 'errMsgSidebar' : hexColor('#fda798'),
    # 'errMsgContent' : hexColor('#ffd8d2'),
    # #warning message colors
    # 'warnMsgHead' : hexColor('#ffe78d'),
    # 'warnMsgText' : hexColor('#000000'),
    # 'warnMsgSidebar' : hexColor('#ffd965'),
    # 'warnMsgContent' : hexColor('#ffeeaa'),
    # #info message colors
    # 'infoMsgHead' : hexColor('#5599ff'),
    # 'infoMsgText' : hexColor('#000000'),
    # 'infoMsgSidebar' : hexColor('#2a7fff'),
    # 'infoMsgContent' : hexColor('#80b3ff'),
    # 'msgBorder' : hexColor('#666666')
}

styles = {
    #colors
    'defaultEnaColor': colors['oldblue'],
    'defaultBg': colors['black'], #TODO: still used?
    'enaColor0': colors['oldblue'],
    'enaColor1': colors['orange'],
    'warning': colors['lightred'],
    'defaultFiller': colors['lightblue'],
    #'itemColor0': colors['darkgray'],
    'itemColor0': colors['black'],
    'itemColor1': colors['black'],
    #'itemColor1': colors['darkestgray'],
    'volumeIndicatorBG': colors['gray'],
    'volumeIndicatorColor': colors['blue'],
    'headerColor0': colors['darkblue'],
    'headerColor1': colors['gray'],
    #sizes
    'selectItemHeight': 80,
    "fontSize": "25sp",
    "playlistHeadHeight": 40,
    #Dailogs
    'dialogBorderHeight': 5,
    #Playlist color Indicator
    'pListIndiactorHeight':25,
    'plistIndicatorColor':colors['darkblue']
}

#Media player instance we can use in all modules
player = Player()

#configuration file
defaultConf = {
    "tmpdir": "/tmp",
    "music": {
        "rootdir": "/mnt/Ishamedia",
        "types": "mp3,wav",
        "autoplay": "false"
    },
    "playlist": {
        "rootdir": "/mnt/Ishamedia",
        "types": "json"
    },
    "video": {
        "rootdir": "/mnt/Ishamedia",
        "types": "mp4",
        "autoplay": "false"
    },
    "settings": {
        "osdTime": 10,
        "runtimeInterval": 1,
        "screensaverTime": 5,
        "hdmiBoost": 4,
        "audioSource":0,
        "hdmiResolution":0
    },
    "httpServerIp":{
        "ip":"127.0.0.1",
        "port":"11111"
    },
    "mpv":{
        "parameters":[
            "mpv",
            "--fs",
            "--start=+{start}",
            "--no-border",
            "--no-input-default-bindings",
            "{path}",
            "--really-quiet",
            "--no-osc",
            "--no-input-terminal",
            #"-config={config}",
            "--input-ipc-server={socket}"
        ]
    },
    "ipcOsdPort":40001,
    "ipcWmPort":40002,
    "hdmiCfgPath":"/tmp/imc_hdmi.txt", #TODO needs to point to boot dir of pi

}

syspath = os.path.dirname(os.path.realpath(__file__))
cfgPath = os.path.join(syspath,'config.json')
configFile = {}

if os.path.exists(cfgPath):
    with open(cfgPath) as config_file:
        configFile = json.load(config_file)

#config = mergeConfig(defaultConf, configFile)
config = mergeConfig(defaultConf, configFile)


def writeJson(path, dict):
        f = open(path, "w")
        f.write(json.dumps(dict, sort_keys=True, indent=4))
        f.close()

def writeConfig():
    writeJson(cfgPath, config)

#Global instance of screen saver
screenSaver = None #will be initialized by main-menu

#database, bsically a json file which we read and write
dbPath = os.path.join(syspath, "resources", "database.json") #TODO: must be in the /opt/ somewhere as it is non volatile
db = None
try:
    with open(dbPath) as dbFile:
        db = json.load(dbFile)
except:
    f = open(dbPath, "w+")
    f.write('''{
                "runtime":0
                }''')
    f.close()

    with open(dbPath) as dbFile:
        db = json.load(dbFile)


def writeDb():
    writeJson(dbPath, db)

#
# Some utilities and helpers
#
def clipInt(value, min, max):
    if value > max:
        return max

    if value < min:
        return min

    return value

def rotateInt(value, min, max):
    if value > max:
        return min

    if value < min:
        return max

    return value


def isRemoteCtrlCmd(cmd):
    if not 'cmd' in cmd:
        return False

    return True


def mpvParams(start, path):
    tmp = []
    mpvParams = config['mpv']['parameters']

    for item in mpvParams:

        if "{start}" in item:
            tmp.append(item.format(start=start))

        elif "{path}" in item:
            tmp.append(item.format(path=path))

        elif "{socket}" in item:
            sock = os.path.join(config['tmpdir'], 'socket')
            tmp.append(item.format(socket=sock))

        # elif "{configFile}" in item:
        #     item = item.format(configFile=config)
        else:
            tmp.append(item)

    return tmp
