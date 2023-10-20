from datetime import datetime

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
                                   amountOfPosts=1,
                                   postLimit=100,
                                   language=None,
                                   compareList=[],
                                   timeLimit=86400,
                                   reference_date=datetime.now(),
                                   minViews=0,
                                   maxDuration=120,
                                   last_received_cursor=None):
        list_of_posts = []
        cursor = last_received_cursor
        while len(list_of_posts) < amountOfPosts:
            clips_found, cursor = self.__twitch_scrapper.get_clips(game=game,
                                                                   clips_to_get_count=amountOfPosts,
                                                                   max_clip_count=postLimit,
                                                                   language=language,
                                                                   previous_clips=compareList,
                                                                   max_time_apart_from_reference_date=timeLimit,
                                                                   reference_date=reference_date,
                                                                   min_view_count=minViews,
                                                                   max_clip_duration=maxDuration,
                                                                   last_received_cursor=cursor)
            list_of_posts += clips_found
        return list_of_posts

    def get_twitch_clips_from_channels(self,
                                       list_of_channels=[],
                                       amountOfPosts=1,
                                       postLimit=100,
                                       language='en',
                                       already_found_clips=[],
                                       timeLimit=86400,
                                       dateCheck=None,
                                       minViews=0,
                                       maxDuration=120,
                                       last_received_cursor=None):

        list_of_posts = []
        cursor = last_received_cursor
        while len(list_of_posts) < amountOfPosts:
            clips_found, cursor = self.__twitch_scrapper.get_clips(channel=list_of_channels[0],
                                                                   clips_to_get_count=amountOfPosts,
                                                                   max_clip_count=postLimit,
                                                                   language=language,
                                                                   previous_clips=already_found_clips + list_of_posts,
                                                                   max_time_apart_from_reference_date=timeLimit,
                                                                   reference_date=dateCheck,
                                                                   min_view_count=minViews,
                                                                   max_clip_duration=maxDuration,
                                                                   last_received_cursor=cursor)
            list_of_posts += clips_found
        return list_of_posts
