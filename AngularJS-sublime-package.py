import sublime, sublime_plugin, os, re, codecs, threading, json, time

class AngularJSSublimePackage(sublime_plugin.EventListener):
	"""
	Provides AngularJS attribute and custom component completions
	"""

	def on_query_completions(self, view, prefix, locations):
		if not hasattr(self, 'settings'):
			self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')

			self.settings.add_on_change('angular_components', self.process_angular_components)
			self.process_angular_components()

			self.settings.add_on_change('core_attribute_list', self.process_attributes)
			self.settings.add_on_change('extended_attribute_list', self.process_attributes)
			self.settings.add_on_change('AngularUI_attribute_list', self.process_attributes)
			self.settings.add_on_change('enable_data_prefix', self.process_attributes)
			self.settings.add_on_change('enable_AngularUI_directives', self.process_attributes)
			self.process_attributes()

		if self.settings.get('disable_plugin'):
			return []

		single_match = False
		all_matched = True

		for scope in self.settings.get('attribute_avoided_scopes'):
			if view.match_selector(locations[0], scope):
				return []

		for scope in list(self.settings.get('attribute_defined_scopes')):
			if view.match_selector(locations[0], scope):
				single_match = True
			else:
				all_matched = False

		if not self.settings.get('ensure_all_scopes_are_matched') and single_match:
			return self.completions(view, locations, True)
		elif self.settings.get('ensure_all_scopes_are_matched') and all_matched:
			return self.completions(view, locations, True)
		else:
			return self.completions(view, locations, False)

	def completions(self, view, locations, is_inside_tag):
		print(view.scope_name(view.sel()[0].end()))
		if is_inside_tag :
			attrs = self.attributes[:]
			if self.settings.get('add_indexed_directives'):
				attrs += self.add_indexed_directives()
			return (attrs + self.add_indexed_directives(), sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

		if not is_inside_tag:
			in_scope = False

			for scope in self.settings.get('component_defined_scopes'):
				if view.match_selector(locations[0], scope):
					in_scope = True

			if in_scope:
				return self.custom_components
			else:
				return []

	def add_indexed_directives(self):
		indexed_attrs = []
		indexes = AngularjsFileIndexCommand.windows["".join(sublime.active_window().folders())]
		if indexes:
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
		self.attributes = []
		add_data_prefix = self.settings.get('enable_data_prefix')

		for attr in self.settings.get('core_attribute_list'):
			if add_data_prefix:
				attr[1] = "data-" + attr[1]

			self.attributes.append(attr)

		for attr in self.settings.get('extended_attribute_list'):
			if add_data_prefix:
				attr[1] = "data-" + attr[1]

			self.attributes.append(attr)

		if self.settings.get('enable_AngularUI_directives'):
			for attr in self.settings.get('AngularUI_attribute_list'):
				if add_data_prefix:
					attr[1] = "data-" + attr[1]

				self.attributes.append(attr)

		self.attributes = [tuple(attr) for attr in self.attributes]

	def process_angular_components(self):
		self.custom_components = []
		for component in self.settings.get('angular_components'):
			self.custom_components.append((component + "\tAngularJS Component", component + "$1>$2</" + component + '>'))

	def on_post_save(self, view):
		settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')

		thread = AngularjsWalkThread(
			file_path = view.file_name(), 
			exclude_dirs = settings.get('exclude_dirs'),
			match_definitions = settings.get('match_definitions'),
			match_expression = settings.get('match_expression'),
			match_expression_group = settings.get('match_expression_group'),
			index_key = "-".join(sublime.active_window().folders())
		)
		thread.start()


class AngularjsFileIndexCommand(sublime_plugin.WindowCommand):
	is_indexing = False
	windows = {}

	def run(self):
		AngularjsFileIndexCommand.is_indexing = True
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')

		thread = AngularjsWalkThread(
			folders = sublime.active_window().folders(), 
			exclude_dirs = self.settings.get('exclude_dirs'),
			match_definitions = self.settings.get('match_definitions'),
			match_expression = self.settings.get('match_expression'),
			match_expression_group = self.settings.get('match_expression_group')
		)

		thread.start()
		self.track_walk_thread(thread)

	def track_walk_thread(self, thread):
		sublime.status_message("AngularJS: indexing definitions")
		self.index_key = "-".join(sublime.active_window().folders())

		if thread.is_alive():
			sublime.set_timeout(lambda: self.track_walk_thread(thread), 1000)
		else:
			AngularjsFileIndexCommand.windows[self.index_key] = thread.result
			sublime.status_message('AngularJS: indexing completed in ' + str(thread.time_taken))
			sublime.set_timeout(lambda: sublime.status_message(''), 1500)

			# save new indexes to file
			j_data = open(sublime.packages_path() + '/AngularJS-sublime-package/index.cache', 'w')
			j_data.write(json.dumps(AngularjsFileIndexCommand.windows))
			j_data.close()
			AngularjsFileIndexCommand.is_indexing = False


class AngularjsFindCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')
		self.index_key = "-".join(sublime.active_window().folders())
		self.old_view = sublime.active_window().active_view()

		if AngularjsFileIndexCommand.is_indexing:
			return


		if not self.index_key in AngularjsFileIndexCommand.windows:
			try:
				j_data = open(sublime.packages_path() + '/AngularJS-sublime-package/index.cache', 'r').read()
				AngularjsFileIndexCommand.windows = json.loads(j_data)
				j_data.close()
			except:
				pass

		if not self.index_key in AngularjsFileIndexCommand.windows:
			sublime.active_window().run_command('angularjs_file_index')
			return

		self.definition_List = AngularjsFileIndexCommand.windows[self.index_key]
		self.current_window = sublime.active_window()
		self.current_file = self.current_window.active_view().file_name()
		self.current_file_location = self.current_window.active_view().sel()[0].end()

		if int(sublime.version()) >= 3000 and self.settings.get('show_file_preview'):
			self.current_window.show_quick_panel(self.definition_List, self.on_done, False, -1, self.on_highlight)
		else:
			self.current_window.show_quick_panel(self.definition_List, self.on_done)

	def on_highlight(self, index):
		self.current_window.open_file(self.definition_List[index][1], sublime.TRANSIENT)
		view = self.current_window.active_view()
		view.show_at_center(view.text_point(int(self.definition_List[index][2]), 0))

	def on_done(self, index):
		if index > -1:
			self.current_window.open_file(self.definition_List[index][1])
			self.handle_file_open_go_to(int(self.definition_List[index][2]))
		else:
			self.current_window.focus_view(self.old_view)
			self.current_window.active_view().show_at_center(
				self.current_file_location
			)

	def handle_file_open_go_to(self, line):
		if not self.current_window.active_view().is_loading():
			self.current_window.active_view().run_command("goto_line", {"line": line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)


class AngularjsLookUpDefinitionCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.active_view = sublime.active_window().active_view()
		self.index_key = "-".join(sublime.active_window().folders())

		if not self.index_key in AngularjsFileIndexCommand.windows:
			try:
				j_data = open(sublime.packages_path() + '/AngularJS-sublime-package/index.cache', 'r').read()
				AngularjsFileIndexCommand.windows = json.loads(j_data)
				j_data.close()
			except:
				pass

		if not self.index_key in AngularjsFileIndexCommand.windows:
			sublime.status_message("AngularJS: No definition indexing found for project")
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
		print(definition)
		print('searching for lookup item now: . '+definition+'$')
		for item in AngularjsFileIndexCommand.windows[self.index_key]:
			if(re.search('. '+definition+'$', item[0])):
				print('item found')
				print(item)
				sublime.active_window().open_file(item[1])
				self.handle_file_open_go_to(int(item[2]))
				break

	def find_word(self, region):
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')
		non_char = re.compile(self.settings.get('non_word_chars'))
		look_up_found = ""
		start_point = region.end()
		begin_point = start_point-1
		end_point = start_point+1
		start_ing = 0
		tolerance = 10

		while (not non_char.search(self.active_view.substr(sublime.Region(start_point, end_point))) 
		and end_point and start_ing < tolerance):
			end_point += 1
			start_ing += 1
		start_ing = 0
		while (not non_char.search(self.active_view.substr(sublime.Region(begin_point, start_point)))
		and start_ing < tolerance):
			start_ing += 1
			begin_point -= 1

		look_up_found = self.active_view.substr(sublime.Region(begin_point+1, end_point-1))
		print('AngularJS: look up found: ' + look_up_found)
		return look_up_found

	def handle_file_open_go_to(self, line):
		print(line)
		if not self.active_view.is_loading():
			sublime.active_window().active_view().run_command("goto_line", {"line": line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)


class AngularjsWalkThread(threading.Thread):
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
			'match_definitions',
			'match_expression',
			'match_expression_group'
		)

		reindex_file_requirements = (
			'file_path',
			'index_key',
			'exclude_dirs',
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
				if not [skip for skip in self.kwargs['exclude_dirs'] if path + '/' + skip in r]:
					for _file in f:
						self.parse_file(_file, r, match_expressions)

	def reindex_file(self, index_key):
		self.index_key = index_key
		file_path = self.kwargs['file_path']
		if (file_path.endswith(".js")
		and self.index_key in AngularjsFileIndexCommand.windows
		and not [skip for skip in self.kwargs['exclude_dirs'] if skip in file_path]):
			print('AngularJS: Reindexing ' + self.kwargs['file_path'])
			AngularjsFileIndexCommand.windows[self.index_key][:] = [
				item for item in AngularjsFileIndexCommand.windows[self.index_key]
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
						AngularjsFileIndexCommand.windows[self.index_key].append([definition_name, file_path, str(line_number)])
				line_number += 1
			# save new indexes to file
			j_data = open(sublime.packages_path() + '/AngularJS-sublime-package/index.cache', 'w')
			j_data.write(json.dumps(AngularjsFileIndexCommand.windows))
			j_data.close()

	def parse_file(self, file_path, r, match_expressions):
		if file_path.endswith(".js"):
			_file = codecs.open(r+'/'+file_path)
			_lines = _file.readlines();
			_file.close()
			line_number = 1

			for line in _lines:
				matches = self.get_definition_details(line, match_expressions)
				if matches:
					for matched in matches:
						definition_name = matched[0] + ":  "
						definition_name += matched[1].group(int(self.kwargs['match_expression_group']))
						self.function_matches.append([definition_name, r + '/' +file_path, str(line_number)])
				line_number += 1

	def get_definition_details(self, line_content, match_expressions):
		matches = []
		for expression in match_expressions:
			matched = expression[1].search(repr(line_content))
			if matched:
				matches.append((expression[0], matched))

		return matches
