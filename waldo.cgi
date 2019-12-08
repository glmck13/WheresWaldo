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

if [ "$Password" ]; then
	htpasswd -b .htpasswd $REMOTE_USER "$(eval urlencode -d "$Password")"
fi

cd $BUTTONDIR
typeset -A conf

if [ -f ${REMOTE_USER}.conf ]; then
	while IFS=":" read clickType contacts
	do
		conf["$clickType"]="$contacts"
	done <${REMOTE_USER}.conf
fi
>${REMOTE_USER}.conf
for clickType in SINGLE DOUBLE LONG
do
	contacts="$(eval urlencode -d "\$$clickType")"
	if [ ! "$contacts" ]; then
		contacts="${conf[$clickType]}"
	else
		conf["$clickType"]="$contacts"
	fi
	print "$clickType:$contacts" >>${REMOTE_USER}.conf
done

cat - <<EOF
Content-type: text/html

<html>
<head>
<!-- http://tristen.ca/tablesort/demo/ -->
<script src='/js/tablesort.min.js'></script>
<link href='/css/tablesort.css' rel='stylesheet'>
<link href='/css/style.css' rel='stylesheet'>
<meta name="viewport" content="width=device-width">
<meta charset=utf-8 />
<title>Where's Waldo?</title>
</head>
<body>
<table id='sort' class='style'>
<thead><tr><th>Who</th><th>What</th><th>When</th><th>Where</th></tr></thead>
<tbody>
EOF

for owner in $(ls *.csv 2>/dev/null)
do
	unset deviceId clickType reportedTime cellId address

	IFS="," read deviceId clickType reportedTime cellId address <$owner; owner=${owner%.*}

	(( secs = $(date +%s) - $(date --date="$reportedTime" +%s) ))

	print "<tr><td>$owner</td><td>$clickType click</td><td data-sort=$secs>$(timeElapsed)</td><td>$cellId: $address</td></tr>"
done

cat - <<EOF
</tbody></table>
<script>new Tablesort(document.getElementById('sort'));</script>
<form>
<table class='style'>
<thead><tr><th>Click Type</th><th>$REMOTE_USER's Contacts</th></tr></thead>
<tbody>
EOF

for clickType in SINGLE DOUBLE LONG
do
cat - <<EOF
<tr><td>$clickType</td><td><input type="text" size=30 name="$clickType" value="${conf[$clickType]}"></td></tr>
EOF
done

cat - <<EOF
</tbody></table>
$REMOTE_USER's Password: <input type="password" name="Password">
<input type="submit">
</form>
</body>
</html>
EOF
