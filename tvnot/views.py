from flask import render_template, request, redirect, url_for, g, session, abort
from jinja2 import TemplateNotFound

from tvnot import app
from tvnot.databases import get_db, connect_db
from tvnot import config


@app.before_first_request
def make_session_permanent():
    session.permanent = True


def generate_videos():
    """returns videos based on current session profile configuration"""
    if not session.get('authors'):
        session['authors'] = config.AUTHORS
    db = connect_db()
    authors_ph = ', '.join('?' for a in session['authors'].values())
    cur = db.execute('SELECT * '
                     'FROM entries '
                     'WHERE author_id IN ({}) '
                     'ORDER BY date DESC'.format(authors_ph), list(session['authors'].values()))
    values = [c['watch_id'] for c in cur.fetchall()]
    cur.close()
    return values


def get_videos():
    if not session.get('videos'):
        session['videos'] = generate_videos()
    return session['videos']


@app.route('/')
def index():
    # update videos every time in case config changed or new videos in the database
    videos = get_videos()
    del session['videos']
    session['videos'] = videos
    return redirect(url_for('post', post=0))


@app.route('/post/<int:post>')
def post(post):
    if post >= len(get_videos()):
        return redirect(url_for('post', post=0))
    db = get_db()
    cur = db.execute('SELECT * '
                     'FROM entries '
                     'WHERE watch_id=:watch_id', {'watch_id': get_videos()[post]})
    item = cur.fetchone()
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
    db = get_db()
    cur = db.execute('SELECT * '
                     'FROM entries '
                     'ORDER BY date DESC')
    all_videos = cur.fetchall()
    return render_template('archive.html', videos=all_videos)


@app.route('/<string:page_name>')
def static_page(page_name):
    try:
        return render_template('{}.html'.format(page_name))
    except TemplateNotFound:
        return abort(404)
