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

[ "$REMOTE_USER" ] || exit

if [ "$Password" ]; then
	htpasswd -b .htpasswd $REMOTE_USER "$(eval urlencode -d "$Password")"
fi

cd $BUTTONDIR
typeset -A conf

if [ -f ${REMOTE_USER}.conf ]; then
	while IFS="|" read key value
	do
		conf["$key"]="$value"
	done <${REMOTE_USER}.conf
fi
>${REMOTE_USER}.conf
for key in SINGLE DOUBLE LONG HOME WORK GYM OTHER
do
	value="$(eval urlencode -d "\$$key")"
	if [ ! "$value" ]; then
		value="${conf[$key]}"
	else
		value=$(print "$value" | sed -e "s/^ \+//" -e "s/ \+$//")
		conf["$key"]="$value"
	fi
	print "$key|$value" >>${REMOTE_USER}.conf
done

cat - <<-EOF
Content-type: text/html

<html>
<head>
<link href='/css/style.css' rel='stylesheet'>
<meta name="viewport" content="width=device-width">
<link rel="apple-touch-icon" href="/images/waldo.png">
</head>
<body>
<form method="post">
<table class='style'><tbody>
EOF

print "<tr style='background-color:cornsilk;font-weight:bold;'><td>ClickType</td><td>$REMOTE_USER's Actions</td></tr>"
for key in SINGLE DOUBLE LONG
do
cat - <<-EOF
<tr><td>$key</td><td><input size=30 type="text" name="$key" value="${conf[$key]}"></td></tr>
EOF
done

print "<tr style='background-color:cornsilk;font-weight:bold;'><td>Location</td><td>$REMOTE_USER's Cellids</td></tr>"
for key in HOME WORK GYM OTHER
do
cat - <<-EOF
<tr><td>$key</td><td><input size=30 type="text" name="$key" value="${conf[$key]}"></td></tr>
EOF
done

cat - <<-EOF
<tr style='background-color:cornsilk;font-weight:bold;'><td>Profile</td><td>$REMOTE_USER's Settings</td></tr>
<tr><td>Password</td><td><input size=30 type="password" name="Password"></td></tr>
</tbody></table>
<input type="submit">
</form>
</body>
</html>
EOF
