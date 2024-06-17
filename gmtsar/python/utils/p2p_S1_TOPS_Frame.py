#! /usr/bin/env python3
"""
p2p_S1_TOPS_Frame is part of GMTSAR. 
Process Sentinel-1A TOPS data; automatically process a single frame of interferogram. 
"""

import sys
import os
import glob
import subprocess
import multiprocessing
from gmtsar_lib import *




def getFilenameWithPolXml(searchDir, searchStr1, pol, fileFormat):
    fileList = os.listdir(searchDir+'/annotation')
    for fileName in fileList:
        if (searchStr1 in fileName) and (pol in fileName) and (fileFormat in fileName):
            selectedFile = fileName[:-4]
            print(selectedFile)
    return selectedFile


def linkFiles(subswathId, masterSafe, masterEof, alignedSafe, alignedEof, fmList, fsList):
    rootDir = 'F'+str(subswathId+1)
    run('mkdir -p '+rootDir)  # FIXME: use os.mkdir
    run('mkdir -p '+rootDir+'/raw')
    run('mkdir -p '+rootDir+'/topo')
    os.chdir(rootDir)
    os.system('pwd')
    print('P2P_S1_TOPS_FRAME: Linking files for Subswath '+str(subswathId))
    os.chdir('topo')
    os.system('pwd')
    file_shuttle('../../topo/dem.grd', '.', 'link')
    os.chdir('../raw')
    os.system('pwd')
    file_shuttle('../../topo/dem.grd', '.', 'link')
    file_shuttle('../../raw/'+masterSafe+'/annotation/' +
                 fmList[subswathId]+'.xml', '.', 'link')
    file_shuttle('../../raw/'+masterSafe+'/measurement/' +
                 fmList[subswathId]+'.tiff', '.', 'link')
    file_shuttle('../../raw/'+masterEof, './' +
                 fmList[subswathId]+'.EOF', 'link')
    file_shuttle('../../raw/'+alignedSafe+'/annotation/' +
                 fsList[subswathId]+'.xml', '.', 'link')
    file_shuttle('../../raw/'+alignedSafe+'/measurement/' +
                 fsList[subswathId]+'.tiff', '.', 'link')
    file_shuttle('../../raw/'+alignedEof, './' +
                 fsList[subswathId]+'.EOF', 'link')
    os.chdir('../..')


def processingF1F2F3(seq, fmList, fsList):
    if seq == 0:
        for subswathId in range(3):
            fm = fmList[subswathId]
            fs = fsList[subswathId]
            processOneSubswath(subswathId, fm, fs)
    elif seq == 1:
        os.environ['OMP_NUM_THREADS'] = '3'
        subswathIdList = [0, 1, 2]
        with multiprocessing.Pool(processes=3) as pool:
            pool.starmap(processOneSubswath, zip(
                subswathIdList, fmList, fsList))


def processOneSubswath(subswathId, fm, fs):
    folderName = 'F'+str(subswathId+1)
    print('Processing subswath ' + folderName)
    file_shuttle('config.py', folderName+'/config.py', 'cp')
    os.chdir(folderName)
    os.system('pwd')
    cmd = ['p2p_processing.py', 'S1_TOPS', fm, fs, 'config.py']
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    with open('output.log.txt', 'w') as f:
        f.write(result.stdout)
    os.chdir('..')
    os.system('pwd')


def getPathPrmFileName(subswathId):
    intfDir = '../F'+str(subswathId+1)+'/intf'
    return glob.glob(intfDir+'/*')[0]


def shortenPrmFileName(fn):
    return 'S1_'+fn[15:15+8]+'_'+fn[24:24+6]+'_F'+fn[6:7]+'.PRM'


def mergeUnwrapGeocodeTops(correct_iono, det_stitch):  # TODO: encorperate into the wrapper
    if correct_iono != 0:
        print('not available yet for correct_iono!=0')
    else:
        file_shuttle('../config.py', '.', 'cp')
        merge_unwrap_geocode_tops_csh('tmp.filelist config.py '+str(det_stitch))


