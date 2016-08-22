from celery import Celery
from celery import Task

from chat_generator import ChatGenerator

def make_celery(app):
  celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'],
                  broker=app.config['CELERY_BROKER_URL'])
  celery.conf.update(app.config)
  TaskBase = celery.Task
  class ContextTask(TaskBase):
    abstract = True
    def __call__(self, *args, **kwargs):
      with app.app_context():
        return TaskBase.__call__(self, *args, **kwargs)
  celery.Task = ContextTask
  return celery

#celery = make_celery(app)
celery = Celery('tasks', broker='redis://localhost:6379', backend='redis://localhost:6379')

class GenerateResponse(Task):
  def __init__(self):
    ### Chat Generation ###
    cg = ChatGenerator(corpus_path='../src/corpus.pkl')

  def run(self, query):
    return cg.generate_response(query)

