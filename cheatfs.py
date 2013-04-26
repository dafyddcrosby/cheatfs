#!/usr/bin/env python
# Copyright 2013 Dafydd Crosby <dafydd@dafyddcrosby.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
A filesystem to look at the Ruby cheat pages
"""

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context
from stat import S_IFDIR, S_IFREG
import urllib2
import sys
from time import time

import logging
logging.basicConfig(filename='cheatfs.log', level=logging.DEBUG)

class CheatFS(LoggingMixIn, Operations):
    """
    Access the Cheat website, lay it out like a filesystem
    """
    # TODO - Write access to the cheat pages
    def __init__(self):
        logging.info("init")
        self.host = "http://cheat.errtheblog.com/"
        fileobj = urllib2.urlopen(self.host + "/ya/")
        filelist = []
        for line in fileobj:
            filelist.append(line[2:-1])
        fileobj.close()
        # Drop the first two lines, since they aren't pages
        self.files = filelist[2:]

    def getattr(self, path, fh=None):
        """
        Return a dictionary of stat values
        """
        logging.info("getattr")
        uid, gid, pid = fuse_get_context()
        # FIXME - Find a solution to st_size that doesn't slap server hard.
        fdict = {
            'st_gid': gid,
            'st_mode': (S_IFREG | 0666),
            'st_size': 1000000,
            'st_uid': uid,
        }
        if path == '/':
            fdict["st_nlink"] = 2
            fdict["st_mode"] = (S_IFDIR | 0666)

        fdict['st_ctime'] = fdict['st_mtime'] = fdict['st_atime'] = time()
        return fdict

    def read(self, path, size, offset, fh):
        url = self.host + "/y/" + path
        logging.debug(url)
        fileobj = urllib2.urlopen(url)
        buf = fileobj.read()
        fileobj.close()
        return buf

    def readdir(self, path, fh):
        """
        Returns a list of file paths
        """
        files = ['.', '..' ]
        return files + self.files

    # Disable unused operations:
    access = None
    flush = None
    getxattr = None
    listxattr = None
    open = None
    opendir = None
    release = None
    releasedir = None
    statfs = None

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <mountpoint>' % sys.argv[0])
        exit(1)

    fuse = FUSE(CheatFS(), sys.argv[1])
