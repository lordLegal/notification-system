import os
import threading


def main():
    os.system("python3 main.py")


def noti():
    os.system("python3 notification.py")


threading.Thread(target=main).start()
threading.Thread(target=noti).start()
