import sys
sys.path.insert(0, '../')

from ranking.skipthoughts import skipthoughts
from ranking.skipthoughts import eval_rank

import config

import cPickle as pickle
import numpy as np
from sklearn.preprocessing import normalize

import sys
sys.path.insert(0, '../../src')

class ChatSkipthoughts(object):
  """ Class that generates rankings from skipthoughts model """

  def __init__(self, corpus_path=config.CORPUS_PATH):
      """ Loading sentences to do rankings """
      with open(corpus_path) as f:
          source_train, target_train, source_test, self.target_test = pickle.load(f)

      #source_train_vectors, target_train_vectors, source_test_vectors, target_test_vectors = \
      #        [x[1] for x in np.load(corpus_vectors).items()]

      self.model = skipthoughts.load_model()
      self.target_vectors = skipthoughts.encode(self.model, self.target_test)

  def rank(self, query):
    source_vector = skipthoughts.encode(self.model, [query])
    query_triplet = (self.target_test, source_vector, self.target_vectors)

    source, target = eval_rank.evaluate(query_triplet, '../models/ranking', out=True)

    score_list = self.compute_rank(source, target)

    # Make assumption that only one query
    return score_list[0]

  def compute_rank(self, source, target):
    target = normalize(target)

    npts = source.shape[0]
    score_list = []
    for idx in range(npts):
      s = source[idx, :]
      s = normalize(s)

      d = np.dot(s, target.T).flatten()

      sorted_args = np.argsort(d)
      score_list.append(zip(sorted_args[::-1], d[sorted_args][::-1]))

    return score_list

if __name__ == "__main__":
  cs = ChatSkipthoughts()

  score_list = cs.rank("This is a test of the emergency broadcast system")
  import IPython; IPython.embed();
