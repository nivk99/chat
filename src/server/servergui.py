from tkinter import *
from tkinter import messagebox as mb, simpledialog

class ServerGui:

    def __init__(self, server) -> None:
        self._server = server
        self._running = True
        self._chatWindow = None
        self._root=None
        self.start_mode()

    def get_running(self) -> bool:
        return self._running

    def writing_window(self, message) -> None:
        self._chatWindow.insert(END, message)

    def stop_gui(self) -> None:
        self._running = False
        self._root.quit()
        self._server.get_soc().close()
        exit(0)

    def start_mode(self) -> None:
        # Draw start ip
        ip = Tk()
        ip.withdraw()
        self._server.set_ip(simpledialog.askstring("ip", "Type the server ID number", parent=ip))

        # Draw start port
        pr = Tk()
        pr.withdraw()
        self._server.set_port(simpledialog.askstring("port", "Type a port number", parent=pr))
        if int(self._server.get_port()) < 123 or int(self._server.get_port()) > 65535:
            self.gui_error("forbidden", "The port is not working properly")

    def gui_error(self, title, mes) -> None:
        mb.showerror(title, mes)
        self.stop_gui()

    def ranGui(self) -> None:
        self._root = Tk()
        self._root.title("Server")
        self._root.minsize(700, 500)
        self._root.configure(background="grey")
        scroll = Scrollbar( self._root, orient=VERTICAL)
        self._chatWindow = Text( self._root, bd=1, width=50, borderwidth=6, yscrollcommand=scroll.set)
        self._chatWindow.place(height=385, width=500, bordermode=OUTSIDE, relx=0.1, rely=0.1)
        scroll.config(command=self._chatWindow.yview)
        scroll.place(x=590, y=70, height=385)
        self.writing_window("Setting up server...\n" + "Listening for client...\n")

        # Draw a button stop server
        button_logout = Button( self._root, text='stop server', bg="white", fg="black",
                               font=("Arial Bold", 10), pady=5, command=self.stop_gui,
                               padx=20)
        button_logout.grid(row=0, column=0)
        self._root.protocol("WM_DELETE_WINDOW", self.stop_gui)
        self._root.mainloop()
