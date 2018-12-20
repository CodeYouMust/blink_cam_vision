import os
from tempfile import gettempdir
import time


class PoliteAccess:
    def __init__(self, label):
        tmp = gettempdir()
        if not os.path.exists(tmp):
            os.makedirs(tmp)
        self.fpath = os.path.join(tmp, '{}.log'.format(label))

    def set_access_time(self):
        with open(self.fpath, 'wt') as f:
            f.write(str(int(time.time())))    

    def calc_sleep_seconds(self, polite_freq_seconds):
        last_access = self.get_access_time()
        return sleep_calc(last_access, polite_freq_seconds)

    def is_impolite(self, polite_freq_seconds):
        return self.calc_sleep_seconds(polite_freq_seconds) > 0

    def is_polite(self, polite_freq_seconds):
        return not self.is_impolite(polite_freq_seconds)

    def get_access_time(self):
        access_time = None
        if os.path.exists(self.fpath):
            with open(self.fpath, 'rt') as f:
                access_time = int(f.read().strip())
        return access_time
    
    def sleep_until_polite(self, polite_freq_seconds):
        s = self.calc_sleep_seconds(polite_freq_seconds)
        if s:
            time.sleep(s)

def sleep_calc(last_access, polite_freq_seconds):
    sleep_seconds = 0
    if last_access:
        elapsed = time.time() - last_access
        sleep_seconds = int(calc_wait_seconds(polite_freq_seconds,
                                              elapsed))
    return sleep_seconds

def calc_wait_seconds(min_wait, elapsed):
    return max(min_wait - elapsed, 0)
