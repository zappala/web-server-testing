# Web Server Testing

This is a collection of static files you can use to test a web
server. Be sure to change the permissions of the file test.txt so you
get a 403 code when accessing it:

> chmod ugo-r web/static/files/test.txt

To verify what your web server should display, use:

> cd web

> python -m SimpleHTTPServer

In the test directory are protocol and load testing scripts. You can
run various HTTP protocol tests using

> cd tests

> python protocol.py [-s server] [-p port]

You can load test a web server using

> cd tests

> python stress-test.py [host]:[port][path] -t [threads] -d [duration]

For example:

> python stress-test.py localhost:8000/static/files/largefile.txt -t 10 -d 10

