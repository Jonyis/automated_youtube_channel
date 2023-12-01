from typing import List

import cv2
import imagehash
from PIL import Image
from decord import VideoReader, cpu
from line_profiler_pycharm import profile

__CROP_PERCENTAGE_HORIZONTAL = 0.25
__CROP_PERCENTAGE_VERTICAL = 0.25
__MAX_HASH_DIFFERENCE = 16
__MIN_MATCH_PERCENTAGE = 0.75
__VIDEO_FRAME_STEP = 20
__FRAME_WINDOW_TO_CHECK = 5


class VideoData:

    def __init__(self, path: str):
        self.path = path
        self.frame_hashes = []

    def __eq__(self, other):
        if isinstance(other, VideoData):
            return self.path == other.path
        return False


def check_videos_for_duplicates(video_list: List[VideoData], previous_videos: List[VideoData] = None):
    if previous_videos is None:
        previous_videos = []
    return do_check_videos_for_duplicates(video_list, previous_videos)


@profile
def do_check_videos_for_duplicates(current_videos: List[VideoData], previous_videos: List[VideoData]):
    video_count = 0
    # For each video get hash and compare to other video hashes
    for video1 in current_videos:
        if video_count >= len(current_videos):
            break
        video1_frame_hashes = do_get_video_hash(video1)
        for video2 in current_videos[video_count + 1:] + previous_videos:
            if video1 == video2:
                print("removing video: " + video2.path)
                current_videos.remove(video2)
            else:
                video2_frame_hashes = do_get_video_hash(video2)
                if is_video_duplicate(video1_frame_hashes, video2_frame_hashes):
                    if video2 in current_videos:
                        video_to_delete = video2
                    else:
                        video_to_delete = video1
                    print("removing video: " + video_to_delete.path)
                    current_videos.remove(video_to_delete)
        video_count += 1

    return current_videos


@profile
def do_get_video_hash(video: VideoData):
    if len(video.frame_hashes) == 0:
        video.frame_hashes = do_compute_video_hash_decord(video)
    return video.frame_hashes


@profile
def do_compute_video_hash_cv2(video: VideoData):
    frame_counter = 0
    frame_step = __VIDEO_FRAME_STEP
    frame_hashes = []
    video_capture = cv2.VideoCapture(video.path)
    while video_capture.isOpened():
        if frame_counter % frame_step != 0:
            frame_counter += 1
            continue
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_counter - 1)
        read_success, cv2_frame = video_capture.read()
        if read_success:
            converted = cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB)

            pil_frame = Image.fromarray(converted)
            relevant_frame = get_significant_portion_of_frame(pil_frame)
            frame_hashes.append(get_frame_hash(relevant_frame))
        elif not read_success:
            print('failed at frame ' + str(frame_counter))
            break
        frame_counter += 1

    video_capture.release()

    return frame_hashes


@profile
def do_compute_video_hash_decord(video: VideoData):
    frame_counter = 0
    frame_step = __VIDEO_FRAME_STEP
    frame_hashes = []
    vr = VideoReader(video.path, ctx=cpu(0), width=1280, height=720)
    while frame_counter < len(vr):
        if frame_counter % frame_step != 0:
            frame_counter += 1
            continue
        frame = vr[frame_counter].asnumpy()
        pil_frame = Image.fromarray(frame)
        pil_frame_grayscale = pil_frame.convert('L')
        relevant_frame = get_significant_portion_of_frame(pil_frame_grayscale)
        frame_hashes.append(get_frame_hash(relevant_frame))
        frame_counter += 1

    return frame_hashes


@profile
def get_significant_portion_of_frame(frame: Image):
    crop_x1 = int(frame.width * crop_initial_index(__CROP_PERCENTAGE_HORIZONTAL))
    crop_x2 = int(frame.width * crop_final_index(__CROP_PERCENTAGE_HORIZONTAL))
    crop_y1 = int(frame.height * crop_initial_index(__CROP_PERCENTAGE_VERTICAL))
    crop_y2 = int(frame.height * crop_final_index(__CROP_PERCENTAGE_VERTICAL))
    return frame.crop((crop_x1, crop_y1, crop_x2, crop_y2))


def crop_initial_index(crop_percentage: float):
    return (1 - crop_percentage) / 2


def crop_final_index(crop_percentage: float):
    return (1 + crop_percentage) / 2


@profile
def get_frame_hash(frame: Image):
    gray_scale = frame.convert('L')
    return imagehash.phash(gray_scale)


@profile
def is_video_duplicate(video1_frames, video2_frames) -> bool:
    # Based on https://aws.amazon.com/blogs/media/metfc-automatically-compare-two-videos-to-find-common-content/
    starting_index1 = 0
    while starting_index1 <= len(video1_frames) - __FRAME_WINDOW_TO_CHECK:
        window1 = video1_frames[starting_index1:starting_index1 + __FRAME_WINDOW_TO_CHECK]
        starting_index2 = 0
        while starting_index2 <= len(video2_frames) - __FRAME_WINDOW_TO_CHECK:
            window2 = video2_frames[starting_index2:starting_index2 + __FRAME_WINDOW_TO_CHECK]
            if compare_frame_windows(window1, window2):
                return True
            starting_index2 += __FRAME_WINDOW_TO_CHECK
        starting_index1 += __FRAME_WINDOW_TO_CHECK
    return False


@profile
def compare_frame_windows(window1, window2) -> bool:
    match_count = 0
    for window1_hash in window1:
        for window2_hash in window2:
            diff = window1_hash - window2_hash
            if diff < __MAX_HASH_DIFFERENCE:
                match_count += 1
                window2.remove(window2_hash)
                break

    num_compared = len(window1)
    percentage_match = match_count / num_compared
    matched = (percentage_match >= __MIN_MATCH_PERCENTAGE)
    return matched
