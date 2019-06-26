import ctypes
import os
import msvcrt
import subprocess
import sys
import random
from time import sleep
from ctypes import wintypes

logo = """ 
 _____                                         _
|  __ \                                       (_)
| |  \/ __ _ _ __ ___   ___    ___ _ __   __ _ _ _ __   ___
| | __ / _` | '_ ` _ \ / _ \  / _ \ '_ \ / _` | | '_ \ / _ \\
| |_\ \ (_| | | | | | |  __/ |  __/ | | | (_| | | | | |  __/
 \____/\__,_|_| |_| |_|\___|  \___|_| |_|\__, |_|_| |_|\___|  2.0
                                          __/ |
                                         |___/
"""  # The logo, funnily enough


def fullScreen():
    """Completely useless cosmetic code that does nothing but make things look *fanci*"""
    lines = None
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    user32 = ctypes.WinDLL('user32', use_last_error=True)

    SW_MAXIMIZE = 3

    kernel32.GetConsoleWindow.restype = wintypes.HWND
    kernel32.GetLargestConsoleWindowSize.restype = wintypes._COORD
    kernel32.GetLargestConsoleWindowSize.argtypes = (wintypes.HANDLE,)
    user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)

    fd = os.open('CONOUT$', os.O_RDWR)
    try:
        hCon = msvcrt.get_osfhandle(fd)
        max_size = kernel32.GetLargestConsoleWindowSize(hCon)
        if max_size.X == 0 and max_size.Y == 0:
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        os.close(fd)
    cols = max_size.X
    hWnd = kernel32.GetConsoleWindow()
    if cols and hWnd:
        if lines is None:
            lines = max_size.Y
        else:
            lines = max(min(lines, 9999), max_size.Y)
        subprocess.check_call('mode.com con cols={} lines={}'.format(
            cols, lines))
        user32.ShowWindow(hWnd, SW_MAXIMIZE)


def printLogo():
    """A function to print out the logo with a typewriter effect"""
    for char in logo:
        if char != " ":
            sleep(0.012)
        sys.stdout.write(char)  # Hi C++
        sys.stdout.flush()
    print("\n")

def getLoadingMessage(loadingChar):
    """Gets a loading animation message, and makes it \r safe"""
    messages = ["Pwning nwbz",
                "Loading",
                "Harnessing the darkness",
                "Making Toast",
                "Looking for Dan's Helix",
                "Earning kills",
                "Crying myself to sleep",
                "Looking for swans"]
    message = random.choice(messages)
    longest = max(messages, key=len)
    while len(message) < len(longest)+1:
        message += " "
    return message

