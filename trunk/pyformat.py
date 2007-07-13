#!/usr/bin/python
# -*- coding: utf-8 -*-
# pyformat.py	author: YIN Dian	copyleft 2007	licenced under GPL
# Format plain pinyin text with tone markers into toned pinyin
# version: 20070713
# syllable model: [consonant] + [jieyin] + [vowel(s)] + [terminal] + [suffix]
# Hist:	070624: first version out, pinyin implemented
#	070702: implemented uppercase handling, and make splitting greedy
#	070706: fixed bug in splitsyllable that now vowel is in vietnamese 'gi'
#	070707: improved tone exception rule handling in splitsyllable
#	070713: added support for incomplete tone alpha set, e.g. ee in pinyin.
# TODO: add support for pure-consonant tone mark, e.g. m2 and ng2 in pinyin.
import sys, os, string, types, fileinput
defaultencoding = 'gbk'
TONEATLEFTVOWEL  = 1
TONEATRIGHTVOWEL = 2
TONEATJIEYIN     = 3
def specifyrule(rulefilename):
	global tonemarkset,untonemark,compoundset,delimitrset
	global vowelalphas,jieyinset,consonants,terminalsnd
	global suffixes,TONEATLEFTVOWEL,TONEATRIGHTVOWEL,TONEATJIEYIN
	global tonemarkdefault,tonemarkexceptions,tonetransform,compoundtrasform
	global loweralphas, upperalphas, tonedalphas,untonetransform
	global lower2upper, upper2lower
	# rule specifications
	execfile(rulefilename, globals())
	# computed rules
	tonedalphas = u''.join(filter(None, [toned for alpha, toned in tonetransform.items()]))
	untonetransform = []
	for alpha, toned in tonetransform.items():
		untonetransform += [(tonedalpha, alpha) for tonedalpha in toned]
	untonetransform = dict(untonetransform)
	if len(loweralphas) <> len(upperalphas):
		raise ValueError, 'Unmatched length between lower/upperalphas'
	lower2upper = []
	upper2lower = []
	for i in range(0, len(loweralphas)):
		lower2upper += [(loweralphas[i], upperalphas[i])]
		upper2lower += [(upperalphas[i], loweralphas[i])]
	lower2upper = dict(lower2upper)
	upper2lower = dict(upper2lower)

specifyrule('.'+os.sep+os.path.dirname(sys.argv[0])+os.sep+'pinyin.rule')

def showhelp():
	print "\
pyformat.py	author: YIN Dian	copyleft 2007	licenced in GPL\n\
Format plain pinyin text with tone markers into toned pinyin\n\
version: 20070623\n\
Usage: pyformat.py filename(s)"

def isupper(char):
	return char in upperalphas

def islower(char):
	return char in loweralphas

def toupper(char):
	if char in lower2upper.keys():
		return lower2upper[char]
	else:
		return char

def tolower(char):
	if char in upper2lower.keys():
		return upper2lower[char]
	else:
		return char

def uppercase(str):
	return u''.join(map(toupper, str))

def lowercase(str):
	return u''.join(map(tolower, str))

def istonemark(char):
	return char in tonemarkset or char in untonemark

def iscompound(char):
	return char in compoundset

def isdelim(char):
	return char in delimitrset

def istoned(char):
	return char in tonedalphas

def isjieyin(char):
	return char in jieyinset

