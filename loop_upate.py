import time
import datetime
import random
import os


def loop():
    while True:
        print("\n---start---\n")
        os.system("venv\\Scripts\\python.exe download_thbnl.py")
        print("\n---end---\n")
        now = datetime.datetime.now()
        print("finish update at %s" % now)
        delay = random.randint(3400, 3600)
        print("next update at %s" % (now + datetime.timedelta(seconds=delay)))
        time.sleep(delay)


if __name__ == '__main__':
    loop()
