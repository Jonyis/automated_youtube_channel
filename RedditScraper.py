import datetime
import re

import praw

import TwitchApi
from ClipData import ClipData


class RedditScraper:

    def __init__(self, reddit: praw.reddit.Reddit, twitch: TwitchApi):
        self.__twitch = twitch
        self.__reddit = reddit

    __DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def get_clips(self,
                  subReddit,
                  amountOfPosts=None,
                  topOfWhat=None,
                  minimumScore=0,
                  compareList=[],
                  maxTimeDelta=datetime.timedelta(weeks=1)):
        listOfPosts = []
        i = 0
        j = 0
        gotMaxPosts = False
        date = datetime.date.today().strftime("%Y-%m-%d")

        time = '20:00:00.00'
        dateCheck = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(days=0,
                                                                                                               hours=0)
        print("Looking from posts begining at " + (
                dateCheck - maxTimeDelta).strftime(
            '%Y-%m-%d %H:%M:%S.%f') + " and ending at " + dateCheck.strftime('%Y-%m-%d %H:%M:%S.%f'))
        # search('selftext:"clips.twitch.tv" OR url:"clips.twitch.tv"', sort='relevance', time_filter=topOfWhat,
        # limit=None)

        for submission in self.__reddit.subreddit(subReddit).search('url:"clips.twitch.tv"', sort='relevance',
                                                                  time_filter=topOfWhat, limit=None):
            n = re.search("https?:\/\/(?:[a-z0-9-]+\.)*clips.twitch\.tv(?:\S*)?", submission.selftext, re.IGNORECASE)
            k = submission.score
            datePosted = datetime.datetime.fromtimestamp(submission.created_utc)

            j += 1
            print("Scanned", j, "posts", end="\r", flush=True)

            totalSeconds = (dateCheck - datePosted).total_seconds()

            if k >= minimumScore and maxTimeDelta.total_seconds() > totalSeconds > 0:

                if n:
                    url = self.__url_exctractor(n.group(0))
                else:
                    url = self.__url_exctractor(submission.url)

                # Prevent same post twice
                if any(d.url == url for d in listOfPosts):
                    continue

                # If it's not the first time we're grabbing posts make sure we didn't already grab it before grabbing
                # it (bad wording)
                if any(d.url == url for d in compareList):
                    continue

                clip_info = self.get_clip_info(url)

                # If no clip found or full video unavailable
                if clip_info is None:
                    continue

                clip_data = ClipData(clip_info["creator_name"],
                                     clip_info["id"],
                                     clip_info["title"],
                                     clip_info["url"],
                                     self.__get_clip_real_time(clip_info),
                                     clip_info["thumbnail_url"],
                                     clip_info["view_count"],
                                     clip_info["language"])

                if not clip_data.is_valid(dateCheck, maxTimeDelta, 2*60, compareList+listOfPosts):
                    continue

                listOfPosts.append(clip_data)

                i += 1
                if i == amountOfPosts:
                    gotMaxPosts = True
                    break
        print("Scanned", j, "posts")
        print("Grabbing " + str(len(listOfPosts)) + " posts from r/" + subReddit)
        print("")
        return listOfPosts, gotMaxPosts

    @staticmethod
    def __url_exctractor(urlXX):
        if '?' in urlXX:
            urlTMP = urlXX.partition('?')
            urlXX = urlTMP[0]
        if 'embed?clip=' in urlXX:
            urlXX = urlXX.replace('embed?clip=', '')
        if '?tt_medium=clips_api&tt_content=url' in urlXX:
            urlXX = urlXX.replace('?tt_medium=clips_api&tt_content=url', '')
        if '?tt_medium=redt' in urlXX:
            print(urlXX)
            urlXX = urlXX.replace('?tt_medium=redt', '')
        if ')' in urlXX:
            urlXX = urlXX.replace(')', '')
        if '.' in urlXX[-1:]:
            urlXX = urlXX[:-1]
        if '](' in urlXX:
            TEMPURLXX = urlXX.partition('](')
            urlXX = TEMPURLXX[2]
        return urlXX

    def get_clip_info(self, url):
        clipID = url.split(".tv/", 1)[1]
        return self.__twitch.get_twitch_clips(clip_id=clipID).json()['data'][0]

    def post_video_on_subreddit(self, subReddit, title, url):
        self.__reddit.subreddit(subReddit).submit(title, url=url)

    def __get_clip_real_time(self, clip):
        if len(clip["video_id"]) > 0:
            return datetime.datetime.strptime(self.__twitch.get_twitch_video(clip["video_id"])["created_at"],
                                              self.__DATE_FORMAT) + datetime.timedelta(seconds=clip["vod_offset"])

        return datetime.datetime.strptime(clip["created_at"], self.__DATE_FORMAT)
