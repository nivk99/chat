
from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox as mb
from tkinter import ttk


class ClientGui:

    def __init__(self, client):
        self._client = client
        self._running = True
        self._gui_ran = False
        self._root = None
        self._chatWindow = None
        self.mpb = None
        self.start_mode()

    def get_running(self) -> bool:
        return self._running

    def get_gui_ran(self) -> bool:
        return self._gui_ran

    def writing_window(self, message) -> None:
        self._chatWindow.config(state="normal")
        self._chatWindow.insert("end", message)
        self._chatWindow.yview("end")
        self._chatWindow.config(state="disabled")

    def start_mode(self) -> None:
        # # Draw start name
        name_cl = Tk()
        name_cl.withdraw()
        self._client.set_name(simpledialog.askstring("name", "Type your name", parent=name_cl))
        mb.showinfo("Greeting", f" Hello {self._client.get_name()}")

        # # Draw start ip
        ip = Tk()
        ip.withdraw()
        self._client.set_ip(simpledialog.askstring("ip", "Type the server ID number", parent=ip))

        # # Draw start port
        pr = Tk()
        pr.withdraw()
        port = simpledialog.askstring("port", "Type a port number", parent=pr)
        if port == '':
            port = self._client.get_port()
        else:
            port = int(port)

        if port < 123 or port > 65535:
            self.gui_error("forbidden", "The port is not working properly")
            exit(0)
        self._client.set_port(port)

    def stop_gui(self) -> None:
        message = "disconnect"
        self._client.send_message(message)
        self._running = False
        self._gui_ran = False
        self._root.quit()
        self._client.get_soc().close()
        exit(0)

    def gui_error(self, title, mes) -> None:
        mb.showerror(title, mes)
        self.stop_gui()

    def ranGui(self) -> None:
        self._root = Tk()
        self._root.title("Client -" + self._client.get_name())
        self._root.minsize(800, 700)
        self._root.configure(background="grey")

        # Draw a button logout
        button_logout = Button(self._root, text='Logout', bg="orange", fg="red",
                               font=("Arial Bold", 10), pady=5, command=self.stop_gui,
                               padx=20)
        button_logout.grid(row=0, column=0)

        # Draw a label name
        label_name = Label(self._root, text="Name:", bd=1, relief=SOLID, font=("Arial Bold", 20), bg="orange",
                           fg="red", anchor=NE,
                           wraplength=200)
        label_name.grid(row=0, column=1)

        # Draw a txt name
        txt_name = Entry(self._root, width=10, borderwidth=6)
        txt_name.grid(row=0, column=2)
        txt_name.insert(0, self._client.get_name())

        # Draw a label address
        label_address = Label(self._root, text="Address:", bd=1, relief=SOLID, font=("Arial Bold", 20), bg="orange",
                              fg="red",
                              anchor=NE,
                              wraplength=200)
        label_address.grid(row=0, column=3)

        # Draw a txt address
        txt_address = Entry(self._root, width=10, borderwidth=6)
        txt_address.grid(row=0, column=4)
        txt_address.insert(0, self._client.get_ip())

        # Draw a label Port
        label_port = Label(self._root, text="Port:", bd=1, relief=SOLID, font=("Arial Bold", 20), bg="orange",
                           fg="red",
                           anchor=NE,
                           wraplength=200)
        label_port.grid(row=0, column=5)

        # Draw a txt port
        txt_port = Entry(self._root, width=10, borderwidth=6)
        txt_port.grid(row=0, column=6, columnspan=2)
        txt_port.insert(0, self._client.get_port())

        # Draw a button Online
        Online = Button(self._root, text='Online', bg="orange", fg="red",
                        font=("Arial Bold", 10), pady=5, command=lambda: self._client.send_message("get_users"),
                        padx=20)
        Online.grid(row=0, column=8)

        # Add a Scroll bar to chatWindow
        scroll = Scrollbar(self._root, orient=VERTICAL)
        # Draw a txt Message board
        self._chatWindow = Text(self._root, bd=1, width=50, borderwidth=6, yscrollcommand=scroll.set)
        self._chatWindow.place(height=385, width=700, bordermode=OUTSIDE, relx=0.02, rely=0.1)
        scroll.config(command=self._chatWindow.yview)
        scroll.place(x=720, y=70, height=385)

        # Draw a label TO
        label_to = Label(self._root, text="TO", bd=1, relief=SOLID, font=("Arial Bold", 15), bg="orange",
                         fg="red",
                         anchor=NE,
                         wraplength=200, pady=5,
                         padx=20)
        label_to.place(relx=0.1, rely=0.65)

        # Draw a txt TO
        txt_to = Entry(self._root, width=20, borderwidth=6)
        txt_to.place(relx=0.02, rely=0.7)

        # Draw a label Message
        label_Message = Label(self._root, text="Message", bd=1, relief=SOLID, font=("Arial Bold", 15), bg="orange",
                              fg="red",
                              anchor=NE,
                              wraplength=200, pady=5,
                              padx=20)
        label_Message.place(relx=0.53, rely=0.65)

        # Draw a txt  Message
        txt_Message = Entry(self._root, width=48, borderwidth=6)
        txt_Message.place(relx=0.30, rely=0.7)

        # Draw a button Send
        button_Send = Button(self._root, text='Send', bg="orange", fg="red",
                             command=lambda: self._client.write_msg(txt_to, txt_Message), font=("Arial Bold", 10),
                             pady=5,
                             padx=20)
        button_Send.place(relx=0.88, rely=0.7)

        # Draw a label Server file Name
        label_Server = Label(self._root, text="Server file Name", bd=1, relief=SOLID, font=("Arial Bold", 15),
                             bg="orange",
                             fg="red",
                             anchor=NE,
                             wraplength=200, pady=5,
                             padx=20)
        label_Server.place(relx=0.07, rely=0.8)

        # Draw a text Server file Name
        txt_Server = Entry(self._root, width=34, borderwidth=6)
        txt_Server.place(relx=0.01, rely=0.85)

        # Draw a label Client file Name
        label_Client = Label(self._root, text="Client file Name", bd=1, relief=SOLID, font=("Arial Bold", 15),
                             bg="orange",
                             fg="red",
                             anchor=NE,
                             wraplength=200, pady=5,
                             padx=20)
        label_Client.place(relx=0.53, rely=0.8)

        # Draw a  button File names
        File_names = Button(self._root, text='File names', bg="orange", fg="red",
                            font=("Arial Bold", 10), pady=5, command=lambda: self._client.send_message("get_list_file"),
                            padx=20)
        File_names.place(relx=0.84, rely=0.78)

        # Draw a text Client file Name
        txt_Client = Entry(self._root, width=34, borderwidth=6)
        txt_Client.place(relx=0.43, rely=0.85)

        # Draw a button Send
        download = Button(self._root, text='Download', bg="orange", fg="red",
                          command=lambda: self._client.download(txt_Server, txt_Client), font=("Arial Bold", 10),
                          pady=4,
                          padx=20)
        download.place(relx=0.84, rely=0.85)
        self._gui_ran = True
        self._root.protocol("WM_DELETE_WINDOW", self.stop_gui)
        self._root.mainloop()

    def download_question(self, byte) -> bool:
        # Draw a Download bar
        self.mpb = ttk.Progressbar(self._root, orient="horizontal", length=600, mode="determinate")
        self.mpb.place(relx=0.05, rely=0.95)
        self.mpb["maximum"] = 100
        self.mpb["value"] = 50
        self.writing_window(f"User {self._client.get_name()} downloaded 50% out of file. List byte is: {byte}\n")
        cl = Tk()
        cl.withdraw()
        answer = mb.askquestion("Download file", "Moved 50% of the file. Continue downloading?", parent=cl)
        if answer == 'yes':
            return True
        else:
            return False

    def fin_file(self, sum, byte) -> None:
        self.mpb = ttk.Progressbar(self._root, orient="horizontal", length=600, mode="determinate")
        self.mpb.place(relx=0.05, rely=0.95)
        self.mpb["maximum"] = 100
        self.mpb["value"] = 0
        if sum >= 100:
            self.writing_window(f"User {self._client.get_name()} downloaded 100% out of file. List byte is: {byte}\n")
        else:
            self.writing_window(f"User {self._client.get_name()} downloaded {sum} out of file. List byte is: {byte}\n")
