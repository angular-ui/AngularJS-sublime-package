import sublime, sublime_plugin, os, re, codecs, threading, json, time, glob, itertools

class AngularJS():
	def init(self, isST2):
		self.isST2 = isST2
		self.projects_index_cache = {}
		self.index_cache_location = os.path.join(
			sublime.packages_path(),
			'User',
			'AngularJS.cache'
		)
		self.is_indexing = False
		self.attributes = []
		self.settings = sublime.load_settings('AngularJS-sublime-package.sublime-settings')
		self.settings_completions = sublime.load_settings('AngularJS-completions.sublime-settings')
		self.settings_js_completions = sublime.load_settings('AngularJS-js-completions.sublime-settings')

		try:
			json_data = open(self.index_cache_location, 'r').read()
			self.projects_index_cache = json.loads(json_data)
			json_data.close()
		except:
			pass

		self.settings_completions.add_on_change('core_attribute_list', self.process_attributes)
		self.settings_completions.add_on_change('extended_attribute_list', self.process_attributes)
		self.settings_completions.add_on_change('AngularUI_attribute_list', self.process_attributes)
		self.settings.add_on_change('enable_data_prefix', self.process_attributes)
		self.settings.add_on_change('enable_AngularUI_directives', self.process_attributes)
		self.process_attributes()

	def view_settings(self):
		return self.active_view().settings().get('AngularJS', {})

	def active_window(self):
		return sublime.active_window()

	def active_view(self):
		return self.active_window().active_view()

	def get_index_key(self):
		return "".join(sublime.active_window().folders())

	def get_project_indexes_at(self, index_key):
		return self.projects_index_cache[index_key]['definitions']

	def exclude_dirs(self):
		exclude_dirs = []
		for folder in ng.active_window().folders():
			exclude_dirs += [glob.glob(folder+"/"+path) for path in ng.settings.get('exclude_dirs', [])]
			exclude_dirs += [glob.glob(folder+"/"+path) for path in ng.view_settings().get('exclude_dirs', [])]
		return list(itertools.chain(*exclude_dirs))

	def get_current_project_indexes(self):
		if self.get_index_key() in self.projects_index_cache:
			if 'definitions' not in self.projects_index_cache[self.get_index_key()]:
				self.projects_index_cache[self.get_index_key()] = {'definitions':[], 'attributes': {}}
			return self.projects_index_cache[self.get_index_key()]
		else:
			return {'definitions':[], 'attributes': {}}
	def add_indexes_to_cache(self, indexes):

		self.projects_index_cache[self.get_index_key()] = {
			'definitions': indexes[0],
			'attributes': indexes[1]
		}
		# save new indexes to file
		j_data = open(self.index_cache_location, 'w')
		j_data.write(json.dumps(self.projects_index_cache))
		j_data.close()

	def find_word(self, region):
		non_char = re.compile(self.settings.get('non_word_chars'))
		look_up_found = ""
		start_point = region.end()
		begin_point = start_point-1
		end_point = start_point+1

		while (not non_char.search(self.active_view().substr(sublime.Region(start_point, end_point))) 
		and end_point):
			end_point += 1
		while (not non_char.search(self.active_view().substr(sublime.Region(begin_point, start_point)))):
			begin_point -= 1

		look_up_found = self.active_view().substr(sublime.Region(begin_point+1, end_point-1))
		self.alert('Looking up: ' + look_up_found)
		return look_up_found

	def handle_file_open_go_to(self, line):
		if not self.active_view().is_loading():
			self.active_view().run_command('goto_line', {'line': line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)

	def alert(self, status_message):
		sublime.status_message('AngularJS: %s' % status_message)

	#
	# completions definitions/logic
	#
	def isSource(self, sourceSelector):
		view = self.active_view()
		return view.score_selector(view.sel()[0].begin(), sourceSelector) > 0

	# TODO: DRY this up where possible
	def convertElementToSourceType(self, elems):
		'''
			Adds support for markup outside of HTML
			Currently just Jade and HAML
		'''
		getAttrsRegex = re.compile(r'(([A-z-].-?\w+[ >])|(\w+=)|(>[\$0-9]+))')
		def convertToJadeElement(completion):
			#list of tag partials, tag start, attrs, tag end
			pieces = [item[0] for item in getAttrsRegex.findall(completion)]
			for tagStart in pieces[:1]:
				completion = completion.replace(tagStart, "%s(" % tagStart[:-1])
			has_tab_in_body = False
			for attr in pieces[2:-1]:
				# right now tab stops are picked up in the regex so check to
				# make sure it's not a tap stop that we're at
				if not '>$' in attr: completion = completion.replace(attr, ", " + attr)
				else:
					completion = completion.replace(attr, attr.replace('>',')'))
					has_tab_in_body = True
			for tagEnd in pieces[-1:]:
				# if the tag has no atts and no tab stops
				# it got mutated, so fix it here
				if len(pieces) == 2: completion = completion.replace('</'+tagEnd.replace('>','('), ')')
				# there was no tab stop in the body
				# so clean up the end angle from the start tag
				elif not has_tab_in_body: completion = completion.replace('></'+tagEnd, ')')
				# there was a tab stop in the body
				# so just clean out the end tag
				else: completion = completion.replace('</'+tagEnd, '')
			return completion

		def convertToHamlElement(completion):
			#list of tag partials, tag start, attrs, tag end
			pieces = [item[0] for item in getAttrsRegex.findall(completion)]
			for tagStart in pieces[:1]:
				completion = '%' + completion.replace(tagStart, '%s{' % tagStart[:-1])
			has_tab_in_body = False
			for attr in pieces[2:-1]:
				# right now tab stops are picked up in the regex so check to
				# make sure it's not a tap stop that we're at
				if not '>$' in attr: completion = completion.replace(attr, ", " + attr)
				else:
					completion = completion.replace(attr, attr.replace('>','}'))
					has_tab_in_body = True
			for tagEnd in pieces[-1:]:
				# if the tag has no atts and no tab stops
				# it got mutated, so fix it here
				if len(pieces) == 2: completion = completion.replace('</'+tagEnd.replace('>','{'), '}')
				# there was no tab stop in the body
				# so clean up the end angle from the start tag
				elif not has_tab_in_body: completion = completion.replace('></'+tagEnd, '}')
				# there was a tab stop in the body
				# so just clean out the end tag
				else: completion = completion.replace('</'+tagEnd, '')
			return completion

		if self.isSource('text.html'): return elems
		if self.isSource('source.jade'):
			return [(elem[0], convertToJadeElement(elem[1])) for elem in elems]
		if self.isSource('text.haml'):
			return [(elem[0], convertToHamlElement(elem[1])) for elem in elems]

	# TODO: DRY this up where possible
	def convertAttributesToSourceType(self, attrs):
		'''
			Adds support for markup outside of HTML
			Currently just Jade and HAML
		'''
		# pattern to find multiple attributes within the completion
		jadeAttrRegex = re.compile(r'([A-z-]+-\w+|\w+=)')
		hamlAttrRegex = re.compile(r'([A-z-]+-\w+.|\w+=)')
		def convertToHamlCompletion(attr):
			attrList = hamlAttrRegex.findall(attr)
			if attrList:
				for item in attrList[:1]:
					last_char = item[-1:]
					if last_char == ' ':
						attr = attr.replace(item, '"%s" ' % item.strip())
					elif last_char == '$':
						attr = attr.replace(item, '"%s"$' % item)
					elif last_char == '=':
						attr = attr.replace(item, '"%s" => ' % item.replace('=',''))
				for item in attrList[1:]:
					attr = attr.replace(item, ', "%s" => ' % item.replace('=',''))

			return attr

		def convertMultipleAttrExpantionToJade(attr):
			# remove the first attr from the list
			attrList = jadeAttrRegex.findall(attr)[1:]
			if attrList:
				for item in attrList:
					attr = attr.replace(item, ", " + item)
			return attr

		if self.isSource('text.html'): return attrs
		if self.isSource('source.jade'):
			return [(attr[0], convertMultipleAttrExpantionToJade(attr[1])) for attr in attrs]
		if self.isSource('text.haml'): return [(attr[0], convertToHamlCompletion(attr[1])) for attr in attrs]
		return attrs;

	def convertIndexedDirectiveToTag(self, directive):
		'''
			Converts the indexed directives to element form.
			Currently any indexed directive is used as a possible element
		'''
		if self.isSource('source.jade'):
			return directive.replace('="$1"$0','')+'${1:($2)}$0'
		elif self.isSource('text.haml'):
			return '%' + directive.replace('="$1"$0','')+'${1:\\{$2\\}}$0'
		else: #assume HTML
			return directive.replace('="$1"$0','')+'$1>$0</'+directive.replace('="$1"$0','')+'>'

	def completions(self, view, prefix, locations, is_inside_tag):
		if is_inside_tag:
			pt = locations[0] - len(prefix) - 1
			ch = view.substr(sublime.Region(pt, pt + 1))

			if(ch != '<' 
			and not ng.settings.get('disable_default_directive_completions')): attrs = self.attributes[:]
			else: attrs = []
			attrs += self.get_isolate_completions(view, prefix, locations, pt)
			attrs += self.add_indexed_directives()

			attrs = self.convertAttributesToSourceType(attrs)

			return (attrs, 0)

		if not is_inside_tag:
			if not ng.isST2 and ng.isSource('text.html'):
				if(view.substr(view.sel()[0].b-1) == '<'): return []
			if ng.isST2 and ng.isSource('text.html'):
				if(view.substr(view.sel()[0].b-1) != '<'): return []
			in_scope = False

			for scope in ng.settings.get('component_defined_scopes'):
				if view.match_selector(locations[0], scope):
					in_scope = True

			if in_scope:
				completions = []
				#adjust how completions work when used for completing a tag
				completions += [
					(directive[0], self.convertIndexedDirectiveToTag(directive[1])) for directive in self.add_indexed_directives()
				]
				if not ng.settings.get('disable_default_element_completions'):
					elems = [tuple(element) for element in list(ng.settings_completions.get('angular_elements', []))]
					elems = self.convertElementToSourceType(elems)
					completions += elems
				return (completions, 0)
			else:
				return []

	def get_isolate_completions(self, view, prefix, locations, pt):
		if ng.settings.get('disable_indexed_isolate_completions'): return []

		# pulled lots from html_completions.py
		SEARCH_LIMIT = 500
		search_start = max(0, pt - SEARCH_LIMIT - len(prefix))
		line = view.substr(sublime.Region(search_start, pt + SEARCH_LIMIT))

		line_head = line[0:pt - search_start]

		# find the tag from end of line_head
		i = len(line_head) - 1
		tag = None
		space_index = len(line_head)
		while i >= 0:
			c = line_head[i]
			if c == '<':
				# found the open tag
				tag = line_head[i + 1:space_index]
				break
			if c == ' ':
				space_index = i
			i -= 1

		# check that this tag looks valid
		if not tag:
			return []

		try:
			attrs = self.get_current_project_indexes().get('attributes').get(tag)
		except:
			return []
		if attrs:
			return [('isolate: ' + a[0] + '\t'+a[1]+'attr', a[0] + '="$1"$0') for a in attrs]
		else:
			return []

	def filter_completions(self):
		current_point = ng.active_view().sel()[0].end()
		previous_text_block = ng.active_view().substr(sublime.Region(current_point-2,current_point))
		if(previous_text_block == '| '):
			filter_list = ng.get_current_project_indexes().get('definitions')
			filter_list = [(i[0], i[0][9:]) for i in filter_list if i[0][:6] == 'filter']
			filter_list = list(set(filter_list)) #attempt to remove duplicates
			filter_list += list(ng.settings_completions.get('filter_list'))
			return(filter_list)
		else:
			return []

	def js_completions(self):
		# ugly hack to fix ST bug
		# https://github.com/angular-ui/AngularJS-sublime-package/issues/14
		current_word_separators = r'./\\()\"\'-:,.;<>~!@#%^&*|+=[]{}`~?'
		def st_hack():
			ng.active_view().settings().set('word_separators', current_word_separators)

		if self.settings.get('disable_default_js_completions'): return []
		else:
			# ugly hack to fix ST bug
			ng.active_view().settings().set('word_separators', "/\()\"'-:,;<>~!@#%^&*|+=[]{}`~?")
			completions = [tuple(completion) for completion in list(self.settings_js_completions.get('js_completions', []))]
			sublime.set_timeout(st_hack, 300)
			return completions

	def add_indexed_directives(self):
		if ng.settings.get('disable_indexed_directive_completions'): return []

		try:
			indexes = ng.get_current_project_indexes().get('definitions')
		except:
			return []

		indexed_attrs = [
			tuple([
				'ngDir_' + self.definitionToDirective(directive) + '\tAngularJS',
				self.definitionToDirective(directive)+'="$1"$0'
			]) for directive in indexes if re.match('directive:', directive[0])
		]
		return list(set(indexed_attrs))

	def definitionToDirective(self, directive):
		return re.sub('([a-z0-9])([A-Z])', r'\1-\2', directive[0].replace('directive:  ', '')).lower()

	def process_attributes(self):
		add_data_prefix = ng.settings.get('enable_data_prefix')

		for attr in ng.settings_completions.get('core_attribute_list'):
			if add_data_prefix:
				attr[1] = "data-" + attr[1]

			self.attributes.append(attr)

		for attr in ng.settings_completions.get('extended_attribute_list'):
			if add_data_prefix:
				attr[1] = "data-" + attr[1]

			self.attributes.append(attr)

		if ng.settings.get('enable_AngularUI_directives'):
			for attr in ng.settings_completions.get('AngularUI_attribute_list'):
				if add_data_prefix:
					attr[1] = 'data-' + attr[1]

				self.attributes.append(attr)

		self.attributes = [tuple(attr) for attr in self.attributes]

ng = AngularJS()

if int(sublime.version()) < 3000:
	ng.init(isST2=True)

def plugin_loaded():
	global ng
	ng.init(isST2=False)

class AngularJSEventListener(sublime_plugin.EventListener):
	global ng

	def on_query_completions(self, view, prefix, locations):
		if ng.settings.get('disable_all_completions'):
			return []
		if ng.settings.get('show_current_scope'):
			print(view.scope_name(view.sel()[0].a))

		single_match = False
		all_matched = True
		_scope = view.sel()[0].a

		if(view.score_selector(_scope, 'source.js - string.quoted - comment')):
			return (ng.js_completions(), 0)

		if(view.score_selector(_scope, 'text.html string.quoted')):
			return ng.filter_completions()
		for selector in ng.settings.get('attribute_avoided_scopes'):
			if view.score_selector(_scope, selector):
				return []
		attribute_defined_scopes = list(ng.settings.get('attribute_defined_scopes'))

		for selector in attribute_defined_scopes:
			if view.score_selector(_scope, selector):
				single_match = True
			else:
				all_matched = False
		
		is_inside_tag = view.score_selector(_scope, ', '.join(attribute_defined_scopes)) > 0

		if not ng.settings.get('ensure_all_scopes_are_matched') and single_match:
			return ng.completions(view, prefix, locations, is_inside_tag)
		elif ng.settings.get('ensure_all_scopes_are_matched') and all_matched:
			return ng.completions(view, prefix, locations, is_inside_tag)
		else:
			return ng.completions(view, prefix, locations, False)

	def on_post_save(self, view):
		thread = AngularJSThread(
			file_path = view.file_name(),
			folder_exclude_patterns = view.settings().get('folder_exclude_patterns'),
			exclude_dirs = ng.exclude_dirs(),
			exclude_file_suffixes = ng.settings.get('exclude_file_suffixes'),
			match_definitions = ng.settings.get('match_definitions'),
			match_expression = ng.settings.get('match_expression'),
			match_expression_group = ng.settings.get('match_expression_group'),
			index_key = ng.get_index_key()
		)
		thread.start()

class AngularjsDeleteCacheCommand(sublime_plugin.WindowCommand):
	global ng

	def run(self):
		ng.alert('Deleting Cache')
		os.remove(ng.index_cache_location)

class AngularjsFileIndexCommand(sublime_plugin.WindowCommand):

	global ng

	def run(self):
		ng.is_indexing = True
		thread = AngularJSThread(
			folders = ng.active_window().folders(),
			folder_exclude_patterns = ng.active_view().settings().get('folder_exclude_patterns'),
			exclude_dirs = ng.exclude_dirs(),
			exclude_file_suffixes = ng.settings.get('exclude_file_suffixes'),
			match_definitions = ng.settings.get('match_definitions'),
			match_expression = ng.settings.get('match_expression'),
			match_expression_group = ng.settings.get('match_expression_group')
		)

		thread.start()
		self.track_walk_thread(thread)

	def track_walk_thread(self, thread):
		ng.alert('indexing definitions')

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
		try:
			self.definition_List = ng.get_current_project_indexes().get('definitions')
		except:
			self.definition_List = None

		if ng.is_indexing:
			return

		if not self.definition_List:
			ng.active_window().run_command('angularjs_file_index')
			return

		self.current_window = ng.active_window()
		self.current_view = ng.active_view()
		self.current_file = self.current_view.file_name()
		self.current_file_location = self.current_view.sel()[0].end()

		formated_definition_list = []
		for item in self.definition_List:
			current_definition = [
				item[0],
				[item[1].replace(path,'') for path in ng.active_window().folders()][0][1:]
			]
			formated_definition_list.append(current_definition);

		if int(sublime.version()) >= 3000 and ng.settings.get('show_file_preview'):
			self.current_window.show_quick_panel(formated_definition_list, self.on_done, False, -1, self.on_highlight)
		else:
			self.current_window.show_quick_panel(formated_definition_list, self.on_done)

	def on_highlight(self, index):
		self.current_window.open_file(self.definition_List[index][1], sublime.TRANSIENT)
		ng.active_view().run_command('goto_line', {'line': int(self.definition_List[index][2])} )

	def on_done(self, index):
		if index > -1:
			self.current_view = self.current_window.open_file(self.definition_List[index][1])
			self.handle_file_open_go_to(int(self.definition_List[index][2]))
		else:
			self.current_window.focus_view(self.old_view)
			self.current_view.show_at_center(self.current_file_location)

	def handle_file_open_go_to(self, line):
		if not self.current_view.is_loading():
			self.current_view.run_command('goto_line', {'line': line} )
		else:
			sublime.set_timeout(lambda: self.handle_file_open_go_to(line), 100)


class AngularjsGoToDefinitionCommand(sublime_plugin.WindowCommand):

	global ng

	def run(self):
		self.active_view = ng.active_view()

		if not ng.get_current_project_indexes().get('definitions'):
			ng.alert('No indexing found for project')
			return

		# grab first region
		region = self.active_view.sel()[0]

		# no selection has been made
		# so begin expanding to find word
		if not region.size():
			definition = ng.find_word(region)
		else:
			definition = self.active_view.substr(region)

		# ensure data- is striped out before trying to
		# normalize and look up
		definition = definition.replace('data-', '')

		# convert selections such as app-version to appVersion
		# for proper look up
		definition = re.sub('(\w*)-(\w*)', lambda match: match.group(1) + match.group(2).capitalize(), definition)
		for item in ng.get_current_project_indexes().get('definitions'):
			if(re.search('. '+definition+'$', item[0])):
				self.active_view = ng.active_window().open_file(item[1])
				ng.handle_file_open_go_to(int(item[2]))
				return
		ng.alert('definition "%s" could not be found' % definition)


class AngularjsGoToDocumentationCommand(sublime_plugin.WindowCommand):

	global ng

	def run(self):
		import webbrowser

		self.active_view = ng.active_view()

		# grab first region
		region = self.active_view.sel()[0]

		# no selection has been made
		# so begin expanding to find word
		if not region.size():
			definition = ng.find_word(region)
		else:
			definition = self.active_view.substr(region)

		# ensure data- is striped out before trying to
		# normalize and look up
		definition = definition.replace('data-', '')

		# convert selections such as app-version to appVersion
		# for proper look up
		definition = re.sub('(\w*)-(\w*)', lambda match: match.group(1) + match.group(2).capitalize(), definition)

		webbrowser.open('http://docs.angularjs.org/api/ng.directive:' + definition)


class AngularJSThread(threading.Thread):

	global ng

	def __init__(self, **kwargs):
		self.kwargs = kwargs
		threading.Thread.__init__(self)

	def run(self):
		self.function_matches = []
		self.function_match_details = []
		self.attribute_dict = {}
		start = time.time()

		walk_dirs_requirements = (
			'folders',
			'folder_exclude_patterns',
			'exclude_dirs',
			'exclude_file_suffixes',
			'match_definitions',
			'match_expression',
			'match_expression_group'
		)

		reindex_file_requirements = (
			'file_path',
			'index_key',
			'folder_exclude_patterns',
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
		self.result = [self.function_matches, self.attribute_dict]

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
				d[:] = [_d for _d in d if _d not in self.kwargs['folder_exclude_patterns']]
				if not [skip for skip in self.kwargs['exclude_dirs'] if os.path.join(path, os.path.normpath(skip)) in r]:
					for _file in f:
						self.parse_file(_file, r, match_expressions)

	def reindex_file(self, index_key):
		file_path = self.kwargs['file_path']

		if not file_path.endswith(".js"): return

		current_path = os.path.split(file_path)[0]
		# adds limit, to insure we never hit an infinite loop...
		folders, limit, count = [], 100, 0
		while True and count < limit:
			count += 1
			current_path, folder = os.path.split(current_path)
			if folder != "": folders.append(folder)
			if current_path == "" or folder == "": break
		if not [f for f in folders if f in list(self.kwargs['exclude_file_suffixes'])]:
			return

		if (not file_path.endswith(tuple(self.kwargs['exclude_file_suffixes']))
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
			previous_matched_directive = ''

			for line in _lines:
				if previous_matched_directive != '':
					self.look_for_directive_attribute(line, previous_matched_directive)

				matches = self.get_definition_details(line, self.compile_patterns(self.kwargs['match_definitions']))
				if matches:
					for matched in matches:
						definition_name = matched[0] + ':  '
						definition_value = matched[1].group(int(self.kwargs['match_expression_group']))
						definition_name += definition_value
						project_index.append([definition_name, file_path, str(line_number)])
						if(matched[0] == 'directive'): previous_matched_directive = definition_value
						else: previous_matched_directive = '';
				line_number += 1
			ng.add_indexes_to_cache([project_index, self.attribute_dict])

	def parse_file(self, file_path, r, match_expressions):
		if (file_path.endswith(".js")
		and not file_path.endswith(tuple(self.kwargs['exclude_file_suffixes']))):
			_abs_file_path = os.path.join(r, file_path)
			_file = codecs.open(_abs_file_path)
			_lines = _file.readlines();
			_file.close()
			line_number = 1
			previous_matched_directive = ''

			for line in _lines:
				if previous_matched_directive != '':
					self.look_for_directive_attribute(line, previous_matched_directive)

				matches = self.get_definition_details(line, match_expressions)
				if matches:
					for matched in matches:
						definition_name = matched[0] + ':  '
						definition_value = matched[1].group(int(self.kwargs['match_expression_group']))
						definition_name += definition_value
						self.function_matches.append([definition_name, _abs_file_path, str(line_number)])
						if(matched[0] == 'directive'): previous_matched_directive = definition_value
						else: previous_matched_directive = '';
				line_number += 1

	def look_for_directive_attribute(self, line_content, directive):
		try:
			line_content = line_content.decode('utf8')
		except:
			return
		match = re.findall(r'(\w+.)[:\s]+[\'"](\=|@|&)[\'"]', line_content)
		if(match):
			directive = ng.definitionToDirective([directive])
			if directive not in self.attribute_dict:
				self.attribute_dict[directive] = []
			for attribute in match:
				normliazed_attribute = ng.definitionToDirective([attribute[0].replace(':','').strip()])
				self.attribute_dict[directive].append([normliazed_attribute, attribute[1]])

	def get_definition_details(self, line_content, match_expressions):
		matches = []
		for expression in match_expressions:
			 # [2:-1] removes b'' wrapping
			 # TODO: figure out a better way...
			matched = expression[1].search(repr(line_content)[2:-1])
			if matched:
				matches.append((expression[0], matched))
		return matches
