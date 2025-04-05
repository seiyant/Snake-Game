#Content of main.py; use as is
from tkinter import *
import multiprocessing
import time

import snake_game_part2_client as client
import snake_game_part2_server as server

if __name__ == "__main__":
    server = multiprocessing.Process(target=server.main)
    server.start()
    time.sleep(1)  #to ensure server is up and running; 
                   #may be commented out or changed, so your code must work without it as well

    numberOfClients = 3  #Change this value for a different number of clients
    for count in range(1, numberOfClients+1):
        multiprocessing.Process(target=client.main, name=f"Client{count}").start()