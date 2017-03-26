from itertools import islice

from wisdomcat import redis


def all_videos(limit=None):
    videos = redis.scan_iter(match='video_*')
    results = []
    if limit:
        videos = islice(videos, 0, limit)
    for v in videos:
        results.append(redis.hgetall(v))
    return results
