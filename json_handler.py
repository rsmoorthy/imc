import includes
import os
import subprocess
import logging

ERR_MISSING_PARAMS = -2
ERR_METHOD_NOT_FOUND = -3
ERR_KEY = -4
ERR_VALUE = -5
ERR_PERMISSION_DENIED = -5

_jsonHandler = {}
_systemCallbacks = {}

# ------------------------------------------------------------------------------
# Decorators
def _addHandler(url):
    def inner_decorator(f):
        _jsonHandler[url] = f
        return f
    return inner_decorator

def _addJsonSystemcall(url):
    def inner_decorator(f):
        _systemCallbacks[url] = f
        return f
    return inner_decorator

def _jsonHandlerCheck(handler):
    def wrapper(jsonId, params):
        if params is None:
            msg = "params not specified"
            resp = _jsonErrResponse(jsonId, ERR_MISSING_PARAMS, msg)
            return resp
        try:
            return handler(jsonId, params)

        except KeyError as e:
            msg = "key not correct [{}]".format(e)
            resp = _jsonErrResponse(jsonId, ERR_KEY, msg)
            return resp

    return wrapper

#-------------------------------------------------------------------------------
# Pre defined error response
def _jsonErrResponse(id, code, message):
    ret = {}
    ret['error'] = {}
    ret['error']['code'] = code
    ret['error']['message'] = message
    ret['id'] = id
    ret['jsonrpc'] = "2.0"
    return ret

#-------------------------------------------------------------------------------
# Json command handlers
#
@_addHandler("Files.GetDirectory")
@_jsonHandlerCheck
def _filesGetDirectory(jsonId, params):
    directory = None
    media = None
    properties = None

    directory = params['directory']
    media = params['media']
    properties = params['properties']

    if media != "video" and media != "music":
        msg = "vaule media can only be 'video' or 'music' value"
        resp = _jsonErrResponse(jsonId, server.ERR_VALUE, msg)
        return resp

    if directory.startswith(includes.config[media]['rootdir']):
        dirContent = os.listdir(directory)
        tmp = []
        types = includes.config[media]['types']
        types = tuple(types.split(','))

        #Only return video or music files and directories
        for item in dirContent:
            if os.path.isdir(item):
                tmp.append(itemm)
            elif item.lower().endswith(types):
                tmp.append(item)

        tmp.sort()

        files = []
        for item in tmp:
            file = os.path.join(directory,item)
            if not os.path.exists(file):
                continue


            filetype = "file"
            if os.path.isdir(file):
                filetype = "directory"

            label = os.path.dirname(item)
            size = os.path.getsize(file)

            duration = "TODO: needs to be implemented"
            type = "unknown"

            tmpFile = {}
            tmpFile['file'] = file
            tmpFile['filetype'] = filetype
            tmpFile['label'] = label
            tmpFile['size'] = size
            tmpFile['duration'] = duration
            tmpFile['type'] = type
            files.append(tmpFile)

        resp = {}
        resp['id'] = jsonId
        resp['jsonrpc'] = "2.0"
        resp['result'] = {}
        resp['result']['file'] = files

        return resp

    else:
        msg = "permission denied"
        return _jsonErrResponse(jsonId, server.ERR_PERMISSION_DENIED, msg)


@_addHandler("Application.SetVolume")
@_jsonHandlerCheck
def _applicationSetVolume(jsonId, params):
    if params is None:
        msg = "params not specified"
        resp = _jsonErrResponse(jsonId, ERR_MISSING_PARAMS, msg)
        return resp

    try:
        vol = params['volume']
        subprocess.run(['amixer', 'sset', '\'Master\'', str(vol), '% > /dev/null'])
        resp = {}
        resp['id'] = jsonId
        resp['jsonrpc'] = "2.0"
        resp['result'] = vol
        return resp

    except KeyError as e:
        msg = "key not correct [{}]".format(e)
        resp = _jsonErrResponse(jsonId, ERR_KEY, msg)
        return resp


@_addHandler("Application.GetProperties")
@_jsonHandlerCheck
def _applicationGetProperties(jsonId, params):
    properties = params['properties']
    resp = {}
    resp['result'] = {}

    volume = _systemCallbacks['getVolume']()
    for item in properties:
        if item == "volume":
            resp['result']['volume'] = volume
        elif item == "muted":
            resp['result']['muted'] = (volume == 0)

    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    return resp


@_addHandler("Player.GetItem")
def _playerGetItem(jsonId, params):
    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"

    result = {}
    label = includes.playerCore.getCurrentFile()
    result['item'] = {"label":label, "type":"unknown"}
    resp['result'] = result
    return resp


