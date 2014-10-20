#!/bin/bash
#organize them in parallel, if you dont care about what happens (ie synchronized logs)
#find /media/K/family/queue1 -type f -print0 | xargs -0 -n 1 -P 3 bash organize.sh /media/K/family/sort 'mv' &> log.log

#add exif and date where none existed
#i=10; for f in ../../../family/queue/2012-03-30/*; do exif -c -t 306 --ifd 0 --set-value "2012:03:30 13:00:$i" $f; i=`expr $i + 1`; done


#THE PRESCRIBED METHOD:

if [ -z "$3" ]; then
	echo "Usage: $0 fromDir toDir tempDir [threads=1]"
	echo "Example: $0 /media/$(id -un)/mounted_sd_card/ /media/$(id -un)/mounted_internal_drive/sorted/ ./temp 8"
	exit 1
fi

if [ -z "$4" ]; then
	threads=1
else
	threads="$4"
fi

from="$1"
to="$2"
temp="$3"

mkdir -p "$1" "$2" "$3"
rm -rf $temp/list $temp/log*

#check what types of files you get
find "$from" -type f -name "*.JPG" -o -name "*.jpg" -o -name "*.MTS" -o -name "*.mp4" -o -name "*.MP4" | sed -e "s/.*\.//g" | sort | uniq -c
echo "Press ctl+c if you dont like the files types you are seeing here"
sleep 10 

#only take the ones you like
find "$from" -type f -name "*.JPG" -o -name "*.jpg" -o -name "*.MTS" -o -name "*.mp4" -o -name "*.MP4" | shuf > "$temp/list"

#run a bunch of threads to copy the stuff over
< "$temp/list" parallel -j$threads ./organize.sh $to 'cp' {} &> "$temp/log"

#check the logs until done...
d=`wc -l $temp/log | awk '{print $1}'`
t=`wc -l $temp/list | awk '{print $1}'`
if [ $d -ne $t ]; then
	echo "Warning: expected number of copies doesnt match actual"
fi
