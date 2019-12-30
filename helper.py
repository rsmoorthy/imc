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
        int(nodeId):{
            'path': path,
            'pre' : None,
            'post' : None,
            'start' : start,
        }
    }
    return tmp


def checkPlaylist(playlist):
    try:
        #Check if its consecutive numbers, if key does not exist exception !
        for i in range(len(playlist)):
            tmp = playlist[i]
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
