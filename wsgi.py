from main import app
from gunicorn.app.base import BaseApplication
from gunicorn.workers.sync import SyncWorker


class FlaskApplication(BaseApplication):

  def __init__(self, app, options=None):
    self.options = options or {}
    self.application = app
    super().__init__()

  def load_config(self):
    config = {
      key: value
      for key, value in self.options.items()
      if key in self.cfg.settings and value is not None
    }
    for key, value in config.items():
      self.cfg.set(key.lower(), value)

  def load(self):
    return self.application


if __name__ == '__main__':
  options = {
    'bind': '0.0.0.0:8080',  # Replace with the port you want to use
    'workers': 4  # Increase the number of workers as needed
  }
  FlaskApplication(app, options).run()
