import sublime

# Settings file names
ANGULARJS_SUBLIME_PACKAGE = 'AngularJS-sublime-package.sublime-settings'
ANGULARJS_JS_COMPLETIONS = 'AngularJS-js-completions.sublime-settings'


def js_disabled():
	package_settings = sublime.load_settings(ANGULARJS_SUBLIME_PACKAGE)
	return package_settings.get('disable_default_js_completions', False)


def global_completions(view, prefix, locations, project_index):
	if js_disabled():
		return []

	selector = 'meta.brace.round.js, meta.delimiter.object.comma.js'
	if view.score_selector(locations[0]-2, selector):
		return DI_completions(prefix, project_index)

	js_completions = sublime.load_settings(ANGULARJS_JS_COMPLETIONS)
	word = None
	if prefix == '':
		word = view.substr(view.word(locations[0] - 2))
		# Check if we're possibly at a directive attrs param
		if 'attrs' in word.lower():
			word = 'attrs'
		# Check if we're possibly at a scope var
		if 'scope' in word.lower():
			word = '$rootScope'
	if word:
		symbol = js_completions.get(word, [])
		# in the settings we can have strings, instead of a list, for completions
		# since multiple symbols can have the same set of completions
		# which we prefix with '_'
		if len(symbol) and symbol[0] == '_':
			symbol = js_completions.get(symbol, [])
		return [tuple(completion) for completion in list(symbol)]
	else:
		return [tuple(completion) for completion in list(js_completions.get('js_completions', []))]


def in_string_completions(prefix, project_index):
	if js_disabled():
		return []
	events = event_completions(prefix, project_index)
	injectables = DI_completions(prefix, project_index)
	return events + injectables


def DI_completions(prefix, project_index):
	js_completions = sublime.load_settings(ANGULARJS_JS_COMPLETIONS)
	# TODO: Add option to turn off DI inject completions
	if js_disabled():
		return []
	DIs = []
	if prefix == '$':
		DIs_list = list(js_completions.get('js_completions', []))
		# filter out the js_completions list so that we only include
		# items prefixed with '$' and use their simple form for the completion
		# Also, suffix them with (DI) to signify that they're a Dependency Injection
		for DI in DIs_list:
			if DI[0].startswith('$'):
				DIs.append((DI[0] + '(DI)', '\\'+DI[0].split('\t')[0]))
	# Now look for any injectable items that have been indexed
	injectables = ('constant', 'factory', 'service', 'value')
	custom_DIs = get(injectables, project_index, '(DI)')
	return DIs + custom_DIs


def event_completions(prefix, project_index):
	js_completions = sublime.load_settings(ANGULARJS_JS_COMPLETIONS)
	# TODO: Add option to turn off event completions
	if js_disabled():
		return []
	events = []
	if prefix == '$':
		events = list(js_completions.get('events', []))
		events = [tuple(event) for event in events]
	return events


def get(type, project_index, suffix=''):
	all_defs = project_index.get('definitions')
	types = []
	for completion in all_defs:
		if completion[0].startswith(type):
			# Split based on 'Type: name'
			trigger = completion[0].split(':  ')[1]
			result = trigger
			# Ensure we remove any '.' to prevent breaking ST completions
			trigger = trigger.replace('.', '_') + '\tAngularJS' + suffix
			types.append((trigger, result))
	return list(set(types))
