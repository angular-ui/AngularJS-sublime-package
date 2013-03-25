import sublime, sublime_plugin


class AngularJSAttributesCompletion(sublime_plugin.EventListener):
	"""
	Provides AngularJS attribute completions
	"""

	def __init__(self):
		self.settings = sublime.load_settings('AngularJS Attributes Completion.sublime-settings')

	def on_query_completions(self, view, prefix, locations):
		# Only trigger within HTML
		if not view.match_selector(locations[0],
				"text.html - source"):
			return []

		# check if we are inside a tag
		is_inside_tag = view.match_selector(locations[0],
				"text.html meta.tag - text.html punctuation.definition.tag.begin")

		return self.completions(is_inside_tag)

	def completions(self, is_inside_tag):
		if is_inside_tag :
			core_attrs = [tuple(attr) for attr in self.settings.get('core_attribute_list')]
			extended_attrs = [tuple(attr) for attr in self.settings.get('extended_attribute_list')]
			extended_attrs += core_attrs
			return (extended_attrs, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

		if not is_inside_tag:
			components = []
			for component in self.settings.get('angular_components'):
				components.append((component + "\tAngularJS Component", component + "$1>$2</" + component + '>'))
			return components
