#!/bin/bash

USR=$1

LG='\033[1;34m'
NC='\033[0m'

echo -e "${LG}* Clustering DBSCAN${NC}"
python lndLandWeb.py $USR 'Burkina Faso' 'BFA' 'Fanka' '13.1490, -1.0171' '2500' '0.0175' '3'
python lndLandWeb.py $USR 'Burkina Faso' 'BFA' 'Manga' '11.6679, -1.0760' '2000' '0.0225' '3'
python lndLandWeb.py $USR 'Burkina Faso' 'BFA' 'Niangoloko' '10.2826803, -4.9240132' '4500' '0.02' '5'
python lndLandWeb.py $USR 'Burkina Faso' 'BFA' 'Nouna' '12.7326, -3.8603' '5000' '0.018' '3'
python lndLandWeb.py $USR 'Burkina Faso' 'BFA' 'Banfora' '10.6376, -4.7526' '4000' '0.0175' '3'

echo -e "${LG}* Calculating Migration${NC}"
python lndMigrationMatrix.py $USR 'Burkina Faso' 'BFA' 'Fanka' '13.1490, -1.0171'
python lndMigrationMatrix.py $USR 'Burkina Faso' 'BFA' 'Manga' '11.6679, -1.0760'
python lndMigrationMatrix.py $USR 'Burkina Faso' 'BFA' 'Niangoloko' '10.2826803, -4.9240132'
python lndMigrationMatrix.py $USR 'Burkina Faso' 'BFA' 'Nouna' '12.7326, -3.8603'
python lndMigrationMatrix.py $USR 'Burkina Faso' 'BFA' 'Banfora' '10.6376, -4.7526'
