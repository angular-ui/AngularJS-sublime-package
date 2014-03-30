import sublime


def matches(selector):
	view = sublime.active_window().active_view()
	region = view.sel()[0].begin()
	return view.score_selector(region, selector) > 0
