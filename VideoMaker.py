from typing import List

from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.video.compositing.concatenate import concatenate, concatenate_videoclips
from moviepy.video.compositing.transitions import crossfadein
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip

import ShortVideoMaker
from ClipData import ClipData


def make_video_from_clips(final_video_path: str,
                          clip_list: List[ClipData],
                          max_video_duration: int = 600,
                          clips_should_fade: bool = True,
                          video_is_short: bool = False,
                          intro_video_path: str = None,
                          outro_video_path: str = None):
    clips = []
    duration = 0

    # For every video in our clip folder
    for clip in clip_list:

        # Turns clip into videoFileClip
        vid = VideoFileClip(clip.path)

        # Normalizes clip audio to max 0dB
        vid = audio_normalize(vid)

        # Resizes so every clip has the same size
        if vid.w != 1920 or vid.h != 1080:
            vid = resize(vid, (1920, 1080))

        # crop to "YouTube shorts" size
        if video_is_short:
            vid = ShortVideoMaker.make_short_default(vid)
            # TODO: improve shorts cropping

        # Adds the video to our list and if total duration is above 10 minutes we break
        duration += vid.duration
        clips.append(vid)
        if duration >= max_video_duration:
            break

    # Makes first clip fade in
    if clips_should_fade:
        clips[0] = fadein(clips[0], 1.5)
        clips[0] = audio_fadein(clips[0], 1.5)

    if intro_video_path is not None:
        vid = VideoFileClip(intro_video_path)
        # Resizes so every clip has the same size
        if vid.w != 1920 or vid.h != 1080:
            vid = resize(vid, (1920, 1080))
        clips.insert(1, vid)
        duration += vid.duration
        # Fades out previous clip and fades in next one
        clips[0] = fadeout(clips[0], 1.5)
        clips[0] = audio_fadeout(clips[0], 1.5)
        clips[2] = fadein(clips[2], 1.5)
        clips[2] = audio_fadein(clips[2], 1.5)

    if outro_video_path is not None:
        vid = VideoFileClip(outro_video_path)
        # Resizes so every clip has the same size
        if vid.w != 1920 or vid.h != 1080:
            vid = resize(vid, (1920, 1080))

        duration += vid.duration
        clips[-1] = concatenate([clips[-1], crossfadein(vid, 1)], padding=-1, method="compose")

    # If no outro fades out the last clip
    elif clips_should_fade:
        clips[-1] = fadeout(clips[-1], 2.5)
        clips[-1] = audio_fadeout(clips[-1], 2.5)

    print('Fusing', len(clips), 'clips with total duration', int(duration / 60), 'minutes and', int(duration % 60),
          'seconds')

    vid = concatenate_videoclips(clips)

    try:
        vid.write_videofile(final_video_path, codec='libx264', fps=30, preset='ultrafast', threads=4)
        print("")
        print("Video created successfully")
    except:
        print("Failed during the making of the video")
        print("")

    for clip in clips:
        clip.close()

    vid.close()
    return final_video_path


def make_short_single_video(final_video_path: str,
                            clip: ClipData):
    # Turns clip into videoFileClip
    vid = VideoFileClip(clip.path)

    # Make video into short format
    vid = ShortVideoMaker.make_short_blurry_background(vid)

    try:
        vid.write_videofile(final_video_path, codec='h264_nvenc', fps=30, threads=4)
        print("")
        print("Video created successfully")
    except:
        print("Failed during the making of the video")
        print("")

    vid.close()
    return final_video_path

