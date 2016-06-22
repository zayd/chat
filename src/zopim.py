""" Implements Zopim API Interface """
import requests
from requests_oauthlib import OAuth2Session
import json
import config

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--username", type=str, help="Username for Zopim")
parser.add_argument("--save", action='store_true', help="Save to Database")
parser.add_argument("--display", type=int, help="Display first N chats")

from chat_database import ChatDatabase


class Zopim(object):

  def __init__(self, token):
    self.ZOPIM_URL = config.ZOPIM_URL

    self.zopim = OAuth2Session(config.ZOPIM_CLIENT_ID, token=token)

  def get_chats(self):
    chat_url = self.ZOPIM_URL + '/api/v2/chats'
    response = self.zopim.get(chat_url).json()

    # Get chats by batch
    page_idx = 1
    while True:
      for chat in response['chats']:
        yield chat

      if response['next_url'] is None:
        break;
      else:
        print "Getting page {0} of chats".format(page_idx)
        chat_url = response['next_url']
        response = self.zopim.get(chat_url).json()
        page_idx += 1


if __name__ == "__main__":

  args = parser.parse_args()

  if args.save:
    from chat_database import ChatDatabase
    cd = ChatDatabase()
    token = next(cd.get_token(username=args.username))

    zo = Zopim(token=token)
    chats = zo.get_chats()

    for idx, chat in enumerate(chats):
      chat["_username"] = args.username
      cd.save_chat(chat)

      if idx % 1000 == 0:
        print "Saved {0} chats".format(idx)

      #for message in chat['history']:
      #  cd.save_message(message)

  elif args.display > 0:
    from chat_database import ChatDatabase
    cd = ChatDatabase()
    token = next(cd.get_token(username=args.username))

    zo = Zopim(token=token)
    chats = zo.get_chats()

    for idx, chat in enumerate(chats):
      if idx < int(args.display):
        print chat
      else:
        break

  else:
    parser.print_help()
