#!/bin/bash

inputDir=${1:-"./"}

doUnzip=${2:-1}

echo "Going to merge files in $inputDir"

counter=0


for dir in $inputDir/*
do
    echo "In directory: $dir"
    if [[ $dir ==  *clean_input* ]]
    then
	echo "Found clean_input dir: skipping"
	continue
    fi
    if [[ $dir ==  *test* ]]
    then
	echo "Found test dir: skipping"
	continue
    fi
    if [[ $dir ==  *plots* ]]
    then
	continue
    fi
    if [[ $dir !=  *run* ]]
    then
	continue
    fi

    if [ $counter -eq 0 ]
    then			
	refDir=$dir
    fi						
    ((counter+=1))
    #first unzip all files
    for file in $dir/*
    do
	echo ""
	gunzip $file
    done
    echo "Now creating ntuples for directory: $dir"
    #now run the ntuple making script
    python makeNtuple.py --inputDir "$dir" --outputDir "$dir"
done


#Now merge all the root files
for file in $refDir/*root
do
newstring=${file##$refDir}
filename=${newstring##/}
hadd -f $inputDir/$filename $inputDir/run*/$filename
rm $inputDir/run*/$filename
done
  

echo $refDir
