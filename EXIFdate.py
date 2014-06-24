from sys import argv
from exif import get_exif

#get whatever tags it has
try:	
	filename = ' '.join(argv[1:])
	data = get_exif(filename)
except:
	print 'no exif data found for %s' % filename
	exit(1)

#try for the time it was taken
if data.has_key('Date_and_Time_(Original)'):
	date = data['Date_and_Time_(Original)']
elif data.has_key('Date_and_Time'):
	date = data['Date_and_Time']
elif data.has_key('Date_and_Time_(Digitized)'):
	date = data['Date_and_Time_(Digitized)']
else:
	print 'no date found %s' % filename
	exit(1)

#date is formated like so: Y:M:D H:M:S
#change to Y_M_D_H_M_S
print date.replace(':','_').replace(' ','_')
