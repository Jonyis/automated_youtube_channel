from typing import List

from moviepy.video.io.VideoFileClip import VideoFileClip

from ClipData import ClipData
from youtube_upload import main as youtube_upload


class YoutubeUploader:

    def __init__(self,
                 client_secret: str,
                 credentials: str,
                 video_title_suffix: str,
                 video_max_characters: int,
                 max_video_duration: int,
                 time_stamping: bool,
                 notify_subscribers: bool):
        self.client_secret = client_secret
        self.credentials = credentials
        self.video_title_suffix = video_title_suffix
        self.video_max_characters = video_max_characters
        self.max_video_duration = max_video_duration
        self.time_stamping = time_stamping
        self.notify_subscribers = notify_subscribers

    def upload_video(self,
                     video_path,
                     videoTitle,
                     dateToPost,
                     video_description,
                     video_tags=None):
        print(video_description)
        print(videoTitle)
        print(dateToPost)
        upload_request = ["-t" + self.__clean_clip_title(videoTitle),
                          "--description=" + video_description,
                          "--tags=" + video_tags,
                          "--category=Gaming",
                          "--client-secrets=" + self.client_secret,
                          "--credentials-file=" + self.credentials,
                          "--publish-at=" + dateToPost.strftime("%Y-%m-%dT%H:%M:%S.0Z"),
                          video_path]
        if not self.notify_subscribers:
            upload_request.append("--stop-notify-subscribers")
        return youtube_upload.main(upload_request)

    def get_video_title(self, clipList: List[ClipData]) -> str:
        for clip in clipList:
            title = clip.title + self.video_title_suffix
            if len(title) <= self.video_max_characters:
                return title

        return self.video_title_suffix

    def get_video_description(self,
                              clipList: List[ClipData],
                              intro_video_path: str = None) -> str:
        description = self.__get_channel_data(clipList, intro_video_path)
        description += "\nClips in this video:\n"
        description += self.__get_clip_data(clipList, intro_video_path)
        return description

    def __get_channel_data(self,
                           clipList: List[ClipData],
                           intro_video_path: str) -> str:
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
                channel_data = self.ChannelTimeStampData(postInfo.channel)
                if self.time_stamping:
                    channel_data.add_time_stamp(timeStamp)
                listOfChannels.append(channel_data)
            elif self.time_stamping:
                # If channel is present add current timestamp to it
                next(item for item in listOfChannels if item.channel_name == postInfo.channel).add_time_stamp(timeStamp)

            duration += clip.duration
            i += 1
            clip.close()
            if duration >= self.max_video_duration:
                break

        channel_string = "Streamers featured in this video:\n"
        for channel_data in listOfChannels:
            channel_string += str(channel_data)
            channel_string += "\n"

        return channel_string

    def __get_clip_data(self,
                        clipList: List[ClipData],
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
            clipName = self.__clean_clip_title(clipInfo.title)
            if self.time_stamping:
                clipString += clipName + " " + timeStamp + "\n"
            duration += clip.duration
            clip.close()

        return clipString

    @staticmethod
    def __clean_clip_title(clip_title):
        if '<3' in clip_title:
            clip_title = clip_title.replace('<3', '')
        if '>' in clip_title:
            clip_title = clip_title.replace('>', '')
        return clip_title

    class ChannelTimeStampData:

        def __init__(self, channel_name: str):
            self.channel_name = channel_name
            self.time_stamps = []

        def add_time_stamp(self, time_stamp):
            self.time_stamps.append(time_stamp)

        def __str__(self):
            channel_string = self.channel_name + ' '
            for time_stamp in self.time_stamps:
                channel_string += time_stamp + ' '
            return channel_string
