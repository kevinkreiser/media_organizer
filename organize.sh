#!/bin/bash

#returns an alias for a file
function get_alias
{
	name=`echo "$1" | awk -F '.' '{print \$1}'`
	id=`echo "$1" | awk -F '.' '{print \$2}'`
	ext=`echo "$1" | awk -F '.' '{print \$3}'`

	if [ -z $ext ]; then
	        ext=$id
	        id="0"
	else
	        id="`expr $id + 1`"
	fi

	echo $name.$id.$ext	
}

#only copy the file if it isnt already there
#and if one has the same name but is different alias it
function safe_copy
{
	m=$1
	c=$2
	d=$3
	shift 3
	s="$@"

	#the file already exists
	if [ -f "$d" ]; then
		#if they are different files we need to keep it
		if [ `wc -c "$s" | sed -e "s/ .*//g"` != `wc -c "$d" | sed -e "s/ .*//g"` ] || [ "`head -c 524288 "$s" | md5sum`" != "`head -c 524288 "$d" | md5sum`" ]; then
			name=`get_alias "$d"`
			#recurse because we want duplication check again
			safe_copy $m $c $name $s
		else
			echo "Duplicate: $s and $d ($m)"
			exit 1
		fi
	#file isnt there already just copy it
	else
		echo "$c $s $d ($m)"
		$c "$s" "$d"
	fi
}

#what to do when you cant get metadata
function no_meta
{
	#get all the stat info about the file
	mod=`stat -c %Y "$@"`
	#use the mod time as the time stamp
	echo `date -d "1970-01-01 $mod sec GMT" +%Y_%m_%d_%H_%M_%S`
}

if [ -z "$3" ]; then
	echo "Usage: dest relocationCommand src_file"
	echo "Example: $0 /media/K/family/sort \"cp -rp\" /media/K/family/queue/img.jpg"
	exit 1
fi

args="$@"

sorted="$1"
cmd="$2"
shift 2
file="$@"

#if it doesnt have a place to go make it
mkdir -p "$sorted" 

if [ ! -d $sorted ] || [ ! -w $sorted ]; then
	echo "Couldn't create or access output dir"
	exit 1
fi

if [ ! -f "$@" ]; then
	echo "Couldn't find input file when run as: $args"
	exit 1
fi

#check for exif data first
meth="EXIF"
date=`python EXIFdate.py "$file"`

#if it failed
if [ $? -ne 0 ]; then
	#check for mts header information
	meth="META"
	date=`python MTSdate.py "$file"`
	#if it failed
	if [ $? -ne 0 ]; then
		#see if we can get it from the file timestamps
		meth="STAT"
		date=$(no_meta "$file")
		#if it failed
		if [ $? -ne 0 ]; then
			echo "Failed: $cmd $file $date"
			exit 1
		fi
	fi
fi

#grab the extension
ext="${file##*.}"
#change the date into a day only
day=`echo $date | awk -F '_' '{print $1"_"$2"_"$3}'`
mkdir -p "$sorted"/$day
#copy it
safe_copy $meth "$cmd" "$sorted"/$day/$date.$ext "$file"
exit 0
