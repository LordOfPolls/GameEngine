import os
import msvcrt
import cursor
import sys
from . import formatters


#add items to this list to add items to the menu
# Key:
# [ "name", "function to run" ]
defaultOptions = [
    ["The Hunt", "self.CoreLoop.games.theHunt()"],
    ["Zombies", "self.CoreLoop.games.zombies()"],
    ["Teams", "self.CoreLoop.games.Teams()"],
    ["Juggernaut", "self.CoreLoop.games.Juggernaut()"],
    ["Tea Party", "self.CoreLoop.games.TeaParty()"],
    ["Clean Slate", "self.CoreLoop._cleanSlate()"],
    ["Dump", "self.CoreLoop._dumpAndOpen()"]
]
key = ""

# Basically ive made a game engine inside of GameEngine to make a nicer user experience
class Engine:
    def __init__(self, coreLoop = None, options=defaultOptions):
        self.options = options  # The list of options defined above
        self.location = 0  # The current item selected
        self.lastRender = ""
        self.CoreLoop = coreLoop  # The main class from main.py, allows callbacks
        self._fixOptions()

    def _fixOptions(self):
        for item in self.options:
            if "games" in item[1]:
                item[1] = item[1].replace("()", "(self.CoreLoop)")

    def _runSelected(self):
        cursor.show()
        print("Running", self.options[self.location][0])
        self.lastRender = ""
        try:
            if self.CoreLoop is not None:
                exec(self.options[self.location][1])
            else:
                print("Cannot run due to no core loop")
        except Exception as e:
            print(e)

    def _input(self):
        """Blocking input function"""
        while msvcrt.kbhit():
            key = None
            try:
                key = msvcrt.getch().decode("ascii")
            except UnicodeDecodeError:
                pass
            except Exception as e:
                print(e)
            if key == "w":
                self.location -= 1
                return
            elif key == "s":
                self.location += 1
                return
            elif key == "\r" or key == " ":
                self._runSelected()
        if self.location > len(self.options) - 1:
            self.location = 0
        elif self.location == -1:
            self.location = len(self.options) - 1

    def _render(self):
        # # obtains console width for dynamic center align
        # try:
        #     width = os.get_terminal_size().columns
        # except OSError:
        #     width = sys.maxsize
        num = 0
        render = ""
        for item in self.options:
            string = item[0]
            if self.location == num:
                string = formatters.formatters.bold + "■" + string
            else:
                string = formatters.formatters.default + "□" + string
            # string = string.ljust(width)  # dynamic center align
            string = string.center(70)  # centers with the logo
            render = render + string + "\n"
            num += 1

        # stops console from flickering from rapid reprints
        if render != self.lastRender:
            if self.CoreLoop is not None:
                self.CoreLoop.clearScreen()
            else:
                os.system("cls")
            cursor.hide()
            optInString = "=={} members are opted in==\n".format(len(self.CoreLoop.targetPool))
            print(optInString.center(65) + "\n")
            print(render)
        self.lastRender = render

    def loop(self):
        # self._render()
        while True:
            self._input()
            self._render()


if __name__ == "__main__":
    engine = Engine()
    engine.loop()
