from runserver import setup_scheduler
from tvnot import app

if __name__ == "__main__":
    setup_scheduler()
    app.run(use_reloader=False, debug=True)
