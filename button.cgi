#!/bin/ksh

PATH=$PWD:$PATH
BUTTONDIR=~www-data/html/run/button

[ "$REQUEST_METHOD" = "POST" ] && read -r QUERY_STRING

vars="$QUERY_STRING"
while [ "$vars" ]
do
	print $vars | IFS='&' read v vars
	[ "$v" ] && export $v
done

entry="$deviceId,$clickType,$(urlencode -d $reportedTime)"

UNWIREDURL=https://us1.unwiredlabs.com/v2/process.php
UNWIREDTOKEN=""
NETWORKMCC=310
NETWORKMNC=410

if [ "$cellId" ]; then
	let cellId=16#$cellId
	lacIds=$(urlencode -d $lacIds)

	for lac in ${lacIds//,/ }
	do
		address=$(
		curl -s -d@- $UNWIREDURL <<-EOF | python -c 'import sys, json; print json.load(sys.stdin).get("address")'
		{
		"token": "$UNWIREDTOKEN",
		"radio": "lte","mcc": $NETWORKMCC,"mnc": $NETWORKMNC,
		"cells": [{"lac": $lac,"cid": $cellId}],
		"address": 1
		}
		EOF
		)
		[ "$address" != "None" ] && break
	done

	entry+=",$cellId,$address"
fi

cd $BUTTONDIR; print "$entry" >$owner.csv

cat - <<EOF
Content-type: text/plain

$owner.csv:$entry
EOF