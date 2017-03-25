from datetime import datetime

from flask import render_template, request, redirect, url_for, g, session, abort
from jinja2 import TemplateNotFound

from tvnot import app
from tvnot import config
from tvnot.storage import all_videos


@app.before_first_request
def make_session_permanent():
    session.permanent = True


def generate_videos():
    """returns videos based on current session profile configuration"""
    if not session.get('authors'):
        session['authors'] = config.AUTHORS
    authors = session['authors'].values()
    videos = all_videos()
    videos.sort(key=lambda v: datetime.strptime(v['date'], '%Y-%m-%d'), reverse=True)
    values = [v for v in videos if v['author_id'] in authors]
    return values


def get_videos(regenerate=False):
    if not session.get('videos') or regenerate:
        session['videos'] = generate_videos()
    return session['videos']


@app.route('/')
def index():
    # update videos every time in case config changed or new videos in the database
    # todo smarter video regeneration system - update only when new crawl or settings have changed
    videos = get_videos(regenerate=True)
    del session['videos']
    session['videos'] = videos
    return redirect(url_for('post', post=0))


@app.route('/post/<int:post>')
def post(post):
    if post >= len(get_videos()):
        return redirect(url_for('post', post=0))
    item = get_videos()[post]
    return render_template('index.html',
                           item=item,
                           video_index=post)


@app.route('/configure', methods=['GET', 'POST'])
def configure():
    if request.method == 'POST':
        authors = dict()
        for author, author_id in config.AUTHORS.items():
            if request.form.get(author_id, 'off') == 'on':
                authors[author] = author_id
        session['authors'] = authors
    return render_template('configure.html')


@app.route('/archive')
def archive():
    videos = all_videos()
    return render_template('archive.html', videos=videos)


@app.route('/<string:page_name>')
def static_page(page_name):
    try:
        return render_template('{}.html'.format(page_name))
    except TemplateNotFound:
        return abort(404)
