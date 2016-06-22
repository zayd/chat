from ranker import app
context = ('server.crt', 'server.key')
context = ('letsencrypt.crt', 'letsencrypt.key')
import uuid
app.secret_key = str(uuid.uuid4())
app.run(host='0.0.0.0', port=3799, debug=True, ssl_context=context)
