#!/bin/bash
#returns the exif tags found in a given image

if [ -z $1 ]; then
	echo "Usage: $0 imageFile"
	exit 1
fi

echo "{"
tags=`LANG=C LANGUAGE=C  exif -l $1 | grep "^0x" | sed -e "s/ [\* \-]\+//g" -e "s/^\(0x[a-f0-9]\+\) \(.*\)/\1:\2/g" -e "s/ /_/g"`
first=1
for tag in $tags; do
	if [ "$first" -ne 1 ]; then
		echo ","
	fi
	first=0
	#grab the hex tag
	hex=`echo "$tag" | sed -e "s/:.*//g"`
	let int=$hex
	echo -n "$tag" | sed -e "s/:/\":\"/g" -e "s/^/\"/g" -e "s/\$/\"/g" -e "s/$hex/$int/g"
done
echo
echo "}"
