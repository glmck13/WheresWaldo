#!/bin/ksh

plural () {
	if (( $1 == 1 )); then
		print ${1} ${2%s}
	else
		print ${1} ${2%s}s
	fi
}

timeElapsed () {
typeset -i relmajor relminor

if (( secs < $oneMin )); then
	(( relmajor = secs ))
	print -- "$(plural $relmajor seconds) \\c"
	print "ago"
elif (( secs < $oneHour )); then
	(( relmajor = secs / oneMin ))
	(( relminor = secs % oneMin ))
	print -- "$(plural $relmajor minutes) \\c"
	(( relminor > 0 )) && print -- "and $(plural $relminor seconds) \\c"
	print "ago"
elif (( secs < $oneDay)); then
	(( relmajor = secs / oneHour ))
	(( relminor = (secs % oneHour) / oneMin ))
	print -- "$(plural $relmajor hours) \\c"
	(( relminor > 0 )) && print -- "and $(plural $relminor minutes) \\c"
	print "ago"
else
	(( relmajor = secs / oneDay ))
	(( relminor = (secs % oneDay) / oneHour ))
	print -- "$(plural $relmajor days) \\c"
	(( relminor > 0 )) && print -- "and $(plural $relminor hours) \\c"
	print "ago"
fi
}

PATH=$PWD:$PATH
BUTTONDIR=~www-data/html/run/button

[ "$REQUEST_METHOD" = "POST" ] && read -r QUERY_STRING

vars="$QUERY_STRING"
while [ "$vars" ]
do
	print $vars | IFS='&' read v vars
	[ "$v" ] && export $v
done

(( oneMin = 60 ))
(( oneHour = oneMin*60 ))
(( oneDay = oneHour*24 ))

cd $BUTTONDIR
typeset -Z8 secs

cat - <<-EOF
Content-type: text/html

<html>
<head>
<!-- http://tristen.ca/tablesort/demo/ -->
<script src='/js/tablesort.min.js'></script>
<link href='/css/tablesort.css' rel='stylesheet'>
<link href='/css/style.css' rel='stylesheet'>
<meta name="viewport" content="width=device-width">
<link rel="apple-touch-icon" href="/images/button.png">
<title>Button Up!</title>
</head>
<body>
<table id='uptab' class='style'>
<thead><tr>
<th data-sort-default>When</th>
<th>What</th>
<th>Who</th>
<th>Where</th>
</tr></thead>
<tbody>
EOF

for owner in $(ls *.csv 2>/dev/null)
do
	unset deviceId clickType reportedTime cellId address message

	IFS="|" read deviceId clickType reportedTime cellId address message <$owner; owner=${owner%.*}

	if [ "$cellId" ]; then
		grep "$cellId" $owner.conf 2>/dev/null | IFS="|" read alias x
		[ "$alias" ] && address="$alias"
	fi

	(( secs = $(date +%s) - $(date --date="$reportedTime" +%s) ))

	cat - <<-EOF
	<tr>
	<td data-sort=$secs>$(timeElapsed)</td>
	<td>$clickType click</td>
	<td>$owner</td>
	<td>$cellId: $address: $message</td>
	</tr>
	EOF
done

cat - <<-EOF
</tbody></table>
<script>new Tablesort(document.getElementById('uptab'));</script>
<a href="upconf.cgi">Edit ${REMOTE_USER:-Who}'s Config</a>
</body>
</html>
EOF
