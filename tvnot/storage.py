from tvnot import redis


def all_videos():
    videos = redis.scan(match='video_*')[1]
    return [redis.hgetall(v) for v in videos]
