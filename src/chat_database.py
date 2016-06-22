""" Interface to save and load responses """
import pymongo
import config

class ChatDatabase(object):

  def __init__(self, MONGO_URI=config.MONGO_URI):

    self.MONGO_URI = MONGO_URI

    self.client = pymongo.MongoClient(self.MONGO_URI)
    self.db = self.client['chats-db']

  #def save_message(self, message):
  #  self.db['messages'].insert(message)

  def save_chat(self, chat):
    self.db['chats'].update(chat, chat, upsert=True)
    # Don't want to duplicate chats
    # self.db['chats'].insert(chat)

  #def get_all_responses(self, chat):
  #  """ TO DO: Currently filtering by not Visitor """

  def get_all_by_chat(self,
        fields={u'agent_names': True, u'history': [u'msg', u'name']}):
    """ Yield chat responses one-by-one

        fields: Dict of fields to return for each response
                If None, returns all fields.
    """

    if fields == None:
      for response in self.db['chats'].find():
        yield response
    else:
      for response in self.db['chats'].find():
        if not response.get('history', None):
          continue

        filtered = {}

        for field in fields:
          if fields[field] is True:
            filtered[field] = response.get(field, None)
          elif type(fields[field]) is list:
            filtered[field] = [self._extract_fields(message, fields=fields[field])
                                 for message in response.get(field, None)]

        yield filtered

  def _extract_fields(self, response, fields=['agent_names', 'history']):
    """ Extract fields from response dict
        fields: List
    """
    filtered = {}

    for field in fields:
      filtered[field] = response.get(field, '')

    return filtered

  #def save_response(self, text, chat_id, time=None):
  #  response = {'text': text, 'chat_id': chat_id, 'time': time}
  #  self.db['responses'].insert(response)

  #def save_query(self, text, chat_id, time=None):
  #  response = {'text': text, 'chat_id': chat_id, 'time': time}
  #  self.db['queries'].insert(response)

  def get_token(self, username=None):

    if username:
      query_filter = {"username": username}
    else:
      query_filter = {}

    for token in self.db['tokens'].find(query_filter):
      yield token
