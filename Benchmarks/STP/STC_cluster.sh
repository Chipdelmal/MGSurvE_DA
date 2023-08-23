#!/bin/bash

JOBS=32
TRAPS_NUM=8
###############################################################################
# Auxiliary terminal constants
###############################################################################
LG='\033[1;34m'; RD="\033[1;31m"; NC='\033[0m';
###############################################################################
# Processing loop
#   https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop
###############################################################################
python STC_PreProcessMatrices.py
(
for eps in `seq 200 1 1500`; do
    ((i=i%JOBS)); ((i++==0)) && wait
    echo -e "${LG}* Processing $eps${NC}"
    CLS_NUM=$(python STC_ClusterAndAggregate.py "$eps")
    python STC_GenerateLandscape.py "$CLS_NUM" "$TRAPS_NUM" &
done
)
