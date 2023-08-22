#!/bin/bash

TRAPS_NUM=10
RLO=1
RHI=4
STEP=50
DIRECTORY="/RAID5/marshallShare/STC/DTA"
###############################################################################
# Auxiliary terminal constants
###############################################################################
LG='\033[1;34m'; RD="\033[1;31m"; NC='\033[0m';
###############################################################################
# Processing loop
###############################################################################
FNAMES=($DIRECTORY/**LND.pkl)
for ((n=$STEP;n<${#FNAMES[@]};n++)); do
    if (( $(($n % $STEP )) == 0 )); then
        fname="${FNAMES[$n]}"
        echo -e "${LG}* Optimizing $fname${NC}"
        for rep in `seq $RLO 1 $RHI`; do
            echo -e "${RD}\t* Repetition $rep/$RHI${NC}"
            python STC_Optimize.py $(basename "$fname") $TRAPS_NUM $rep
        done
    fi
done