def isvowel(char):
	return char in vowelalphas

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
		elif isupper(char) and istoned(tolower(char)):
			char = tolower(char)
			alpha = untonetransform[char]
			tone = tonetransform[alpha].index(char) + 1
			result += toupper(alpha)
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
	j = len(syllable)
	#while i < len(syllable) and not isjieyin(tolower(syllable[i])) and\
	#		not isvowel(tolower(syllable[i])):
	#	consonant += syllable[i]
	#	i += 1
	#if consonant and not lowercase(consonant) in consonants:
	#	raise ValueError, "Unrecognized consonant %s" % consonant
	for possiblecon in consonants:
		if len(possiblecon) <= j and \
			lowercase(syllable[:len(possiblecon)]) == \
			possiblecon and len(possiblecon) > len(consonant):
				consonant = syllable[:len(possiblecon)]
	i += len(consonant)
	if i < len(syllable) and not isjieyin(tolower(syllable[i])) and\
			not isvowel(tolower(syllable[i])):
		raise ValueError, "Not a syllable: %s" % syllable
	if i < len(syllable) and isjieyin(tolower(syllable[i])):
		jieyin = syllable[i]
		i += 1
	for possiblesuffix in suffixes:
		if len(possiblesuffix) <= j - i and \
			lowercase(syllable[j-len(possiblesuffix):j]) == \
			possiblesuffix and len(possiblesuffix) > len(suffix):
				suffix = syllable[j-len(possiblesuffix):j]
	j -= len(suffix)
	for possibleterm in terminalsnd:
		if len(possibleterm) <= j - i and \
			lowercase(syllable[j-len(possibleterm):j]) == \
			possibleterm and len(possibleterm) > len(terminal):
				terminal = syllable[j-len(possibleterm):j]
	j -= len(terminal)
	vowels = syllable[i:j]
	for char in lowercase(vowels):
		if not isvowel(char):
			raise ValueError, "Unrecognized vowel %s" % vowels
	if terminal:
		terminalisvowel = True
		for char in lowercase(terminal):
			if not isvowel(char):
				terminalisvowel = False
	else:
		terminalisvowel = False
	if terminalisvowel and not vowels:
		terminal, vowels = u'', terminal
	if jieyin and not vowels:
		jieyin, vowels = u'', jieyin
	if not vowels and consonant and isvowel(tolower(consonant[-1])):
		consonant, vowels = consonant[:-1], consonant[-1]
	print (consonant, jieyin, vowels, terminal, suffix),
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
			if (case[0] in (0, len(consonant), lowercase(consonant))) and\
				(case[1] in (0, len(jieyin), lowercase(jieyin))) and\
				(case[2] in (0, len(vowels), lowercase(vowels))) and\
				(case[3] in (0, len(terminal), lowercase(terminal))) and\
				(case[4] in (0, len(suffix), lowercase(suffix))):
					markrule = tonemarkexceptions[case]
		print 'markrule= %s' % markrule,
		if (markrule == TONEATLEFTVOWEL or (
				markrule == TONEATJIEYIN and not jieyin)) and\
					tonetransform[tolower(vowels[0])][tone-1] <> u'\0':
			if not isupper(vowels[0]):
				vowels = tonetransform[vowels[0]][tone-1] + vowels[1:]
			else:
				vowels = toupper(tonetransform[tolower(vowels[0])
						][tone-1]) + vowels[1:]
		elif markrule == TONEATRIGHTVOWEL and\
			tonetransform[tolower(vowels[-1])][tone-1] <> u'\0':
			if not isupper(vowels[-1]):
				vowels = vowels[:-1] + tonetransform[vowels[-1]][tone-1]
			else:
				vowels = vowels[:-1] + toupper(tonetransform[tolower(
					vowels[-1])][tone-1])
		elif markrule == TONEATJIEYIN and jieyin and\
			tonetransform[tolower(jieyin)][tone-1] <> u'\0':
			if not isupper(jieyin):
				jieyin = tonetransform[jieyin][tone - 1]
			else:
				jieyin = toupper(tonetransform[tolower(jieyin)][tone - 1])
		else:
			raise ValueError, ("Don't know how to mark tone %s "+\
					"on %s") % (`tonemark`, syllable)
		print 'marked vowel = %s' % `vowels`,
		return consonant + jieyin + vowels + terminal + suffix

def makecompound(str):
	"deal with compound input sequence such as uu, ee"
	if not str:
		return u'', False
	changed = 0
	for case in compoundtrasform.keys():
		if len(case) <= len(str):
			if str[-len(case):] == case:
				str = str[:-len(case)] + compoundtrasform[case]
				changed = True
				break
			elif lowercase(str[-len(case):]) == case:
				str = str[:-len(case)] + uppercase(compoundtrasform[case])
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
		elif isupper(char) and istoned(tolower(char)):
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
		if istonemark(tolower(char)):
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
					syllable = marktone(syllable, tolower(char))
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
		elif iscompound(tolower(char)):
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
	if isvalid(syllable):
		syllable = marktone(syllable, -1)
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
