#!/usr/env python -*- coding: utf-8 -*-

class arcStandard(object):
	
	def __init__(self, grammar, sequence):
		self.stack = list()
		self.template = grammar
		self.sequence = sequence
		self.labeledEdges = list()
		self.queue = range(len(sequence))# + [len(sequence)] #NOTE with dummy ROOT

	def isFinalState(self):
		"""
		Checks if the parser is in final configuration i.e. only root node is left in the stack (dummy root not considered)
		"""
		return (len(self.stack) == 1 and len(self.queue) == 0)

	def parse(self):
		"""
		Parses the sequence incrementaly till all the input is consumed and only root node is left.
		"""
		while not self.isFinalState():
			next_move, label = self.predict()
			next_move(label)
		return self

	def predict(self):
		"""
		Predicts the next transition for the parser based on a hand crafted grammar.
		"""	
		if len(self.stack) == 0: 
			return self.SHIFT, None
		
		else:
			s0 = self.sequence[self.stack[-1]]
			b0 = self.sequence[self.queue[0]]
			if s0.pos in self.template["LEFTARC"] and b0.pos in self.template["LEFTARC"][s0.pos].get("exception", {}):
				if len(self.queue) is 1: return self.LEFTARC, self.template["LEFTARC"][s0.pos]["exception"][b0.pos]
				else: 	return self.SHIFT, None
			elif s0.pos in self.template["LEFTARC"] and (b0.pos in self.template["LEFTARC"][s0.pos].get("norm",{}) or \
										b0.pos in self.template["LEFTARC"][s0.pos]):
				label = self.template["LEFTARC"][s0.pos].get("norm",{}).get(b0.pos) or self.template["LEFTARC"][s0.pos][b0.pos]
				return self.LEFTARC, label
			elif b0.pos in self.template["RIGHTARC"] and s0.pos in self.template["RIGHTARC"][b0.pos]:
				has_dependents = self.hasDependents(b0)
				if has_dependents: return self.SHIFT, None
				else: return self.RIGHTARC , self.template["RIGHTARC"][b0.pos][s0.pos]
			else: return self.SHIFT, None

	def hasDependents (self, b0):# NOTE only for right dependents
		""" checks for potential children of `b0` in buffer"""
		for c in self.queue[1:]:
			cI = self.sequence[c]
			if cI.pos in self.template["RIGHTARC"] and b0.pos in self.template["RIGHTARC"][cI.pos]: return True
		return False
		 
	def SHIFT(self, label=None):
		"""
		Moves the input from buffer to stack.
		"""
		self.stack.append(self.queue.pop(0))
		return self

	def RIGHTARC(self, label=None):
		"""
		Right reduces the tokens at the buffer and stack.
		"""
		s0 = self.stack.pop()
		b0 = self.queue[0]
		self.queue[0] = s0
		self.labeledEdges.append((self.sequence[b0], (self.sequence[s0].name, label)))
		return self

	def LEFTARC(self, label=None):
		"""
		Left reduces the tokens at the stack and buffer.
		"""
		s0 = self.stack.pop()
		b0 = self.queue[0]
		self.labeledEdges.append((self.sequence[s0], (self.sequence[b0].name,label)))
		return self
