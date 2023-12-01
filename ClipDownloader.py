import os
from typing import List

import requests

from ClipData import ClipData


def download_clips(clip_list: List[ClipData], clips_path: str):
    downloaded_clips = []
    for clip in clip_list:
        downloaded_clips.append(download_clip(clip, clips_path))

    return downloaded_clips


def download_clip(clip: ClipData, clips_path: str):
    # Inspired by https://github.com/viniciusenari/twitch-highlights-bot
    index = clip.thumbnail_url.find('-preview')
    clip_url = clip.thumbnail_url[:index] + '.mp4'

    r = requests.get(clip_url)
    path = clips_path + '/' + clip.slug + '.mp4'
    if r.headers['Content-Type'] == 'binary/octet-stream':
        if not os.path.exists(clips_path):
            os.makedirs(clips_path)
        with open(path, 'wb') as f:
            f.write(r.content)
        clip.path = path
    else:
        print(f'Failed to download clip from thumb: {clip.url}')

    return clip

