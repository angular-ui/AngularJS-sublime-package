import sublime, sublime_plugin, os, re, codecs, threading, time

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

		if is_inside_tag :
			return (self.attributes, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

		if not is_inside_tag:
			in_scope = False

			for scope in self.settings.get('component_defined_scopes'):
				if view.match_selector(locations[0], scope):
					in_scope = True

			if in_scope:
				return self.custom_components
			else:
				return []

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


class AngularjsFileIndexCommand(sublime_plugin.WindowCommand):
	is_indexing = False
	windows = {}

	def run(self):
		is_indexing = True
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')

		thread = AngularjsWalkThread(
			sublime.active_window().folders(), 
			self.settings.get('exclude_dirs'),
			self.settings.get('match_definitions'),
			self.settings.get('match_expression'),
			self.settings.get('match_expression_group')
		)

		thread.start()
		self.track_walk_thread(thread)

	def track_walk_thread(self, thread):
		sublime.status_message("AngularJS: indexing definitions")

		if thread.is_alive():
			sublime.set_timeout(lambda: self.track_walk_thread(thread), 1000)
		else:
			AngularjsFileIndexCommand.windows[sublime.active_window().id()] = thread.result
			sublime.status_message('AngularJS: indexing completed in ' + str(thread.time_taken))
			sublime.set_timeout(lambda: sublime.status_message(''), 1500)
			AngularjsFileIndexCommand.is_indexing = False


class AngularjsFindCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')
		self.current_window_id = sublime.active_window().id()

		if AngularjsFileIndexCommand.is_indexing:
			return

		if not sublime.active_window().id() in AngularjsFileIndexCommand.windows:
			sublime.active_window().run_command('angularjs_file_index')
			return

		self.definition_List = AngularjsFileIndexCommand.windows[self.current_window_id]
		self.current_window = sublime.active_window()
		self.current_file = self.current_window.active_view().file_name()

		if int(sublime.version()) >= 3000 and self.settings.get('show_file_preview'):
			self.current_window.show_quick_panel(self.definition_List, self.on_done, False, -1, self.on_highlight)
		else:
			self.current_window.show_quick_panel(self.definition_List, self.on_done)

	def on_highlight(self, index):
		self.current_window.open_file(self.definition_List[index][1], sublime.TRANSIENT)
		self.current_window.active_view().run_command("goto_line", {"line": int(self.definition_List[index][2])} )

	def on_done(self, index):
		if index > -1:
			self.current_window.open_file(self.definition_List[index][1])
			self.handle_file_open_go_to(int(self.definition_List[index][2]))
		else:
			self.current_window.open_file(self.current_file)

	def handle_file_open_go_to(self, line):
		if not self.current_window.active_view().is_loading():
			self.current_window.active_view().run_command("goto_line", {"line": line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)


class AngularjsLookUpDefinitionCommand(sublime_plugin.WindowCommand):
	def run(self):
		for region in sublime.active_window().active_view().sel():
			
			# temporarily change word_separators so that - and . are excluded from list
			sublime_preferences = sublime.load_settings("Preferences.sublime-settings")
			original_word_separators = sublime_preferences.get('word_separators')
			sublime_preferences.set('word_separators', "/\\()\"':,;<>~!@#$%^&*|+=[]{}`~?")
			
			word_point = sublime.active_window().active_view().word(region)
			definition = sublime.active_window().active_view().substr(word_point)

			# set word_separators back to their original value
			sublime_preferences.set('word_separators', original_word_separators)

			definition = re.sub(
				'(\w*)-(\w*)',
				lambda match: match.group(1) + match.group(2).capitalize(),
				definition
			)

		for item in AngularjsFileIndexCommand.windows[sublime.active_window().id()]:
			if(re.search(definition, item[0])):
				print(item)
				sublime.active_window().open_file(item[1])
				self.handle_file_open_go_to(int(item[2]))
				break

	def handle_file_open_go_to(self, line):
		active_view = sublime.active_window().active_view()
		if not active_view.is_loading():
			active_view.run_command("goto_line", {"line": line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)


class AngularjsWalkThread(threading.Thread):
	def __init__(self, folders, exclude_dirs, match_definitions, match_expression, match_expression_group):
		self.folders = folders
		self.exclude_dirs = exclude_dirs
		self.match_definitions = match_definitions
		self.match_expression = match_expression
		self.match_expression_group = match_expression_group
		self.match_expressions = []
		threading.Thread.__init__(self)

	def run(self):
		self.function_matches = []
		self.function_match_details = []
		start = time.time()
		for definition in self.match_definitions:
			self.match_expressions.append(
				(definition, re.compile(self.match_expression.format(definition)))
			)

		project_folders = self.folders
		skip_dirs = self.exclude_dirs

		for path in project_folders:
			for r,d,f in os.walk(path):
				if not [skip for skip in skip_dirs if path + '/' + skip in r]:
					for files in f:
						if files.endswith(".js"):
							_file = codecs.open(r+'/'+files)
							_lines = _file.readlines();
							_file.close()
							line_number = 1
							for line in _lines:
								matches = self.get_definition_details(line)
								if len(matches):
									for matched in matches:
										definition_name = matched[0] + ":  "
										definition_name += matched[1].group(int(self.match_expression_group))
										self.function_matches.append([definition_name, r+'/'+files, str(line_number)])
								line_number += 1
		self.time_taken = time.time() - start
		self.result = self.function_matches

	def get_definition_details(self, line_content):
		matches = []
		for expression in self.match_expressions:
			matched = expression[1].search(repr(line_content))
			if matched:
				#print('matched it', expression)
				matches.append((expression[0], matched))
		return matches
