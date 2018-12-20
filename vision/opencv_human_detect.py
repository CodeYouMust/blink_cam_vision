import tempfile
import requests
import cv2
import time
import os

HC_UPPERBODY = 'haarcascade_upperbody.xml'
HC_LOWERBODY = 'haarcascade_lowerbody.xml'
HC_FULLBODY = 'haarcascade_fullbody.xml'
HC_FACES = [
    #'haarcascade_frontalface_alt.xml',
    #'haarcascade_frontalface_alt2.xml',
    #'haarcascade_frontalface_default.xml',
    #'haarcascade_profileface.xml',
    ]
SKIP_FRAMES = 0 # use multithreads and not multiprocess to ensure SKIP global
JPEG_SIZE = (640, 360)

def dl_haar_cascade(fname):
    tf = os.path.join(tempfile.gettempdir(), 'cv2_classifier_data')
    if not os.path.exists(tf):
        os.makedirs(tf)
    tp = os.path.join(tf, fname)
    if not os.path.exists(tp):
        base_url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/'
        url = base_url + fname
        print('Reading: {} >> {}'.format(url, tp))
        r = requests.get(url)
        with open(tp, 'wb') as f:
            f.write(r.content)
    return tp

def gen_hc_file_colors_lst():
    RED = (255, 0, 0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    BLUE_GREEN = (0,255,255)
    hc_pairs = [
            (HC_UPPERBODY, RED),
            (HC_LOWERBODY, GREEN),
            (HC_FULLBODY, BLUE),
            ]
    for face in HC_FACES:
        hc_pairs.append((face, BLUE_GREEN))
    hcp = []
    for fname, rgb in hc_pairs:
        hc_path = dl_haar_cascade(fname)
        casc_clasifr = cv2.CascadeClassifier(hc_path)
        hcp.append((casc_clasifr, rgb))
    return hcp

def detect_humans(video_file, skip=720, img_size=JPEG_SIZE):
    '''
    CV2 extract humans.
    Core CV2 code/logic is based on sample snippet from web.
    See 'credits' for attribution.
    @param video_file: path to mp4
    @param skip: # frames to skip
    @param img_size: (width,height) of jpeg for resize
    '''
    print('Detecting humans: {}'.format(video_file))
    hc_pairs = gen_hc_file_colors_lst()
    cap = cv2.VideoCapture(video_file)
    vid_time = time.time()
    ctr = -1
    while True:
        r, frame = cap.read()
        ctr += 1
        if (skip is not None) and ((ctr % skip) != 0):
            continue
        if r:
            # Downscale to improve frame rate
            frame = cv2.resize(frame, img_size)
            # Haar-cascade classifier needs a grayscale image
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            rects_color = []
            for cascade, rgb in hc_pairs:
                rects = cascade.detectMultiScale(gray_frame)
                if (rects is not None) and (len(rects) > 0):
                    rects_color.append((rects, rgb))
            if rects_color:
                for rects, rgb in rects_color:
                    for (x, y, w, h) in rects:
                        cv2.rectangle(frame,
                                      (x,y),
                                      (x+w,y+h),
                                      rgb,
                                      2)
                yield frame
        if not r:
            break
        # to limit time spent on each file.
        #if (time.time() - vid_time) > 15:
        #    break
    return

def run_file(video_file, skip=None):
    for frame in detect_humans(video_file, skip=skip):
        display_frame(frame, wait=1)
    return

def collect_human_frames(video_file, skip=None):
    if skip is None:
        skip = SKIP_FRAMES
    frames = [frame for frame in detect_humans(video_file, skip=skip)]
    return video_file, frames


def set_skip_frames(skip=None):
    if skip is not None:
        global SKIP_FRAMES
        SKIP_FRAMES = int(skip)
        #print('SKIP-FRAMES: {}'.format(SKIP_FRAMES))

def save_frame(frame, out_file):
    '''
    Save jpeg to file
    '''
    cv2.imwrite(out_file, frame)

def display_frame(frame, wait=1000):
    '''
    display jpeg to screen
    '''
    cv2.imshow("preview", frame)
    k = cv2.waitKey(wait)

# make sure the files
_ = gen_hc_file_colors_lst()
