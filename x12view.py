#!/usr/bin/env python
"""
EDI X12 class to display EDI X12 file in a more human readable way
"""
# Mel - 2018-10-16 - display EDI X12 file in a more human readable way
# Mel - 2018-10-23 - fix x12 in MSDOS CR/LF problem
# Mel - 2018-10-24 - add readable file check
# Mel - 2018-10-26 - remove testing line

# import os.path
from os import R_OK, access
from os.path import isfile


class X12(object):
    """
    Class for an X12 file requires the path/filename.
    Replaces print of object with a more human readable X12
    broken into one segment per line.

    attibutes:
    filename - the file read
    readable - if the file is readable
    raw - the full unformatted X12
    edix12 - Boolean: True if it appears to be X12 structure
    fieldsep - the field separator - commonly '*'
    segsep - the segment separator - commonly '~'
    segments - list of segments with separator removed
    """

    def __init__(self, givenfile):
        self.filename = givenfile
        self.readable = False
        self.raw = ''
        self.edix12 = False
        self.fieldsep = ''
        self.segsep = ''
        self.segments = []
        if isfile(self.filename):
            self.isafile = True
        else:
            self.isafile = False
        if self.isafile:
            if access(self.filename, R_OK):
                self.readable = True
                with open(self.filename, 'r') as onefile:
                    self.raw = onefile.read()
                if self.raw[:3] == "ISA":
                    self.edix12 = True
                else:
                    self.edix12 = False
                    self.fieldsep = ''
                    self.segsep = ''
                    self.segments = []
                if self.edix12:
                    self.fieldsep = self.raw[3]
                    # standard says GS should be at 106, unless optional CR/LF is included, then 108
                    pos = self.raw.find("GS", 105)
                    # get last field in first segement which we can define as everything before GS
                    lastfieldsep = self.raw.rfind(self.fieldsep, 0, pos)
                    # 2nd char last field is segment separator, any char including CR, tilde is typical
                    self.segsep = self.raw[lastfieldsep+2]
                    self.segments = self.raw.split(self.segsep)
                    # DOS CR/LF will be at the begining of each segment after split (...~\r\n) - remove
                    self.segments = '\t'.join(self.segments).replace('\r', '').split('\t')
                    self.segments = '\t'.join(self.segments).replace('\n', '').split('\t')
                    # remove blank resulting from split where last char is the split char
                    if '' in self.segments:
                        self.segments.remove('')

    def __str__(self):
        if not self.isafile:
            return "Not a file: %s" % self.filename
        if not self.readable:
            return "File not readable: %s" % self.filename
        if not self.edix12:
            return "Not an X12 file: %s" % self.filename
        tabs = 0
        prettyx12 = ''
        for seg in self.segments:
            if seg[:2] == "GS" or seg[:2] == "ST":
                tabs += 1
            if seg[:2] == "SE":
                tabs -= 1
            prettyx12 = prettyx12 + " " * (tabs*4) + seg + self.segsep
            if self.segsep != '\n':
                prettyx12 = prettyx12 + '\n'
            if seg[:2] == "ST":
                tabs += 1
            if seg[:2] == "GE" or seg[:2] == "SE":
                tabs -= 1
        return prettyx12


if __name__ == '__main__':
    import sys
    for argument in sys.argv[1:]:
        data = X12(argument)
        print(data)
