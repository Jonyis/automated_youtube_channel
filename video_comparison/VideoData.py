import imagehash
from PIL import Image
from decord import VideoReader, cpu


class VideoData:

    __CROP_PERCENTAGE_HORIZONTAL = 0.25
    __CROP_PERCENTAGE_VERTICAL = 0.25
    __MAX_HASH_DIFFERENCE = 16
    __MIN_MATCH_PERCENTAGE = 0.75
    __VIDEO_FRAME_STEP = 20
    __FRAME_WINDOW_TO_CHECK = 5

    def __init__(self, path: str):
        self.path = path
        self.frame_hashes = []

    def __eq__(self, other):
        if isinstance(other, VideoData):
            return self.path == other.path
        return False

    def check_if_duplicate(self, other_video) -> bool:
        return self.path == other_video.path or self.__is_video_duplicate(other_video)

    def __do_get_video_hash(self):
        if len(self.frame_hashes) == 0:
            self.frame_hashes = self.__do_compute_video_hash()
        return self.frame_hashes

    def __do_compute_video_hash(self):
        frame_counter = 0
        frame_step = self.__VIDEO_FRAME_STEP
        frame_hashes = []
        vr = VideoReader(self.path, ctx=cpu(0), width=1280, height=720)
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

    def __is_video_duplicate(self, other_video) -> bool:
        # Based on https://aws.amazon.com/blogs/media/metfc-automatically-compare-two-videos-to-find-common-content/
        cur_video_hash = self.__do_get_video_hash()
        other_video_hash = other_video.__do_get_video_hash()

        starting_index1 = 0
        while starting_index1 <= len(cur_video_hash) - self.__FRAME_WINDOW_TO_CHECK:
            window1 = cur_video_hash[starting_index1:starting_index1 + self.__FRAME_WINDOW_TO_CHECK]
            starting_index2 = 0
            while starting_index2 <= len(other_video_hash) - self.__FRAME_WINDOW_TO_CHECK:
                window2 = other_video_hash[starting_index2:starting_index2 + self.__FRAME_WINDOW_TO_CHECK]
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
