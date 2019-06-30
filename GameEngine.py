import os
import pprint
import re
import shutil
from collections import defaultdict
from time import sleep
from string import ascii_lowercase
from backend import backendGoogle
from backend import games
from backend import formatters
from backend import responseHandler as RH
from backend import cosmetics
from backend import menu

# todo: Support for configuration file to help future committees after I, Dan, leave
# todo: Support for generating a killsheet for other societies -- unlikely, but a nice thought
# todo: COMMENTS! I really let the commenting slack, i should fix that
# todo: Make game definitions easier to make
# todo: Improve UI in all sections of the program, no more Y/N typing
# todo: Add self authentication script, so anyone can run this
# todo: Backup past hunts to the cloud. Maybe Gists?

class Main:
    def __init__(self):
        """Defines variables that the main class will use"""
        self.cacheDir = "cache"  # the directory of the cache
        self.pprint = pprint.PrettyPrinter().pprint  # pprint instance so i dont need to type as much
        self.offline = False  # used to flag if the code is running without google, can be manually set
        self.values = []  # temporary variable holding EVERYTHING google sends back
        self.pastHunt = []  # a list holding all past hunts/teams/whatever tf you want
        self.targetPool = []   # a list of members opted in the hunt this week
        self.optOut = []  # a list of members opted out, deprecated
        self.weeksWithoutRepeat = 6  # how many weeks gameEngine should try not to repeat for
        self.games = games
        self.logo = cosmetics.getLogo()

        self.dataRows = [  # The row letter for each bit of information on google sheets
            "A",  # Rank
            "B",  # First Name
            "C",  # Last Name
            "H",  # Alias
            "D",  # ID/Email
            "I",  # Kills
            "J"  # Credits
        ]

        ### Overrides ###
        self.debugMode = True  # disables cosmetics, and enables more verbose outputs
        self.detailMode = False  # detailed output by default, where applicable
        self.incCouncil = True  # default to include council, and not ask

    def clearScreen(self):
        """Wrapper function to clear the screen and keep the logo on screen"""
        os.system("cls")
        if not self.debugMode:
            print(self.logo)
        else:
            print("LordOfPolls' GameEngine".center(65, "="))
        print("")

    def _cleanSlate(self):
        """Nukes all of GameEngine's stored data for a clean slate, gettit?"""
        os.system("cls")
        print(formatters.formatters.red, "CLEARING ALL SAVED DATA", formatters.formatters.default)
        sleep(1)
        print("Deleting OptOut.txt")
        try:  # Using loads of try and except conditions because i dont want the entire function to stop if one fails
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
        shutil.rmtree("cache", ignore_errors=True)  # rmtree removes a directory and EVERYTHING in it, no matter what
        shutil.rmtree("DEBUGCache", ignore_errors=True)
        print("Clean Slate completed...")
        if not self.debugMode:
            print("Exiting Game Engine in...", end="\r")
            print("Exiting Game Engine in... 3", end="\r")
            sleep(1)
            print("\rExiting Game Engine in... 2", end="\r")
            sleep(1)
            print("\rExiting Game Engine in... 1", end="\r")
            sleep(1)
        exit(0)

    @staticmethod
    def alphabet_position(text):
        LETTERS = {letter: int(index) for index, letter in enumerate(ascii_lowercase, start=0)}

        data = ""
        for char in text:
            data += char

        data = data.lower()

        numbers = [LETTERS[character] for character in data if character in LETTERS]

        return numbers

    def _dumpAndOpen(self):
        """Dumps the current targetpool to a file and opens it"""
        f = open("temp.txt", "w")
        f.write("**KILLSHEET DUMP**\n\n")
        for member in self.targetPool:
            f.write(member['name'])
            f.write("\n")
        f.close()
        self.clearScreen()
        print("Waiting for notepad to close...")
        os.system("notepad.exe temp.txt")
        os.unlink("temp.txt")
        print("File deleted, resuming")

    def _options(self):
        """Check if Council to be included in target pool"""
        if self.incCouncil is None:
            council = input("Opt in Council? ")
            self.incCouncil = RH.yesorno(council)
        else:
            self.incCouncil = False

        # Opt out menu`
        self.clearScreen()

    def _processMembers(self):
        dataRows = self.alphabet_position(self.dataRows)
        data = defaultdict()  # creates an empty, assignable dictionary
        for row in self.values:
            try:
                if row[5] == "TRUE" and "{} {}".format(row[1], row[2]) not in self.optOut: #  is this twat in the opt out list?
                    if row[0] == "Council" and not self.incCouncil:  # is this a council member, and are we including them?
                        if self.debugMode:
                            print("{} is Council, and council are opted out".format(row[1] + " " + row[2]))
                    else:
                        # the basic data structure of a member, will be replaced with a class rather than a dictionary
                        data = {'rank': row[dataRows[0]],
                                'name': row[dataRows[1]] + " " + row[dataRows[2]],
                                'alias': row[dataRows[3]],
                                'id': row[dataRows[4]],
                                'kills': float(re.sub("[^0-9]", "", str(row[dataRows[5]]))),
                                'credits': float(re.sub("[^0-9]", "", str(row[dataRows[6]])))
                                }
                        self.targetPool.append(data)  # add this member to the targetPool
                        if self.debugMode:
                            print("{} has been opted in".format(data['name']))
                elif row[5] == "FALSE" and row[0] != "Council" and "{} {}".format(row[1], row[2]) not in self.optOut:
                    # Is this person set to be opted out on the killSheet?
                    if self.debugMode:
                        print("{} is set to opt out on the sheet".format(row[1] + " " + row[2]))
            except Exception as e:
                # if this code EVER hits an error, i can put money on it being a formatting error on the killSheet
                print("Unable to add {} due to invalid data formatting || {}".format(row[1], e))
        if self.debugMode:
            print("{} members opted in\n{} members opted out".format(len(self.targetPool), len(self.values)-len(self.targetPool)))
        # if len(self.targetPool) == 1 or len(self.targetPool) % 2 == 1:
            # You need an even number to balance the games, and gameEngine cant yet support one person being targeted
            # by two people at once
            # print("{}Even number of members required for hunt to be possible{}".format(formatters.formatters.red, formatters.formatters.default))
            # input("Press any key to exit")
            # exit()

    def mainMenu(self):
        if not self.debugMode:
            cosmetics.fullScreen()
            if self.offline:  # let the user know game engine is running offline
                cosmetics.logo = "{} OFFLINE MODE {}\n{}".format(formatters.formatters.red,
                                                            formatters.formatters.default,
                                                            self.logo)
            sleep(0.5)
            cosmetics.printLogo()

        print("Loading KillSheet Data...", end="\r")
        self.values = backendGoogle.getValues(self.offline)  # get the killSheet data from google sheets
        if not self.debugMode:
            sleep(0.1)
            print(formatters.formatters.green + "Loading KillSheet Data...        " + formatters.formatters.default)

        print("Processing members...", end="\r")
        self._processMembers()
        if not self.debugMode:
            sleep(0.1)
            print(formatters.formatters.green + "Processing members...          " + formatters.formatters.default)

        print("Ready!")
        if not self.debugMode:
            sleep(0.7)

        self._options()
        menuManager = menu.Engine(coreLoop=self)
        menuManager.loop()


if __name__ == "__main__":
    # the code wont execute if you import it, only if you open it
    assassin = Main()  # run the innit code once ONLY (apparently this was necessary :( )
    assassin.mainMenu()  # BOOT
