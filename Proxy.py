import socket
from threading import Thread
from DecodeMask import *
import pyautogui as mouse
import json
import os
os.environ['DISPAY']=':0'



'''Use port 8080 in usendmii'''
'''change the ip in the end of the code'''
'''connect to http://'usendmii ip'/pc.html'''


mouse.FAILSAFE = False
mouse.PAUSE = 0


class Proxy2Server(Thread):
    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, 8080))

    def run(self):
        while True:
            data = self.server.recv(7780)
            if data:
                self.game.sendall(data)


class Game2Proxy(Thread):
    def __init__(self, host, port):
        super(Game2Proxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        self.game, addr = sock.accept()

    def run(self):
        x = 0
        y = 0
        state = False
        while True:

            data = self.game.recv(7780)

            if data:

                if data[0] == 129:
                    try:

                        mask = bytearray(data[4:8])
                        decoded = apply_mask(bytearray(data[8::]), mask)

                        status_dict = json.loads(str(decoded)[27::].replace('\\x00', '')[0:-3])
                     

                        if status_dict['hold'] == 256:

                            state = True
                        if status_dict['hold'] == 512:
                            state = False
                        # if status_dict['hold'] == 2048:
                        #
                        #     state2 = True
                        # if status_dict['hold'] == 1024:
                        #     state2 = False

                        # if state2:
                        #     if mouse.mouseDown:
                        #         mouse.mouseDown()
                        # else:
                        #     if mouse.mouseUp:
                        #         mouse.mouseUp()

                        if state:
                            if status_dict['tpX'] and status_dict['tpY']:
                                mouse.move(status_dict['tpX']-x, status_dict['tpY']-y)
                                x += status_dict['tpX']-x
                                y += status_dict['tpY']-y
                                state = True
                        else:
                            if status_dict['tpX']:
                                x = status_dict['tpX']
                            if status_dict['tpY']:
                                y = status_dict['tpY']
                            mouse.moveTo(x * 2.25, y * 2.25)
                    except:
                        pass
                self.server.sendall(data)


class Proxy(Thread):
    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        while True:
            print("[proxy({})] setting up".format(self.port))
            self.g2p = Game2Proxy(self.from_host, self.port)  # waiting for a client
            self.p2s = Proxy2Server(self.to_host, self.port)
            print("[proxy({})] connection established".format(self.port))
            self.g2p.server = self.p2s.server
            self.p2s.game = self.g2p.game
            self.g2p.start()
            self.p2s.start()


master_server = Proxy('0.0.0.0', 'put here the ip address that is in usendmii', 80)
master_server.start()
