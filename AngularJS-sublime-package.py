import sublime, sublime_plugin, os, re, codecs, threading, json, time

class AngularJS():
	def init(self):
		self.projects_index_cache = {}
		self.index_cache_location = os.path.join(
			sublime.packages_path(),
			'User',
			'AngularJS.cache'
		)
		self.is_indexing = False
		self.attributes = []
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')

		try:
			json_data = open(self.index_cache_location, 'r').read()
			self.projects_index_cache = json.loads(json_data)
			json_data.close()
		except:
			pass

		self.settings.add_on_change('angular_components', self.process_angular_components)
		self.process_angular_components()

		self.settings.add_on_change('core_attribute_list', self.process_attributes)
		self.settings.add_on_change('extended_attribute_list', self.process_attributes)
		self.settings.add_on_change('AngularUI_attribute_list', self.process_attributes)
		self.settings.add_on_change('enable_data_prefix', self.process_attributes)
		self.settings.add_on_change('enable_AngularUI_directives', self.process_attributes)
		self.process_attributes()


	def active_window(self):
		return sublime.active_window()

	def active_view(self):
		return self.active_window().active_view()

	def get_index_key(self):
		return "".join(sublime.active_window().folders())

	def get_project_indexes_at(self, index_key):
		return self.projects_index_cache[index_key]

	def get_current_project_indexes(self):
		if self.get_index_key() in self.projects_index_cache:
			return self.projects_index_cache[self.get_index_key()]
		else:
			return []

	def add_indexes_to_cache(self, indexes):
		self.projects_index_cache[self.get_index_key()] = indexes
		# save new indexes to file
		j_data = open(self.index_cache_location, 'w')
		j_data.write(json.dumps(self.projects_index_cache))
		j_data.close()

	def alert(self, status_message):
		sublime.status_message('AngularJS: %s' % status_message)

	#
	# completions definitions/logic
	#

	def completions(self, view, locations, is_inside_tag):
		if is_inside_tag:
			attrs = self.attributes[:]
			if ng.settings.get('add_indexed_directives'):
				attrs += self.add_indexed_directives()
			return (attrs, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

		if not is_inside_tag:
			in_scope = False

			for scope in ng.settings.get('component_defined_scopes'):
				if view.match_selector(locations[0], scope):
					in_scope = True

			if in_scope:
				return self.custom_components
			else:
				return []

	def add_indexed_directives(self):
		indexes = ng.get_current_project_indexes()
		indexed_attrs = [
			tuple([
				self.definitionToDirective(directive) + "\t ng Indexed",
				self.definitionToDirective(directive)
			]) for directive in indexes if re.match('directive:', directive[0])
		]
		return list(set(indexed_attrs))

	def definitionToDirective(self, directive):
		return re.sub('([a-z0-9])([A-Z])', r'\1-\2', directive[0].replace('directive:  ', '')).lower()

	def process_attributes(self):
		add_data_prefix = ng.settings.get('enable_data_prefix')

		for attr in ng.settings.get('core_attribute_list'):
			if add_data_prefix:
				attr[1] = "data-" + attr[1]

			self.attributes.append(attr)

		for attr in ng.settings.get('extended_attribute_list'):
			if add_data_prefix:
				attr[1] = "data-" + attr[1]

			self.attributes.append(attr)

		if ng.settings.get('enable_AngularUI_directives'):
			for attr in ng.settings.get('AngularUI_attribute_list'):
				if add_data_prefix:
					attr[1] = "data-" + attr[1]

				self.attributes.append(attr)

		self.attributes = [tuple(attr) for attr in self.attributes]

	def process_angular_components(self):
		self.custom_components = []
		for component in ng.settings.get('angular_components'):
			self.custom_components.append((component + "\tAngularJS Component", component + "$1>$2</" + component + '>'))


ng = AngularJS()

if int(sublime.version()) < 3000:
	ng.init()

def plugin_loaded():
	global ng
	ng.init()

class AngularJSEventListener(sublime_plugin.EventListener):
	global ng

	def on_query_completions(self, view, prefix, locations):
		if ng.settings.get('disable_plugin'):
			return []
		if ng.settings.get('show_current_scope'):
			print(view.scope_name(view.sel()[0].end()))

		single_match = False
		all_matched = True

		for scope in ng.settings.get('attribute_avoided_scopes'):
			if view.match_selector(locations[0], scope):
				return []

		for scope in list(ng.settings.get('attribute_defined_scopes')):
			if view.match_selector(locations[0], scope):
				single_match = True
			else:
				all_matched = False

		if not ng.settings.get('ensure_all_scopes_are_matched') and single_match:
			return ng.completions(view, locations, True)
		elif ng.settings.get('ensure_all_scopes_are_matched') and all_matched:
			return ng.completions(view, locations, True)
		else:
			return ng.completions(view, locations, False)

	def on_post_save(self, view):
		thread = AngularJSThread(
			file_path = view.file_name(), 
			exclude_dirs = ng.settings.get('exclude_dirs'),
			exclude_file_suffixes = ng.settings.get('exclude_file_suffixes'),
			match_definitions = ng.settings.get('match_definitions'),
			match_expression = ng.settings.get('match_expression'),
			match_expression_group = ng.settings.get('match_expression_group'),
			index_key = ng.get_index_key()
		)
		thread.start()


class AngularjsFileIndexCommand(sublime_plugin.WindowCommand):

	global ng

	def run(self):
		ng.is_indexing = True

		thread = AngularJSThread(
			folders = ng.active_window().folders(),
			exclude_dirs = ng.settings.get('exclude_dirs'),
			exclude_file_suffixes = ng.settings.get('exclude_file_suffixes'),
			match_definitions = ng.settings.get('match_definitions'),
			match_expression = ng.settings.get('match_expression'),
			match_expression_group = ng.settings.get('match_expression_group')
		)

		thread.start()
		self.track_walk_thread(thread)

	def track_walk_thread(self, thread):
		ng.alert("indexing definitions")

		if thread.is_alive():
			sublime.set_timeout(lambda: self.track_walk_thread(thread), 1000)
		else:
			ng.add_indexes_to_cache(thread.result)
			ng.alert('indexing completed in ' + str(thread.time_taken))
			ng.is_indexing = False


class AngularjsFindCommand(sublime_plugin.WindowCommand):

	global ng

	def run(self):
		self.old_view = ng.active_view()
		self.definition_List = ng.get_current_project_indexes()

		if ng.is_indexing:
			return

		if not self.definition_List:
			ng.active_window().run_command('angularjs_file_index')
			return

		self.current_window = ng.active_window()
		self.current_view = ng.active_view()
		self.current_file = self.current_view.file_name()
		self.current_file_location = self.current_view.sel()[0].end()

		if int(sublime.version()) >= 3000 and ng.settings.get('show_file_preview'):
			self.current_window.show_quick_panel(self.definition_List, self.on_done, False, -1, self.on_highlight)
		else:
			self.current_window.show_quick_panel(self.definition_List, self.on_done)

	def on_highlight(self, index):
		self.current_window.open_file(self.definition_List[index][1], sublime.TRANSIENT)
		ng.active_view().run_command("goto_line", {"line": int(self.definition_List[index][2])} )

	def on_done(self, index):
		if index > -1:
			self.current_view = self.current_window.open_file(self.definition_List[index][1])
			self.handle_file_open_go_to(int(self.definition_List[index][2]))
		else:
			self.current_window.focus_view(self.old_view)
			self.current_view.show_at_center(self.current_file_location)

	def handle_file_open_go_to(self, line):
		if not self.current_view.is_loading():
			self.current_view.run_command("goto_line", {"line": line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)


class AngularjsGoToDefinitionCommand(sublime_plugin.WindowCommand):

	global ng

	def run(self):
		self.active_view = ng.active_view()

		if not ng.get_current_project_indexes():
			ng.alert("No indexing found for project")
			return

		# grab first region
		region = self.active_view.sel()[0]

		# no selection has been made
		# so begin expanding to find word
		if not region.size():
			definition = self.find_word(region)
		else:
			definition = self.active_view.substr(region)

		# ensure data- is striped out before trying to
		# normalize and look up
		definition = definition.replace('data-', '')

		# convert selections such as app-version to appVersion
		# for proper look up
		definition = re.sub('(\w*)-(\w*)', lambda match: match.group(1) + match.group(2).capitalize(), definition)
		for item in ng.get_current_project_indexes():
			if(re.search('. '+definition+'$', item[0])):
				self.active_view = ng.active_window().open_file(item[1])
				self.handle_file_open_go_to(int(item[2]))
				return
		ng.alert('definition "%s" could not be found' % definition)

	def find_word(self, region):
		non_char = re.compile(ng.settings.get('non_word_chars'))
		look_up_found = ""
		start_point = region.end()
		begin_point = start_point-1
		end_point = start_point+1

		while (not non_char.search(self.active_view.substr(sublime.Region(start_point, end_point))) 
		and end_point):
			end_point += 1
		while (not non_char.search(self.active_view.substr(sublime.Region(begin_point, start_point)))):
			begin_point -= 1

		look_up_found = self.active_view.substr(sublime.Region(begin_point+1, end_point-1))
		ng.alert('Looking up: ' + look_up_found)
		return look_up_found

	def handle_file_open_go_to(self, line):
		if not self.active_view.is_loading():
			self.active_view.run_command("goto_line", {"line": line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)


class AngularJSThread(threading.Thread):

	global ng

	def __init__(self, **kwargs):
		self.kwargs = kwargs
		threading.Thread.__init__(self)

	def run(self):
		self.function_matches = []
		self.function_match_details = []
		start = time.time()

		walk_dirs_requirements = (
			'folders',
			'exclude_dirs',
			'exclude_file_suffixes',
			'match_definitions',
			'match_expression',
			'match_expression_group'
		)

		reindex_file_requirements = (
			'file_path',
			'index_key',
			'exclude_dirs',
			'exclude_file_suffixes',
			'match_definitions',
			'match_expression',
			'match_expression_group'
		)

		if all(keys in self.kwargs for keys in walk_dirs_requirements):
			self.walk_dirs()

		if all(keys in self.kwargs for keys in reindex_file_requirements):
			self.reindex_file(self.kwargs['index_key'])

		self.time_taken = time.time() - start
		self.result = self.function_matches

	def compile_patterns(self, patterns):
		match_expressions = []
		for definition in patterns:
			match_expressions.append(
				(definition, re.compile(self.kwargs['match_expression'].format(definition)))
			)
		return match_expressions

	def walk_dirs(self):
		match_expressions = self.compile_patterns(self.kwargs['match_definitions'])

		for path in self.kwargs['folders']:
			for r,d,f in os.walk(path):
				if not [skip for skip in self.kwargs['exclude_dirs'] if os.path.join(path, os.path.normpath(skip)) in r]:
					for _file in f:
						self.parse_file(_file, r, match_expressions)

	def reindex_file(self, index_key):
		file_path = self.kwargs['file_path']

		if (file_path.endswith(".js")
		and not file_path.endswith(tuple(self.kwargs['exclude_file_suffixes']))
		and index_key in ng.projects_index_cache
		and not [skip for skip in self.kwargs['exclude_dirs'] if os.path.normpath(skip) in file_path]):
			ng.alert('Reindexing ' + self.kwargs['file_path'])
			project_index = ng.get_project_indexes_at(index_key)

			project_index[:] = [
				item for item in project_index
				if item[1] != file_path
			]

			_file = codecs.open(file_path)
			_lines = _file.readlines();
			_file.close()
			line_number = 1

			for line in _lines:
				matches = self.get_definition_details(line, self.compile_patterns(self.kwargs['match_definitions']))
				if matches:
					for matched in matches:
						definition_name = matched[0] + ":  "
						definition_name += matched[1].group(int(self.kwargs['match_expression_group']))
						project_index.append([definition_name, file_path, str(line_number)])
				line_number += 1
			ng.add_indexes_to_cache(project_index)

	def parse_file(self, file_path, r, match_expressions):
		if (file_path.endswith(".js")
		and not file_path.endswith(tuple(self.kwargs['exclude_file_suffixes']))):
			_abs_file_path = os.path.join(r, file_path)
			_file = codecs.open(_abs_file_path)
			_lines = _file.readlines();
			_file.close()
			line_number = 1

			for line in _lines:
				matches = self.get_definition_details(line, match_expressions)
				if matches:
					for matched in matches:
						definition_name = matched[0] + ":  "
						definition_name += matched[1].group(int(self.kwargs['match_expression_group']))
						self.function_matches.append([definition_name, _abs_file_path, str(line_number)])
				line_number += 1

	def get_definition_details(self, line_content, match_expressions):
		matches = []
		for expression in match_expressions:
			matched = expression[1].search(repr(line_content))
			if matched:
				matches.append((expression[0], matched))

		return matches
