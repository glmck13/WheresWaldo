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
for key in SINGLE DOUBLE LONG HOME WORK GYM OTHER Address
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
<meta name="viewport" content="width=device-width">
<link rel="apple-touch-icon" href="/images/button.png">
<style>
.collapsible {
background-color: gainsboro;
color: black;
width: 100%;
text-align: left;
border: none;
outline: none;
padding: 15px;
font-weight: bold;
}
.collapsible:after {
content: "[+]";
font-weight: bold;
float: right;
}
.collapsible.active {
background-color: chartreuse;
}
.collapsible.active:after {
content: "[-]";
font-weight: bold;
float: right;
}
.content {
display: none;
background-color: white;
}
</style>
</head>
<body>
<form method="post">
EOF

print "<button type=\"button\" class=\"collapsible\">$REMOTE_USER's Actions</button>"
print "<div class=\"content\">"
print "<table>"
for key in SINGLE DOUBLE LONG
do
	print "<tr><td>$key</td><td><input size=30 type=\"text\" name=\"$key\" value=\"${conf[$key]}\"></td></tr>"
done
print "</table>"
print "</div>"

print "<button type=\"button\" class=\"collapsible\">$REMOTE_USER's CellIds</button>"
print "<div class=\"content\">"
print "<table>"
for key in HOME WORK GYM OTHER
do
	print "<tr><td>$key</td><td><input size=30 type=\"text\" name=\"$key\" value=\"${conf[$key]}\"></td></tr>"
done
print "</table>"
print "</div>"

print "<button type=\"button\" class=\"collapsible\">$REMOTE_USER's Settings</button>"
print "<div class=\"content\">"
print "<table>"
for key in Address Password
do
	if [ "$key" = "Password" ]; then
		print "<tr><td>$key</td><td><input size=30 type=\"password\" name=\"$key\"></td></tr>"
	else
		print "<tr><td>$key</td><td><input size=30 type=\"text\" name=\"$key\" value=\"${conf[$key]}\"></td></tr>"
	fi
done
print "</table>"
print "</div>"

cat - <<-EOF
<input type="submit">
</form>
<script>
var coll = document.getElementsByClassName("collapsible");
var i;
for (i = 0; i < coll.length; i++) {
coll[i].addEventListener("click", function() {
this.classList.toggle("active");
var content = this.nextElementSibling;
if (content.style.display === "block") {
content.style.display = "none";
} else {
content.style.display = "block";
}
});
}
</script>
</body>
</html>
EOF
