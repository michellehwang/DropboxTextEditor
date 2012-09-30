from dropbox import *
from bottle import *
from pystache2 import *

APP_KEY = 'c2zss6wfrvqwc6i'
APP_SECRET = 'biqwmipv5t986v3'
ACCESS_TYPE = 'app_folder' # should be 'dropbox' or 'app_folder' as configured for your app

TOKEN_STORE = {}


def get_session():
    return session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

def get_client(access_token):
    sess = get_session()
    sess.set_token(access_token.key, access_token.secret)
    return client.DropboxClient(sess)

@route('/home')
def dropbox_home():
	sess = get_session()
	request_token = sess.obtain_request_token()
	TOKEN_STORE[request_token.key] = request_token

	callback = "http://%s/viewfiles" % (request.headers['host'])
	url = sess.build_authorize_url(request_token, oauth_callback=callback)
	prompt = """<a href="%s"><img src = "http://i47.tinypic.com/et5mra.jpg"></a>"""
	return prompt % url 


@route('/callback')
def callback_page(oauth_token=None):
    # note: the OAuth spec calls it 'oauth_token', but it's
    # actually just a request_token_key...
    
	
	access_token = sess.obtain_access_token(request_token)
	TOKEN_STORE[access_token.key] = access_token
	return view_files()

token_key = None


@route('/viewfiles/<path:path>')
def view_files(path = '.'):
	global token_key
	request_token_key = request.query.oauth_token
	
	if token_key == None:
		sess = get_session()
		if not request_token_key:
			return "Expected a request token key back!"
		request_token = TOKEN_STORE[request_token_key]
		access_token = sess.obtain_access_token(request_token) #gets the actual access_token from the server's cache `TOKEN_STORE` based on the key on the previous line
		access_token_key = access_token.key
		TOKEN_STORE[access_token.key] = access_token
		token_key = access_token.key

	else:
		access_token = TOKEN_STORE[token_key]

	client = get_client(access_token) #get_client, the function from the Dropbox example code
	context = client.metadata(path) #client.metadata is the Dropbox library call to get the list of files in the directory. You should look at the documentation of the Dropbox Python library to confirm this.
	if context['is_dir'] == True:
		return render_file('viewfiles.mustache', context)
	else: 
		file = client.get_file_and_metadata(path)[0].read()
		meta = client.get_file_and_metadata(path)[1]
		return render_file('open.mustache', {'file' : file, 'path' : path, 'rev' : meta['rev']})

@route('/viewfiles')
@route('/viewfiles/')
def view():
	return view_files()

@post('/submission')
def submit():
	file = request.params.text
	path = request.params.path
	rev = request.params.rev
	access_token = TOKEN_STORE[token_key]
	client = get_client(access_token) 
	client.put_file(path, file, overwrite = True, parent_rev=rev)

	sess = get_session()
	request_token = sess.obtain_request_token()
	TOKEN_STORE[request_token.key] = request_token

	callback = "http://%s/viewfiles" % (request.headers['host'])
	prompt = """<font face = "Helvetica">Click <a href="%s">here</a> to return to file listing</font>"""
	return prompt % callback

run(host = 'localhost', port = 8080, debug = True)