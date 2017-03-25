from threading import Thread

import schedule
import time

from tvnot import app
from tvnot import scraper


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(10)


def setup_scheduler():
    print('setting up scheduler')
    job = schedule.every(30).minutes
    job.do(scraper.scrape)
    t = Thread(target=run_schedule)
    t.start()


if __name__ == "__main__":
    setup_scheduler()
    app.run(host='0.0.0.0', use_reloader=False)
