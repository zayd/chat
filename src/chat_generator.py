""" Interface between server app and ranking back-end. Do pre/post processing here """

from chat_ranker import ChatRanker

import config
import cPickle as pickle

class ChatGenerator(object):

  def __init__(self, corpus_path=config.CORPUS_PATH, mode='deploy'):
    self.mode = mode
    self.ranker = ChatRanker(corpus_path=corpus_path, mode=mode)

    with open(corpus_path) as f:
        source_train, target_train, source_test, self.target_test = pickle.load(f)

    if self.mode == 'final':
      self.target_test = self.target_test + target_train

  def generate_response(self, query):
    topk = self._postprocess(
            self.ranker.topk(self._preprocess(query)))

    return topk

  def _preprocess(self, query):
    """ Identity for now """
    return query

  def _postprocess(self, responses):
    """ Convert list to dicts for frontend """
    for idx, response in enumerate(responses):
      responses[idx] = {'id': response[0],
                        'text': self.target_test[response[0]]}

      for jdx, score in enumerate(response[1:]):
        responses[idx]['score_' + str(jdx)] = response[1:][jdx]

    return responses


if __name__ == "__main__":
  cg = ChatGenerator()

  topk = cg.generate_response("This is a test of the emergency broadcast system")
  import IPython; IPython.embed();
