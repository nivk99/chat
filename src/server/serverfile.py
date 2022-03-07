
import pickle
import socket
import time
import os
ip = "0.0.0.0"
port = 9989
time_out = 6
fragment_size = 1024

class UDP_MSG:
    def __init__(self, seq, dat):
        self.seq = seq
        self.dat = dat
class ServerFile:

    def __init__(self,file_name,port):
        self._test=False
        self._port=port
        self._file_name=file_name
        self.window_size = 5
        self.packet_num = -1
        self.seq_num = 0
        self.data_buffer = {}
        self.max_time_out = 3
        self.number_time_out = 0
        self.f = None
        self._add_window = True
        self._linar = False
        self._sum_ack = 0
        chek=True
        self.len_data=0
        try:
            self.UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDP_socket.bind((ip, self._port))
        except Exception as e:
            print(e)
            chek =False
        if chek:
            self.UDP_socket.settimeout(time_out)
            self.ran()
            self.f.close()
            self.UDP_socket.close()


    def ran(self):
        msg, client_addr = self.UDP_socket.recvfrom(fragment_size)
        if msg.decode() == "SYN":
            self.send_request("SYN_ACK".encode(), client_addr)
        else:
            return
        clint_response = self.get_response()
        if clint_response == "ACK":
            file_size = os.path.getsize(self._file_name)

            # Send window
            self.send_request(str(self.window_size).encode(), client_addr)
            server_response = self.get_response()
            if server_response == "NACK" or server_response != "ACK":
                return
            print("file", file_size)
            self.send_request(str(file_size).encode(), client_addr)
            server_response = self.get_response()
            if server_response != "ACK":
                return
            self.f = open(self._file_name, "rb")
            data = self.f.read(fragment_size)
            final_packet = int(file_size / fragment_size)  # Index of final packet
            boo = True
            self.loop(final_packet, client_addr, data,file_size ,boo)
        else:
            return

    def loop(self, final_packet, client_addr, data,file_size ,boo):
        while True:
            if self.packet_num == final_packet:
                print("ACK_END")
                MSG = UDP_MSG(-2, "ACK_END")
                b_msg = pickle.dumps(MSG)
                self.send_request(b_msg, client_addr)
                bo = self.check(client_addr)
                if bo == False:
                    return
                print("FIN")
                message = self.get_response()
                if message == "FIN":
                    self.fin(client_addr)
                    message = self.get_response()
                    if message == "ACK":
                        time.sleep(0.1)
                        return
            if self.seq_num < self.window_size:
                self.packet_num += 1
                self.seq_num += 1
                self.data_buffer[self.packet_num]=data
                # ////////////////////////////////// test
                if self._test:
                    if self.packet_num == 5 or self.packet_num == 6 or self.packet_num == 7:
                        data = self.f.read(fragment_size)
                        continue
                MSG = UDP_MSG(self.packet_num, data )
                b_msg = pickle.dumps(MSG)
                self.send_request(b_msg, client_addr)
                time.sleep(0.2)
                self.len_data += len(data)
                if 100.0 * self.len_data / file_size > 50.0 and boo:
                    boo=False
                    self.UDP_socket.settimeout(500)
                    message = self.get_response()
                    if message == "F":
                        message = self.get_response()
                        if message =="FIN":
                            self.fin(client_addr)
                            return

                print("%d%% " % (100.0 * self.len_data / file_size))
                data = self.f.read(fragment_size)

            else:
                bo = self.check(client_addr)
                if bo == False:
                    return

    def get_response(self):
        try:
            rec_msg = self.UDP_socket.recvfrom(fragment_size)
            return rec_msg[0].decode()
        except Exception as e:
            print(e)
            return "time out"

    def send_request(self, msg, client_addr):
        try:
            self.UDP_socket.sendto(msg, client_addr)
            return True
        except:
            return False

    def check(self, client_addr) -> bool:
        windo = self.window_size
        self.UDP_socket.settimeout(time_out)
        message = self.get_response()
        if message == "ACK_ALL":
            self.ack_all()
            print("ACL_ALL")
            MSG = UDP_MSG(-1, str(self.window_size).encode())
            b_msg = pickle.dumps(MSG)
            self.send_request(b_msg, client_addr)
            # self.send_request(str(self.window_size).encode(), client_addr)
            return True
        if message == "FIN":
            self.fin(client_addr)
            message = self.get_response()
            if message == "ACK":
                time.sleep(0.1)
                self.f.close()
                return False

        if message == "time out":
            if self.number_time_out < self.max_time_out:
                self.time_out(client_addr, windo)
                self.check(client_addr)
                self.window_size /= 2
            else:
                self.fin(client_addr)
                self.f.close()
                exit(0)
                return False
        if message[0:4] == "NACK":
            self.nack(message, client_addr)
            self.check(client_addr)
        else:
            self.check(client_addr)

    def ack_all(self) -> None:
        if self._add_window:
            self._sum_ack += 1
            if self._linar and self._sum_ack < 2:
                self.window_size += 2
            else:
                self.window_size *= 2

        self._add_window = True
        self.seq_num = 0
        self.number_time_out = 0

    def fin(self, client_addr) -> None:
        MSG = UDP_MSG(-1, "FIN")
        b_msg = pickle.dumps(MSG)
        self.send_request(b_msg, client_addr)

    def time_out(self, client_addr, windo) -> None:
        self.number_time_out += 1
        self._add_window = False
        i = self.packet_num - windo + 1
        while i <= self.packet_num:
            print("i", i)
            data = self.data_buffer[i]
            MSG = UDP_MSG(i, data)
            b_msg = pickle.dumps(MSG)
            self.send_request(b_msg, client_addr)
            time.sleep(0.1)
            i += 1

    def nack(self, message, client_addr) -> None:
        print(message)
        self._add_window = False
        self._linar = True
        self._sum_ack = 0
        self.window_size -= 1
        message = int(message[4:])
        data = self.data_buffer[message]
        MSG = UDP_MSG(message, data)
        b_msg = pickle.dumps(MSG)
        self.send_request(b_msg, client_addr)
