#organize them in parallel, if you dont care about what happens (ie synchronized logs)
#find /media/K/family/queue1 -type f -print0 | xargs -0 -n 1 -P 3 bash organize.sh /media/K/family/sort 'mv' &> log.log

#add exif and date where none existed
#i=10; for f in ../../../family/queue/2012-03-30/*; do exif -c -t 306 --ifd 0 --set-value "2012:03:30 13:00:$i" $f; i=`expr $i + 1`; done


#THE PRESCRIBED METHOD:

if [ -z "$3" ]; then
	echo "Usage: $0 fromDir toDir tempDir [process_count=1]"
	echo "Example: $0 /media/kkreiser/9016-4EF8/ /media/kkreiser/K/family/sort/ ./temp 8"
	exit 1
fi

if [ -z "$4" ]; then
	thread=1
else
	thread="$4"
fi

from="$1"
to="$2"
temp="$3"

mkdir -p "$1" "$2" "$3"
rm -rf "$temp/l.*" "$temp/list"

#check what types of files you get
find "$from" -type f | sed -e "s/.*\.//g" | sort | uniq -c
echo "Press ctl+C if you dont like the files you are seeing here"
sleep 30

#only take the ones you like
find "$from" -type f | grep "JPG$\|jpg$\|MTS$\|mp4$\|MP4$" | shuf > "$temp/list"

#split it up
c=`wc -l $temp/list | awk '{print $1}'`
split -l `echo "($c / $thread) + 1" | bc` -d "$temp/list" "$temp/l."

exit 0

#run a bunch of threads to copy the stuff over
for f in l.*; do
	nohup cat "$f" | xargs -n 1 -P 1 bash organize.sh "$to" 'cp' &> "$f.log" &
done

wait

#check the logs until done...
d=`wc -l "$temp/l.*log" | tail -n 1 | awk '{print $1}'`
t=`wc -l "$temp/list" | awk '{print $1}'`
if [ $d -ne $t ]; then
	echo "Warning: expected number of copies doesnt match actual"
fi

