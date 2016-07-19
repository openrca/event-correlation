import logging

logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")


def trace(self, message, *args, **kws):
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, message, args, **kws)


logging.Logger.trace = trace
logger = logging.getLogger()

if (len(logger.handlers) == 0):
    handler = logging.StreamHandler()
    handler.setLevel(logging.TRACE)

    formatter = logging.Formatter('%(asctime)s - %(name)s: %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.setLevel(logging.TRACE)
    logger.propagate = False
    logger.addHandler(handler)
