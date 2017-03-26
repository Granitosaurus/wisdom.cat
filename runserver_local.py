from runserver import setup_scheduler
from wisdomcat import app

if __name__ == "__main__":
    setup_scheduler()
    app.run(use_reloader=False, debug=True)
