from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config.from_pyfile('config.py')
redis = FlaskRedis(app, decode_responses=True)


import wisdomcat.views
import wisdomcat.scraper
import wisdomcat.scheduler
