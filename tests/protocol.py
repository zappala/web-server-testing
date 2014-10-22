import argparse
import socket
import sys

class Tester:
    def __init__(self):
        self.cache = ''
        self.size = 10000

    def parse_arguments(self):
        parser = argparse.ArgumentParser(prog='Web Server Protocol Tester', description='Tests whether a web server passes various HTTP protocol tests', add_help=True)
        parser.add_argument('-p', '--port', type=int, action='store', help='Port the server is running on',default=80)
        parser.add_argument('-s', '--server', type=str, action='store', help='Host name of the server',default='localhost')
        parser.add_argument('-e', '--extra', action='store_true', help='Verbose output',default=False)
        parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output',default=False)
        args = parser.parse_args()
        self.host = args.server
        self.port = args.port
        self.verbose = args.verbose
        self.extra = args.extra

    def run(self):
        self.parse_arguments()
        self.testHeaders()
        self.testPersistent()
        self.testBad()
        self.testNotFound()
        self.testForbidden()
        self.testNotImplemented()
        self.testNonBlocking()
        if self.extra:
            self.testRange()

    def testHeaders(self):
        print "*** Headers ***"
        print "Manually check that the Date, Server, Content-Length, Content-Type, and Last-Modified headers are present and have the right format"
        print
        self.open_socket()
        self.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([200],check=True)
        self.close_socket()

    def testPersistent(self):
        print "*** Persistent Connection ***"
        self.open_socket()
        self.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([200],quiet=True)
        self.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([200],quiet=True)
        self.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([200],quiet=True)
        self.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([200])
        self.close_socket()

    def testBad(self):
        print "*** Bad Request (400) ***"
        self.open_socket()
        self.send("BAD / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([400,405,501])
        self.close_socket()

    def testNotFound(self):
        print "*** Not Found (404) ***"
        self.open_socket()
        self.send("GET /fjldsfjslf HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([404])
        self.close_socket()

    def testForbidden(self):
        print "*** Forbidden (403) ***"
        self.open_socket()
        self.send("GET /static/files/test.txt HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([403])
        self.close_socket()

    def testNotImplemented(self):
        print "*** Not Implemented (501) ***"
        self.open_socket()
        self.send("DELETE / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([501,405])
        self.close_socket()

    def testNonBlocking(self):
        print "*** Partial Data and Non-Blocking I/O ***"
        self.open_socket()
        # send part of a request on first socket
        self.send("GET / ")
        # setup second tester
        t = Tester()
        t.host = self.host
        t.port = self.port
        t.verbose = self.verbose
        t.open_socket()
        # send full request on second socket
        t.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        t.get_response([200],quiet=True)
        # send second part of request on first socket
        self.send("HTTP/1.1\r\nHost: %s\r\n\r\n" % self.host)
        self.get_response([200])
        self.close_socket()

    def testRange(self):
        import requests
        print "*** HEAD ***"
        r = requests.head('http://%s:%s/static/files/largefile.txt' % (self.host,self.port))
        if r.status_code != 200:
            print "FAILED: Expected 200, got",r.status_code
        print "*** Range Request ***"
        headers = {'Range':'bytes=0-999','Accept-Encoding': 'identity'}
        r = requests.get('http://%s:%s/static/files/largefile.txt' % (self.host,self.port),headers=headers)
        if r.status_code != 206:
            print "FAILED: Expected 206, got",r.status_code
            return
        if len(r.content) != 1000:
            print "FAILED: Expected 1000 bytes, got",len(r.content)
            return
        print "PASSED"

    def send(self,message):
        self.server.sendall(message)

    def get_response(self,codes,check=False,quiet=False):
        ''' Check if response code is what was expected '''
        headers = self.read_headers()
        if self.verbose or check:
            print headers,
        entity = self.read_entity(headers)
        if not entity:
            return
        if not self.check_headers(headers,'Date'):
            print "FAILED: No Date header"
            return
        if not self.check_headers(headers,'Server'):
            print "FAILED: No Server header"
            return
        if not self.check_headers(headers,'Content-Type'):
            print "FAILED: No Content-Type header"
            return
        if not self.check_headers(headers,'Content-Length'):
            print "FAILED: No Content-Length header"
            return
        lines = headers.split('\r\n')
        first = lines[0].split()
        if int(first[1]) not in codes:
            print "FAILED: expected",codes,"got",first[1]
        else:
            if quiet:
                return
            print "PASSED"

    ### Opening and closing socket ###

    def open_socket(self):
        """ Connect to the server """
        self.cache = ''
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.host,self.port))
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def close_socket(self):
        self.server.close()
        
    ### Read HTTP message from socket ###

    def read_headers(self):
        while True:
            data = self.server.recv(self.size)
            if not data:
                response = self.cache
                self.cache = ''
                return response
            self.cache += data
            headers = self.get_headers()
            if not headers:
                continue
            return headers

    def read_bytes(self,length):
        while len(self.cache) < length:
            data = self.server.recv(self.size)
            if not data:
                self.cache = ''
                print "FAILED: Length of entity doesn't match Content-Length"
                return False
            self.cache += data
        self.cache = self.cache[length:]
        return True

    def get_headers(self):
        ''' Check if headers present in cache '''
        index = self.cache.find("\r\n\r\n")
        if index == -1:
            return None
        headers = self.cache[0:index+4]
        self.cache = self.cache[index+4:]
        return headers

    def read_entity(self,headers):
        ''' Read entity body '''
        length = self.get_length(headers)
        if not length:
            print "FAILED: No Content-Length header"
            return False
        return self.read_bytes(length)

    def get_length(self,headers):
        ''' Get content length '''
        lines = headers.split('\r\n')
        for line in lines:
            if line == lines[0]:
                continue
            if line == '':
                continue
            name, value = line.split(':',1)
            value = value.strip()
            if name == 'Content-Length':
                length = int(value)
                return length
        return None

    def check_headers(self,headers,expected):
        lines = headers.split('\r\n')
        for line in lines:
            if line == lines[0]:
                continue
            if line == '':
                continue
            name, value = line.split(':',1)
            if name == expected:
                return True
        return False


if __name__ == '__main__':
    t = Tester()
    t.run()
