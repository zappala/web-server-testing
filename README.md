# Web Server Testing

This is a collection of static files you can use to test a web
server. Be sure to change the permissions of the file test.txt so you
get a 403 code when accessing it:

```
chmod ugo-r web/static/files/test.txt
```

To verify what your web server should display, use:

```
cd web
```

```
python -m SimpleHTTPServer
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

You can use a generated workload to test your web server using

```
python generator.py --server [host] --port [port] -l [load] -d [duration]
```

This will generate load on your server using an exponential
distribution whose average is given by [load], for [duration] seconds.

For example,

```
python generator.py --port 8000 -l 10 -d 30
```

will generate 10 clients per second, for 30 seconds, accessing the web
server on localhost at port 8000.

When the script runs, each session generates output with the format:

```
[sessionID] [URI] [status] [bytes] [seconds]
```

where:

```
[sessionID] is a unique identifier for the session
[URI] is the URI of the file downloaded
[status] is the status phrase returned by the server
[bytes] is the number of bytes downloaded
[seconds] is the time it took to download the URI, in seconds
```
