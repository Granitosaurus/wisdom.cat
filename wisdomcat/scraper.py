import json
from datetime import datetime
from urllib.parse import urljoin

import requests
import click
from parsel import Selector
from wisdomcat import app, redis
from wisdomcat import config

DEFAULT_COUNT = 1


@app.cli.command('clean')
def clean():
    if 'y' not in input('are you sure you want to delete all of the videos? (y/n)').lower():
        return
    redis.flushall()


@app.cli.command('show')
def show():
    for channel in redis.scan_iter(match='channel:*'):
        videos = [json.loads(v) for v in redis.lrange(channel, 0, -1)]
        print('{: <55} {}'.format(channel.split(':')[1], videos[0]['author_id']))
        for video in videos:
            print('  {: <65.62}: {}'.format(video['name'], video['watch_id']))


@app.cli.command('scrape')
@click.option('-c', '--count', type=click.INT, help='limit of videos per channel [default:5]')
def scrape(count=None):
    """update database with new entries"""
    count = count or DEFAULT_COUNT
    channels = config.AUTHORS
    for name, chanel_id in channels.items():
        click.echo('scraping "{}"'.format(name))
        items = scrape_channel(chanel_id, count)
        for item in items:
            result = redis.lpush('channel:{}'.format(item['author']), json.dumps(item))
            if not result:
                print('  failed to store: {}'.format(item))
        click.echo('  scraped {} items'.format(len(items)))


def scrape_channel(channel, count):
    url = "https://www.youtube.com/channel/{}/videos".format(channel)
    resp = requests.get(url)
    sel = Selector(text=resp.text)
    videos = sel.xpath("//h3/a/@href").extract()[:count]
    all_videos = [redis.lrange(i, 0, -1) for i in redis.scan_iter(match='channel:*')]
    all_videos = [json.loads(i)['watch_id'] for ch in all_videos for i in ch]
    items = []
    for url in videos:
        url = urljoin(resp.url, url)
        if url.split('?v=')[1] in all_videos:
            continue
        print('  crawling {}'.format(url))
        item = scrape_video(url)
        items.append(item)
    return items


def scrape_video(url):
    resp = requests.get(url)
    sel = Selector(text=resp.text)
    item = dict()
    itemprop = lambda name: sel.xpath("//meta[@itemprop='{}']/@content".format(name)).extract_first()
    item['watch_id'] = url.split('?v=')[1]
    item['name'] = itemprop('name')
    item['date'] = itemprop('datePublished')
    item['timestamp'] = datetime.strptime(itemprop('datePublished'), '%Y-%m-%d').timestamp()
    item['views'] = itemprop('interactionCount')
    item['author'] = sel.xpath("//div[@class='yt-user-info']/a/text()").extract_first()
    item['author_id'] = itemprop('channelId')
    return item
