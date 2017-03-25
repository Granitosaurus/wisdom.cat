from collections import OrderedDict
from urllib.parse import urljoin

import requests
import click
from parsel import Selector
from tvnot import app, redis
from tvnot.databases import connect_db
from tvnot import config

DEFAULT_COUNT = 5


@app.cli.command('scrape')
@click.option('-c', '--count', type=click.INT, help='limit of videos per channel [default:5]')
def scrape(count=DEFAULT_COUNT):
    """update database with new entries"""
    channels = config.AUTHORS
    db = connect_db()
    for name, chanel_id in channels.items():
        click.echo('scraping "{}"'.format(name))
        items = scrape_channel(chanel_id, count)
        for item in items:
            redis.set('video_{}'.format(item['watch_id'], item))
        click.echo('  scraped {} items'.format(len(items)))
    db.commit()
    db.close()


def scrape_channel(channel, count):
    url = "https://www.youtube.com/channel/{}/videos".format(channel)
    resp = requests.get(url)
    sel = Selector(text=resp.text)
    videos = sel.xpath("//h3/a/@href").extract()[:count]
    cur = connect_db().cursor()
    all_videos = []  # todo don't scrape the same
    cur.close()
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
    item = OrderedDict()
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
