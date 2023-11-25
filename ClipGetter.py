from RedditScraper import RedditScraper
from TwitchScraper import TwitchScraper


class ClipGetter:

    class ClipGetterParams:
        def __init__(self, max_clip_count, min_view_count,
                     max_clip_duration, reference_date,
                     max_time_apart_from_reference_date, clip_language):
            self.max_clip_count = max_clip_count
            self.min_view_count = min_view_count
            self.max_clip_duration = max_clip_duration
            self.reference_date = reference_date
            self.max_time_apart_from_reference_date = max_time_apart_from_reference_date
            self.clip_language = clip_language

    def __init__(self,
                 reddit_scrapper: RedditScraper,
                 twitch_scrapper: TwitchScraper,
                 params: ClipGetterParams):
        self.__twitch_scrapper = twitch_scrapper
        self.__reddit_scrapper = reddit_scrapper
        self.params = params

    def get_clips_from_reddit(self,
                              subReddit,
                              amountOfPosts=None,
                              topOfWhat=None,
                              minimumScore=0,
                              compareList=[]):
        clip_list, got_all_posts_available = \
            self.__reddit_scrapper.get_clips(subReddit,
                                             amountOfPosts,
                                             topOfWhat,
                                             minimumScore,
                                             compareList,
                                             self.params.max_clip_duration,
                                             self.params.reference_date,
                                             self.params.max_time_apart_from_reference_date)
        return clip_list, got_all_posts_available

    def get_twitch_clips_from_game(self,
                                   game=None,
                                   clips_to_get_count=1,
                                   previous_clips=[],
                                   last_received_cursor=None):
        list_of_posts = []
        cursor = last_received_cursor
        while len(list_of_posts) < clips_to_get_count:
            clips_found, cursor = \
                self.__do_get_twitch_clips(game=game,
                                           clips_to_get_count=clips_to_get_count,
                                           already_found_clips=previous_clips,
                                           last_received_cursor=cursor)
            list_of_posts += clips_found
        return list_of_posts

    def get_twitch_clips_from_channels(self,
                                       list_of_channels=[],
                                       clips_to_get_count=1,
                                       already_found_clips=[],
                                       last_received_cursor=None):

        clips_found = []
        cursor = last_received_cursor
        while len(clips_found) < clips_to_get_count:
            clips_found, cursor = \
                self.__do_get_twitch_clips(channel=list_of_channels[0],
                                           clips_to_get_count=clips_to_get_count,
                                           already_found_clips=already_found_clips + clips_found,
                                           last_received_cursor=cursor)
            clips_found += clips_found
        return clips_found

    def __do_get_twitch_clips(self,
                              game=None,
                              channel=None,
                              clip_id=None,
                              clips_to_get_count=1,
                              already_found_clips=[],
                              last_received_cursor=None):
        clips_found, cursor = \
            self.__twitch_scrapper.get_clips(
                channel=channel,
                game=game,
                clip_id=clip_id,
                clips_to_get_count=clips_to_get_count,
                max_clip_count=self.params.max_clip_count,
                language=self.params.clip_language,
                previous_clips=already_found_clips,
                max_time_apart_from_reference_date=
                self.params.max_time_apart_from_reference_date,
                reference_date=self.params.reference_date,
                min_view_count=self.params.min_view_count,
                max_clip_duration=self.params.max_clip_duration,
                last_received_cursor=last_received_cursor)
        return clips_found, cursor
