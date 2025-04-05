# Group#:        A34
# Student Names: Alvina Gakhokidze 
#                Seiya Nozawa-Temchenko

#Content of client.py; to complete/implement

from tkinter import *
import socket
import threading
from multiprocessing import current_process #only needed for getting the current process name

class ChatClient:
    """
    This class implements the chat client.
    It uses the socket module to create a TCP socket and to connect to the server.
    It uses the tkinter module to create the GUI for the chat client.
    """
    def __init__(self, window: Tk) -> None:
        self.window = window
        self.window.title("tk")

        #create client socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #connect to server
        self.client_id = "Unknown"
        self.client_port = -1
        try:
            self.client_socket.connect(('127.0.0.1', 8008))
            self.client_id = self.client_socket.recv(1024).decode()
            self.client_port = self.client_socket.getsockname()[1]
        except:
            print("ERROR: Server connection failure")
        
        client_frame = Frame(self.window)
        client_frame.grid(row = 1, column = 0, padx = 5, sticky = W)
        self.client_name = current_process().name #get current process name
        Label(client_frame, text = f"{self.client_name} @port #{self.client_port}").pack(side = LEFT)

        message_frame = Frame(self.window)
        message_frame.grid(row = 2, column = 0, padx = 5, sticky = W)
        Label(message_frame, text = "Chat message:").pack(side = LEFT)
        self.client_entry = Entry(message_frame, width = 22, justify = LEFT, font=('Calibri 13'))
        self.client_entry.pack(side = LEFT)
        self.client_entry.bind("<Return>", self.send_message)
        
        history_frame = Frame(self.window)
        history_frame.grid(row = 3, column = 0, padx = 5, sticky = W)
        Label(history_frame, text = "Chat History:").pack(side = LEFT)

        chat_frame = Frame(self.window)
        chat_frame.grid(row = 4, column = 0, padx = 5, pady = 5)
        self.text_area = Text(chat_frame, wrap = WORD, height = 10, width = 35)
        self.text_area.pack(side = LEFT, fill = BOTH)
        self.text_area.bind("<1>", lambda e: "break") #disables mouse clicks

        #indented messaging formatting
        self.text_area.tag_configure(LEFT, justify = LEFT, lmargin1 = 5, lmargin2 = 5)
        self.text_area.tag_configure(RIGHT, justify = LEFT, lmargin1 = 30, lmargin2 = 30)

        scroll = Scrollbar(chat_frame, command = self.text_area.yview)
        scroll.pack(side = RIGHT, fill = Y)
        self.text_area.config(yscrollcommand = scroll.set)

        threading.Thread(target = self.receive_message, args = (self.client_socket,), daemon = True).start()

    def send_message(self, event) -> None:
        """
        Sends typed message to server and displays in client GUI
        """
        entry_message = self.client_entry.get()
        if entry_message:
            try:
                self.client_socket.send(entry_message.encode())
            except Exception:
                self.update_chat("ERROR: Unable to send message", CENTER) #i.e. disconnected server
                return
            
            display_message = f"{self.client_id}: {entry_message}"
            self.update_chat(display_message, LEFT)

            #clear entry box
            self.client_entry.delete(0, END)
        else:
            return

    def receive_message(self, client_socket) -> None:
        """
        Listen for messages in background thread and schedule display update
        """
        while True:
            try:
                client_message = client_socket.recv(1024).decode()
                if client_message:
                    self.window.after(0, self.update_chat, client_message, RIGHT) #after is a thread-safe update (schedules update to happen)
            except Exception: #must be a tuple
                break #i.e. forced disconnnect

    def update_chat(self, message, align) -> None:
        """
        Appends message to text section in GUI with alignment"""
        self.text_area.config(state = NORMAL)
        self.text_area.insert(END, f"{message}\n", align)
        self.text_area.config(state = DISABLED)
        self.text_area.see(END)

def main(): #Note that the main function is outside the ChatClient class
    window = Tk()
    c = ChatClient(window)
    window.mainloop()
    #May add more or modify, if needed 

if __name__ == '__main__': # May be used ONLY for debugging
    main()