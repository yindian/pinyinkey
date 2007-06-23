#!/usr/bin/python
# -*- coding: utf-8 -*-
# pyformat.py	author: YIN Dian	copyleft 2007	licenced under GPL
# Format plain pinyin text with tone markers into toned pinyin
# version: 20070623
# syllable model: [consonant] + [jieyin] + [vowel(s)] + [terminal] + [suffix]
import sys, os, string, types, fileinput
defaultencoding = 'gbk'
tonemarkset = u'1234'
untonemark  = u'0'
compoundset = u'ue'
delimitrset = u"' \t\n,." # no need to be complete
vowelalphas = u'aoeiuüê'
jieyinset   = u'iuü'
consonants  = (u'b', u'p', u'm', u'f', u'd', u't', u'n', u'l', 
		u'g', u'k', u'h', u'j', u'q', u'x', u'y', 
		u'zh', u'ch', u'sh', u'r', u'z', u'c', u's', u'w',
		# extended
		#u'ng', u'v', u'qh'
		)
terminalsnd = (u'n', u'ng',
		# extended
		#u'm', u'p', u't', u'k', u'q'
		)
suffixes    = (u'r')
TONEATLEFTVOWEL  = 1
TONEATRIGHTVOWEL = 2
TONEATJIEYIN     = 3
tonemarkdefault  = TONEATLEFTVOWEL
tonemarkexceptions = {(0, u'i', u'u', 0, 0): TONEATJIEYIN}
tonetransform = {
	u'a': u'āáǎà',
	u'o': u'ōóǒò',
	u'e': u'ēéěè',
	u'i': u'īíǐì',
	u'u': u'ūúǔù',
	u'ü': u'ǖǘǚǜ'
}
compoundtrasform = {
	u'uu': u'ü',
	u'ee': u'ê'
}
# computed rules
tonedalphas = u''.join([toned for alpha, toned in tonetransform.items()])
untonetransform = []
for alpha, toned in tonetransform.items():
	untonetransform += [(tonedalpha, alpha) for tonedalpha in toned]
untonetransform = dict(untonetransform)

def showhelp():
	print "\
pyformat.py	author: YIN Dian	copyleft 2007	licenced in GPL\n\
Format plain pinyin text with tone markers into toned pinyin\n\
version: 20070623\n\
Usage: pyformat.py filename(s)"

def istonemark(char):
	return char in tonemarkset or char in untonemark

def iscompound(char):
	return char in compoundset

def isdelim(char):
	return char in delimitrset

def istoned(char):
	return char in tonedalphas

def striptone(syllable):
	"return (syllable_without_tone, tone)"
	if not type(syllable) in types.StringTypes:
		raise TypeError, 'Expect string, but %s given' %\
				`type(syllable)`
	result = u''
	tone = 0
	for char in syllable:
		if istoned(char):
			alpha = untonetransform[char]
			tone = tonetransform[alpha].index(char) + 1
			result += alpha
		else:
			result += char
	return result, tone

def splitsyllable(syllable):
	"""return (consonant, jieyin, vowels, terminal, suffix)
	requires the input syllable to be stripped of tone mark"""
	if not type(syllable) in types.StringTypes:
		raise TypeError, 'Expect string, but %s given' %\
				`type(syllable)`
	consonant = jieyin = vowels = terminal = suffix = u''
	i = 0
	while i < len(syllable) and not syllable[i] in jieyinset and\
			not syllable[i] in vowelalphas:
		consonant += syllable[i]
		i += 1
	if consonant and not consonant in consonants:
		raise ValueError, "Unrecognized consonant %s" % consonant
	if i < len(syllable) and syllable[i] in jieyinset:
		jieyin = syllable[i]
		i += 1
	j = len(syllable)
	for possiblesuffix in suffixes:
		if len(possiblesuffix) <= j - i and \
			syllable[j-len(possiblesuffix):j] == possiblesuffix:
				suffix = possiblesuffix
				j -= len(possiblesuffix)
				break
	for possibleterm in terminalsnd:
		if len(possibleterm) <= j - i and \
			syllable[j-len(possibleterm):j] == possibleterm:
				terminal = possibleterm
				j -= len(possibleterm)
				break
	vowels = syllable[i:j]
	for char in vowels:
		if not char in vowelalphas:
			raise ValueError, "Unrecognized vowel %s" % vowels
	if jieyin and not vowels:
		jieyin, vowels = u'', jieyin
	return consonant, jieyin, vowels, terminal, suffix

