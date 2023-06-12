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
# cities[0]='Basberike;13.14717,-1.03444;750;0.005;1'
# cities[1]='Reo;12.3201,-2.4753;1000;0.02;1'
# cities[2]='Fanka;13.1490,-1.0171;2500;0.0175;3'
cities[3]='Manga;11.6679,-1.0760;2000;0.023;2'
cities[4]='Nouna;12.7326,-3.8603;2000;0.0225;3'
# cities[5]='Niangoloko;10.2826803,-4.9240132;4500;0.02;5'
# cities[6]='Banfora;10.6376,-4.7526;4000;0.0175;3'
# cities[7]='Koudougou;12.2560,-2.3588;5500;0.0325;'
# cities[8]='Kaya;13.0801,-1.0700;5500;0.02;3'

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
    python lndLandWeb.py $USR 'Burkina Faso' 'BFA'\
        "$name" "$lonlat" "$distance" "$eps" "$neighbors"
    echo -e "${LG}\t* Aggregating...${NC}"
    python lndMigrationMatrix.py $USR 'Burkina Faso' 'BFA'\
        "$name" "$lonlat"
done
