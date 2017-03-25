from tvnot import redis


def all_videos():
    videos = redis.scan_iter(match='video_*')
    return [redis.hgetall(v) for v in videos]
