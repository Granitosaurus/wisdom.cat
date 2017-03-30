from threading import Thread

import schedule
import time

from wisdomcat import app as application
from wisdomcat import scraper


def setup_scheduler():
    def run_schedule():
        while 1:
            schedule.run_pending()
            time.sleep(10)
    print('setting up scheduler')
    job = schedule.every(30).minutes
    job.do(scraper.scrape)
    t = Thread(target=run_schedule)
    t.start()


if __name__ == "__main__":
    setup_scheduler()
    application.run(use_reloader=False)
