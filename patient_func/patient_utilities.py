import itertools
import threading
import time
import sys
import os


def loader():
    done = False
    #animation

    def animate():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if done:
                break
            sys.stdout.write('\rDownloading... ' + c)
            sys.stdout.flush()
            time.sleep(0.1)

    t = threading.Thread(target=animate)
    t.start()

    #  timeout
    time.sleep(1)
    done = True


def clear():
    # clear terminal function
    _ = os.system('cls||clear')
