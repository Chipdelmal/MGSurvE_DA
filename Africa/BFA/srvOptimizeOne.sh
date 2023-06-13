#!/bin/bash

USR=$1
GENS=1000
###############################################################################
# Auxiliary terminal constants
###############################################################################
LG='\033[1;34m'
RD="\033[1;31m"
NC='\033[0m'

###############################################################################
# Declare cities to loop through
###############################################################################
declare -a cities
cities[0]='Reo;12.3201,-2.4753;1000;0.02;1'


###############################################################################
# Loop through cities
###############################################################################
for FRACTION in 100 90 80 70 60 50 40 30 20 10
do
    for city in "${cities[@]}"
    do
        # Split elements of array ---------------------------------------------
        IFS=";" read -r -a arr <<< "${city}"
        name="${arr[0]}"
        lonlat="${arr[1]}"
        echo -e "${RD}* Optimizing $name...${NC}"
        for REP in {0..5}
        do
            # Launch scripts --------------------------------------------------
            echo -e "${LG}\t* Processing ($FRACTION:$REP)...${NC}"
            python srvOptimize.py "$USR" "Burkina Faso" "BFA" "$name" "$lonlat"\
                "$GENS" "$FRACTION" "$REP"
        done
    # Launch scripts ----------------------------------------------------------
    echo -e "${LG}\t* Summarizing...${NC}"
done
python srvCompare.py "$USR" "Burkina Faso" "BFA" "$name" "$lonlat"\
    "$GENS" "$FRACTION"
done
