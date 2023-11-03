import instagrapi
import json
import requests
import os

# Load configs
config = {}
with open('conf.json', 'r') as f:
    config = json.load(f)

# cl means client and it is our client for connect to instagram
cl = instagrapi.Client()
if config.get('use_instagram', False):
    cl.login(config['instagram_username'], config['instagram_password'])

def get_post_id(post_url) -> int:
    return cl.media_pk_from_url(post_url)

def get_post_info(post_id):
    return cl.media_info(post_id).dict()

def get_post_media_urls(post_url):
    post_id = get_post_id(post_url)
    post_info = get_post_info(post_id)
    urls = []
    print('start get urls')
    if 'video_url' in post_info:
        if post_info['video_url']!=None:
            print('it has video')
            url = post_info['video_url']
            urls.append(url)
    if 'resources' in post_info:
        print('get to all')
        media_list = post_info['resources']
        for media in media_list:
            if media['video_url'] != None:
                url = media['video_url']
                print(url)
                urls.append(url)
            else:
                url = media['thumbnail_url']
                print(url)
                urls.append(url)
    print(urls)
    return urls
        
def download_from_instagram(url):
    r = requests.get(url, allow_redirects=True)
    filename = url.split('/')[-1].split('?')[0]
    mime_type = r.headers.get('content-type')
   
    if not 'instagram' in os.listdir():
        os.mkdir("instagram")
    os.chdir("instagram")
    open(filename, 'w+').close()
    with open(filename, 'wb') as file:
        file.write(r.content)
    os.chdir('..')
    return {'photo':'./instagram/'+filename, 'name': filename, 'mime': mime_type}
