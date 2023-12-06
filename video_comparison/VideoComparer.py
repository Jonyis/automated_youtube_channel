from typing import List

from video_comparison.VideoData import VideoData


class VideoComparer:

    def __init__(self):
        self.__previous_videos = []

    @staticmethod
    def to_video_data(path: str):
        return VideoData(path)

    def check_videos_for_duplicates(self, video_list: List[VideoData]):
        return self.__check_videos_for_duplicates(video_list)

    def __check_videos_for_duplicates(self, current_videos: List[VideoData]):
        not_previous_clips = self.__check_videos_for_duplicates_against_previous_videos(current_videos)
        unique_clips = self.__check_videos_for_duplicates_against_current_videos(not_previous_clips)
        self.__previous_videos.extend(unique_clips)
        return unique_clips

    def __check_videos_for_duplicates_against_previous_videos(self, current_videos: List[VideoData]):
        videos_to_remove = []
        for reference_video in self.__previous_videos:
            for cur_video in current_videos:
                if cur_video in videos_to_remove:
                    continue
                if cur_video.check_if_duplicate(reference_video):
                    print("removing video: " + cur_video.path + ", matched with reference: " + reference_video.path)
                    videos_to_remove.append(cur_video)

        return [vid for vid in current_videos if vid not in videos_to_remove]

    def __check_videos_for_duplicates_against_current_videos(self, current_videos: List[VideoData]):
        video_count = 0
        videos_to_remove = []
        # For each video get hash and compare to other video hashes
        for video1 in current_videos:
            if video_count >= len(current_videos):
                break
            if video1 in videos_to_remove:
                continue
            for video2 in current_videos[video_count + 1:]:
                if video2 in videos_to_remove:
                    continue
                if video1.check_if_duplicate(video2):
                    print("removing video: " + video2.path + ", matched with: " + video1.path)
                    videos_to_remove.append(video2)

            video_count += 1
        return [vid for vid in current_videos if vid not in videos_to_remove]
