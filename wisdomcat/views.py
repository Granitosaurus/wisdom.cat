import json

from flask import render_template, request, redirect, url_for, g, session, abort
from jinja2 import TemplateNotFound

from wisdomcat import app, redis
from wisdomcat import config


@app.before_first_request
def make_session_permanent():
    session.permanent = True


def get_authors():
    if not session.get('authors'):
        session['authors'] = config.AUTHORS
    return session['authors']


def get_videos():
    videos = []
    for channel in get_authors():
        key_name = 'channel:{}'.format(channel)
        videos.extend(redis.lrange(key_name, 0, -1))
    videos = sorted([json.loads(v) for v in videos], key=lambda v: v['timestamp'], reverse=True)
    return videos


@app.route('/')
def index():
    # todo maybe shouldn't redirect to post list and render first video on homepage
    # todo SCRAPER should update view count from time to time?
    return _render_video(0)


def _render_video(video_index):
    # todo maybe make this javascript'y blah blah blah
    # load every video into doc and change it with javascript
    videos = get_videos()
    if video_index >= len(videos):
        # todo should let user know the list is empty, maybe redirect to last?
        return redirect(url_for('post', post=0))
    item = videos[video_index]
    return render_template('index.html',
                           item=item,
                           video_index=video_index)


@app.route('/meow/<int:post>')
def post(post):
    return _render_video(post)


@app.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        authors = dict()
        for author, author_id in config.AUTHORS.items():
            if request.form.get(author_id, None):
                authors[author] = author_id
        session['authors'] = authors
        return redirect(url_for('index'))
    return render_template('configure.html')


@app.route('/archive')
def archive():
    videos = get_videos()
    return render_template('archive.html', videos=videos)


@app.route('/<string:page_name>')
def static_page(page_name):
    try:
        return render_template('{}.html'.format(page_name))
    except TemplateNotFound:
        return abort(404)
