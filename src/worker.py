#!/usr/bin/env python
import sys
from rq import Connection, Worker

# Preload libraries
from chat_module import generate_response

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with Connection():
    qs = sys.argv[1:] or ['default']

    w = Worker(qs)
    w.work()
