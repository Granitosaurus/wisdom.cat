from flask import Flask
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config.from_pyfile('config.py')
redis = FlaskRedis(app)



import tvnot.views
import tvnot.scraper
import tvnot.scheduler
