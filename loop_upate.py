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
        # print("finish time : %d:%d:%d" % (now.tm_hour, now.tm_min, now.tm_sec))
        print("finish update at %s" % now)
        delay = random.randint(3400, 3600)
        print("next update at %s" % (now + datetime.timedelta(seconds=delay)))
        time.sleep(delay)


loop()
