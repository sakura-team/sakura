#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#Michael ORTEGA for STEAMER/LIG/CNRS- 23/07/2018

from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
import json
import threading

ws_cb_list = None

class EchoApplication(WebSocketApplication):
    def on_open(self):
        print("Connection: open")

    def on_message(self, message):
        if message:
            m = json.loads(message)
        else:
            return

        if m['key'] in ws_cb_list.keys():
            p = ''
            if 'data' in m.keys():
                p = m['data']
            back_message = ws_cb_list[m['key']](*p)
            if not back_message:
                back_message = m['key']
        else:
            print('Unknown message', m['key'])
            back_message = 'Unknown'
        if (m['key'] != 'image'):
            self.ws.send(json.dumps({'key': m['key'], 'value' :back_message}))
        else:
            self.ws.send(back_message)

    def on_close(self, reason):
        print('Connection: closed')


class ws_server():

    def __init__(self, ip = '', port = 1234):
        self.ip         = ip
        self.port       = port
        self.ea         = None

        print('Server created')

    def _run(self):
        self.ws = WebSocketServer((self.ip, self.port), Resource(OrderedDict([('/', EchoApplication)])))
        print('Server started')
        self.ws.serve_forever(1)

    def start(self, cbl):
        global ws_cb_list
        ws_cb_list = cbl

        self.ws = WebSocketServer((self.ip, self.port), Resource(OrderedDict([('/', EchoApplication)])))
        print('Server started')
        self.ws.serve_forever(1)

    def _stop(self):
        print('Server stopped')
        self.ws.close()
