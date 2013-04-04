import sublime, sublime_plugin


class AngularJSAttributesCompletion(sublime_plugin.EventListener):
	"""
	Provides AngularJS attribute completions
	"""

	def on_query_completions(self, view, prefix, locations):
		if not hasattr(self, 'settings'):
			self.settings = sublime.load_settings('AngularJS Attributes Completion.sublime-settings')

		single_match = False
		all_matched = True

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
			core_attrs = [tuple(attr) for attr in self.settings.get('core_attribute_list')]
			extended_attrs = [tuple(attr) for attr in self.settings.get('extended_attribute_list')]
			extended_attrs += core_attrs
			return (extended_attrs, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

		if not is_inside_tag:
			components = []
			in_scope = False
			for scope in self.settings.get('component_defined_scopes'):
				if view.match_selector(locations[0], scope):
					in_scope = True

			if in_scope:
				for component in self.settings.get('angular_components'):
					components.append((component + "\tAngularJS Component", component + "$1>$2</" + component + '>'))

			return components
