from bottle import route, run

@route('/wiki/<pagename>')
def show_wiki_page(pagename):
	...
	
run(host = 'localhost', port = 8080, debug = True)