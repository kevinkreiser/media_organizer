'''
This snippet was altered from the original found here: http://code.activestate.com/recipes/522991-converting-xml-to-dict-for-a-xpath-like-access-syn/
It's been changed so that text between nodes is also captured and so that we dont have every sub object as a list unless is appropriate (lots of the same node name repeated)
Thanks to Rodrigo Strauss for the original snippet
'''

from xml.parsers import expat

def xml_to_dict(xml):
	""" Load a dict from a XML string """

	def list_to_dict(l, ignore_root = True):
		""" Convert our internal format list to a dict. We need this
			 because we use a list as a intermediate format during xml load """
		root_dict = {}
		inside_dict = {}
		# index 0: node name
		# index 1: attributes list
		# index 2: children node list
		root_dict[l[0]] = inside_dict
		inside_dict.update(l[1])
		# if it's a node containing lot's of nodes with same name,
		# like <list><item/><item/><item/><item/><item/></list>
		for x in l[2]:
			d = list_to_dict(x, False)
			for k, v in d.iteritems():
				#we have never seen this key before so just keep the value
				if not inside_dict.has_key(k):
					inside_dict[k] = v
				#we only saw this key once before so we need to start a list of them
				elif isinstance(inside_dict[k], dict):
					inside_dict[k] = [inside_dict[k], v]
				#we already have a list so keep the next item in it
				else:
					inside_dict[k].append(v)


		ret = root_dict.values()[0] if ignore_root else root_dict
			
		return ret
	
	class M:
		""" This is our expat event sink """
		def __init__(self):
			self.lists_stack = []
			self.current_list = None
		def start_element(self, name, attrs):
			l = []
			# root node?
			if self.current_list is None:
				self.current_list = [name, attrs, l]
			else:
				self.current_list.append([name, attrs, l])

			self.lists_stack.append(self.current_list)
			self.current_list = l
			pass
		def end_element(self, name):
			self.current_list = self.lists_stack.pop()
			pass
		def char_data(self, data):
			#TODO: allow text in the root node
			if self.current_list is not None:
				#grab the most recent lists attribs
				recentList = self.lists_stack[len(self.lists_stack) - 1]
				attrs = recentList[len(recentList) - 1][1]
				#see what kind of name we can use
				keyName = u'value1'
				#TODO: make it not fail to put something just because all the possiblities of keyName were taken
				for i in range(1, len(keyName)):
					#can we use this key name
					if attrs.has_key(keyName[:i]) == False:
						#insert it as another attribute
						attrs[keyName[:i]] = data
						break
			pass

	p = expat.ParserCreate()
	m = M()

	p.StartElementHandler = m.start_element
	p.EndElementHandler = m.end_element
	p.CharacterDataHandler = m.char_data

	p.Parse(xml)

	d = list_to_dict(m.current_list)
	
	return d

