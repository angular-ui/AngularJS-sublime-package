import sublime


def alert(msg):
	sublime.status_message('AngularJS: %s' % msg)
