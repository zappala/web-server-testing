#!/usr/bin/env python
# 
# Workload generator for a web server
#       Daniel Zappala
#       2008

import gc
import httplib
import optparse
import random
import socket
import sys
import threading
import thread
import time
import traceback

class Logger:
    def __init__(self):
        self.sem = threading.Semaphore()
        self.log_lines = []

    def log(self,line):
        self.sem.acquire()
        if len(self.log_lines) > 1000:
            self.flush()
        self.log_lines.append(line)
        self.sem.release()

    def flush(self):
        for line in self.log_lines:
            print line
        sys.stdout.flush()
        self.log_lines = []

class Connection:
    def __init__(self,number,host,port):
        self.number = number
        self.host = host
        self.port = port
        self.conn = httplib.HTTPConnection(self.host, self.port)


    def get(self,uri):
        start = time.time()
        try:
            self.conn.request("GET",uri)
            resp = self.conn.getresponse()
            # Check response code
            if int(resp.status) != 200:
                return "%d %s %s %s -" % (self.number,uri,resp.status,resp.reason.strip())

            length = resp.getheader('content-length')
            mimetype = resp.getheader('content-type')

            # Check for content length
            if not length:
                return "%d %s 600 NoContentLength 0 0" % (self.number,uri)

            # Check for numeric value in content length
            if not length.isdigit():
                return "%d %s 601 BadContentLength 0 0" % (self.number,uri)

            # Download the given number of bytes
            return self.download(uri,resp,int(length),start)

        except:
            error = sys.exc_info()[0]
            reason = sys.exc_info()[1]
            # traceback.print_exc()
            return "%d %s 610 %s 0 0" % (self.number, uri,str(error)+str(reason))
    def download(self,uri,resp,length,start):
        buflen = 0
        while True:
            buf = resp.read(65000)
            if len(buf) > 0:
                buflen += len(buf)
            else:
                return "%d %s 602 MessageShort 0 0" % (self.number,uri)
            if buflen > length:
                return "%d %s 603 MessageLong 0 0" % (self.number,uri)
            if buflen == length:
                resp.close()
                break
        elapsedtime = time.time() - start
        return "%d %s 200 OK %d %f" % (self.number,uri,buflen,elapsedtime)


    def close(self):
        self.conn.close()

class Session(threading.Thread):
    def __init__(self, number, host, port, chooser, logger):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.number = number
        self.host = host
        self.port = port
        self.chooser = chooser
        self.logger = logger
        self.conn = Connection(number,host,port)

    def pause(self):
        alpha = 1.5
        return random.paretovariate(alpha)

    def request(self,uri):
        value = self.conn.get(uri)
        self.logger.log(value)
        
    def run(self):
        uri = "/" + self.chooser.chooseFile()
        self.request(uri)
        self.conn.close()

class Chooser:
    def __init__(self):
        self.total = 1000
        self.pop = self.generatePops()

    def generatePops(self):
        pop = []
        # zipf alpha constant
        alpha = 1.0
        # compute normalization constant
        c = 0.0
        for i in xrange(1,self.total+1):
            c = c + (1.0 / (i**alpha))
        c = 1.0 / c
        # choose popularity of each file
        for i in xrange(1,self.total+1):
            pop.append(c/(i**alpha))
        return pop

    def chooseFile(self):
        x = random.random()
        sum = 0
        for p in self.pop:
            sum = sum + p
            if sum >= x:
                break
        return 'file'+str(self.pop.index(p)).zfill(3)+'.txt'


class WorkloadGenerator:
    def __init__(self, host, port, load):
        self.host = host
        self.port = port
        self.load = load
        self.chooser = Chooser()
        self.logger = Logger()

    def pause(self):
        return random.expovariate(self.load)

    def startTotal(self,total):
        sessionNumber = 0
        threads = []
        for i in xrange(0,total):
            try:
                s = Session(sessionNumber,self.host,self.port,self.chooser,self.logger)
                s.start()
            except:
                print "Too many threads"
                return
            threads.append(s)
            # sleep
            pause = self.pause()
            time.sleep(pause)
            sessionNumber += 1
            
        for t in threads:
            t.join()

        self.logger.flush()

    def startDuration(self,duration):
        start = time.time()
        sessionNumber = 0
        threads = []
        while True:
            now = time.time()
            if (now - start) > duration:
                break
            try:
                s = Session(sessionNumber,self.host,self.port,self.chooser,self.logger)
                s.start()
            except:
                continue
            threads.append(s)
            # sleep
            pause = self.pause()
            time.sleep(pause)
            sessionNumber += 1
            
        for t in threads:
            t.join()

        self.logger.flush()


if __name__ == "__main__":
    gc.set_debug(gc.DEBUG_LEAK)
    parser = optparse.OptionParser(usage="%prog -s [server] -p [port] -l [load (sessions/s)] -d [duration (seconds)] -t [total (sessions)] -n [seed]", version="%prog 1.0")
    parser.add_option("-s", "--server", dest="host", type="str", default="localhost",
                      help= "server to connect to")
    parser.add_option("-p", "--port", dest="port", type="int", default=80,
                      help= "port number to connect to")
    parser.add_option("-l", "--load", dest="load", type="int", default=1,
                      help= "number of sessions to create per second")
    parser.add_option("-t", "--total", dest="total", type="int", default=None,
                      help= "total number of sessions to generate")
    parser.add_option("-d", "--duration", dest="duration", type="int", default=1,
                      help= "total number of seconds to generate load")
    parser.add_option("-n", "--seed", dest="seed", type="int", default=100,
                      help= "random number generator seed")
    
    (options, args) = parser.parse_args()

    # seed random number generator
    random.seed(options.seed)

    thread.stack_size(50000)

    # launch generator
    wg = WorkloadGenerator(options.host, options.port, options.load)
    if options.total:
        wg.startTotal(options.total)
    else:
        wg.startDuration(options.duration)

