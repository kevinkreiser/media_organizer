from sys import argv
from os import stat
from mmap import mmap

MAX_WINDOW = 2097152

#16 byte guid
guid = ''.join(['\x17','\xee','\x8c','\x60','\xf8','\x4d','\x11','\xd9','\x8c','\xd6','\x08','\x00','\x20','\x0c','\x9a','\x66'])

#open the file
filename = ' '.join(argv[1:])
mem = stat(filename).st_size
if mem == 0:
	print "Zero length file"
	exit(1)
if mem > MAX_WINDOW:
	mem = MAX_WINDOW
with open(filename, 'r+b') as f:
	#mmap the file
	data = mmap(f.fileno(), mem)

	try:
		'''find the guid within the first set of video frames'''

		#keep going until there is nothing left to look at
		match = 0
		messages = []
		while match < mem - len(guid):
			#match position
		        match = data.find(guid[0:14], match, mem)
			#fail
			if match == -1:
				match = data.find(guid[0:8], 0, mem)
				if match != -1:
					messages.append('partial differing by: %s' % list(set(guid)-set(data[match:match+len(guid)])))
				else:
					messages.append('no guid found for %s' % filename)
				break

			'''skip over "MD...PM"'''
		
			#find the MP part right after the guid
			match += len(guid)
			pos = data.find('MD', match, match + 128)
			#fail
			if pos == -1:
				messages.append('MD...PM string directly after guid')
				continue
			#find the PM part reasonably close to the MP part
			pos = data.find('PM', pos + 2, pos + 128)
			if match == -1:
				messages.append('no PM portion of MD...PM string reasonably close')
				continue

			'''get all tags and all data, each tag is 1 byte for the tag and 4 bytes of data'''

			match = pos + 2
			tag_count = ord(data[match])
			match += 1
			tags = dict([(data[pos],list(data[pos + 1 : pos + 5])) for pos in range(match, match + tag_count * 5, 5)])
			#need the date tags
			if '\x19' not in tags or '\x18' not in tags:
				messages.append('no date tags found directly after the MD...PM string')
				continue

			'''make a date and time from the tags'''
			ym = tags['\x18']
			year = "%x%x" % (ord(ym[1]), ord(ym[2]))
			month = "%x" % ord(ym[3])
			
			dhms = tags['\x19']
			day  = "%x" % ord(dhms[0])
			hour  = "%x" % ord(dhms[1])
			minute  = "%x" % ord(dhms[2])
			second  = "%x" % ord(dhms[3])

			print '%04d_%02d_%02d_%02d_%02d_%02d' % (int(year), int(month), int(day), int(hour), int(minute), int(second))
			exit(0)

		#if we failed to find it, show some error messages and signal
		for m in messages:
			print m
		exit(len(m))
	finally:
		'''cleanup'''
		data.close()
