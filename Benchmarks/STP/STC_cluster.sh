#!/bin/bash

###############################################################################
# Auxiliary terminal constants
###############################################################################
LG='\033[1;34m'
RD="\033[1;31m"
NC='\033[0m'
###############################################################################
# Processing loop
###############################################################################
python STC_PreProcessMatrices.py
for i in `seq 200 25 1500`;
do
    echo -e "${LG}* Processing $i${NC}"
    python STC_ClusterAndAggregate.py "$i"
    CLS_NUM=$?
    python STC_GenerateLandscape.py "$CLS_NUM" "10"
done
