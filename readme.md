# wisdom.cat

    $ cat wisdom 
    =( ^ >w< ^ )=
    wisdom.cat - is a video aggregator website that aggregates bite size videos 
    which are in some way educational. The intention of this website is 
    to have something beneficial to watch during short down-time periods; 
    i.e. while grabbing a snack in between work sessions.

₍˄·͈༝·͈˄₎◞ ̑̑ෆ⃛ http://www.wisdom.cat


## Architecture

Wisdom cat runs on three things: `requests` and `parsel` to scrape the videos, `redis` to store them and `flask` to display everything in an interactive fashion.

## Setup and running
    
    git clone git@github.com:Granitosaurus/wisdom.cat.git wisdomcat
    cd wisdomcat
    pip install -r requirements.txt
    export FLASK_APP='wisdomcat'
    flask scrape
    ...
    flask run
    # or with constant scraping updates:
    python runserver_local.py 

