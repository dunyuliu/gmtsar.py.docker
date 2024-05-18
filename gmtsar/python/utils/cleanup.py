#! /usr/bin/env python3
"""
cleanup is part of GMTSAR. 
It is the Python version and migrated from cleanup.csh.
Originally it was written by David T. Sandwell on March 11 2010.
Dunyu Liu, 20230424.

Purpose: to clean the disk area in preparation for process2pass.csh
This should be run in the top directory. 
An ls will show raw SLC intf topo.
"""

import sys
import os
from gmtsar_lib import *



def cleanup(directory):
    """
    Usage: cleanup directory
    
    directory could be: raw, SLC, topo, or all
    
    Example: cleanup all')
    """
    print("CLEANUP - START ... ...")

    if directory == 'all':
        print(' ')
        print('CLEANUP: cleanup all ... ...')
        delete('SLC')
        delete('intf')
        delete('raw/*.PRM*')
        delete('raw/*.raw')
        delete('raw/*.LED')
        delete('raw/*.SLC')
        delete('F1/intf')
        delete('F2/intf')
        delete('F3/intf')
        delete('F1/SLC')
        delete('F2/SLC')
        delete('F3/SLC')
        delete('F1/config.py')
        delete('F2/config.py')
        delete('F3/config.py')
        delete('merge')
        os.chdir('topo')
        # original csh command: ls | grep -v dem.grd | xargs rm -f
        # delete all the files except 'dem.grd'
        pwd = os.getcwd()
        all_files = os.listdir(pwd)
        exclude_filename = 'dem.grd'
        for filename in all_files:
            if filename != exclude_filename:
                delete(filename)

    if directory == 'raw':
        print(' ')
        print('CLEANUP: cleanup raw/ folder ... ...')
        delete('raw/*.PRM*')
        delete('raw/*.raw')
        delete('raw/*.LED')
        print(' ')

    if directory == 'SLC':
        print(' ')
        print('CLEANUP: clean up SLC/ folder ... ...')
        delete('SLC/*')
        print(' ')

    if directory == 'intf':
        print(' ')
        print('CLEANUP: clean up intf/ folder ... ...')
        delete('intf/*')
        print(' ')

    if directory == 'topo':
        print(' ')
        print('CLEANUP: clean up topo/ folder ... ...')
        os.chdir('topo')
        # delete all the files except 'dem.grd'
        pwd = os.getcwd()
        all_files = os.listdir(pwd)
        exclude_filename = 'dem.grd'
        for filename in all_files:
            if filename != exclude_filename:
                delete(filename)
        print(' ')

    print("CLEANUP - END ... ...")


if __name__ == "__main__":
    n = len(sys.argv)
    if n < 2:
        # if no arguments were input ... ...
        print(' ')
        print('CLEANUP: ERROR - missing input args ... ...')
        print('CLEANUP: exiting ... ...')
        print(' ')
        print(cleanup.__doc__)
        sys.exit()
    cleanup(sys.argv[1])
