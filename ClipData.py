from __future__ import annotations
from datetime import datetime
from typing import List


class ClipData:

    def __init__(self,
                 creator_name: str,
                 slug: str,
                 title: str,
                 url: str,
                 date_created: datetime,
                 thumbnail_url: str,
                 view_count: int,
                 language: str):
        self.channel = "https://twitch.tv/" + creator_name
        self.slug = slug
        self.title = title
        self.url = url
        self.date_created = date_created
        self.thumbnail_url = thumbnail_url
        self.view_count = view_count
        self.language = language
        self.path = None

    def __repr__(self):
        return f'Clip(title: \'{self.title}\', ' \
               f'url: {self.url}, ' \
               f'channel: {self.channel}, ' \
               f'slug: {self.slug}, ' \
               f'date_created: {self.date_created}, ' \
               f'path: {self.path})'

    def is_valid(self,
                 reference_date: datetime,
                 max_time_apart_from_reference_date: int,
                 min_time_apart: int,
                 already_found_clips: List[ClipData]) -> bool:

        # Check if clip was posted within desired range from specified date
        if (reference_date - self.date_created).total_seconds() > max_time_apart_from_reference_date:
            return False

        # If clips from the same channel were created less than X seconds apart we assume they are the same clip
        for post in already_found_clips:
            if post.channel == self.channel:
                if post.date_created > self.date_created:
                    time_diff = (post.date_created - self.date_created)
                else:
                    time_diff = (post.date_created - self.date_created)
                if time_diff.total_seconds() < min_time_apart:
                    return False
        return True
