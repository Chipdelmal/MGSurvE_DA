#!/bin/bash

TRAPS_NUM=8
RLO=8
RHI=15
STEP=2
DIRECTORY="/RAID5/marshallShare/STC/DTA"
###############################################################################
# Auxiliary terminal constants
###############################################################################
LG='\033[1;34m'; RD="\033[1;31m"; NC='\033[0m';
###############################################################################
# Processing loop
###############################################################################
FNAMES=($DIRECTORY/**LND.pkl)
for rep in `seq $RLO 1 $RHI`; do
    echo -e "${RD}* Repetition $rep/$RHI${NC}"
    for ((n=$STEP;n<${#FNAMES[@]};n++)); do
        if (( $(($n % $STEP )) == 0 )); then
            fname="${FNAMES[$n]}"
            echo -e "${LG}\t* Optimizing $fname${NC}"                
            python STC_Optimize.py $(basename "$fname") $TRAPS_NUM $rep
        fi
    done
done
python STC_Compare.py 
