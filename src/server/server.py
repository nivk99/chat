import select
import socket
import struct
import threading
import time
import sys
sys.path.append('../../')
import src.file.path as p
from src.server.serverfile import ServerFile
from src.server.servergui import ServerGui

threadLock = threading.Lock()
IP = "0.0.0.0"
# IP="10.102.2.194"
# socket.gethostbyname(socket.gethostname())
PORT = 5544
MSG = struct.Struct('!I')


def red_message(soc) -> str:
    mes = soc.recv(MSG.size)
    mesage_len = MSG.unpack(mes)[0]
    return soc.recv(mesage_len).decode()


def write_message(soc, message) -> None:
    message = message.encode()
    message_len = len(message)
    message = MSG.pack(message_len) + message
    soc.sendall(message)


class Server:
    def __init__(self, port: int = PORT, ip: str = IP,test: bool = False) -> None:
        self._port_file = 55000
        self._port: int = port
        self._ip: str = ip
        self._clients = {}
        self._sockets = []
        self._file_names = p.get_path()
        self._root_path_file = p.get_root_path() + "\\"
        self._file_name_read: str = ""
        self._server_socket: socket = None
        self._down = False
        self._test: bool = test
        if not self._test:
            print("!")
            self._gui: ServerGui = ServerGui(self)
            self.starting_path()
            self.start_mode()
            self.starting_Processes()

    def get_soc(self) -> socket:
        return self._server_socket

    def get_port(self) -> int:
        return self._port

    def get_ip(self) -> str:
        return self._ip

    def set_port(self, port: int) -> None:
        if port == "" or port == None:
            port = PORT
        self._port = port

    def set_ip(self, ip: str) -> None:
        if ip == "" or ip == None:
            ip = IP
        self._ip = ip

    def starting_path(self) -> None:
        self._file_names.remove("__pycache__")
        self._file_names.remove("path.py")
        self._file_names.append("\n")

    def starting_Processes(self) -> None:
        # thread_server_file = threading.Thread(target=self.file_Protocol)
        gui_thread = threading.Thread(target=self.start_gui)
        receive_thread = threading.Thread(target=self.receive)
        gui_thread.start()
        # thread_server_file.start()
        time.sleep(0.5)
        receive_thread.start()

    def start_mode(self) -> None:
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((self._ip, int(self._port)))
            self._server_socket.listen()
            self._clients["server"] = self._server_socket
            self._sockets.append(self._server_socket)
        except Exception as e:
            print(e)
            self._gui.gui_error("Login problem",
                                "Check your internet connection again!\n" + "Check the  ID and port number!")
            exit(0)

    def get_name(self, client) -> str:
        for v in self._clients.keys():
            if self._clients[v] is client:
                return v

    def start_gui(self) -> None:
        self._gui.ranGui()

    def receive(self) -> None:
        while self._gui.get_running():
            ready, _, _ = select.select(self._sockets, [], [])
            for user in ready:
                try:
                    if user is self._server_socket:
                        (client_socket, client_address) = user.accept()
                        self._gui.writing_window("New client joined!\n")
                        self._sockets.append(client_socket)
                        self._gui.writing_window(f"clent {client_address} connected\n")
                    else:
                        self.send_message(user)
                except Exception:
                    self._gui.stop_gui()
                    exit(0)

    def sent_all(self, msg, client) -> None:
        for connection in self._sockets:
            if connection is not client and connection is not self._server_socket:
                write_message(connection, msg)

    def send_message(self, client) -> None:
        try:
            data: str = red_message(client)
        except Exception:
            for v in self._clients.keys():
                if self._clients[v] is client:
                    del self._clients[v]
                    self._sockets.remove(client)
                    self.sent_all(f"client {v} left\n", [])
                    self._gui.writing_window(f"clent {client.getpeername()} left\n")
                    client.close()
                    break
            return

        if str(data).startswith("connect"):
            st = data.replace("connect ", '')
            print(st)
            self._clients[st] = client
            self.sent_all(f"client {st} connected\n", client)
            return
        if data[0:8] == "download":
            if data[9:] not in self._file_names:
                return
            write_message(client, "port!" + str(self._port_file))
            list_data = data.split()
            self._file_name_read = self._root_path_file + "" + list_data[1]
            self._port_file += 1
            thread_server_file = threading.Thread(target=ServerFile, args=(self._file_name_read, self._port_file - 1,))
            if self._port_file > 55016:
                self._port_file = 55000
            thread_server_file.start()
            self._down = True
            self._gui.writing_window(f"User {self.get_name(client)}  downloads {list_data[1]} file\n")
            return
        if data[0:] == "get_users":
            self._gui.writing_window(f"User {self.get_name(client)} want to get the list of online\n")
            for v in self._clients.keys():
                if self._clients[v] is not client:
                    if v == "server":
                        write_message(client, "_____get_users__________\n")
                    else:
                        write_message(client, (v + ", "))
            write_message(client, '\n')
            return
        if data[0:] == "get_list_file":
            self._gui.writing_window(f"User {self.get_name(client)} want to get the list of file\n")
            write_message(client, "_____get_list_file__________\n")
            write_message(client, '\n'.join(self._file_names))
            return

        if data[0:] == "disconnect":
            print("disconnect")
            for v in self._clients.keys():
                if self._clients[v] is client:
                    del self._clients[v]
                    self._sockets.remove(client)
                    self.sent_all(f"client {v} left\n", [])
                    self._gui.writing_window(f"clent {client.getpeername()} left\n")
                    client.close()
                    break
            return

        if data[0:7] == "set_msg":
            ms = data.split()
            for v in self._clients.keys():
                if ms[1] == v:
                    print(v)
                    write_message(self._clients[v], (self.get_name(client) + " send: " + ms[2] + "\n"))
                    write_message(client, ("you: " + ms[2] + "\n"))
                    return
        self.sent_all(str(self.get_name(client) + " send: " + data + "\n"), client)
        write_message(client, ("you: " + data + "\n"))

print(IP)
se = Server()
