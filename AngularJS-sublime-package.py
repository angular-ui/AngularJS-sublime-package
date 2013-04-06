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


class AngularjsFindCommand(sublime_plugin.WindowCommand):
	def __init__(self, window):
		self.is_indexing = True
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')
		thread = AngularjsWalkThread(
			sublime.active_window().folders(), 
			self.settings.get('exclude_dirs'),
			self.settings.get('match_definitions')
		)
		thread.start()
		self.track_walk_thread(thread)

	def run(self):
		if(self.is_indexing):
			return

		self.current_window = sublime.active_window()
		self.current_file = self.current_window.active_view().file_name()
		if int(sublime.version()) >= 3000 and self.settings.get('show_file_preview'):
			print('st3')
			self.current_window.show_quick_panel(self.function_matches, self.on_done, False, -1, self.on_highlight)
		else:
			self.current_window.show_quick_panel(self.function_matches, self.on_done)

	def on_highlight(self, index):
		self.current_window.open_file(self.function_matches[index][2],sublime.TRANSIENT)
		self.current_window.active_view().run_command("goto_line", {"line": int(self.function_matches[index][3])} )

	def on_done(self, index):
		if index > -1:
			self.current_window.open_file(self.function_matches[index][2])
			self.handle_file_open_go_to(int(self.function_matches[index][3]))
		else:
			self.current_window.open_file(self.current_file)

	def track_walk_thread(self, thread):
		sublime.status_message("AngularJS: indexing definitions")
		if thread.is_alive():
			sublime.set_timeout(lambda: self.track_walk_thread(thread), 1000)
		else:
			self.function_matches = thread.result
			sublime.status_message('AngularJS: indexing completed in ' + str(thread.time_taken))
			sublime.set_timeout(lambda: sublime.status_message(''), 1500)
			self.is_indexing = False

	def handle_file_open_go_to(self, line):
		if not self.current_window.active_view().is_loading():
			self.current_window.active_view().run_command("goto_line", {"line": line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)

class AngularjsWalkThread(threading.Thread):
	def __init__(self, folders, exclude_dirs, match_definitions):
		# TODO: clean up things
		self.folders = folders
		self.exclude_dirs = exclude_dirs
		self.match_definitions = match_definitions
		threading.Thread.__init__(self)

	def run(self):
		self.function_matches = []
		self.function_match_details = []
		start = time.time()
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
								matched = self.get_definition_details(line)
								if matched:
									self.function_matches.append([matched[1].group(3),matched[0],r+'/'+files, str(line_number)])
								line_number += 1
		self.time_taken = time.time() - start
		self.result = self.function_matches

	def get_definition_details(self, line_content):
		for match in self.match_definitions:
			matched = re.search('(\s(\.'+match+'|'+match+')[ ]*\([ ]*["\'])([\w\.]*)(["\'])', repr(line_content))
			if matched:
				return (match, matched)
