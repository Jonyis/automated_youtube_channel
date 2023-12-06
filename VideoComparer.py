from typing import List

import cv2
import imagehash
from PIL import Image
from decord import VideoReader, cpu


class VideoComparer:

    __CROP_PERCENTAGE_HORIZONTAL = 0.25
    __CROP_PERCENTAGE_VERTICAL = 0.25
    __MAX_HASH_DIFFERENCE = 16
    __MIN_MATCH_PERCENTAGE = 0.75
    __VIDEO_FRAME_STEP = 20
    __FRAME_WINDOW_TO_CHECK = 5

    __previous_videos = []

    class VideoData:
        def __init__(self, path: str):
            self.path = path
            self.frame_hashes = []

        def __eq__(self, other):
            if isinstance(other, VideoComparer.VideoData):
                return self.path == other.path
            return False

    def check_videos_for_duplicates(self, video_list: List[VideoData]):
        return self.__check_videos_for_duplicates(video_list)

    def __check_videos_for_duplicates(self, current_videos: List[VideoData]):
        not_previous_clips = self.__check_videos_for_duplicates_against_previous_videos(current_videos)
        unique_clips = self.__check_videos_for_duplicates_against_current_videos(not_previous_clips)
        self.__previous_videos.extend(unique_clips)
        return unique_clips

    def __check_videos_for_duplicates_against_previous_videos(self, current_videos: List[VideoData]):
        for reference_video in self.__previous_videos:
            for cur_video in current_videos:
                cur_video_frame_hashes = self.__do_get_video_hash(cur_video)
                if cur_video == reference_video:
                    print("removing video: " + cur_video.path + ", same as reference: " + reference_video.path)
                    current_videos.remove(cur_video)
                else:
                    reference_video_frame_hashes = self.__do_get_video_hash(reference_video)
                    if self.__is_video_duplicate(cur_video_frame_hashes, reference_video_frame_hashes):
                        print("removing video: " + cur_video.path + ", matched with reference: " + reference_video.path)
                        current_videos.remove(cur_video)

        return current_videos

    def __check_videos_for_duplicates_against_current_videos(self, current_videos: List[VideoData]):
        video_count = 0
        # For each video get hash and compare to other video hashes
        for video1 in current_videos:
            if video_count >= len(current_videos):
                break
            video1_frame_hashes = self.__do_get_video_hash(video1)
            for video2 in current_videos[video_count + 1:]:
                if video1 == video2:
                    print("removing video: " + video2.path + ", equal to: " + video1.path)
                    current_videos.remove(video2)
                else:
                    video2_frame_hashes = self.__do_get_video_hash(video2)
                    if self.__is_video_duplicate(video1_frame_hashes, video2_frame_hashes):
                        print("removing video: " + video2.path + ", matched with: " + video1.path)
                        current_videos.remove(video2)
            video_count += 1

        return current_videos

    def __do_get_video_hash(self, video: VideoData):
        if len(video.frame_hashes) == 0:
            video.frame_hashes = self.do_compute_video_hash_decord(video)
        return video.frame_hashes

    def __do_compute_video_hash_cv2(self, video: VideoData):
        frame_counter = 0
        frame_step = self.__VIDEO_FRAME_STEP
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
                relevant_frame = self.__get_significant_portion_of_frame(pil_frame)
                frame_hashes.append(self.__get_frame_hash(relevant_frame))
            elif not read_success:
                print('failed at frame ' + str(frame_counter))
                break
            frame_counter += 1

        video_capture.release()

        return frame_hashes

    def do_compute_video_hash_decord(self, video: VideoData):
        frame_counter = 0
        frame_step = self.__VIDEO_FRAME_STEP
        frame_hashes = []
        vr = VideoReader(video.path, ctx=cpu(0), width=1280, height=720)
        while frame_counter < len(vr):
            if frame_counter % frame_step != 0:
                frame_counter += 1
                continue
            frame = vr[frame_counter].asnumpy()
            pil_frame = Image.fromarray(frame)
            pil_frame_grayscale = pil_frame.convert('L')
            relevant_frame = self.__get_significant_portion_of_frame(pil_frame_grayscale)
            frame_hashes.append(self.__get_frame_hash(relevant_frame))
            frame_counter += 1

        return frame_hashes

    def __get_significant_portion_of_frame(self, frame: Image):
        crop_x1 = int(frame.width * self.__crop_initial_index(self.__CROP_PERCENTAGE_HORIZONTAL))
        crop_x2 = int(frame.width * self.__crop_final_index(self.__CROP_PERCENTAGE_HORIZONTAL))
        crop_y1 = int(frame.height * self.__crop_initial_index(self.__CROP_PERCENTAGE_VERTICAL))
        crop_y2 = int(frame.height * self.__crop_final_index(self.__CROP_PERCENTAGE_VERTICAL))
        return frame.crop((crop_x1, crop_y1, crop_x2, crop_y2))

    def __crop_initial_index(self, crop_percentage: float):
        return (1 - crop_percentage) / 2

    def __crop_final_index(self, crop_percentage: float):
        return (1 + crop_percentage) / 2

    def __get_frame_hash(self, frame: Image):
        gray_scale = frame.convert('L')
        return imagehash.phash(gray_scale)

    def __is_video_duplicate(self, video1_frames, video2_frames) -> bool:
        # Based on https://aws.amazon.com/blogs/media/metfc-automatically-compare-two-videos-to-find-common-content/
        starting_index1 = 0
        while starting_index1 <= len(video1_frames) - self.__FRAME_WINDOW_TO_CHECK:
            window1 = video1_frames[starting_index1:starting_index1 + self.__FRAME_WINDOW_TO_CHECK]
            starting_index2 = 0
            while starting_index2 <= len(video2_frames) - self.__FRAME_WINDOW_TO_CHECK:
                window2 = video2_frames[starting_index2:starting_index2 + self.__FRAME_WINDOW_TO_CHECK]
                if self.__compare_frame_windows(window1, window2):
                    return True
                starting_index2 += self.__FRAME_WINDOW_TO_CHECK
            starting_index1 += self.__FRAME_WINDOW_TO_CHECK
        return False

    def __compare_frame_windows(self, window1, window2) -> bool:
        match_count = 0
        for window1_hash in window1:
            for window2_hash in window2:
                diff = window1_hash - window2_hash
                if diff < self.__MAX_HASH_DIFFERENCE:
                    match_count += 1
                    window2.remove(window2_hash)
                    break

        num_compared = len(window1)
        percentage_match = match_count / num_compared
        matched = (percentage_match >= self.__MIN_MATCH_PERCENTAGE)
        return matched
