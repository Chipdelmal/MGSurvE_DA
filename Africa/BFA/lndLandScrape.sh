#!/bin/bash

LG='\033[1;34m'
NC='\033[0m'

echo -e "${LG}* Clustering DBSCAN${NC}"
python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Fanka' '13.1490, -1.0171' '2500' '0.0175' '3'
python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Manga' '11.6679, -1.0760' '2000' '0.0225' '3'
python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Niangoloko' '10.2826803, -4.9240132' '4500' '0.02' '5'
python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Nouna' '12.7326, -3.8603' '5000' '0.018' '3'
python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Banfora' '10.6376, -4.7526' '4000' '0.0175' '3'

echo -e "${LG}* Calculating Migration${NC}"
python lndMigrationMatrix.py 'sami' 'Burkina Faso' 'BFA' 'Fanka' '13.1490, -1.0171'
python lndMigrationMatrix.py 'sami' 'Burkina Faso' 'BFA' 'Manga' '11.6679, -1.0760'
python lndMigrationMatrix.py 'sami' 'Burkina Faso' 'BFA' 'Niangoloko' '10.2826803, -4.9240132'
python lndMigrationMatrix.py 'sami' 'Burkina Faso' 'BFA' 'Nouna' '12.7326, -3.8603'
python lndMigrationMatrix.py 'sami' 'Burkina Faso' 'BFA' 'Banfora' '10.6376, -4.7526'



# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Toece' '11.8302, -1.2656' '1000'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Fada NGourma' '12.0627, 0.3695' '2000'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Pissila' '13.1658, -0.8288' '2000'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Douna' '10.6162, -5.1024' '2000'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Dori' '14.0301, -0.0218' '3250'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Bobo-Dioulasso' '11.2004, -4.2951' '4500'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Gorom-Gorom' '14.4446, -0.2345' '5000'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Ouahigouya' '13.5684, -2.4087' '5000'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Koudougou' '12.2521, -2.3555 ' '5000'
# python lndLandWeb.py 'sami' 'Burkina Faso' 'BFA' 'Ouagadougou' '12.3732634, -1.5437957' '15000'
