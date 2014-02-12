import sublime, re

isST2 = int(sublime.version()) < 3000

if isST2:
	import message
else:
	from . import message


def settings():
	return sublime.load_settings('AngularJS-sublime-package.sublime-settings')


def at_line_with_module(view, locations):
	line = view.substr(view.line(locations[0]))
	return 'module(' in line


def at_html_attribute(view, attribute, locations):
	selector = view.match_selector(locations[0], 'text.html string')
	if not selector:
		return False
	check_attribute = ''
	view_point = locations[0]
	char = ''
	while(char != ' ' and view_point > -1):
		char = view.substr(view_point)
		if(char != ' '):
			check_attribute += char
		view_point -= 1
	check_attribute = check_attribute[::-1]
	if check_attribute.startswith(attribute):
		return True
	return False


def find_word(view, region):
	non_char = re.compile(settings().get('non_word_chars'))
	look_up_found = ""
	start_point = region.end()
	begin_point = start_point-1
	end_point = start_point+1

	while (
		not non_char.search(view.substr(sublime.Region(start_point, end_point)))
		and end_point
	):
		end_point += 1
	while (
		not non_char.search(view.substr(sublime.Region(begin_point, start_point)))
	):
		begin_point -= 1

	look_up_found = view.substr(sublime.Region(begin_point+1, end_point-1))
	message.alert('Looking up: ' + look_up_found)
	return look_up_found
