#! /usr/bin/env python3
"""
dem2topo_ra is a Python script belongs to GMTSAR. 
It was migrated from dem2topo_ra.csh by Dunyu Liu on 20230915.
dem2topo_ra.csh was originally written by Matt Wei on Feb 1st 2010.
It was later modified by E. Fielding, DST, XT to add TSX data on Jan 10th 2014.

Purpose: to make topography for interferograms. The USGS elevations are height above WGS84 so this is OK.
"""

import sys
import os
from gmtsar_lib import *


def dem2topo_ra():
    """
    Usage: dem2topo_ra master.PRM dem.grd [interpolation_approach]
    
    NOTE: interpolation approach default is 0: surface with tension.
            set to 1 for gmt triangulate.
    """
    print('DEM2TOPO_RA - START ... ...')

    n = len(sys.argv)
    if n != 4 and n != 3:
        print('FILTER: Wrong # of input arguments; # should be 3 or 2 ... ...')
        print(dem2topo_ra.__doc__)

    print(' ')
    print("DEM2TOPO_RA: check if ~/.quiet file exists ... ...")
    if check_file_report('~/.quiet') is True:
        V = ''
    else:
        V = '-V'
    print('DEM2TOPO_RA: flag V is ', V)
    scale = '-JX7i'

    print('DEM2TOPO_RA - START ... ...')
    print(' ')
    tension = 0.1
    mode = 0
    if n == 4:
        mode = sys.argv[3]
    print('DEM2TOPO_RA: tension is ', tension)
    print('DEM2TOPO_RA: interpolation approach mode is ', mode)

    print(' ')
    print('DEM2TOPO_RA: Mosaic topo data ... ...')
    print('DEM2TOPO_RA: get bounds in radar coordinates ... ...')

    XMAX = int(grep_value(sys.argv[1], 'num_rng_bins', 3))
    yvalid = int(grep_value(sys.argv[1], 'num_valid_az', 3))
    num_patch = int(grep_value(sys.argv[1], 'num_patches', 3))
    YMAX = yvalid*num_patch
    SC = int(grep_value(sys.argv[1], 'SC_identity', 3))
    # original csh command: set PRF = `grep PRF *.PRM | awk 'NR == 1 {printf("%d", $3)}'`
    # set PRF to be the value of first encounter of PRF in *.PRM files.
    pwd = os.getcwd()
    all_files = os.listdir(pwd)
    for filename in all_files:
        if os.path.splitext(filename)[1] == '.PRM':
            PRF = float(grep_value(filename, 'PRF', 3))

    region = "0/"+str(XMAX)+"/0/"+str(YMAX)

    print('DEM2TOPO_RA: XMAX is ', XMAX)
    print('DEM2TOPO_RA: yvalid is ', yvalid)
    print('DEM2TOPO_RA: num_patch is ', num_patch)
    print('DEM2TOPO_RA: YMAX is ', YMAX)
    print('DEM2TOPO_RA: SC is ', SC)
    print('DEM2TOPO_RA: PRF is ', PRF)
    print('DEM2TOPO_RA: region is ', region)

    print(' ')
    print('DEM2TOPO_RA: working over ', region, ' ... ...')
    print('DEM2TOPO_RA: look for range sampling rate ... ...')

    # original csh command: set rng_samp_rate = `grep rng_samp_rate $1 | awk 'NR == 1 {printf("%d", $3)}'`
    rng_samp_rate = float(grep_value(sys.argv[1], 'rng_samp_rate', 3))
    print('DEM2TOPO_RA: rng_samp_rate is ', rng_samp_rate)
    print(' ')
    print('DEM2TOPO_RA: set the range of simulation in units of image range pixel size ... ...')
    if rng_samp_rate > 0 and rng_samp_rate < 25000000:
        rng = 1
    elif (rng_samp_rate >= 25000000 and rng_samp_rate < 72000000) or SC == 7:
        rng = 2
    elif rng_samp_rate >= 72000000:
        rng = 4
    else:
        print('DEM2TOPO_RA: ERROR: range sampling rate out of bounds ... ...')

    print('DEM2TOPO_RA: range decimation rng is ', rng)
    if SC == 10 or SC == 11:
        run('gmt grd2xyz --FORMAT_FLOAT_OUT=%lf ' +
            sys.argv[2]+' -s | SAT_llt2rat '+sys.argv[1]+' 1 -bod  > trans.dat')
    else:
        run('gmt grd2xyz --FORMAT_FLOAT_OUT=%lf ' +
            sys.argv[2]+' -s | SAT_llt2rat '+sys.argv[1]+' 0 -bod  > trans.dat')

    print(' ')
    print('DEM2TOPO_RA: use an azimuth spacing of 2 for low PRF data such as S1 TOPS ... ...')

    if PRF < 1000:
        print('DEM2TOPO_RA: if PRF<1000, then ... ...')
        run("gmt gmtconvert trans.dat -o0,1,2 -bi5d -bo3d | gmt blockmedian -R" +
            str(region)+" -I"+str(rng)+"/2 -bi3d -bo3d -r "+str(V)+" > temp.rat ")
        if mode == 0:
            run("gmt surface temp.rat -R"+str(region)+" -I"+str(rng) +
                "/2 -bi3d -T"+str(tension)+" -N1000 -Gpixel.grd -r -Q >& tmp")

            print('DEM2TOPO_RA: ?? is it possible that file tmp is not created? ... ')
            if check_file_report('tmp') is True:
                # Defining RR
                # Original cmd: set RR = `grep Hint tmp | head -1 | awk '{for(i=1;i<=NF;i++) print $i}' | grep /`
                with open('tmp', 'r') as f:
                    # Read the content of the file 'tmp'
                    content = f.read()
                # Split the content into lines
                lines = content.split('\n')

                # Find the first line containing 'Hint'
                hint_line = next(
                    (line for line in lines if 'Hint' in line), None)

                # If a 'Hint' line is found, split it into words and filter those containing '/'
                if hint_line:
                    words = hint_line.split()
                    RR = [word for word in words if '/' in word]
                else:
                    RR = []
            else:
                RR = []
            # Print the result
            print('DEM2TOPO_RA: RR is ', RR)

            if RR == []:  # if RR is empty or unset
                run("gmt surface temp.rat -R"+str(region)+" -I"+str(rng) +
                    "/2 -bi3d -T"+str(tension)+" -N1000 -Gpixel.grd -r "+str(V))
            else:
                run("gmt surface temp.rat "+str(RR)+" -I"+str(rng) +
                    "/2 -bi3d -T"+str(tension)+" -N1000 -Gpixel.grd -r "+str(V))
                run("gmt grdcut pixel.grd -R"+str(region)+" -Gtmp.grd")
                file_shuttle('tmp.grd', 'pixel.grd', 'mv')
        elif mode == 1:
            rng2 = rng*8
            print('DEM2TOPO_RA: mode == 1 and rng2 is ', rng2)
            run("gmt triangulate temp.rat -R"+str(region)+" -I" +
                str(rng)+"/2 -bi3d -Gtopo_ra_tmp.grd -r "+str(V))
            run("gmt blockmean temp.rat -R"+str(region) +
                " -I"+str(rng2)+"/16 -bi3d -bo3d -r > mean.rat")
            run("gmt surface mean.rat -R"+str(region)+" -I" +
                str(rng2)+"/16 -bi3d -T0.1 -N1000 -Gcoarse.grd -r")
            run("gmt grdfill topo_ra_tmp.grd -Agcoarse.grd -Gpixel.grd")
            delete('topo_ra_tmp.grd')
            delete('coarse.grd')
            delete('mean.rat')
    else:
        print('DEM2TOPO_RA: if PRF>=1000, then ... ...')
        run("gmt gmtconvert trans.dat -o0,1,2 -bi5d -bo3d | gmt blockmedian -R" +
            str(region)+" -I"+str(rng)+"/4 -bi3d -bo3d -r "+str(V)+" > temp.rat")
        if mode == 0:
            run("gmt surface temp.rat -R"+str(region)+" -I"+str(rng) +
                "/4 -bi3d -T"+str(tension)+" -N1000 -Gpixel.grd -r -Q >& tmp")

            print('DEM2TOPO_RA: ?? is it possible that file tmp is not created? ... ')
            if check_file_report('tmp') is True:
                # Defining RR
                # Original cmd: set RR = `grep Hint tmp | head -1 | awk '{for(i=1;i<=NF;i++) print $i}' | grep /`
                with open('tmp', 'r') as f:
                    # Read the content of the file 'tmp'
                    content = f.read()
                # Split the content into lines
                lines = content.split('\n')

                # Find the first line containing 'Hint'
                hint_line = next(
                    (line for line in lines if 'Hint' in line), None)

                # If a 'Hint' line is found, split it into words and filter those containing '/'
                if hint_line:
                    words = hint_line.split()
                    RR = [word for word in words if '/' in word]
                else:
                    RR = []
            else:
                RR = []

            # Print the result
            print('DEM2TOPO_RA: RR is ', RR)

            if RR == []:  # if RR is empty or unset
                run("gmt surface temp.rat -R"+str(region)+" -I"+str(rng) +
                    "/4 -bi3d -T"+str(tension)+" -N1000 -Gpixel.grd -r "+str(V))
            else:
                run("gmt surface temp.rat "+str(RR)+" -I"+str(rng) +
                    "/4 -bi3d -T"+str(tension)+" -N1000 -Gpixel.grd -r "+str(V))
                run("gmt grdcut pixel.grd -R"+str(region)+" -Gtmp.grd")
                file_shuttle('tmp.grd', 'pixel.grd', 'mv')
        elif mode == 1:
            rng2 = rng*8
            print('DEM2TOPO_RA: mode == 1 and rng2 is ', rng2)
            run("gmt triangulate temp.rat -R"+str(region)+" -I" +
                str(rng)+"/4 -bi3d -Gtopo_ra_tmp.grd -r "+str(V))
            run("gmt blockmean temp.rat -R"+str(region) +
                " -I"+str(rng2)+"/32 -bi3d -bo3d -r > mean.rat")
            run("gmt surface mean.rat -R"+str(region)+" -I" +
                str(rng2)+"/32 -bi3d -T0.1 -N1000 -Gcoarse.grd -r")
            run("gmt grdfill topo_ra_tmp.grd -Agcoarse.grd -Gpixel.grd")
            delete('topo_ra_tmp.grd')
            delete('coarse.grd')
            delete('mean.rat')

    print(' ')
    print('DEM2TOPO_RA: flip top to bottom for both ascending and descending passes ... ...')
    run('gmt grdmath pixel.grd FLIPUD = topo_ra.grd')

    print(' ')
    print('DEM2TOPO_RA: plotting ... ...')
    run('gmt grd2cpt topo_ra.grd -Cgray '+str(V)+' -Z > topo_ra.cpt')
    run('''gmt grdimage topo_ra.grd '''+str(scale) +
        ''' -P -Ctopo_ra.cpt -Bxaf+lRange -Byaf+l"Reversed Azimuth" -BWSen '''+str(V)+''' -K > topo_ra.ps''')
    run("gmt psscale -Rtopo_ra.grd -J -DJTC+w5i/0.2i+h -Ctopo_ra.cpt -Bxaf -By+lm -O >> topo_ra.ps")
    run('gmt psconvert -Tf -P -A -Z topo_ra.ps')

    print(' ')
    print("DEM2TOPO_RA: Topo range/azimuth map: topo_ra.pdf")

    print(' ')
    print('DEM2TOPO_RA: clean up ... ...')
    delete('pixel.grd')
    delete('temp.grd')
    delete('dem.xyz')
    delete('tmp')
    delete('topo_ra.cpt')

    print(' ')
    print("DEM2TOPO_RA - END ... ...")


def _main_func(description):
    dem2topo_ra()


if __name__ == "__main__":
    _main_func(__doc__)
