#from player import *
#from vlc_player import Player
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
    'white': (1,1,1,1),
    'gray': (0.4,0.4,0.4,1),
    'black' : (0, 0, 0, 1),
    'darkblue': hexColor('#2c2c57'),
    'lightblue' : hexColor('#035972'),
    #These are the main color used for the GUI
    'oldblue': hexColor('#0f85a5'),
    'imcBlue': hexColor('#063541'), #used for lines, deviders etc
    'imcLigthGray': hexColor('#3d3d3d'), #used for lined, divider etc
    'imcDarkGray': hexColor('#2c2c2c'), #used for lined, divider etc
}

styles = {
    #colors
    'defaultEnaColor': colors['oldblue'],
    'defaultBg': colors['black'], #TODO: still used?
    'enaColor0': colors['oldblue'],
    'defaultFiller': colors['lightblue'],
    'menuBarColor': colors['imcDarkGray'],
    'itemColor0': colors['black'], #FileList fiew even row color
    'itemColor1': colors['black'], #Filelist view odd row color
    #sizes
    'selectItemHeight': 60,
    "fontSize": "25sp",
    "playlistHeadHeight": 40,
    #Dailogs
    'dialogBorderHeight': 5,
    #Playlist color Indicator
    'pListIndiactorHeight':25,
    'plistIndicatorColor':colors['darkblue'],
    #dialog message colors
    'dialogMsgHead' : colors['imcDarkGray'],
    'dialogMsgText' : colors['white'],
    'dialogMsgContent' : colors['imcLigthGray'],
}


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
        "types": "imc,json"
    },
    "video": {
        "rootdir": "/mnt/Ishamedia",
        "types": "mp4",
        "autoplay": "false"
    },
    "settings": {
        "osdTime": 5,
        "runtimeInterval": 1,
        "screensaverTime": 5,
        "hdmiBoost": 4,
        "audioSource":0,
        "hdmiResolution":0,
        "volIncVal":5,
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
changeFooterColor = None
playerCore = None

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
    try:
        writeJson(dbPath, db)
    except:
        logging.error("Inludes: not able to write database!!!")
        pass
