# Web Server Testing

This is a collection of static files you can use to test a web
server. Be sure to change the permissions of the file test.txt so you
get a 403 code when accessing it:

```
chmod ugo-r web/static/files/test.txt
```

## Protocol Testing

In the test directory is a script to test how well your server
conforms to the HTTP protocol:

```
python protocol.py [-s server] [-p port]
```

This will send various messages and check for the proper response.

## Load Testing

You can load test a web server using

```
python stress-test.py [host]:[port][path] -t [threads] -d [duration]
```

For example:

```
python stress-test.py localhost:8000/static/files/largefile.txt -t 10 -d 10
```

This will create 10 threads each downloading the given file for 10
seconds.

## Workload Testing

You can use the (tsung)[http://tsung.erlang-projects.org/] tool to
test your web server under a variety of conditions. This directory
contains a set of tsung scripts.
