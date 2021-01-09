import time
import itertools
import threading
import sys
import os


def loader(message):
    done = False
    #  animation

    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write('\r' + message + '... ' + c)
            sys.stdout.flush()
            time.sleep(0.1)

    t = threading.Thread(target=animate)
    t.start()

    #  timeout
    time.sleep(1)
    done = True


def clear():
    # clear terminal function
    os.system('cls' if os.name == 'nt' else 'clear')
