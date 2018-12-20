import requests
import os
from datetime import datetime
from .fsystem import cpath

LOGIN_HOST = 'https://rest.prod.immedia-semi.com'
BLINK_HOST = 'prod.immedia-semi.com'


class BlinkApi:
    def __init__(self, authtoken=None, region=None):
        '''
        @param authtoken: Optional.
        @param region: Optional.
        if both authtoken and region are specified, ok to skip login()
        '''
        self.authtoken = authtoken
        self.region = region
        self.networks = None
        
    def login(self, email, pwd):
        headers = {
            'Host' : BLINK_HOST,
        }
        data = {
            "password" : pwd, 
            "client_specifier" : "iPhone 9.2 | 2.2 | 222", 
            "email" : email,
        }
        r = requests.post(LOGIN_HOST + '/login', data=data, headers=headers)
        r.raise_for_status()
        j = r.json()
        self.authtoken = j['authtoken']['authtoken']
        self.region = list(j['region'].keys())[0]
        self.networks = j['networks']
        return r

    def get_region_host(self):
        return LOGIN_HOST.replace('prod', self.region)

    def gen_headers(self):
        return {
            'Host' : BLINK_HOST,
            'TOKEN_AUTH': self.authtoken,
            }
            
    def gen_url(self, path):
        return self.get_region_host() + path

    def get_request(self, path, content=False):
        headers = self.gen_headers()
        r = requests.get(self.gen_url(path),
                headers=headers)
        r.raise_for_status()
        c = None
        if content:
            c = r.content
        else:
            c = r.json()
        return c
        
    def get_networks(self):
        return self.get_request('/networks')
        
    def get_sync_module(self, network_id):
        path = path = '/network/{}/syncmodules'.format(network_id)
        return self.get_request(path)

    def get_homescreen(self):
        return self.get_request('/homescreen')
    
    def get_media_content(self, path):
        content = self.get_request(path, content=True)
        return content
        
    def dl_media(self, path, local_path):
        content = self.get_media_content(path)
        print('Saving: ' + local_path)
        with open(local_path, 'wb') as f:
            f.write(content)
    
    def dl_all_videos(self, dest_fldr, max=999999):
        videos = self.get_videos()
        print("Videos available: [{}]".format(len(videos)))
        dest_fldr = cpath(dest_fldr)
        for v in videos[:max]:
            pre = [ v['account_id'], v['network_id'], v['camera_id']]
            pre = [str(p) for p in pre]
            ppath = '/'.join(pre)
            fldr = dest_fldr + '/' + ppath
            if not os.path.exists(fldr):
                print('Creating: ' + fldr)
                os.makedirs(fldr)
            remote_path = v['address']
            fname = remote_path.split('/')[-1]
            local_path = fldr + '/' + fname
            if os.path.exists(local_path):
                #print(local_path, os.stat(local_path).st_size, v['size'])
                continue
            self.dl_media(remote_path, local_path)

    def list_events(self, network_id=None):
        '''
        first_boot
        heartbeat
        armed
        usage
        battery
        disarmed
        sm_offline
        offline
        '''
        path = '/events'
        if network_id:
            path = '/events/network/{}'.format(network_id)
        r = self.get_request(path)
        return r['event']
    
    def get_videos_count(self):
        path = '/api/v2/videos/count'
        r = self.get_request(path)
        return r['count']
    
    def _enrich_videos(self, videos):
        if videos:
            for v in videos:
                v['thumbnail_jpg'] = v['thumbnail'] + '.jpg' # doesnt work

    def get_video_page(self, pg=1):
        path = '/api/v2/videos/page/{}'.format(pg)
        videos = self._get_videos(path)
        return videos
    
    def get_videos(self):
        videos = []
        for pg in range(1, 999999):
            curr = self.get_video_page(pg)
            if curr:
                videos.extend(curr)
            else:
                break
        return videos
        
    def get_videos_unwatched(self):
        path = '/api/v2/videos/unwatched'
        r = self.get_request(path)
        videos = self._get_videos(path)
        return videos

    def _get_videos(self, path):
        r = self.get_request(path)
        videos = r
        self._enrich_videos(videos)
        return videos

    def get_video_info(self, video_id):
        path = '/api/v2/video/{}'.format(video_id)
        videos = self._get_videos(path)
        v = None
        if videos:
            v = videos[0]
        return v
    
    def get_cameras(self, network_id):
        path = '/network/{}/cameras'.format(network_id)
        r = self.get_request(path)
        return r['devicestatus']

    def get_camera(self, network_id, camera_id):
        c = None
        for camera in self.get_cameras(network_id):
            if int(camera_id) == int(camera['camera_id']):
                c = camera
                break
        return c
        
    def get_programs(self, network_id):
        path = '/api/v1/networks/{}/programs'.format(network_id)
        return self.get_request(path)

    def get_account_clients(self):
        path = '/account/clients'
        return self.get_request(path)

    def get_health(self):
        path = '/health'
        return self.get_request(path)

def extract_dt(fpath):
    '''
    @param fpath: Temp/blink/<acct-id>/<sync-module-id>/<cam-id>/clip__<clip-id>_YYYY_MM_DD__HH_MM<AM/PM>.mp4
    acct-id: ddddd 5 digit account id
    sync-module-id: ddddd 5 digit id for sync module
    cam-id: dddddd 6 digit camera id
    clip_id: id of the clip
    Time is in UTC (i think)
    HH: 24 hour format
    It is followed by AM/PM
    @return datetime object
    '''
    f = cpath(fpath).split('/')[-1].split('.')[0]
    dts = f[-19:-2]
    dt = datetime.strptime(dts, '%Y_%m_%d__%H_%M')
    return dt
