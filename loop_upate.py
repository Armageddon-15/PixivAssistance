import time
import datetime
import random
from download_thbnl import update


def loop():
    while True:
        print("\n---start---\n")
        try:
            update()
        except Exception as e:
            print(e)
        print("\n---end---\n")
        now = datetime.datetime.now()
        print("finish update at %s" % now)
        delay = random.randint(3400, 3600)
        print("next update at %s" % (now + datetime.timedelta(seconds=delay)))
        time.sleep(delay)


if __name__ == '__main__':
    loop()
