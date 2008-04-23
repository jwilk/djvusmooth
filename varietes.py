#!/usr/bin/python
# encoding=UTF-8
# Copyright © 2008 Jakub Wilk <ubanus@users.sf.net>

import re
import exceptions
import warnings
import weakref
from cStringIO import StringIO

class NotOverriddenWarning(exceptions.UserWarning):
	pass

def not_overridden(f):
	r'''
	>>> warnings.filterwarnings('error', category=NotOverriddenWarning)
	>>> class B(object):
	...   @not_overridden
	...   def f(self, x, y): pass
	>>> class C(B):
	...   def f(self, x, y): return x * y
	>>> B().f(6, 7)
	Traceback (most recent call last):
	...
	NotOverriddenWarning: `varietes.B.f()` is not overriden
	>>> C().f(6, 7)
	42
	'''
	def new_f(self, *args, **kwargs):
		cls = type(self)
		warnings.warn(
			'`%s.%s.%s()` is not overriden' % (cls.__module__, cls.__name__, f.__name__),
			category = NotOverriddenWarning,
			stacklevel = 2
		)

		return f(self, *args, **kwargs)
	return new_f

def wref(obj):
	r'''
	>>> class O(object):
	...   pass
	>>> x = O()
	>>> xref = wref(x)
	>>> xref() is x
	True
	>>> del x
	>>> xref() is None
	True

	>>> xref = wref(None)
	>>> xref() is None
	True
	'''
	if obj is None:
		ref = weakref.ref(set())
		assert ref() is None
	else:
		ref = weakref.ref(obj)
	return ref

def indents_to_tree(lines):
	r'''
	>>> lines = [
	... 'bacon',
	... '	egg',
	... '		eggs',
	... 'ham',
	... '	sausage',
	... '	spam',
	... '		bacon',
	... '	egg'
	... ]
	>>> indents_to_tree(lines)
	[None, ['bacon', ['egg', ['eggs']]], ['ham', ['sausage'], ['spam', ['bacon']], ['egg']]]

	'''
	root = [None]
	memo = [(-1, root)]
	for line in lines:
		old_len = len(line)
		line = line.lstrip()
		current = [line]
		indent = old_len - len(line)
		while memo[-1][0] >= indent:
			memo.pop()
		memo[-1][1].append(current)
		memo += (indent, current),
	return root

URI_SPECIAL_CHARACTERS = \
(
	':/?#[]@' +    # RFC 3986, `gen-delims`
	"!$&()*+,;=" + # RFC 3986, `sub-delims`
	'%'            # RFC 3986, `pct-encoded`
)

def fix_uri(s):
	r'''
	>>> uri = 'http://eggs.spam/'
	>>> fix_uri(uri) == uri
	True
	>>> uri = fix_uri('http://eggs.spam/eggs and spam/')
	>>> uri
	'http://eggs.spam/eggs%20and%20spam/'
	>>> fix_uri(uri) == uri
	True
	'''
	from urllib import quote
	if isinstance(s, unicode):
		s = s.encode('UTF-8')
	return quote(s, safe=URI_SPECIAL_CHARACTERS)

replace_control_characters = re.compile('[\0-\x1f]+').sub

class idict(object):

	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)
	
	def __repr__(self):
		return '%s.%s(%r)' % (self.__module__, self.__class__.__name__, self.__dict)

# vim:ts=4 sw=4
