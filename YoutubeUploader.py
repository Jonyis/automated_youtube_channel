import os
from typing import List

from moviepy.video.io.VideoFileClip import VideoFileClip

from ClipData import ClipData
from youtube_upload import main as youtube_upload


def upload_video(video_path,
                 videoTitle,
                 dateToPost,
                 video_description,
                 video_tags=None,
                 notify_subscribers=True):
    clientSecretPath = os.getcwd() + '/client_secret.json'
    credentialsFilePath = os.getcwd() + '/.youtube-upload-credentials.json'
    print(video_description)
    print(videoTitle)
    print(dateToPost)
    upload_request = ["-t" + videoTitle,
                      "--description=" + video_description,
                      "--tags=" + video_tags,
                      "--category=Gaming",
                      "--client-secrets=" + clientSecretPath,
                      "--credentials-file=" + credentialsFilePath,
                      "--publish-at=" + dateToPost.strftime("%Y-%m-%dT%H:%M:%S.0Z"),
                      video_path]
    if not notify_subscribers:
        upload_request += "--stop-notify-subscribers"

    return youtube_upload.main(upload_request)


def get_video_title(clipList: List[ClipData],
                    title_suffix: str = "",
                    max_characters: int = 100) -> str:
    for clip in clipList:
        title = clip.title + " | " + title_suffix
        if len(title) <= max_characters:
            return title

    return title_suffix


def get_video_description(clipList: List[ClipData],
                          max_video_duration: int,
                          time_stamping: bool = False,
                          intro_video_path: str = None) -> str:
    description = __get_channel_data(clipList, intro_video_path, max_video_duration, time_stamping=time_stamping)
    description += "\nClips in this video:\n"
    description += __get_clip_data(clipList, intro_video_path)
    return description


def __get_channel_data(clipList: List[ClipData],
                       intro_video_path: str,
                       max_video_duration: int,
                       time_stamping: bool = False) -> str:
    i = 0
    duration = 0
    listOfChannels = []
    if intro_video_path is not None:
        clip = VideoFileClip(intro_video_path)
        duration += clip.duration
        clip.close()
    for postInfo in clipList:
        clip = VideoFileClip(postInfo.path)

        roundDuration = round(duration)
        timeStamp = str(int(roundDuration / 60)).zfill(2) + ':' + str(int(roundDuration % 60)).zfill(2)

        if not any(d.channel_name == postInfo.channel for d in listOfChannels):
            # If channel not yet present add it
            channelData = ChannelTimeStampData(postInfo.channel, timeStamp)
            listOfChannels.append(channelData)
        else:
            # If channel is present add current timestamp to it
            next(item for item in listOfChannels if item.channel_name == postInfo.channel).add_time_stamp(timeStamp)

        duration += clip.duration
        i += 1
        clip.close()
        if duration >= max_video_duration:
            break

    channel_string = "Streamers featured in this video:\n"
    for channel_data in listOfChannels:
        channel_string += str(channel_data)
        channel_string += "\n"

    return channel_string


def __get_clip_data(clipList: List[ClipData],
                    intro_video_path: str) -> str:
    duration = 0
    clipString = ""
    if intro_video_path is not None:
        clip = VideoFileClip(intro_video_path)
        duration += clip.duration
        clip.close()
    for clipInfo in clipList:
        clip = VideoFileClip(clipInfo.path)
        roundDuration = round(duration)
        timeStamp = str(int(roundDuration / 60)).zfill(2) + ':' + str(int(roundDuration % 60)).zfill(2)
        clipName = clean_clip_title(clipInfo.title)
        clipString += clipName + " " + timeStamp + "\n"
        duration += clip.duration
        clip.close()

    return clipString


def clean_clip_title(clip_title):
    if '<3' in clip_title:
        clip_title = clip_title.replace('<3', '')
    if '>' in clip_title:
        clip_title = clip_title.replace('>', '')
    return clip_title


class ChannelTimeStampData:

    def __init__(self, channel_name: str, initial_time_stamp: str):
        self.channel_name = channel_name
        self.time_stamps = [initial_time_stamp]

    def add_time_stamp(self, time_stamp):
        self.time_stamps.append(time_stamp)

    def __str__(self):
        channel_string = self.channel_name + ' '
        for time_stamp in self.time_stamps:
            channel_string += time_stamp + ' '
        return channel_string