def p2pS1TopsFrame():
    """
    Usage: p2p_S1_TOPS_Frame.csh Master.SAFE Master.EOF Aligned.SAFE Aligned.EOF config.s1a.txt polarization parallel')

    Example: p2p_S1_TOPS_Frame.csh S1A_IW_SLC__1SDV_20150607T014936_20150607T015003_006261_00832E_3626.SAFE S1A_OPER_AUX_POEORB_OPOD_20150615T155109_V20150525T225944_20150527T005944.EOF S1A_IW_SLC__1SSV_20150526T014935_20150526T015002_006086_007E23_679A.SAFE S1A_OPER_AUX_POEORB_OPOD_20150627T155155_V20150606T225944_20150608T005944.EOF config.s1a.txt vv 1')
    Place the .SAFE file in the raw folder, DEM in the topo folder.')
    During processing, F1, F2, F3 and merge folder will be generated.')
    Final results will be placed in the merge folder, with phase.')
    corr [unwrapped phase]')
    polarization = vv vh hh or hv')
    parallel = 0-sequential / 1-parallel')
    Reference: Xu, X., Sandwell, D.T., Tymofyeyeva, E., González-Ortega, A. and Tong, X., ')
       2017. Tectonic and Anthropogenic Deformation at the Cerro Prieto Geothermal ')
       Step-Over Revealed by Sentinel-1A InSAR. IEEE Transactions on Geoscience and Remote Sensing.')
    """
    config = init_config()  # FIXME: Figure out where these variables are and which satelite they are for
    correct_iono = config['make_filter_intfs']['correct_iono']
    det_stitch = config['misc']['S1_TOPS']['det_stitch']
    iono_filt_rng = config['iono_filt_rng']
    iono_filt_azi = config['iono_filt_azi']

    def merge(skip_master, fmList, fsList):
        if skip_master != 2:
            run('mkdir -p merge')  # FIXME: Use os.mkdir
            os.chdir('merge')
            file_shuttle('../topo/dem.grd', '.', 'link')
            file_shuttle('../config.py', '.', 'cp')
            run("ln -s ../F1/intf/*/gauss* .")  # FIXME: find os command for this
            if check_file_report('tmp.filelist') is True:
                delete('tmp.filelist')

            pth = [getPathPrmFileName(subswathId=0),
                getPathPrmFileName(subswathId=1),
                getPathPrmFileName(subswathId=2)]
            prm1m = [shortenPrmFileName(fmList[0]),
                    shortenPrmFileName(fmList[1]),
                    shortenPrmFileName(fmList[2])]
            prm1s = [shortenPrmFileName(fsList[0]),
                    shortenPrmFileName(fsList[1]),
                    shortenPrmFileName(fsList[2])]

            with open('tmp.filelist', 'w') as f:
                for i in range(3):
                    f.write(pth[i]+'/:'+prm1m[i]+':'+prm1s[i]+'\n')

            sys.path.insert(0, os.getcwd())
            mergeUnwrapGeocodeTops(correct_iono, det_stitch)
        else:
            print('P2P_S1_TOPS_FRAME: No radar product is produced as only master image is processed.')
    print('P2P_S1_TOPS_FRAME - START')

    numOfArg = len(sys.argv)
    print('P2P_S1_TOPS_FRAME: arguments are ', sys.argv)
    print('P2P_S1_TOPS_FRAME: num of arguments are ', numOfArg)
    if numOfArg != 8:
        print('P2P_S1_TOPS_FRAME: Wrong # of input arguments; # should be 7 ... ...')
        print(p2pS1TopsFrame.__doc__)

    masterSafe = sys.argv[1]  # FIXME: These should be function parameters instead of command line arguments
    masterEof = sys.argv[2]
    alignedSafe = sys.argv[3]
    alignedEof = sys.argv[4]
    pol = sys.argv[6]
    seq = int(sys.argv[7])


    fmList = [getFilenameWithPolXml('raw/'+masterSafe, 'iw1', pol, '.xml'),
              getFilenameWithPolXml('raw/'+masterSafe, 'iw2', pol, '.xml'),
              getFilenameWithPolXml('raw/'+masterSafe, 'iw3', pol, '.xml')]
    fsList = [getFilenameWithPolXml('raw/'+alignedSafe, 'iw1', pol, '.xml'),
              getFilenameWithPolXml('raw/'+alignedSafe, 'iw2', pol, '.xml'),
              getFilenameWithPolXml('raw/'+alignedSafe, 'iw3', pol, '.xml')]
    print('P2P_S1_TOPS_FRAME: fmList is ', fmList)
    print('P2P_S1_TOPS_FRAME: fsList is ', fsList)

    skip_master = grep_value('config.py', 'skip_master', 3)

    linkFiles(0, masterSafe, masterEof, alignedSafe,
              alignedEof, fmList, fsList)
    linkFiles(1, masterSafe, masterEof, alignedSafe,
              alignedEof, fmList, fsList)
    linkFiles(2, masterSafe, masterEof, alignedSafe,
              alignedEof, fmList, fsList)

    processingF1F2F3(seq, fmList, fsList)

    merge(skip_master, fmList, fsList)

    print('P2P_S1_TOPS_FRAME - END')


def _main_func(description):
    p2pS1TopsFrame()


if __name__ == '__main__':  # FIXME: Change to allow imports and non-script use
    _main_func(__doc__)
