"""
OPAL Initialization script (Windows)

Rather than configuring an installer +/- Windows service:
* Run manage.py runserver in a thread
* Stall to make sure it gets the chance to start
* Open a webbrowser
* Profit
* There is no step 5
"""
import os
import sys
import threading
import time
import webbrowser

class Server(threading.Thread):
    def run(self):
        os.chdir("D:\Personal Data\hlaptop\Desktop\OPAL\opal-master\opal-master")
        os.system('C:\Python27\python.exe manage.py runserver')
            

def main():
    server = Server()
    server.start()
    time.sleep(1)
    webbrowser.open('http://127.0.0.1:8000')
    return 0

if __name__ == '__main__':
    sys.exit(main())
