# Group#:        A34
# Student Names: Alvina Gakhokidze 
#                Seiya Nozawa-Temchenko

#Content of server.py; To complete/implement

from tkinter import *
import socket
import threading

class ChatServer:
    """
    This class implements the chat server.
    It uses the socket module to create a TCP socket and act as the chat server.
    Each chat client connects to the server and sends chat messages to it. When 
    the server receives a message, it displays it in its own GUI and also sents 
    the message to the other client.  
    It uses the tkinter module to create the GUI for the server client.
    See the project info/video for the specs.
    """ 
    def __init__(self, window: Tk) -> None:
        #create the GUI
        self.window = window
        self.window.title("tk")

        server_frame = Frame(self.window)
        server_frame.grid(row = 1, column = 0, padx = 5, sticky = W)
        Label(server_frame, text = "Chat Server").pack(side = LEFT)
        
        history_frame = Frame(self.window)
        history_frame.grid(row = 2, column = 0, padx = 5, sticky = W)
        Label(history_frame, text = "Chat History:").pack(side = LEFT)

        chat_frame = Frame(self.window)
        chat_frame.grid(row = 3, column = 0, padx = 5, pady = 5)

        #essentially a text widget
        self.text_area = Text(chat_frame, wrap = WORD, height = 10, width = 35)
        self.text_area.pack(side = LEFT, fill = BOTH) #, expand = True)
        self.text_area.bind("<1>", lambda e: "break") #disables mouse clicks

        scroll = Scrollbar(chat_frame, command = self.text_area.yview)
        scroll.pack(side = RIGHT, fill = Y)
        self.text_area.config(yscrollcommand = scroll.set)

        #create and bind a socket (port must be 0-65535)
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('127.0.0.1', 8008)) #send as a tuple
        self.serverSocket.listen()

        #create dictionary of active clients {client_socket: client_id}
        self.clients_dict = {}
        self.client_counter = 0

        #thread for client acceptance
        threading.Thread(target = self.accept_client, daemon = True).start() #make parent exit and kill the demons

    def accept_client(self) -> None:
        """
        Makes a connection between a client and the server to begin message exchanges.
        Each client has a unique ID
        """
        while True:
            try: 
                client_socket, client_address = self.serverSocket.accept()
            except Exception:
                break #i.e. socket closed or any other error

            self.client_counter += 1 #add a new client
            client_id = f"Client {self.client_counter}"

            #send client its ID and register it in dict
            client_socket.send(client_id.encode())
            self.clients_dict[client_socket] = client_id

            threading.Thread(target = self.receive_message, args = (client_socket,), daemon = True).start()

            #client connected message
            connect_message = f"{client_id} has connected from {client_address}"
            self.window.after(0, self.display_message, connect_message) #after is a thread-safe update (schedules update to happen)

    def receive_message(self, client_socket) -> None:
        """
        Receives message from client and puts it into the text area
        """
        client_id = self.clients_dict.get(client_socket, "Unknown")
        while True:
            try:
                client_message = client_socket.recv(1024).decode()
                if client_message:
                    text_message = f"{client_id}: {client_message}"
                    self.window.after(0, self.display_message, text_message) #after is a thread-safe update (schedules update to happen)
                    self.broadcast_message(text_message, sender_socket = client_socket)
            except Exception: #must be a tuple
                break #i.e. forced disconnnect

        self.remove_client(client_socket)

    def broadcast_message(self, message, sender_socket = None) -> None:
        """
        Sends message to all clients except sender
        """
        for client_socket in list(self.clients_dict.keys()):
            if client_socket != sender_socket:  #makes sure the sender does not receive the message again
                try:
                    client_socket.send(message.encode())
                except Exception:
                    if client_socket in self.clients_dict: #i.e. forced disconnect
                        self.remove_client(client_socket)

    def display_message(self, message: str) -> None:
        """"
        Appends message to text section in GUI
        """
        self.text_area.config(state = NORMAL)
        self.text_area.insert(END, message + "\n")
        self.text_area.config(state = DISABLED)
        self.text_area.see(END)

    def remove_client(self, client_socket: socket.socket) -> None:
        """
        Removes client from dict, closes socket, and sends an outro in chat
        """
        if client_socket in self.clients_dict:
            dead_client = self.clients_dict.pop(client_socket)
            client_socket.close()
            dead_message = f"{dead_client} has left the chat"
            self.display_message(dead_message)
            self.broadcast_message(dead_message, sender_socket = None)

def main(): #Note that the main function is outside the ChatServer class
    window = Tk()
    ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()