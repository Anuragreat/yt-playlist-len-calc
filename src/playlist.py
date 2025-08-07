import json
import logging
import os
from datetime import timedelta

import redis
import asyncio

from pymongo import MongoClient
from src.utils import call_youtube_api, parse
from src.video import Video

REDIS_URL = os.environ["REDIS_URL"]
MONGO_URL = os.environ["MONGO_URL"]
CACHE_TTL = 60 * 60 * 24  # 24 hours

redis_client = redis.from_url(REDIS_URL)
mongo_collection = MongoClient(os.environ["MONGO_URL"])["ytplaylistdb"][
    "ytplaylistcounts"
]

def playlist_stars(views, likes, comments):
    if views == 0:
        return "☆☆☆☆☆☆☆☆☆☆ 0/10"

    # Engagement ratios
    like_ratio = likes / views
    comment_ratio = comments / views

    # Max expected ratios for scaling
    max_like = 0.04
    max_comment = 0.003

    # Scaled score
    score = (min(like_ratio / max_like, 1.0) * 0.6 +
             min(comment_ratio / max_comment, 1.0) * 0.4) * 10

    # Round to nearest 0.5 stars
    rounded_score = round(score * 2) / 2  # e.g., 7.0, 7.5, 8.0

    # Build the star string
    full_stars = int(rounded_score)  # integer part
    half_star = 1 if rounded_score % 1 >= 0.5 else 0
    empty_stars = 10 - full_stars - half_star

    # Create the star string with full, half, and empty stars
    star_string = "★" * full_stars + "⯪" * half_star + "☆" * empty_stars

    # Return both the stars and the numeric score
    return f"{star_string} {rounded_score}/10"
    
class Playlist:
    def __init__(
        self,
        playlist_id,
        custom_speed=None,
        start_range=None,
        end_range=None,
        youtube_api=None,
    ):
        self.playlist_id = playlist_id
        self.next_page = ""  # for pagination
        self.total_duration = timedelta(0)  # total duration
        self.custom_speed = custom_speed
        self.start_range = start_range
        self.end_range = end_range
        self.youtube_api = youtube_api

    async def do_async_work(self):

        found = self.get_video_list_from_cache(self.playlist_id)
        logging.info(f"Playlist {self.playlist_id} in cache: {found}")
        if not found:
            await self.get_video_ids_list()
            await self.get_videos_details()
            self.save_to_cache()

        self.available_count = sum([x.considered for x in self.videos])
        self.unavailable_count = len(self.videos) - self.available_count
        self.total_duration = sum([x.duration for x in self.videos], timedelta(0))
        self.average_duration = self.total_duration / self.available_count
        self.video_count = len(self.videos)
        self.start_range = max(1, self.start_range) if self.start_range else 1
        self.end_range = (
            min(self.available_count, self.end_range)
            if self.end_range
            else self.available_count
        )

        if self.start_range and self.end_range:
            self.videos_range = self.videos[self.start_range - 1 : self.end_range]
            self.total_duration = sum(
                [x.duration for x in self.videos_range], timedelta(0)
            )
            self.available_count = sum([x.considered for x in self.videos_range])
            self.unavailable_count = len(self.videos_range) - self.available_count
            self.average_duration = self.total_duration / self.available_count

    def __repr__(self):
        return f"Playlist(playlist_id={self.playlist_id}, video_count={self.video_count}, total_duration={self.total_duration}, average_duration={self.average_duration})"

    def increment_playlist_count(self, playlist_id):
        try:
            mongo_collection.update_one(
                {"playlist_id": playlist_id}, {"$inc": {"count": 1}}, upsert=True
            )
        except Exception as e:
            logging.error(f"Error incrementing playlist count for {playlist_id}: {e}")

    def get_video_list_from_cache(self, playlist_id):
        key = f"playlist:{playlist_id}"
        self.increment_playlist_count(playlist_id)

        try:
            cached_data = redis_client.get(key)
            if cached_data:
                self.videos = [
                    Video(video_id=None, video_data=video_data)
                    for video_data in json.loads(cached_data)
                ]
                return True
        except Exception as e:
            logging.error(f"Error retrieving cache for {playlist_id}: {e}")

        return False

    def save_to_cache(self):
        try:
            jsonified_videos = json.dumps([video.to_dict() for video in self.videos])
            key = f"playlist:{self.playlist_id}"
            redis_client.setex(key, CACHE_TTL, jsonified_videos)
        except Exception as e:
            logging.error(f"Error saving to cache for playlist {self.playlist_id}: {e}")

    async def get_video_ids_list(self):

        self.video_ids = []
        while True:
            results = await call_youtube_api(
                "playlistItems",
                api=self.youtube_api,
                playlistId=self.playlist_id,
                pageToken=self.next_page,
            )
            self.video_ids += [x["contentDetails"]["videoId"] for x in results["items"]]

            if "nextPageToken" in results and len(self.video_ids) < 500:
                self.next_page = results["nextPageToken"]
            else:
                break

    async def get_videos_details(self):

        self.videos = []
        for i in range(0, len(self.video_ids), 50):
            video_ids = self.video_ids[i : i + 50]
            video_data = await call_youtube_api(
                "videos", api=self.youtube_api, video_ids=video_ids
            )

            for id, data in zip(video_ids, video_data["items"]):
                video = Video(id, data, self.custom_speed)
                self.videos.append(video)

    async def get_videos_details(self):

        self.videos = []
        chunks = [self.video_ids[i : i + 50] for i in range(0, len(self.video_ids), 50)]
        tasks = [
            call_youtube_api("videos", api=self.youtube_api, video_ids=chunk)
            for chunk in chunks
        ]
        responses = await asyncio.gather(*tasks)

        for chunk, video_data in zip(chunks, responses):
            for video_id, data in zip(chunk, video_data["items"]):
                video = Video(video_id, data, self.custom_speed)
                self.videos.append(video)

    def get_output_string(self):
        output_string = [
            "Playlist : " + self.playlist_name,
            "ID : " + self.playlist_id,
            "Creator : " + self.playlist_creator,
        ]
    
        if self.video_count >= 500:
            output_string.append("No of videos limited to 500.")
    
        total_likes = sum([int(x.likes) for x in self.videos_range])
        total_comments = sum([int(x.comments) for x in self.videos_range])
        total_views = sum([int(x.views) for x in self.videos_range])
    
        avg_likes = total_likes // self.available_count if self.available_count else 0
        avg_comments = total_comments // self.available_count if self.available_count else 0
        avg_views = total_views // self.available_count if self.available_count else 0

        quality_rating = playlist_stars(total_views, total_likes, total_comments)
    
        output_string += [
            f"Video count : {self.available_count} (from {self.start_range} to {self.end_range}) ({self.unavailable_count} unavailable)",
            "Average video length : " + parse(self.total_duration / self.available_count),
            "TOTAL LENGTH : " + parse(self.total_duration),
            "At 1.25x : " + parse(self.total_duration / 1.25),
            "At 1.50x : " + parse(self.total_duration / 1.5),
            "At 1.75x : " + parse(self.total_duration / 1.75),
            "At 2.00x : " + parse(self.total_duration / 2),
            f"Average Likes👍 : {avg_likes}",
            f"Average Comments💬 : {avg_comments}",
            f"Average Views👀 : {avg_views}",
            f"Playlist Quality🎶: {quality_rating}"
        ]
    
        if self.custom_speed:
            output_string.append(
                f"At {self.custom_speed:.2f}x : {parse(self.total_duration / self.custom_speed)}"
            )
        
        return output_string
