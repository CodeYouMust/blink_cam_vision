from fire import Fire
from cameras.blink_api import BlinkApi
import time
from util.polite_access import PoliteAccess

POLITE_DL_WAIT_SECONDS = 60 * 1.5
polite = PoliteAccess('blink-api-access')


def dl_blink_videos(user, pwd, fldr):
    x = BlinkApi()
    x.login(user, pwd)
    x.dl_all_videos(fldr)
    polite.set_access_time()
    return


def polite_dl_blink_videos(user, pwd, fldr, skip_if_frequent=True):
    '''
    Prevent frequent access to blink. Helpful in CRON
    '''
    is_dl = can_dl_polite_wait(skip_if_frequent)
    if is_dl:
        dl_blink_videos(user, pwd, fldr)
    return


def can_dl_polite_wait(skip_if_frequent):
    sleep_seconds = polite.calc_sleep_seconds(POLITE_DL_WAIT_SECONDS)
    is_dl = not sleep_seconds
    if sleep_seconds:
        if skip_if_frequent:
            print('Too soon to DL by {} seconds. Skip.'.format(sleep_seconds))
        else:
            print('Too soon to DL. Sleeping: {}'.format(sleep_seconds))
            time.sleep(sleep_seconds)
            is_dl = True
    return is_dl


if __name__ == '__main__':
    Fire(dl_blink_videos)
