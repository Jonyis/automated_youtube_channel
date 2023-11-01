from datetime import datetime, timedelta

from RedditScraper import RedditScraper
from TwitchScraper import TwitchScraper


class ClipGetter:

    def __init__(self, reddit_scrapper: RedditScraper, twitch_scrapper: TwitchScraper):
        self.__twitch_scrapper = twitch_scrapper
        self.__reddit_scrapper = reddit_scrapper

    def get_clips_from_reddit(self,
                              subReddit,
                              amountOfPosts=None,
                              topOfWhat=None,
                              minimumScore=0,
                              compareList=[],
                              maxTimeDelta=0):
        clip_list, cursor = self.__reddit_scrapper.get_clips(subReddit,
                                                             amountOfPosts,
                                                             topOfWhat,
                                                             minimumScore,
                                                             compareList,
                                                             maxTimeDelta)
        return clip_list

    def get_twitch_clips_from_game(self,
                                   game=None,
                                   clips_to_get_count=1,
                                   max_clip_count=100,
                                   language=None,
                                   previous_clips=[],
                                   max_time_apart_from_reference_date=timedelta(weeks=1),
                                   reference_date=datetime.now(),
                                   min_view_count=0,
                                   max_clip_duration=120,
                                   last_received_cursor=None):
        list_of_posts = []
        cursor = last_received_cursor
        while len(list_of_posts) < clips_to_get_count:
            clips_found, cursor = \
                self.__do_get_twitch_clips(game=game,
                                           clips_to_get_count=clips_to_get_count,
                                           max_clip_count=max_clip_count,
                                           language=language,
                                           already_found_clips=previous_clips,
                                           max_time_apart_from_reference_date=max_time_apart_from_reference_date,
                                           reference_date=reference_date,
                                           min_view_count=min_view_count,
                                           max_clip_duration=max_clip_duration,
                                           last_received_cursor=cursor)
            list_of_posts += clips_found
        return list_of_posts

    def get_twitch_clips_from_channels(self,
                                       list_of_channels=[],
                                       clips_to_get_count=1,
                                       max_clip_count=100,
                                       language='en',
                                       already_found_clips=[],
                                       max_time_apart_from_reference_date=timedelta(weeks=1),
                                       reference_date=None,
                                       min_view_count=0,
                                       max_clip_duration=120,
                                       last_received_cursor=None):

        clips_found = []
        cursor = last_received_cursor
        while len(clips_found) < clips_to_get_count:
            clips_found, cursor = \
                self.__do_get_twitch_clips(channel=list_of_channels[0],
                                           clips_to_get_count=clips_to_get_count,
                                           max_clip_count=max_clip_count,
                                           language=language,
                                           already_found_clips=already_found_clips + clips_found,
                                           max_time_apart_from_reference_date=max_time_apart_from_reference_date,
                                           reference_date=reference_date,
                                           min_view_count=min_view_count,
                                           max_clip_duration=max_clip_duration,
                                           last_received_cursor=cursor)
            clips_found += clips_found
        return clips_found

    def __do_get_twitch_clips(self,
                              game=None,
                              channel=None,
                              clip_id=None,
                              clips_to_get_count=1,
                              max_clip_count=100,
                              language='en',
                              already_found_clips=[],
                              max_time_apart_from_reference_date=timedelta(weeks=1),
                              reference_date=None,
                              min_view_count=0,
                              max_clip_duration=120,
                              last_received_cursor=None):
        clips_found, cursor = \
            self.__twitch_scrapper.get_clips(channel=channel,
                                             game=game,
                                             clip_id=clip_id,
                                             clips_to_get_count=clips_to_get_count,
                                             max_clip_count=max_clip_count,
                                             language=language,
                                             previous_clips=already_found_clips,
                                             max_time_apart_from_reference_date=max_time_apart_from_reference_date,
                                             reference_date=reference_date,
                                             min_view_count=min_view_count,
                                             max_clip_duration=max_clip_duration,
                                             last_received_cursor=last_received_cursor)
        return clips_found, cursor
