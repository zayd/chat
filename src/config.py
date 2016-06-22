""" ChatDatabase Options """
MONGO_URI = "mongodb://localhost:10000/"
MONGO_DB = "chats-db"

""" Zopim API Settings Endpoint """
ZOPIM_URL = "https://www.zopim.com"

ZOPIM_CLIENT_SECRET = r"y9yMMdKqtueH6x91b0PKmZ7HnNeXXsxCBxbGXyDMwKZCEiQhI5OuSLv7mddzKrln"
ZOPIM_CLIENT_ID = r"m4nCI1uldbypCOrjw8HMiJQob5DzHD3E28vuFb5qwyGLsI3YNk"
ZOPIM_REDIRECT_URI = "https://parakeet.zaydenam.com:3799/authorize"
ZOPIM_AUTH_URI = "https://www.zopim.com/oauth2/authorizations/new"
ZOPIM_TOKEN_URI = "https://www.zopim.com/oauth2/token"

""" Chat Training Settings """
CUST_TAG, AGENT_TAG= "Customer", "Agent"
AGENT_NAMES = ["The Udacity Team"]
TEST_SIZE = 0.04
SNAPSHOT = "../models/V2"

""" Chat Skipthough Settings """
CORPUS_PATH = "../src/corpus.pkl"
#CORPUS_VECTORS = "../src/corpus.npz"

# ZOPIM_USERNAME = "zayd.enam@gmail.com"
# ZOPIM_PASSWORD = "qdVWyep9CX"
