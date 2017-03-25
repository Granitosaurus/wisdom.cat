from urllib.parse import urljoin

import requests
import click
from parsel import Selector
from tvnot import app, redis
from tvnot import config

DEFAULT_COUNT = 1


@app.cli.command('clean')
def clean():
    if 'y' not in input('are you sure you want to delete all of the videos? (y/n)').lower():
        return
    redis.flushall()


@app.cli.command('show')
def show():
    for video in redis.scan(match='video_*')[1]:
        print(video)
        for k,v in redis.hgetall(video).items():
            print('    {}: {}'.format(k, v))


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
            redis.hmset('video_{}'.format(item['watch_id']), item)
        click.echo('  scraped {} items'.format(len(items)))


def scrape_channel(channel, count):
    url = "https://www.youtube.com/channel/{}/videos".format(channel)
    resp = requests.get(url)
    sel = Selector(text=resp.text)
    videos = sel.xpath("//h3/a/@href").extract()[:count]
    all_videos = [i.decode('utf8').split('video_')[-1] for i in redis.scan(match='video_*')[1]]
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
    item['views'] = itemprop('interactionCount')
    item['author'] = sel.xpath("//div[@class='yt-user-info']/a/text()").extract_first()
    item['author_id'] = itemprop('channelId')
    return item


if __name__ == '__main__':
    scrape()
