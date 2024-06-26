#!/bin/csh -f
#       $Id$
#
#  April 21, 1999 - David T. Sandwell
#  May 23, 2017 - Anders Hogrelius, updated to fully support Envisat formatted SLC data
#
#  Script to calculate a table of parameters from master and
#  aligned PRM files.
#
unset noclobber
#
#  Modified by M.Wei to add ALOS function, 9/27/06
#
 if ($#argv < 2) then
  echo " "
  echo "Usage: baseline_table master.PRM aligned.PRM [GMT] "
  echo "               [GMT] creates table for pstext"
  echo " "
  echo " Output:"
  echo " sat_orb aligned_time aligned_days(1992ERS,2006ALOS) Bpl Bperp xshift yshift"
  echo " "
  exit 1
 endif
#
# Detect if we are dealing with Envisat formatted ERS SLC data without using SC_identity
# Kludge to get correct SC_identity functionality until we can correct the values throughout the chain
#
set ERSSLC = `echo $1|cut -c1-10`

#
#  get the time information from the master
#
 set MT0 = `grep SC_clock_start $1 | awk '{print $3}'`
 set MTF = `grep SC_clock_stop $1 | awk '{print $3}'`
 set MSC = `grep SC_identity $1 | awk '{print $3}'`
#
#  get the time information from the alignedr
#
 set ST0 = `grep SC_clock_start $2 | awk '{print $3}'`
 set STF = `grep SC_clock_stop $2 | awk '{print $3}'`
 set SSC = `grep SC_identity $2 | awk '{print $3}'`

# 
# convert the start time to days since 1992
#
 @ T0  = `grep SC_clock_start $2 | awk '{print $3}' | awk -F"." '{print $1}'`
 @ DAY = $T0 % 1000
#
if ($SSC == 1 || $SSC == 2) then
 SAT_baseline $1 $2 > temp
 set t0 = `echo "" | awk '{print mktime("1992 01 01 00 00 00")}'`
 @ YR = $T0  / 1000
 set t1 = `echo "" | awk '{print mktime("'$YR' 01 01 00 00 00")}'`
 set YDAY = `echo $t0 $t1 | awk '{printf("%d",int(($2-$1)/86400.0+0.5)+'$DAY'-1)}'`
else if ($SSC == 4 || $SSC == 6) then
 SAT_baseline $1 $2 > temp
 set t0 = `echo "" | awk '{print mktime("1992 01 01 00 00 00")}'`
 @ YR = $T0  / 1000
 set t1 = `echo "" | awk '{print mktime("'$YR' 01 01 00 00 00")}'`
 set YDAY = `echo $t0 $t1 | awk '{printf("%d",int(($2-$1)/86400.0+0.5)+'$DAY'-1)}'`
else if ($SSC == 5) then
 SAT_baseline $1 $2 > temp
 @ YR1 = $T0 / 1000
 if ($YR1 < 2013) then
  set t0 = `echo "" | awk '{print mktime("2006 01 01 00 00 00")}'`
 else
  set t0 = `echo "" | awk '{print mktime("2014 01 01 00 00 00")}'`
 endif
 @ YR = $T0  / 1000
 set t1 = `echo "" | awk '{print mktime("'$YR' 01 01 00 00 00")}'`
 set YDAY = `echo $t0 $t1 | awk '{printf("%d",int(($2-$1)/86400.0+0.5)+'$DAY'-1)}'`
else
 SAT_baseline $1 $2 > temp
 if ($SSC == 7 || $SSC == 8) then
  set t0 = `echo "" | awk '{print mktime("2007 01 01 00 00 00")}'`
 else if ($SSC == 9) then
  set t0 = `echo "" | awk '{print mktime("2008 01 01 00 00 00")}'`
 else if ($SSC == 10) then
  set t0 = `echo "" | awk '{print mktime("2014 01 01 00 00 00")}'`
 else
  set t0 = `echo "" | awk '{print mktime("2020 01 01 00 00 00")}'`
 endif
 @ YR = $T0  / 1000
 set t1 = `echo "" | awk '{print mktime("'$YR' 01 01 00 00 00")}'`
 set YDAY = `echo $t0 $t1 | awk '{printf("%d",int(($2-$1)/86400.0+0.5)+'$DAY')}'`
endif
#
#  get the needed parameters from temp
#
 set BPL = `grep B_parallel temp | awk '{print $3}'`
 set BPR = `grep B_perpendicular temp | awk '{print $3}'`
 set XS  = `grep xshift temp | awk '{print $3}'`
 set YS  = `grep yshift temp | awk '{print $3}'`
 set NM  = `grep SC_identity $2 | awk '{print $3}'`
if ($SSC == 5) then
  if ($YR1 < 2013) then
     set ORB = `grep input_file $2 | awk '{print $3}' | awk '{print substr($1,14,5)}'` 
  else
     if ($#argv < 3) then
       set ORB = `grep input_file $2 | awk '{print $3}' | awk -F"." '{print $1".1__D"}'`
     else
       set ORB = `grep input_file $2 | awk '{print $3}' | awk '{print substr($1,13,5)}'` 
     endif
  endif
else if ($SSC == 6 || $ERSSLC == "SAR_IMS_1P") then
 set ORB = `grep input_file $2 | awk '{print $3}' | cut -c50-54`
else if ($SSC == 4) then
 set ORB = `grep input_file $2 | awk '{print $3}' | cut -c17-21`
else if ($SSC == 1 || $SSC == 2) then
 set ORB = `grep input_file $2 | awk '{print $3}' | cut -c1-8`
else 
 set ORB = `grep input_file $2 | awk '{print $3}' | awk -F"." '{print $1}'`
endif
#

 if ($#argv < 3) then
    echo $ORB $ST0 $YDAY $BPL $BPR $XS $YS 
 else 
    echo $YDAY $BPR '8' '0.' '0' '5' $ORB
 endif
#
# clean up
#
  rm temp