def marktone(syllable, tonemark):
	"mark syllable with tonemark and return the result"
	if not syllable:
		if type(tonemark) in types.StringTypes:
			return tonemark
		else:
			return u''
	else:
		syllable, tone = striptone(syllable)
		#print syllable, tonemark
		if type(tonemark) in types.StringTypes:
			if tonemark in tonemarkset:
				tone = tonemarkset.index(tonemark) + 1
			elif tonemark == untonemark:
				return syllable
		elif not tonemark or not tone:
			return syllable
		consonant, jieyin, vowels, terminal, suffix = \
				splitsyllable(syllable)
		if not vowels:
			raise ValueError, ("No vowel to mark tone %s "+\
					"on %s") % (`tonemark`, syllable)
		markrule = tonemarkdefault
		for case in tonemarkexceptions.keys():
			if (not case[0] or case[0] == consonant) and\
				(not case[1] or case[1] == jieyin) and\
				(not case[2] or case[2] == vowels) and\
				(not case[3] or case[3] == terminal) and\
				(not case[4] or case[4] == suffix):
					markrule = tonemarkexceptions[case]
		#print 'markrule= %s' % markrule,
		if markrule == TONEATLEFTVOWEL or not jieyin:
			vowels = tonetransform[vowels[0]][tone-1] + vowels[1:]
		elif markrule == TONEATRIGHTVOWEL:
			vowels = vowels[:-1] + tonetransform[vowels[-1]][tone-1]
		elif markrule == TONEATJIEYIN and jieyin:
			jieyin = tonetransform[jieyin][tone - 1]
		else:
			raise ValueError, ("Don't know how to mark tone %s "+\
					"on %s") % (`tonemark`, syllable)
		return consonant + jieyin + vowels + terminal + suffix

def makecompound(str):
	"deal with compound input sequence such as uu, ee"
	if not str:
		return u'', False
	changed = 0
	for case in compoundtrasform.keys():
		if len(case) <= len(str) and str[-len(case):] == case:
			str = str[:-len(case)] + compoundtrasform[case]
			changed = True
			break
	return str, changed
	
def isvalid(syllable):
	if not syllable:
		return False
	numtoned = 0
	for char in syllable:
		if istoned(char):
			numtoned += 1
	if numtoned > 1:
		return False
	syllable = striptone(syllable)[0]
	try:
		splitsyllable(syllable)
	except ValueError:
		return False
	return True

def pyformat(str):
	"""blah, just format"""
	if type(str) == types.ListType:
		str = u''.join(str)
	if not type(str) in types.StringTypes:
		raise TypeError, 'Must input a string or list of strings, '\
				+ 'but you gave %s' % `type(str)`
	result = syllable = oldsyllable = lastchar = u''
	changed = False
	for char in str:
		#print '(',char,syllable,isvalid(syllable),
		if istonemark(char):
			if char == lastchar and changed:
				syllable = oldsyllable + char
				changed = False
				if not isvalid(syllable):
					result += marktone(oldsyllable, -1)
					if isvalid(char):
						syllable = char
						oldsyllable = u''
					else:
						result += char
						syllable = oldsyllable = u''
			elif isvalid(syllable):
				oldsyllable = syllable
				try:
					syllable = marktone(syllable, char)
					changed = True
				except:
					result += marktone(oldsyllable, -1)
					if isvalid(char):
						syllable = char
						oldsyllable = u''
					else:
						result += char
						syllable = oldsyllable = u''
					changed = False
			else:
				result += marktone(oldsyllable, -1)
				if isvalid(char):
					syllable = char
					oldsyllable = u''
				else:
					result += char
					syllable = oldsyllable = u''
				changed = False
		elif iscompound(char):
			if char == lastchar and changed:
				syllable = oldsyllable + char
				changed = False
				if not isvalid(syllable):
					result += marktone(oldsyllable, -1)
					if isvalid(char):
						syllable = char
						oldsyllable = u''
					else:
						result += char
						syllable = oldsyllable = u''
			else:
				oldsyllable = syllable
				syllable, changed = makecompound(syllable+char)
				if not isvalid(syllable):
					result += marktone(oldsyllable, -1)
					if isvalid(char):
						syllable = char
						oldsyllable = u''
					else:
						result += char
						syllable = oldsyllable = u''
					changed = False
		elif isdelim(char):
			if isvalid(syllable):
				syllable = marktone(syllable, -1)
			result += syllable + char
			syllable = oldsyllable = u''
			changed = False
		else:
			if isvalid(syllable + char):
				oldsyllable = syllable
				syllable += char
			else:
				if isvalid(syllable):
					syllable = marktone(syllable, -1)
				result += syllable
				syllable = char
				oldsyllable = u''
			changed = False
		#print syllable,changed, ')',
		lastchar = char
	result += syllable
	return result

if __name__ == '__main__':
	#for word in unicode(''.join(sys.stdin.readlines())).split():
	#	print word, not isvalid(word) or splitsyllable(word)
	#	print word, striptone(word)
	#
	#for line in sys.stdin.readlines():
	#	line = unicode(line[:-1]).split()
	#	syllable = line[0]
	#	tone = line[1]
	#	print syllable, tone
	#	syllable = marktone(syllable, tone)
	#	print syllable, splitsyllable(striptone(syllable)[0]),
	#	print striptone(syllable)[1]
	#
	if len(sys.argv) > 1:
		for line in fileinput.input():
			print pyformat(unicode(line[:-1],
				defaultencoding)).encode(defaultencoding)
	else:
		showhelp()
		#print tonetransform
		#print tonedalphas
		#print untonetransform
