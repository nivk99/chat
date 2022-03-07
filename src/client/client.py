import socket
import struct
import threading
import time
import sys
sys.path.append('../../')
from src.client.clientfile import ClientFile
from src.client.clientgui import ClientGui
threadLock = threading.Lock()
MSG = struct.Struct('!I')
PORT = 5544
HOST = "127.0.0.1"
# HOST= "10.102.2.194"

# socket.gethostbyname(socket.gethostname())

def red_message(soc) -> str:
    mes = soc.recv(MSG.size)
    mesage_len = MSG.unpack(mes)[0]
    return soc.recv(mesage_len)


def write_message(soc, message) -> None:
    message = message.encode()
    message_len = len(message)
    message = MSG.pack(message_len) + message
    soc.sendall(message)


class Client:
    def __init__(self, port: int = PORT, host: str = HOST, test: bool = False) -> None:
        self._port:int = port
        self._host:str = host
        self._name:str = ""
        self._socket:socket = None
        self._protocolo_file: ClientFile = None
        self._file_name:str = ""
        self._port_file:int = 0
        self._test:bool = test
        if self._test == False:
            self._gui: ClientGui = ClientGui(self)
            self.start_mode()
            self.start_thread()

    def get_soc(self) -> socket:
        return self._socket

    def get_name(self) -> str:
        return self._name

    def get_port(self) -> int:
        return self._port

    def get_ip(self) -> str:
        return self._host

    def set_name(self, name) -> None:
        if not name == "" and not name == None:
            self._name = name

    def set_ip(self, ip) -> None:
        if not ip == "" and not ip == None:
            self._host = ip

    def set_port(self, port) -> None:
        if not port == "" and not port == None and not port < 123 and not port > 65535:
            self._port = port

    def start_thread(self) -> None:
        gui_thread = threading.Thread(target=self.start_gui)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        receive_thread.start()

    def start_mode(self) -> None:
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self._host, int(self._port)))
            write_message(self._socket, ("connect " + self._name))
        except Exception as e:
            print(e)
            self._gui.gui_error("Login problem",
                                "Check your internet connection again!+\n" + "Check the server ID and port number!")
            exit(0)

    def send_message(self, message) -> None:
        write_message(self._socket, message)

    def start_gui(self) -> None:
        self._gui.ranGui()

    def file_Protocol(self, de, list_down) -> None:
        threadLock.acquire()
        write_message(self._socket, list_down)
        time.sleep(0.3)
        if self._gui.get_running():
            self._protocolo_file = ClientFile(de, self._port_file, self._host, self._gui)
        threadLock.release()

    def download(self, txt_Server, txt_Client) -> None :
        sr = txt_Server.get()
        de = txt_Client.get()
        txt_Server.delete(0, "end")
        txt_Client.delete(0, "end")
        if sr == "" or sr == None or len(sr) == 0 or de == "" or de == None or len(de) == 0:
            return
        list_down = "download" + " " + sr
        thread_server_file = threading.Thread(target=self.file_Protocol, args=(de, list_down,))
        thread_server_file.start()

    def write_msg(self, txt_to, txt_Message) -> None:
        to = txt_to.get()
        message = txt_Message.get()
        if len(to) != 0:
            message = "set_msg " + to + " " + message
            txt_to.delete(0, "end")
        write_message(self._socket, message)
        txt_Message.delete(0, "end")

    def receive(self) -> None:
        while self._gui.get_running():
            try:
                if self._gui.get_gui_ran():
                    message = red_message(self._socket)
                    if message[0:5].decode() == "port!":
                        self._port_file = int(message[5:])
                    else:
                        self._gui.writing_window(message)
            except ConnectionAbortedError:
                break
            except Exception as e:
                print(e)
                self._gui.stop_gui()
                break


if __name__ == '__main__':
    cl = Client()
