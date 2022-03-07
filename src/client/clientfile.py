
import pickle
import socket
size_bits = 2000
time_out = 6

class UDP_MSG:
    def __init__(self, seq, dat):
        self.seq = seq
        self.dat = dat

class ClientFile:
    def __init__(self,file_name,port,ip,gui) -> None:
        self._test=False
        self._port=port
        self._ip=ip
        self._file_name=file_name
        self._gui=gui
        self.window_size = 5
        self.seq_num = 0  # Sequence number
        self.index_data_buffer = {}  # data and index buffer
        self.index = []
        self.lost_packages = []
        self._stop=True
        self._file_size=0
        try:
            self.UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception :
            return
        self.start_soc_udp()
        self.UDP_socket.close()

    def start_soc_udp(self) -> None:
        self.UDP_socket.sendto("SYN".encode(), (self._ip, self._port))
        try:
            server_response = self.get_response()
        except Exception:
            return
        if server_response == "SYN_ACK":
            self.UDP_socket.sendto("ACK".encode(), (self._ip, self._port))
            print("ACK")
            self.ran()
        self.UDP_socket.close()

    def ran(self) -> None:
        server_window_size = self.UDP_socket.recvfrom(size_bits)
        if int(server_window_size[0]) != self.window_size:
            self.UDP_socket.sendto("NACK".encode(), (self._ip, self._port))
            return
        else:
            self.UDP_socket.sendto("ACK".encode(), (self._ip, self._port))
        self._file_size= int(self.UDP_socket.recvfrom(size_bits)[0])
        if self._file_size > 0:
            self.UDP_socket.sendto("ACK".encode(), (self._ip, self._port))
        else:
            self.UDP_socket.sendto("NACK".encode(), (self._ip, self._port))
            return
        self.len_data = 0
        self.loop()

    def loop(self) -> None:
        while True:
            # //////////////////////test
            if self._test:
                continue
            try:

                if self.seq_num < self.window_size:
                    self.UDP_socket.settimeout(time_out)
                    da = self.UDP_socket.recvfrom(size_bits)[0]
                    MSG = pickle.loads(da)
                    ind_len = MSG.seq
                    data = MSG.dat
                    if data == "ACK_END" or int(ind_len) == - 1:
                        self.check()
                        self.writing()
                        if self.fin():
                            return
                    else:
                        self.index_data_buffer[ind_len] = data
                        self.seq_num += 1
                        if ind_len in self.lost_packages:
                            self.lost_packages.remove(ind_len)
                        self.len_data += len(data)

                        if 100.0 * self.len_data/self._file_size>50.0 and self._stop:
                            self.UDP_socket.settimeout(700)
                            if len(self.index)==0:
                                self.index.append(0)
                            self._stop=False
                            ans= self._gui.download_question(self.index[-1])
                            if ans ==True:
                                a="T"
                            else:
                                a="F"
                            self.UDP_socket.sendto(a.encode(), (self._ip, self._port))
                            if ans ==False:
                                self.fin()
                                return
                        print("%d%% " % (100.0 * self.len_data / self._file_size))
                        if len(self.index) != 0:
                            if ind_len == self.index[-1] + 1:
                                self.index.append(ind_len)
                            else:
                                self.packages_lost(ind_len)
                        else:
                            self.index.append(ind_len)
                else:
                     ch=self.check()
                     if ch==False:
                         return
                     else:
                         self.lost_packages = []
                         self.seq_num = 0

            except Exception as e:
                print(e)
                return

    def get_response(self):
        try:
            rec_msg = self.UDP_socket.recvfrom(size_bits)
            return rec_msg[0].decode()
        except Exception as e:
            print(e, " ", "End of time")
            return "End_time"

    def send_request(self, msg, server_addr) -> bool:
        try:
            self.UDP_socket.sendto(msg, server_addr)
            return True
        except:
            return False

    def check(self) :
        if len(self.lost_packages) == 0:
            print("ACK_ALL")
            self.UDP_socket.sendto("ACK_ALL".encode(), (self._ip, self._port))
            da = self.UDP_socket.recvfrom(size_bits)[0]
            MSG = pickle.loads(da)
            ind_len = MSG.seq
            data = MSG.dat
            if ind_len==-2:
                da = self.UDP_socket.recvfrom(size_bits)[0]
                self.writing()
                self.fin()
                return False
            else:
                win = int(data)
                self.window_size = win
            return
        else:
            self.UDP_socket.sendto(("NACK" + str(self.lost_packages[0])).encode(), (self._ip, self._port))
            da = self.UDP_socket.recvfrom(size_bits)[0]
            MSG = pickle.loads(da)
            ind_len = MSG.seq
            data = MSG.dat
            self.len_data += len(data)
            self.index_data_buffer[ind_len] = data
            print("ind_len",ind_len)
            self.lost_packages.remove(int(ind_len))
            # self.index.append(ind_len)
        self.index.sort()
        self.check()

    def writing(self) -> None:
        with open(self._file_name, 'ab') as f:
            for i in range(len(self.index_data_buffer)):
                f.write(self.index_data_buffer[i])
        f.close()

    def packages_lost(self, ind) -> None:
        print("packages_lost",ind)
        self.index.sort()
        if (ind - 2) == self.index[-1]:
            self.index.append(ind - 1)
            self.lost_packages.append(ind - 1)
            self.index.append(ind)
            self.seq_num += 1
        else:
            ind2 = self.index[-1]
            ind1 = ind
            self.index.append(ind)
            i = 1
            while ind2 + i < ind1:
                print(ind2, "!!", ind1 - i)
                self.index.append(ind1 - i)
                self.lost_packages.append(ind1 - i)
                self.seq_num += 1
                i += 1
        self.index.sort()

    def fin(self) -> bool:
        self.UDP_socket.sendto("FIN".encode(), (self._ip, self._port))
        da = self.UDP_socket.recvfrom(size_bits)[0]
        MSG = pickle.loads(da)
        server_response = MSG.dat
        if server_response == "FIN":
            self.UDP_socket.sendto("ACK".encode(), (self._ip, self._port))
            self._gui.fin_file((100.0 * self.len_data / self._file_size),self.index[-1])

            return True
        else:
            return False



