import os
import sys


#Decorator for semaphore synchronization
#
def synchronized(lock):
    """ Synchronization decorator. """

    def wrapper(f):
        def syncFunc(*args, **kwargs):
            lock.acquire()
            try:
                return f(*args, **kwargs)
            finally:
                lock.release()
        return syncFunc
    return wrapper

'''
id:    this is an integer value defining the order in which files in playlist
        are played. It should be incremented sequentially without any gap in between
        The python app will check this and will not load the files of the json file

path:   this is the absolute path to the media file
name:   this is the name of the file, which will be displayed in the GUI
pre:    here we can define a set of commands that shall be executed before a
        video starts.
            - blackscreen: will start the video on black screen, waiting for
                         for the user to press the 'enter/ok' button to start
                        playback
post:   here we can define a set of commands that shall be executed after a
        video is played completely.
            - playnext: automatically plays the next file
            - repeat_once: automatically plays the next file
            - repeat_forever: automatically plays the next file
start: start the video from a specified time value in seconds.
'''
def createPlayListEntry(path, nodeId, start):
    tmp = {
        str(nodeId):{
            'path': path,
            'pre' : None,
            'post' : None,
            'start' : start,
        }
    }
    return tmp

#Sanity check for playlist object to ensure player core can process them
#
def checkPlaylist(playlist):
    if type(playlist) != dict:
        return ("PlayistCheck: playlist is not a dict",-4)

    for item in playlist:
        if len(playlist[item]) < 4:
            return ("PlayistCheck: playlist is empty",-5)

    try:
        #Check if its consecutive numbers, if key does not exist exception !
        for i in range(len(playlist)):
            tmp = playlist[str(i)]
    except:
        return ("PlaylistCheck: Indicies are not in sequential order", -1)

    try:
        #check if each element has all elements defined:
        for item in playlist:
            tmp = playlist[item]['path']
            tmp = playlist[item]['pre']
            tmp = playlist[item]['post']
            tmp = playlist[item]['start']
    except KeyError as e:
        return ("PlaylistCheck: [{}]".format(e), -2)

    try:
        #check if all files in the playlist exist
        for item in playlist:
            open(playlist[item]['path'])
    except:
        return ("PlaylistCheck: File does not exits [{}]".format(playlist[item]['path']), -3)

    return (0, 0)

#Clip int defined by min and max boundary
#
def clipInt(value, min, max):
    if value > max:
        return max

    if value < min:
        return min

    return value

#Rotate integer when overflow
#
def rotateInt(value, min, max):
    if value > max:
        return min

    if value < min:
        return max

    return value

#Helper to create correct parameters for the mpv player
#
def mpvParams(start, path, config):
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

        else:
            tmp.append(item)

    return tmp
