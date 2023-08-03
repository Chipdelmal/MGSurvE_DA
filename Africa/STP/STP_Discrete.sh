#!/bin/bash

WHT='\033[0;37m'  
RED='\033[0;31m'
NCL='\033[0m'

for trps in 25 30; do
    printf "${WHT}* Solving for ${trps} traps...${NCL}\n" 
    for id in {1..5}; do
        printf "\t${RED}* Iteration ${id}...${NCL}\n" 
        for m in "man"; do 
            python STP_Discrete.py "$trps" "$id"
        done
    done
done
