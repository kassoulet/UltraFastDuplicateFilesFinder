#!/usr/bin/python
# -*- coding: utf-8 -*-
#

"""
Ultra Fast Duplicate Files Finder
=================================
  by Gautier Portet <kassoulet gmail com>


Takes a list of file from stdin.
And print the duplicate ones.


example use:

  find ~/ -size +10M | ./UltraFastDuplicateFilesFinder.py

to find duplicates in your home folder, all files more than 10MB.

UltraFastDuplicateFilesFinder compares only the very beginning of the files.
Its sufficient for most uses, but use with caution.

But this way is quite useful to detect duplicates within corrupted media files...


this is public domain.
"""

import sys
import os
import hashlib

# read one CHUNK_SIZE bytes to check duplicates
CHUNK_SIZE = 1024

# buffer size when doing whole file md5
BUFFER_SIZE = 64*1024


def get_file_hash(filename, limit_size=None, buffer_size=BUFFER_SIZE):
    """
    Return the md5 hash of given file as an hexadecimal string.
    
    limit_size can be used to read only the first n bytes of file.
    """
    # open file
    try:
        f = file(filename, "rb")
    except IOError:
        return 'NONE'

    # get md5 hasher
    hasher = hashlib.md5()
    
    if limit_size:
        # get the md5 of beginning of file
        chunk = f.read(limit_size)
        hasher.update(chunk)
    else:        
        # get the md5 of whole file
        chunk = True
        while chunk:
            chunk = f.read(buffer_size)
            hasher.update(chunk)

    f.close()
    return hasher.hexdigest()


filelist = []
hashlist = {}
hashcount = {}
duplicates = []

def check_file(filename):
    """
    Compare the given file to our lists of hashes
    """    
    # compute md5
    h = get_file_hash(filename)
    
    # increase count
    i = hashcount.get(h, 0)
    hashcount[h] = i+1
    
    # store md5 and filename for later use
    f = hashlist.get(h, [])
    f.append(filename)
    hashlist[h] = f



totalsize = 0
totalfiles = 0
dupfiles = 0
dupsize = 0

def humanize_size(size):
    """
    Return the file size as a nice, readable string.
    """
    for limit, suffix in ((1024**3, 'GiB'), (1024**2, 'MiB'), (1024, 'KiB')):
        hsize = float(size) / limit
        if hsize > 0.5:
            return '%.2f %s' % (hsize, suffix)


# we start here by checking all files
for filename in sys.stdin:
    filename = filename.strip()

    check_file(filename)
    totalfiles += 1
    totalsize += os.path.getsize(filename)

# print the report
print '%10s   %s' % ('size', 'filename')

for h, f in hashlist.iteritems():
    if hashcount[h] < 2:
        # present one time, skip
        continue
    
    # reference file    
    refsize = os.path.getsize(f[0])
    refmd5 = get_file_hash(f[0])
    print '%10d   %s' % (refsize, f[0])
    
    
    for filename in f[1:]:
        # and its copies
        size = os.path.getsize(filename)
        md5 = get_file_hash(filename)

        status = ' '
        msg = ''
        if md5 != refmd5:
            status = '!'
            msg = ' partial match only!'

        print '%10d %s %s%s' % (size, status, filename, msg)
        dupsize += size
    dupfiles += 1
    print

# final summary
print '%d files checked (%s), %d duplicates (%s).' % (
    totalfiles, humanize_size(totalsize), dupfiles, humanize_size(dupsize))

