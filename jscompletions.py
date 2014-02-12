import sublime


def js_disabled():
	package_settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')
	return package_settings.get('disable_default_js_completions', False)


def global_completions(word=None):
	js_completions = sublime.load_settings('AngularJS-js-completions.sublime-settings')
	if js_disabled():
		return []
	if word:
		symbol = js_completions.get(word, [])
		# in the settings we have strings, instead of a list of completions
		# since multiple symbols can have the same set of completions
		# which we prefix with '_'
		if len(symbol) and symbol[0] == '_':
			symbol = js_completions.get(symbol, [])
		return [tuple(completion) for completion in list(symbol)]
	else:
		return [tuple(completion) for completion in list(js_completions.get('js_completions', []))]


def in_string_completions(prefix):
	js_completions = sublime.load_settings('AngularJS-js-completions.sublime-settings')
	if js_disabled():
		return []
	events = []
	injectables = []
	if prefix == '$':
		events = list(js_completions.get('events', []))
		events = [tuple(event) for event in events]
		injectables = list(js_completions.get('js_completions', []))
		# filter out the js_completions list so that we only include
		# items prefixed with '$' and use their simple form for the completion
		# Also, suffix them with (DI) to signify that they're a Dependency Injection
		injectables = [(injectable[0] + '(DI)', '\\'+injectable[0].split('\t')[0]) for injectable in injectables if injectable[0][0] == '$']
	return events + injectables


def controllers(project_index):
	all_defs = project_index.get('definitions')
	controllers = [(completion[0].split(':  ')[1] + '\tAngularJS', completion[0].split(':  ')[1]) for completion in all_defs if completion[0].startswith('controller')]
	return list(set(controllers))
