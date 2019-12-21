#!/bin/ksh

PATH=$PWD:$PATH
BUTTONDIR=~www-data/html/run/button
WALDOCONF=~www-data/html/etc/waldo.conf

[ "$REQUEST_METHOD" = "POST" ] && read -r QUERY_STRING

vars="$QUERY_STRING"
while [ "$vars" ]
do
	print $vars | IFS='&' read v vars
	[ "$v" ] && export $v
done

[ "$owner" ] || exit
[ "$clickType" ] || exit

entry="$deviceId|$clickType|$(urlencode -d $reportedTime)"

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
fi

cd $BUTTONDIR

grep "^$clickType|" $owner.conf 2>/dev/null | IFS="|:" read x contacts message

entry+="|$cellId|$address|$message"

contacts+=","

while [ "$contacts" ]
do
	print "$contacts" | IFS=", " read id contacts

	case "$id" in

	!*)
		[ "${id#?}" ] && entry+=$(${id#?})
		print "$entry" >$owner.csv
		;;

	*@*)
		sendaway.sh "$id" "$clickType click from $owner!" "${message:-${address:--}}"
		;;

	\#*)
		grep "^${id#?}," $WALDOCONF | IFS="," read x id

		if [ ! "$id" ]; then
			:
		elif [[ "$id" == *@* ]]; then
			sendaway.sh "$id" "$clickType click from $owner!" "${message:-${address:--}}"
		else
			curl -s "https://api.notifymyecho.com/v1/NotifyMe?accessCode=$id&notification=$(urlencode "$clickType click from $owner ${message:-${address:--}}")" >/dev/null
		fi
		;;
	esac
done

cat - <<EOF
Content-type: text/plain

$owner.csv:$entry
EOF
