from PIL import Image
import urllib.request, urllib.error, urllib.parse
from xml_to_dict import xml_to_dict
import json

#download the latest tags set from the official site
def get_latest_tags(url):
    #something to use for downloading
    opener = urllib.request.build_opener()
    #the latest exif tag spec
    response = opener.open(url)
    #the html
    html = response.read().replace('\n','')
    response.close()
    #get the first mention of the 'Exif' table
    tableStart = -1
    while len(html) > 0:
        #begin tag
        start = html.find('<table')
        if start == -1:
            break
        #end tag
        end = html.find('>', start) + 1
        if end == -1:
            break
        #entire declaration
        tableDecl = html[start : end]
        #this is the right one
        if 'Exif' in tableDecl:
            tableStart = start
            break
        else:
            html =  html[end : ]

    #if we found the beginning of the tags
    if tableStart != -1:
        #find the end tag
        tableEnd = html.find('</table', tableStart)
        if tableEnd != -1:
            tableEnd = html.find('>', tableEnd) + 1
            if tableEnd != -1:
                html = html[tableStart : tableEnd]
            else:
                html = ''
        else:
            html = ''

    #grab the body
    body = html[html.find('<tbody') : html.find('>', html.find('</tbody')) + 1]

    #if we have a table we need to parse it
    tags = {}
    if len(body) > 0:
        #pretend its xml and load it into a dict
        rows = xml_to_dict(body)
        for row in rows['tr']:
            columns = row['td']
            #get the tag id number and save the tag name
            tags[int(columns[1]['v'])] = columns[3]['v']

    #give the tags back
    return tags

#recursively parse the dict tag ids into strings
def sanitize(value):
    #if the value isn't a dict we are done
    if isinstance(value, dict) == False:
        return value
    else:
        exif = {}
        #go through piece
        for id, v in value.items():
            #get the tag name using the id if there is no tag with this id
            tag = tags.get(id, str(id))
            #get its value whether it is a value or another dict
            exif[tag] = sanitize(v)
        #send back this branch of the subtree
        return exif

#open the image and read out the exif into a dict
def get_exif(fn, flat = True):
    i = Image.open(fn)
    info = i._getexif()
    if(flat == False):
        data = sanitize(info)
    else:
        data = {}
        for k,v in info.items():
            data[tags.get(k,str(k))] = v
    '''
    #deepen the structure so as to flatten the tag names
    uniqs = set()
    keySets = []
    for k, v in exif.iteritems():
        #get each level
        keys = k.split('.')
        print keys
        #take off the deepest
        deepest = keys.pop()
        #check if we already have this or not
        uniq = ''.join(keys) 
        if uniq in uniqs:
            #TODO: add the key and value of the deepest element
            continue
        else:
            uniqs.add(uniq)
        #flip the order
        keys.reverse()
        #go through each one creating dicts
        inner = {}
        for i in keys:
            parent = {}
            parent[i] = inner
            inner = parent
    '''
    return data

#turn gps info into latlngs that we know and love
#return lat, lng, altitude
def parse_GPS_info(GPSInfo):
    #get the latitude polarity
    latSign = 1 if GPSInfo['Exif.GPSInfo.GPSLatitudeRef'] == 'N' else -1
    #get the longitude polarity
    lngSign = 1 if GPSInfo['Exif.GPSInfo.GPSLongitudeRef'] == 'E' else -1
    #get the latitude in decimal format
    lat = GPSInfo['Exif.GPSInfo.GPSLatitude']
    d = lat[0]; m = lat[1]; s = lat[2]
    lat = d[0]/float(d[1]) + (m[0]/float(m[1]))/60.0 + (s[0]/float(s[1]))/3600.0
    lat *= latSign
    #get the longitude in decimal format
    lng = GPSInfo['Exif.GPSInfo.GPSLongitude']
    d = lng[0]; m = lng[1]; s = lng[2]
    lng = d[0]/float(d[1]) + (m[0]/float(m[1]))/60.0 + (s[0]/float(s[1]))/3600.0
    lng *= lngSign
    #get the altitude
    aboveSeaLevel = GPSInfo['Exif.GPSInfo.GPSAltitudeRef'] == 0
    alt = GPSInfo['Exif.GPSInfo.GPSAltitude']
    #if they were above sealevel its a ratio
    if aboveSeaLevel == 0:    
        alt = alt[0]/float(alt[1])
    #if below sea level its absolute
    else:
        alt = alt[0]
    return lat, lng, alt

'''get the latest tag set every time'''
try:
    tags = {}
    with open('tags.json', 'r') as f:
        str_tags = json.load(f)
        for str_k,v in str_tags.items():
            tags[int(str_k)] = v
except:
    tags = get_latest_tags('http://www.exiv2.org/tags.html')
