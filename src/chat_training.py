""" Class to preprocess and train ranking model """
from chat_database import ChatDatabase
import config
import itertools

from ranking.skipthoughts import skipthoughts
from ranking.skipthoughts import eval_rank

from sklearn.cross_validation import train_test_split

class ChatTraining(object):

  def __init__(self, train=True):

    self.model = skipthoughts.load_model()

    self.cd = ChatDatabase()

    # Chat Processing Pipeline
    self.chats = self.get_chats()
    messages = self.rename(self.chats)
    groups = self.group_speakers(messages)
    self.pairs = self.generate_pairs(groups)
    self.source_train, self.source_test, self.target_train, self.target_test = \
        self.generate_corpus(self.pairs)

    source_train_vectors, target_train_vectors = \
        self.encode_vectors(self.source_train, self.target_train)

    source_test_vectors, target_test_vectors = \
        self.encode_vectors(self.source_test, self.target_test)

    self.train = (self.target_train, source_train_vectors, target_train_vectors)
    self.dev = (self.target_test, source_test_vectors, target_test_vectors)

    import IPython; IPython.embed();

    eval_rank.trainer(self.train, self.dev, saveto=config.SNAPSHOT)


  def get_chats(self):
    return self.cd.get_all_by_chat()

  def rename(self, chats):
    for chat in chats:
      agents = chat['agent_names'] + config.AGENT_NAMES
      messages = [self._rename_message(message, agents) for message in chat['history']]
      yield [message for message in messages if message is not None]

  def group_speakers(self, chats):
    for chat in chats:
      grouped_chat = []
      for name, messages in itertools.groupby(chat, lambda m: m['name']):
        grouped_chat.append({'msg': ' '.join([m['msg'] for m in messages]),
          'name': name})

      yield grouped_chat

  def generate_pairs(self, chats):
    for chat in chats:
      # Yield pairs of chat messages
      for idx, message in enumerate(chat):
        if message['name'] == config.CUST_TAG:
          if idx == len(chat)-1:
            continue
          else:
            yield message, chat[idx+1]

  def generate_corpus(self, pairs):
    source = []
    target = []
    for pair in pairs:
      source.append(pair[0]['msg'])
      target.append(pair[1]['msg'])

    source_train, source_test, target_train, target_test = \
        train_test_split(source, target, test_size=config.TEST_SIZE)

    return source_train, source_test, target_train, target_test

  def encode_vectors(self, source, target):

    source_vectors = skipthoughts.encode(self.model, source)
    target_vectors = skipthoughts.encode(self.model, target)

    return source_vectors, target_vectors

  def _rename_message(self, message, agents):
   # Filter empty messages
   if message.get('msg', '') == '':
     return
   # Replace names
   else:
     renamed = message
     if message.get('name', '') in agents:
       renamed['name'] = config.AGENT_TAG
     else:
       renamed['name'] = config.CUST_TAG
     return renamed

if __name__ == "__main__":
  ct = ChatTraining()
