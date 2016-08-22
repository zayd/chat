""" Chat Generator Front-end Module """

import config
from chat_generator import ChatGenerator

cg = ChatGenerator(corpus_path=config.CORPUS_PATH)

def generate_response(query):
  return cg.generate_response(query)
