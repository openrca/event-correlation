import unittest

import time

from core.timer import Timer


class TestScript(unittest.TestCase):
    def test(self):
        timer = Timer()
        timer.start()
        time.sleep(1)
        timer.stop()
        self.assertRegex(str(timer), "00:0[01],\\d{3}")

    def test_str(self):
        timer = Timer()
        self.assertEqual(str(timer), "Timer instance")
        timer.start()
        self.assertRegex(str(timer), "Timer started \\d{2}:\\d{2},\\d{3} ago")
        timer.stop()
        self.assertRegex(str(timer), "\\d{2}:\\d{2},\\d{3}")

    def test_stopAndLog(self):
        timer = Timer()
        timer.start()
        time.sleep(1)

        res = timer.stopAndLog()
        self.assertRegex(res, "00:0[01],\\d{3}")
        self.assertEqual(timer.stopAndLog(), res)


if __name__ == '__main__':
    unittest.main()
