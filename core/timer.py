import atexit
import logging
import time


class Timer:
    def __init__(self):
        self.__startTime = None
        self.__difference = None

    def start(self):
        self.__startTime = time.perf_counter()
        atexit.register(self.stopAndLog, abort=True)

    def stop(self):
        if (self.__difference is None):
            self.__difference = time.perf_counter() - self.__startTime
            # round to millisecond
            self.__difference = int(self.__difference * 1000)

    def stopAndLog(self, abort=False):
        if (abort and self.__difference is not None):
            return

        self.stop()
        if (abort):
            logging.warning("Calculation aborted after {}".format(Timer.__millisToStr(self.__difference)))
        return str(self)

    def __str__(self):
        if (self.__startTime is not None):
            if (self.__difference is None):
                return "Timer started {} ago".format(Timer.__millisToStr(time.perf_counter() - self.__startTime))
            else:
                return Timer.__millisToStr(self.__difference)
        return "Timer instance"

    @staticmethod
    def __millisToStr(milliSeconds):
        if (isinstance(milliSeconds, float)):
            milliSeconds = int(milliSeconds * 1000)

        s, milli = divmod(milliSeconds, 1000)
        m, s = divmod(s, 60)
        return "{:02d}:{:02d},{:03d}".format(m, s, milli)
