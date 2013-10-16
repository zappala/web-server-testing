# Web Server Testing

This is a collection of static files you can use to test a web
server. Be sure to change the permissions of the file test.txt so you
get a 403 code when accessing it:

> chmod ugo-r static/files/test.txt

To verify what your web server should display, use:

> python -m SimpleHTTPServer
