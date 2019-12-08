#!/bin/ksh

PATH=$PWD:$PATH
BUTTONDIR=~www-data/html/run/button
NOTIFYME=~www-data/html/etc/notifyme.conf
PHONES=~www-data/html/etc/phones.conf

[ "$REQUEST_METHOD" = "POST" ] && read -r QUERY_STRING

vars="$QUERY_STRING"
while [ "$vars" ]
do
	print $vars | IFS='&' read v vars
	[ "$v" ] && export $v
done

entry="$deviceId,$clickType,$(urlencode -d $reportedTime)"

UNWIREDURL=https://us1.unwiredlabs.com/v2/process.php
UNWIREDTOKEN="a6df1ea571a590"
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

cd $BUTTONDIR
print "$entry" >$owner.csv

grep "^$clickType:" $owner.conf 2>/dev/null | IFS=":" read x contacts

contacts=${contacts// /} contacts+=","

while [ "$contacts" ]
do
	id="${contacts%%,*}"

	case "$id" in
	*@*)
		sendaway.sh "$id" "$owner $clickType click!" "${address:--}"
		;;
	\#*)
		grep "^${id#?}," $NOTIFYME | IFS="," read x id
		[ "$id" ] && curl -s "https://api.notifymyecho.com/v1/NotifyMe?accessCode=$id&notification=$(urlencode "$owner $clickType click $address")" >/dev/null
		;;
	!*)
		grep "^${id#?}," $PHONES 2>/dev/null | IFS="," read x id
		[ "$id" ] && sendaway.sh "$id" "$owner $clickType click!" "${address:--}"
		;;
	esac

	contacts="${contacts#*,}"
done

cat - <<EOF
Content-type: text/plain

$owner.csv:$entry
EOF
