import re, sublime

isST2 = int(sublime.version()) < 3000

if isST2:
	import scope
else:
	from . import scope


def elemAttrsRegEx():
	return re.compile(r'(([A-z-].-?\w+[ >])|(\w+=)|(>[\$0-9]+))')


def completionToJadeElement(completion):
	#list of tag partials, tag start, attrs, tag end
	pieces = [item[0] for item in elemAttrsRegEx().findall(completion)]
	for tagStart in pieces[:1]:
		completion = completion.replace(tagStart, "%s(" % tagStart[:-1])
	has_tab_in_body = False
	for attr in pieces[2:-1]:
		# right now tab stops are picked up in the regex so check to
		# make sure it's not a tap stop that we're at
		if not '>$' in attr:
			completion = completion.replace(attr, ", " + attr)
		else:
			completion = completion.replace(attr, attr.replace('>', ')'))
			has_tab_in_body = True
	for tagEnd in pieces[-1:]:
		# if the tag has no atts and no tab stops
		# it got mutated, so fix it here
		if len(pieces) == 2:
			completion = completion.replace('</'+tagEnd.replace('>', '('), ')')
		# there was no tab stop in the body
		# so clean up the end angle from the start tag
		elif not has_tab_in_body:
			completion = completion.replace('></'+tagEnd, ')')
		# there was a tab stop in the body
		# so just clean out the end tag
		else:
			completion = completion.replace('</'+tagEnd, '')
	return completion


def completionToHamlElement(completion):
	#list of tag partials, tag start, attrs, tag end
	pieces = [item[0] for item in elemAttrsRegEx().findall(completion)]
	for tagStart in pieces[:1]:
		completion = '%' + completion.replace(tagStart, '%s{' % tagStart[:-1])
	has_tab_in_body = False
	for attr in pieces[2:-1]:
		# right now tab stops are picked up in the regex so check to
		# make sure it's not a tap stop that we're at
		if not '>$' in attr:
			completion = completion.replace(attr, ", " + attr)
		else:
			completion = completion.replace(attr, attr.replace('>', '}'))
			has_tab_in_body = True
	for tagEnd in pieces[-1:]:
		# if the tag has no atts and no tab stops
		# it got mutated, so fix it here
		if len(pieces) == 2:
			completion = completion.replace('</'+tagEnd.replace('>', '{'), '}')
		# there was no tab stop in the body
		# so clean up the end angle from the start tag
		elif not has_tab_in_body:
			completion = completion.replace('></'+tagEnd, '}')
		# there was a tab stop in the body
		# so just clean out the end tag
		else:
			completion = completion.replace('</'+tagEnd, '')
	return completion


def elements(elems):
	'''
		Adds support for markup outside of HTML
		Currently just Jade and HAML
	'''
	print(elems)
	if scope.matches('text.html'):
		return elems
	if scope.matches('source.jade'):
		return [(elem[0], completionToJadeElement(elem[1])) for elem in elems]
	if scope.matches('text.haml'):
		return [(elem[0], completionToHamlElement(elem[1])) for elem in elems]


def completionToHamlAttr(attr):
	hamlAttrRegex = re.compile(r'([A-z-]+-\w+.|\w+=)')
	attrList = hamlAttrRegex.findall(attr)
	if attrList:
		for item in attrList[:1]:
			last_char = item[-1:]
			if last_char == ' ':
				attr = attr.replace(item, '"%s" ' % item.strip())
			elif last_char == '$':
				attr = attr.replace(item, '"%s"$' % item)
			elif last_char == '=':
				attr = attr.replace(item, '"%s" => ' % item.replace('=', ''))
		for item in attrList[1:]:
			attr = attr.replace(item, ', "%s" => ' % item.replace('=', ''))

	return attr


def completionToJadeAttr(attr):
	jadeAttrRegex = re.compile(r'([A-z-]+-\w+|\w+=)')
	# remove the first attr from the list
	attrList = jadeAttrRegex.findall(attr)[1:]
	if attrList:
		for item in attrList:
			attr = attr.replace(item, ", " + item)
	return attr


def attributes(attrs):
	'''
		Adds support for markup outside of HTML
		Currently just Jade and HAML
	'''

	if scope.matches('text.html'):
		return attrs
	if scope.matches('source.jade'):
		return [(attr[0], completionToJadeAttr(attr[1])) for attr in attrs]
	if scope.matches('text.haml'):
		return [(attr[0], completionToHamlAttr(attr[1])) for attr in attrs]
	return attrs


def indexedDirectiveToTag(directive):
	'''
		Converts the indexed directives to element form.
		Currently any indexed directive is used as a possible element
	'''
	if scope.matches('source.jade'):
		return directive.replace('="$1"$0','')+'${1:($2)}$0'
	elif scope.matches('text.haml'):
		return '%' + directive.replace('="$1"$0','')+'${1:\\{$2\\}}$0'
	else:
		#assumes HTML
		return directive.replace('="$1"$0','')+'$1>$0</'+directive.replace('="$1"$0','')+'>'


def definitionToDirective(directive):
		return re.sub('([a-z0-9])([A-Z])', r'\1-\2', directive[0].replace('directive:  ', '')).lower()
