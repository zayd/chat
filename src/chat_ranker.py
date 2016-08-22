import sys
sys.path.insert(0, '../')

from ranking.skipthoughts import eval_rank

import inflection
import config

import numpy as np
from sklearn.preprocessing import normalize

from features.feature_combiner import FeatureCombiner

class ChatRanker(object):
  """ Combines multiple ranking features to generate rank """

  def __init__(self, feature_names=['SkipthoughtFeatures'], corpus_path=config.CORPUS_PATH, mode='deploy'):
    self.mode = mode
    self.fc = FeatureCombiner(feature_names=feature_names, corpus_path=corpus_path)
    _, self.target_vectors = self.fc.combine_all(mode=self.mode)
    #self.target_embedded_vectors =

  #def __init__(self, feature_names=['ChatSkipthoughts'], corpus_path=config.CORPUS_PATH):
  #  self.features = []
  #  for feature_name in feature_names:
  #    # Convert ChatSkipthoughts to chat_skipthoughts
  #    module_name = inflection.underscore(feature_name)
  #    module = __import__(module_name)
  #    class_ = getattr(module, feature_name)
  #    self.features.append(class_(corpus_path=corpus_path))

  def topk(self, query, k=5, theano_context=None):
    return self.rank(query, theano_context=theano_context)[:k]

  #def score(self, query, features, weights):
  #  """ Combine multiple features to rank results """
  #  """ TODO work with multiple features """

  #  feature_scores = []
  #  for feature in features:
  #    feature_scores.append(feature.rank(query))

  #  return feature_scores[0]

  def rank(self, query, theano_context=None):
    source_vector = self.fc.combine_query(query=query)
    query_triplet = (None, source_vector, self.target_vectors)

    source, target = eval_rank.evaluate(query_triplet, '../models/ranking', out=True, theano_context=theano_context)

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
  cr = ChatRanker()

  score_list = cr.rank("This is a test of the emergency broadcast system")
  import IPython; IPython.embed();
