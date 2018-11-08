import os
import pprint
import re
import shutil
import sys
from collections import defaultdict
from time import sleep
import ctypes
import msvcrt
import subprocess

from backend import backendGoogle
from backend import games
from backend import formatters
from backend import responseHandler as RH
from ctypes import wintypes

class Main:
    def __init__(self):
        self.cacheDir = "cache"
        self.pprint = pprint.PrettyPrinter().pprint
        self.offline = False
        self.values = []
        self.pastHunt = []
        self.weeksWithoutRepeat = 6
        self.logo = """ 
 _____                                         _
|  __ \                                       (_)
| |  \/ __ _ _ __ ___   ___    ___ _ __   __ _ _ _ __   ___
| | __ / _` | '_ ` _ \ / _ \  / _ \ '_ \ / _` | | '_ \ / _ \\
| |_\ \ (_| | | | | | |  __/ |  __/ | | | (_| | | | | |  __/
 \____/\__,_|_| |_| |_|\___|  \___|_| |_|\__, |_|_| |_|\___|
                                          __/ |
                                         |___/
"""
        
        ### Overrides ###
        self.debugMode = True
        self.detailMode = None
        self.incCouncil = None
        self.targetPool = []
        self.optOut = []

    def uselessCosmetics(self):
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

    def _clearScreen(self):
        os.system("cls")
        if not self.debugMode:
            print(self.logo)
        print("")

    def _cleanSlate(self):
        print(formatters.formatters.red, "CLEARING ALL SAVED DATA", formatters.formatters.default)
        sleep(1)
        print("Deleting OptOut.txt")
        try:
            os.unlink("OptOut.txt")
        except OSError:
            pass
        print("Deleting currentHunt.txt")
        try:
            os.unlink("currentHunt.txt")
        except OSError:
            pass
        print("Deleting offlineMemberList")
        try:
            os.unlink("offlineMemberList")
        except OSError:
            pass
        print("Deleting cache dir")
        shutil.rmtree("cache", ignore_errors=True)
        shutil.rmtree("DEBUGCache", ignore_errors=True)

    def _options(self):
        # Check if Council included in target pool
        if self.incCouncil is None:
            council = input("Opt in Council? ")
            self.incCouncil = RH.yesorno(council)
        else:
            self.incCouncil = False

        # Opt out menu`
        self._clearScreen()

    def _processMembers(self):
        data = defaultdict()
        for row in self.values:
            try:
                if row[5] == "TRUE" and "{} {}".format(row[1], row[2]) not in self.optOut:
                    if row[0] == "Council" and not self.incCouncil:
                        if self.debugMode:
                            print("{} is Council, and council are opted out".format(row[1] + " " + row[2]))
                    else:
                        data = {'rank': row[0],
                                'name': row[1] + " " + row[2],
                                'alias': row[7],
                                'id': row[3],
                                'kills': float(re.sub("[^0-9]", "", str(row[8]))),
                                'credits': float(re.sub("[^0-9]", "", str(row[9])))
                                }
                        self.targetPool.append(data)
                        if self.debugMode:
                            print("{} has been opted in".format(data['name']))
                elif row[5] == "FALSE" and row[0] != "Council" and "{} {}".format(row[1], row[2]) not in self.optOut:
                    if self.debugMode:
                        print("{} is set to opt out on the sheet".format(row[1] + " " + row[2]))
            except Exception as e:
                print("Unable to add {} due to invalid data formatting || {}".format(row[1], e))
        if self.debugMode:
            print("{} members opted in\n{} members opted out".format(len(self.targetPool), len(self.values)-len(self.targetPool)))
        if len(self.targetPool) == 1 or len(self.targetPool) % 2 == 1:
            print("{}Even number of members required for hunt to be possible{}".format(formatters.formatters.red, formatters.formatters.default))
            input("Press any key to exit")
            exit()

    def mainMenu(self):
        if not self.debugMode:
            self.uselessCosmetics()
            if self.offline:
                self.logo = "{} OFFLINE MODE {}\n{}".format(formatters.red, formatters.default, self.logo)

            for char in self.logo:
                if char != " ":
                    sleep(0.012)
                sys.stdout.write(char)
                sys.stdout.flush()
            print("\n")

        self.values = backendGoogle.getValues(self.offline)
        self._options()
        self._processMembers()

        choosing = True
        self._clearScreen()
        while choosing:
            self._clearScreen()
            choosing = False
            print("{} members opted in\n".format(len(self.targetPool)))
            gameMode = input("Choose a game mode:\n1)The Hunt\n2)Zombies\n3)VIP\n4)Juggernaut\n5)Tea Party\n\nMode: ")
            if gameMode == "1":
                games.theHunt(self)
            elif gameMode == "2":
                games.zombies(self)
            elif gameMode == "3":
                games.VIP(self)
            elif gameMode == "4":
                games.Juggernaut(self)
            elif gameMode == "5":
                games.TeaParty(self)
            elif gameMode == "6":
                self._cleanSlate()
                exit()
            else:
                choosing = True
                print(formatters.formatters.red, "INVALID CHOICE", formatters.formatters.default)
                sleep(2)


if __name__ == "__main__":
    assassin = Main()
    assassin.mainMenu()


        