import os
import time
from datetime import datetime
from glob import glob
from dask import compute, delayed
from fire import Fire
from vision.opencv_human_detect import set_skip_frames, collect_human_frames,\
    save_frame, display_frame
from cameras.fsystem import cpath

RUN_ID = 'run-{}'.format(time.time())


def parse_videos(fldr,
               imgs=None,
               logs=None,
               new_folder=False,
               reprocess=False,
               skip_frames=None,
               limit_size=999999):
    loop_st = time.time()
    set_skip_frames(skip_frames)
    out_fldr_imgs = make_get_out_fldr(imgs, new_folder=new_folder)
    out_fldr_logs = make_get_out_fldr(logs, new_folder=new_folder)
    vid_paths = gen_new_videos_list(fldr,
                                out_fldr_logs,
                                reprocess=reprocess,
                                limit_size=limit_size)
    d_results = [delayed(collect_human_frames)(x) for x in vid_paths]
    ctr = 0
    for video_file, frames in compute(*d_results, scheduler='threads'):
        print(video_file, len(frames))
        fname = parse_mp4_fname(video_file)
        for frame in frames:
            if out_fldr_imgs:
                if not os.path.exists(out_fldr_imgs):
                    os.makedirs(out_fldr_imgs)
                ctr += 1
                cfn = '{}-{}.jpg'.format(fname, ctr)
                out_file = os.path.join(out_fldr_imgs, cfn)
                print(out_file)
                save_frame(frame, out_file)
            else:
                display_frame(frame)
    if out_fldr_imgs:
        print('Output: ' + out_fldr_imgs)
        if vid_paths:
            elapsed = time.time() - loop_st
            save_processed_videos_list(vid_paths, out_fldr_logs)
            lpl = load_processed_videos_list(out_fldr_logs)
            print('Completed videos: {}. total seconds: {}'.format(len(lpl),
                                                                int(elapsed)))
    return len(vid_paths)


def gen_new_videos_list(fldr,
                        log_fldr,
                        reprocess=False,
                        limit_size=999999):
    vid_paths = list_all_files(fldr, extn='.mp4')
    print('videos found: {}'.format(len(vid_paths)))
    if not reprocess:
        dupes = []
        for exist_path in load_processed_videos_list(log_fldr):
            exist_fname = cpath(exist_path).split('/')[-1]
            for f in vid_paths:
                if f.endswith(exist_fname):
                    dupes.append(f)
        vid_paths = list(sorted(set(vid_paths) - set(dupes)))
        if len(vid_paths) > limit_size:
            print('Limiting batch size: {}'.format(limit_size))
            vid_paths = vid_paths[:limit_size]
        print('Skip extracted videos: [{}] Processing:[{}]'.format(len(dupes),
                                                                   len(vid_paths)))
    return vid_paths

def load_processed_videos_list(out_fldr_logs):
    img_paths = []
    if os.path.exists(out_fldr_logs):
        for fpath in list_all_files(out_fldr_logs, extn='.log'):
            with open(fpath, 'rt') as f:
                imgs = [cpath(i).strip() \
                        for i in f.read().split('\n') if i and i.strip()]
                if imgs:
                    img_paths.extend(imgs)
    return img_paths


def save_processed_videos_list(vid_paths, out_fldr_logs):
    ofl = os.path.join(out_fldr_logs, datetime.now().date().isoformat())
    if not os.path.exists(ofl):
        os.makedirs(ofl)
    fname = 'run-{}.log'.format(time.time())
    fpath = os.path.join(ofl, fname)
    with open(fpath, 'wt') as f:
        txt = '\n'.join(vid_paths)
        f.write(cpath(txt))


def list_all_files(fldr, extn='.mp4'):
    coll = []
    for root, dirs, files in os.walk(fldr):
        for file in files:
            if file.lower().endswith(extn.lower()):
                p = cpath(os.path.join(root, file))
                coll.append(p)
    return coll


def make_get_out_fldr(out=None, new_folder=False):
    out_fldr = None
    if out:
        if new_folder:
            out_fldr = os.path.join(out, RUN_ID)
        else:
            out_fldr = out
        if not os.path.exists(out_fldr):
            print('Creating: ' + out_fldr)
            os.makedirs(out_fldr)
    return out_fldr


def parse_mp4_fname(f):
    fname = cpath(f).split('/')[-1].replace('.mp4', '')
    return fname


if __name__ == '__main__':
    Fire()
