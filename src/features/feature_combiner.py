import inflection
import config

import numpy as np

from features import *

import importlib

class FeatureCombiner(object):

  def __init__(self, feature_names=['SkipthoughtFeatures', 'TfidfFeatures'], combiner='concat', corpus_path=config.CORPUS_PATH):
    self.combiner = combiner

    self.features = []

    for feature_name in feature_names:
      # Convert SkipthoughtFeatures to skipthought_features
      module_name = inflection.underscore(feature_name)
      module = importlib.import_module('features.' + module_name)
      class_ = getattr(module, feature_name)
      self.features.append(class_(corpus_path=corpus_path))

  def combine_all(self, mode='deploy'):
    all_source_vectors = [] # list of actual feature arrays
    all_target_vectors = [] # list of actual feature arrays

    for feature in self.features:
      if mode in ('train', 'dev'):
        source_vectors, target_vectors = feature.get_features(mode=mode)
        all_source_vectors.append(source_vectors)
        all_target_vectors.append(target_vectors)
      elif mode in ('deploy', 'final'):
        target_vectors = feature.get_features(mode=mode)
        all_target_vectors.append(target_vectors)

    if mode in ('train', 'dev'):
      all_source_vectors = np.hstack(all_source_vectors)
      all_target_vectors = np.hstack(all_target_vectors)
      return all_source_vectors, all_target_vectors
    elif mode in ('deploy', 'final'):
      all_target_vectors = np.hstack(all_target_vectors)
      return None, all_target_vectors

  def combine_query(self, query):
    combined_query_features = []

    for feature in self.features:
        query_feature = feature.get_feature(query=query)
        combined_query_features.append(query_feature)

    combined_query_features = np.hstack(combined_query_features)

    return combined_query_features

if __name__ == "__main__":
  fc = FeatureCombiner(feature_names=['SkipthoughtFeatures'])
  source_vectors, target_vectors = fc.combine_all(mode='deploy')
  import IPython; IPython.embed();