@_addHandler("Player.GetProperties")
@_jsonHandlerCheck
def _playerGetProperties(jsonId, params):
    def timeCalc(tmp):
        hour = int(tmp / 3600)
        min = int((tmp - (hour*3600)) / 60)
        sec = int((tmp - hour*3600 - min * 60))
        return (hour, min, sec, 0)

    properties = params['properties']
    resp = {}
    result = {}
    totalTime = includes.playerCore.getTotalTime()
    runtime = includes.playerCore.getRuntime()

    for item in properties:
        if item == "time":
            hour, min, sec, millisecond = timeCalc(runtime)
            result['time']={"hours":hour,"minutes":min, "seconds":sec, "millisecond":0}
        elif item == "speed":
            result['speed'] = 1 #fixed speed we do not change speed of player
        elif item == "percentage":
            if runtime >= totalTime and totalTime != 0:
                result['percentage'] = runtime / totalTime
            else:
                result['percentage'] = 100
        elif item == "totaltime":
            hour, min, sec, millisecond = timeCalc(totalTime)
            result['totaltime']={"hours":hour,"minutes":min, "seconds":sec, "millisecond":0}

    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = result
    return resp


@_addHandler("Input")
def _input(jsonId, params):
    #remapping imc name convention to Kody for compatibility of Mobile app
    if params == "select":
        params = "enter"

    logging.warning("JsonHandler: _input: we need to define how to execute key presses") #TODO
    #self._keyDown((-1, params.lower()))

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = "OK"

    return resp


@_addHandler("Input.ExecuteAction")
@_jsonHandlerCheck
def _inputExecuteAction(jsonId, params):
    action = params['action']

    if action == "mute":           #TODO: we need to make mute toggle command available
        try:
            _systemCallbacks['_cmdMuteToggle'](None, None)
        except:
            pass

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = "OK"

    return resp


@_addHandler('System.Reboot')
def _systemReboot(jsonId, params):
    os.system("sudo reboot")


@_addHandler('Player.Open')
@_jsonHandlerCheck
def _playerOpen(jsonId, params):
    item = params['item']
    file = item['file']

    dirname = os.path.dirname(file)
    isVideoDir = dirname.startswith(includes.config['video']['rootdir'])
    isMusicDir = dirname.startswith(includes.config['music']['rootdir'])

    if (isVideoDir or isMusicDir) and os.path.isfile(file):
        includes.playerCore.startSingle(file, 0)

        resp = {}
        resp['id'] = jsonId
        resp['jsonrpc'] = "2.0"
        resp['result'] = "OK"

        return resp

    else:
        msg = "music/video file does not exist, check path value..."
        resp = _jsonErrResponse(jsonId, ERR_VALUE, msg)
        return resp


@_addHandler('Player.PlayPause')
def _playerPlayPause(jsonId, params):
    includes.playerCore.togglePause(None)

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = {'speed':0}

    return resp

@_addHandler('Player.Play')
def _playerPlayPause(jsonId, params):
    includes.playerCore.play(None)

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = {'speed':0}

    return resp

@_addHandler('Player.Pause')
def _playerPlayPause(jsonId, params):
    includes.playerCore.pause(None)

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = {'speed':0}

    return resp


@_addHandler('Player.Stop')
def _playerStop(jsonId, params):
    includes.playerCore.stop(None)

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = "OK"
    return resp


@_addHandler("Player.IsPlaying")
def _playerIsPlaying(jsonId, params):
    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = str(includes.playerCore.isPlaying())
    return resp

@_addHandler("Player.IsPaused")
def _playerIsPlaying(jsonId, params):
    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = str(includes.playerCore.isPaused())
    return resp

@_addHandler("Player.IsPaused")
def _playerIsPlaying(jsonId, params):
    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = str(includes.playerCore.isPaused())
    return resp

@_addHandler("Player.Seek")
@_jsonHandlerCheck
def _playerSeek(jsonId, params):
    tstart = int(params['start'])

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = str(includes.playerCore.seek(tstart))
    return resp


@_addHandler('IshaPi.ScreenSaver')
def _ishaPiEnableSSaver(jsonId, value):
  #TODO: IshaPiSetProperty should be removed in future version, right
  #now its only used like this in order to not change the pi app
    if value == 1:
        inclides.screenSaver.start(None)
    else:
        inclides.screenSaver.resetTime()

    resp = {}
    resp['id'] = jsonId
    resp['jsonrpc'] = "2.0"
    resp['result'] = "OK"
    return resp
