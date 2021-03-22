"""A python `tail --follow` implementation"""
import time


def follow_file(filename):
    where = 0
    while True:
        # check inode every run, because sometime the inode changed
        # but fp was still tracking to the old inode
        with open(filename) as fp:
            fp.seek(where)
            line = fp.readline()
            if not line or not line.endswith('\n'):
                time.sleep(1)
            else:
                yield line
                where = fp.tell()
