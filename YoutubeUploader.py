import os
from typing import List

from moviepy.video.io.VideoFileClip import VideoFileClip

from ClipData import ClipData
from youtube_upload import main as youtube_upload


def upload_video(video_path,
                 videoTitle,
                 dateToPost,
                 video_description,
                 video_tags=None):
    clientSecretPath = os.getcwd() + '/client_secret.json'
    credentialsFilePath = os.getcwd() + '/.youtube-upload-credentials.json'
    print(video_description)
    print(videoTitle)
    print(dateToPost)

    return youtube_upload.main(
        ["-t" + videoTitle, "--description=" + video_description, "--tags=" + video_tags, "--category=Gaming",
         "--client-secrets=" + clientSecretPath, "--credentials-file=" + credentialsFilePath,
         "--publish-at=" + dateToPost.strftime("%Y-%m-%dT%H:%M:%S.0Z"), video_path])


def get_video_title(clipList: List[ClipData],
                    title_suffix: str = "",
                    max_characters: int = 100) -> str:
    for clip in clipList:
        title = clip.title + " | " + title_suffix
        if len(title) > max_characters:
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
        channelList_ = {}

        if not any(d["channel"] == postInfo.channel for d in listOfChannels):
            # If channel not yet present add it
            channelList_["channel"] = postInfo.channel
            channelList_["timeStamp"] = ' ' + timeStamp
            listOfChannels.append(channelList_)
        else:
            # If channel is present add current timestamp to it
            next(item for item in listOfChannels if item["channel"] == postInfo.channel)["timeStamp"] += ' ' + timeStamp

        duration += clip.duration
        i += 1
        clip.close()
        if duration >= max_video_duration:
            break

    channelString = "Streamers featured in this video:\n"
    for channel in listOfChannels:
        channelString = channelString + channel["channel"]
        if time_stamping:
            channelString += channel["timeStamp"]
        channelString += "\n"

    return channelString


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
        clipName = clipInfo.title
        if '<3' in clipName:
            clipName = clipName.replace('<3', '')
        if '>' in clipName:
            clipName = clipName.replace('>', '')
        clipString += clipName + " " + timeStamp + "\n"
        duration += clip.duration
        clip.close()

    return clipString
