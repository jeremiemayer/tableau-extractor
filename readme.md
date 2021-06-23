## Tableau-extractor
A python based tool for extracting data from the Tableau Server PostgreSQL DB to MSSQL.    

## Usage  
Provided you have configured the relevant PIP packages from requirements.txt, the script can be run directly:  
> python main.py  

Alternatively a docker image has been provided which will build the requirements and execute the script:   
> docker build -t tableau-extractor .   
> docker run -t tableau-extractor    

_note: Initial 'Build' step takes some time due to open issue with the pymssql package_  
