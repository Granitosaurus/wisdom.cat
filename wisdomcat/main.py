from threading import Thread

import schedule
import time

from wisdomcat import scraper, app


def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(5)


def setup_scheduler():
    print('setting up scheduler')
    job = schedule.every(1).minutes
    job.do(scraper.scrape)
    t = Thread(target=run_schedule)
    t.start()


print('trying to set up scheduler')
setup_scheduler()
if __name__ == '__main__':
    app.run(use_reloader=False, debug=True)
