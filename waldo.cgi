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
typeset -Z8 secs

if [ -f ${REMOTE_USER}.conf ]; then
	while IFS="|" read key contacts
	do
		conf["$key"]="$contacts"
	done <${REMOTE_USER}.conf
fi
>${REMOTE_USER}.conf
for key in SINGLE DOUBLE LONG HOME WORK GYM OTHER
do
	contacts="$(eval urlencode -d "\$$key")"
	if [ ! "$contacts" ]; then
		contacts="${conf[$key]}"
	else
		contacts=$(print "$contacts" | sed -e "s/^ \+//" -e "s/ \+$//")
		conf["$key"]="$contacts"
	fi
	print "$key|$contacts" >>${REMOTE_USER}.conf
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
<link rel="apple-touch-icon" href="/images/waldo.png">
<meta charset=utf-8 />
<title>Where's Waldo?</title>
</head>
<body>
<table id='waldo' class='style'>
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
	unset deviceId clickType reportedTime cellId address

	IFS="|" read deviceId clickType reportedTime cellId address <$owner; owner=${owner%.*}

	if [ "$cellId" ]; then
		grep "^.*|$cellId$" $owner.conf 2>/dev/null | IFS="|" read alias x
		[ "$alias" ] && address="$alias"
	fi

	(( secs = $(date +%s) - $(date --date="$reportedTime" +%s) ))

	print "<tr>\\c"
	print "<td data-sort=$secs>$(timeElapsed)</td>\\c"
	print "<td>$clickType click</td>\\c"
	print "<td>$owner</td>\\c"
	print "<td>$cellId: $address</td>\\c"
	print "</tr>"
done

cat - <<EOF
</tbody></table>
<script>new Tablesort(document.getElementById('waldo'));</script>
<form>
<table class='style'><tbody>
EOF

print "<tr style='background-color:cornsilk;font-weight:bold;'><td>ClickType</td><td>$REMOTE_USER's Actions</td></tr>"
for key in SINGLE DOUBLE LONG
do
cat - <<EOF
<tr><td>$key</td><td><input size=30 type="text" name="$key" value="${conf[$key]}"></td></tr>
EOF
done

print "<tr style='background-color:cornsilk;font-weight:bold;'><td>Location</td><td>$REMOTE_USER's Cellids</td></tr>"
for key in HOME WORK GYM OTHER
do
cat - <<EOF
<tr><td>$key</td><td><input size=30 type="text" name="$key" value="${conf[$key]}"></td></tr>
EOF
done

cat - <<EOF
<tr style='background-color:cornsilk;font-weight:bold;'><td>Profile</td><td>$REMOTE_USER's Settings</td></tr>
<tr><td>Password</td><td><input size=30 type="password" name="Password"></td></tr>
</tbody></table>
<input type="submit">
</form>
</body>
</html>
EOF
