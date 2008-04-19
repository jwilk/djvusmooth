#!/usr/bin/python
# encoding=UTF-8
# Copyright © 2008 Jakub Wilk <ubanus@users.sf.net>

import weakref

import djvu.sexpr
import djvu.const

from varietes import not_overridden, wref

class Node(object):

	def __init__(self, sexpr, owner):
		self._onwer = owner

	def _set_children(self, children):
		self._children = list(children)
	
	uri = property()
	title = property()

	def __getitem__(self, item):
		return self._children[item]
	
	def __len__(self):
		return len(self._children)

	def __iter__(self):
		return iter(self._children)

class RootNode(Node):

	def __init__(self, sexpr, owner):
		Node.__init__(self, sexpr, owner)
		self._set_children(InnerNode(subexpr, owner) for subexpr in sexpr)

class InnerNode(Node):

	def __init__(self, sexpr, owner):
		Node.__init__(self, sexpr, owner)
		sexpr = iter(sexpr)
		self._uri = sexpr.next().value
		self._title = sexpr.next().value
		self._set_children(InnerNode(subexpr, owner) for subexpr in sexpr)
	
	@apply
	def uri():
		def get(self):
			return self._uri
		def set(self, value):
			self._uri = value
			self._notify_change(self)
		return property(get, set)
		
	@apply
	def title():
		def get(self):
			return self._title
		def set(self, value):
			self._title = value
			self._notify_change(self)
		return property(get, set)
	
	def _notify_change(self):
		self._owner.notify_node_change(self)

class OutlineCallback(object):

	@not_overridden
	def notify_tree_change(self, node):
		pass

	@not_overridden
	def notify_node_change(self, node):
		pass

class Outline(object):

	def __init__(self):
		self._callbacks = weakref.WeakKeyDictionary()
		self._original_sexpr = self.acquire_data()
		self.revert()

	def register_callback(self, callback):
		if not isinstance(callback, OutlineCallback):
			raise TypeError
		self._callbacks[callback] = 1

	@apply
	def root():
		def get(self):
			return self._root
		return property(get)

	@apply
	def raw_value():
		def get(self):
			return self._root.sexpr
		def set(self, sexpr):
			self._root = RootNode(sexpr, self)
			self.notify_tree_change()
		return property(get, set)

	def revert(self):
		self.raw_value = self._original_sexpr
		self._dirty = False

	def acquire_data(self):
		return djvu.const.EMPTY_LIST

	def notify_tree_change(self):
		self._dirty = True
		for callback in self._callbacks:
			callback.notify_tree_change(self._root)

	def notify_node_change(self, node):
		self._dirty = True
		for callback in self._callbacks:
			callback.notify_node_change(node)

# vim:ts=4 sw=4
