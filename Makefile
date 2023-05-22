
###############################################################################
# Conda environments
###############################################################################
conda_export:
	- pip freeze > ./requirements.txt
	- conda env export | cut -f 1 -d '=' | grep -v "prefix" > ./requirements.yml

conda_update:
	- conda update --all -y
	- pip freeze > ./requirements.txt
	- conda env export | cut -f 1 -d '=' | grep -v "prefix" > ./requirements.yml