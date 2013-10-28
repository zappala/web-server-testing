import os
import random
import sys

if len(sys.argv) < 3:
    # number of files
    total = 1000

    # location to put files
    directory = 'www'
else:
    total = int(sys.argv[1])
    directory = sys.argv[2]

# Pareto distribution parameters for file size
aFile = 1
bFile = 5

# base size 1 KB
base = 1024

os.mkdir(directory)

def make_data(size):
    data = []
    for i in range(0,size):
        data += 'x'
    data = ''.join(data)
    return data

# one KB of data
data = make_data(base)

for i in range(0,total):
    # choose size of file in KB
    size = bFile*random.paretovariate(aFile)
    # create file
    name = "%s/file%03d.txt" %(directory,i)
    f = open(name,'w')
    count = 1
    while count <= size:
        f.write(data)
        count += 1
    count -= 1
    # extra bytes
    extra_bytes = int((size-count)*base)
    extra_data = make_data(extra_bytes)
    f.write(extra_data)
    f.close()
