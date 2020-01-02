import platform
import  http.server
import json
import logging
import threading

import includes

from player_core import PlayerCore
from json_handler import _jsonErrResponse
from json_handler import _jsonHandler as jsonHandler
from json_handler import ERR_KEY, ERR_VALUE, ERR_MISSING_PARAMS, ERR_METHOD_NOT_FOUND, ERR_PERMISSION_DENIED

cmdCallback = None





def _cmdCallback(self, data):
    return cmdCallback(data)

class WebServer(http.server.BaseHTTPRequestHandler, object):
    serverSemaphore = threading.Semaphore()

    def _jsonCmdCallback(self, data):
        """
        This function is the only function that has control over the application
        As this is the http server callback where recieved json commands will be
        passed towards. All other modules should request functions via the json
        rpc server with local socket connection. This way handling race conditions
        remote and local control will be eaiser.

        This is thread save so it cannot only be called from the server but from
        all components within the main menu if they want to. For example "+", "-"
        and mute button are calling this function so volume can potentially be set with less
        latency.
         """
        self.serverSemaphore.acquire()

        logging.debug("MenuMain: req = {}".format(data))

        #check mandatory fields for each JSON request
        method = None
        jsonId = None
        params = None


        for attribute in data:
            if attribute == "method":
                method = data['method']
            elif attribute == "id":
                jsonId = data['id']
            elif attribute == "params":
                params = data['params']

        logging.debug("MenuMain: method = {} | id = {} | params = {}".format(method, jsonId, params))

        if jsonId is None or method is None:
            logging.debug("MenuMain: jsonId or Method not defined in request")
            msg = "id and/or method not defined in request"
            resp = _jsonErrResponse(jsonId, -1, msg)
            method = "None" # make sure no execution happens in the next steps

        if method in jsonHandler:
            logging.error(f"Thomas: {jsonHandler[method]}")
            resp = jsonHandler[method](jsonId, params)

        elif "Input." in method:
            tmp = method.split('.')
            if len(tmp) == 2:
                resp = jsonHandler["Input"](jsonId, tmp[1])
            else:
                msg = "Input function not defined properly"
                resp = _jsonErrResponse(jsonId, ERR_VALUE, msg)
        elif method == "IshaPi.SetProperty":
            if 'value' in data:
                resp = jsonHandler['IshaPi.ScreenSaver'](jsonId, data['value'])
            else:
                msg = "IshaPi Property has no value...."
                resp = _jsonErrResponse(jsonId, ERR_VALUE, msg)

        else:
            logging.debug("MenuMain: json handler not found")
            msg = "method not found...."
            resp = _jsonErrResponse(jsonId, ERR_METHOD_NOT_FOUND, msg)

        self.serverSemaphore.release()
        return resp


    def do_GET(self):
        self.send_response(404)

    def do_POST(self):
        logging.debug("WebServer: Received post request...")
        if 'content-length' not in self.headers:
            return self.send_response(404)

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        self._post_data = self.rfile.read(content_length)

        pd = json.loads(self._post_data)
        ret = self._jsonCmdCallback(pd)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.wfile.write(json.dumps(ret).encode())

    # def __init__(self, *args, **kwargs):
    #     super(WebServer, self).__init__(*args, **kwargs)
    #     self.serverSemaphore = threading.Semaphore()

#
# For Standalone testing only
#
class Main:
    def __init__(self):
        includes.playerCore = PlayerCore()
        httpd = http.server.HTTPServer(('127.0.0.1', 11111), WebServer)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            httpd.server_close()

if (__name__ == "__main__"):
    logging.basicConfig(level=logging.DEBUG)
    Main()
