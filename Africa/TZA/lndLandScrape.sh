#!/bin/bash

USR=$1
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
# cities[0]='Kayense;-2.4209,32.97015;4250;0.025;3'
# cities[1]='Mulema;-1.8468,31.6596;3000;0.025;3'
# cities[2]='Musoma;-1.5156,33.8017;5000;0.03;3'
# cities[3]='Kisesa;-2.5563,33.0470;2750;0;3'
# cities[4]='Muganza;-2.3730,31.7378;5000;0;3'
# cities[5]='Arusha;-3.36897,36.68616;3000;0;3'
# cities[5]='Bukoba;-1.3431,31.8147;3000;0.025;3'
cities[0]='Mwanza;-2.5195,32.9046;2250;0.015;3'
###############################################################################
# Loop through cities
###############################################################################
for city in "${cities[@]}"
do
    # Split elements of array -------------------------------------------------
    IFS=";" read -r -a arr <<< "${city}"
    name="${arr[0]}"
    lonlat="${arr[1]}"
    distance="${arr[2]}"
    eps="${arr[3]}"
    neighbors="${arr[4]}"
    echo -e "${RD}* Scraping $name...${NC}"
    # Launch scripts ----------------------------------------------------------
    echo -e "${LG}\t* Downloading and Clustering...${NC}"
    python lndLandWeb.py $USR 'Tanzania' 'TZA'\
        "$name" "$lonlat" "$distance" "$eps" "$neighbors"
    echo -e "${LG}\t* Aggregating...${NC}"
    python lndMigrationMatrix.py $USR 'Tanzania' 'TZA'\
        "$name" "$lonlat"
done
