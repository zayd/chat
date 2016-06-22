import sys
sys.path.append('../')
import cPickle as pickle
import numpy as np

from ranking.skipthoughts import skipthoughts

import config


class SkipthoughtFeatures(object):

  def __init__(self, corpus_path=config.CORPUS_PATH):
      """ Loading sentences, model weights to compute features """
      self.model = skipthoughts.load_model()

      with open(corpus_path) as f:
          source_train, self.target_train, source_test, self.target_test = pickle.load(f)

  def get_features(self, mode):
      if mode == 'train':
        source_vectors = skipthoughts.encode(self.model, self.source_train)
        target_vectors = skipthoughts.encode(self.model, self.target_train)
        return source_vectors, target_vectors
      elif mode == 'test':
        source_vectors = skipthoughts.encode(self.model, self.source_test)
        target_vectors = skipthoughts.encode(self.model, self.target_test)
        return source_vectors, target_vectors
      elif mode == 'deploy':
        target_vectors = skipthoughts.encode(self.model, self.target_test)
        return target_vectors
      elif mode == 'final':
        target_vectors = []
        target_vectors.append(skipthoughts.encode(self.model, self.target_test))
        target_vectors.append(skipthoughts.encode(self.model, self.target_train))
        target_vectors = np.vstack(target_vectors)
        return target_vectors
      else:
        raise Exception('unknown mode')

  def get_feature(self, query):
    """ Return feature for one query sentence """
    return skipthoughts.encode(self.model, [query])
