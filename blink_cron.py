from blink_dl import polite_dl_blink_videos
from video_batch import parse_videos
from util.smtp_util import send_job_msg
from util.polite_access import PoliteAccess
from fire import Fire
from datetime import datetime
import os
import time

SKIP_FRAMES = 15
SLEEP_SECONDS = 60 * 40
LIMIT_BATCH_SIZE = 999999
POLITE_SMTP_SECONDS = 60
polite_smtp = PoliteAccess('bl-smtp-api')


def video_dl_loop(user,
                  pwd,
                  fldr,
                  seconds=SLEEP_SECONDS,
                  limit_size=LIMIT_BATCH_SIZE,
                  smtp=False):
    print('[{}] BEGIN loop'.format(datetime.now().isoformat()))
    st = time.time()
    seconds = int(seconds)
    while (time.time() - st) < seconds:
        nap = 60
        try:
            ct = dl_videos_and_detect_humans(user,
                                             pwd,
                                             fldr,
                                             limit_size=limit_size)
            if ct:
                nap = 1
        except Exception as ex:
            subject = 'Blink Cam video to jpeg - gen error'
            print('ERROR: ' + subject)
            if smtp and polite_smtp.is_polite(POLITE_SMTP_SECONDS):
                polite_smtp.set_access_time()
                send_job_msg(subject, str(ex))
            else:
                print('Skip SMTP: too soon')
        time.sleep(nap)
    elapsed = time.time() - st
    ndt = datetime.now().isoformat()
    print('[{}] END loop: {} seconds'.format(ndt, int(elapsed)))


def video_dl(user, pwd, fldr):
    try:
        dl_videos_and_detect_humans(user, pwd, fldr)
    except Exception as ex:
        subject = 'Blink Cam video to jpeg - gen error'
        print('ERROR: ' + subject)
        if polite_smtp.is_polite(POLITE_SMTP_SECONDS):
            polite_smtp.set_access_time()
            send_job_msg(subject, str(ex))
        else:
            print('Skip SMTP: too soon')
    return


def dl_videos_and_detect_humans(user,
                                pwd,
                                fldr,
                                limit_size=LIMIT_BATCH_SIZE,
                                skip_if_frequent=True):
    blink_fldr = os.path.join(fldr, 'blink')
    polite_dl_blink_videos(user,
                           pwd,
                           blink_fldr,
                           skip_if_frequent)
    extract_fldr = os.path.join(fldr, 'extract-blink')
    tdt = datetime.today().date().isoformat()
    img = os.path.join(extract_fldr, 'images', tdt)
    log = os.path.join(extract_fldr, 'logs')
    ct = parse_videos(fldr=blink_fldr,
                   imgs=img,
                   logs=log,
                   skip_frames=SKIP_FRAMES,
                   limit_size=limit_size,
                   )
    return ct

if __name__ == '__main__':
    Fire()
