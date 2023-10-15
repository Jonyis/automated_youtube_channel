import datetime

import TwitchApi
from ClipData import ClipData


class TwitchScraper:
    __DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, twitch: TwitchApi):
        self.__headers = None
        self.__twitch = twitch

    def get_clips(self,
                  channel=None,
                  game=None,
                  clips_to_get_count=1,
                  max_clip_count=100,
                  language=None,
                  previous_clips=[],
                  timeLimit=86400,
                  dateCheck=None,
                  min_view_count=0,
                  max_clip_duration=120,
                  last_received_cursor=None):  # TODO: add clips per page

        last_cursor = last_received_cursor
        listOfPosts = []
        returnCursor = None
        startedAt = datetime.datetime.now() - datetime.timedelta(days=1, hours=0)
        endedAt = datetime.datetime.now()
        min_time_apart = 120
        clips_per_page = 25
        game_id = self.__twitch.get_twitch_game_id_by_game_name(game)
        clips_to_get_count = min(clips_to_get_count, max_clip_count)
        while len(listOfPosts) < clips_to_get_count:
            try:
                response = self.__twitch.get_twitch_clips(game_id=game_id,
                                                          broadcaster_name=channel,
                                                          cursor=last_cursor,
                                                          started_at=startedAt,
                                                          ended_at=endedAt,
                                                          clips_per_page=clips_per_page)

                clipList, cursor = self.__get_clip_data(response)
                if cursor is None or cursor == last_cursor:
                    break
                last_cursor = cursor
            except SystemExit as err:
                raise SystemExit(err)

            for clip in clipList:

                # If not the game we want we get another clip
                if game is not None and clip["game_id"] != game_id:
                    continue
                # If clip doesn't have enough views we dont want it
                if clip["view_count"] < min_view_count:
                    continue
                # If clip is longer than we want we dont include the clip
                if clip["duration"] > max_clip_duration:
                    continue

                if language is not None and clip["language"] != language:
                    continue

                # Prevent same post twice
                if any(d.url == clip["url"] for d in previous_clips):
                    continue

                clipInfo = ClipData(clip["broadcaster_name"],
                                    clip["id"],
                                    clip["title"],
                                    clip["url"],
                                    self.__get_clip_real_time(clip),
                                    clip["thumbnail_url"])
                if not clipInfo.is_valid(dateCheck,
                                         timeLimit,
                                         min_time_apart,
                                         previous_clips + listOfPosts):
                    continue
                listOfPosts.append(clipInfo)
                if len(listOfPosts) >= clips_to_get_count:
                    break
            returnCursor = cursor

        return listOfPosts, returnCursor

    @staticmethod
    def __get_clip_data(response=None):
        jsonData = response.json()
        clipList = jsonData['data']
        cursor = jsonData['pagination']['cursor']
        return clipList, cursor

    def __get_clip_real_time(self, clip):
        if len(clip["video_id"]) > 0:
            return datetime.datetime.strptime(self.__twitch.get_twitch_video(clip["video_id"])["created_at"],
                                              self.__DATE_FORMAT) + datetime.timedelta(seconds=clip["vod_offset"])

        return datetime.datetime.strptime(clip["created_at"], self.__DATE_FORMAT)
