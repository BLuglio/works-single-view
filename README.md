# works-single-view

This is the repository for the first part of the test assigned to me by BMAT. 

Once started, the software:
1) processes every csv file inside the data directory
2) waits for new csv files created inside the same directory

Further details regarding the file processing are provided in the answers section.

An example of the workflow:

![Works Single View Demo](demo/demo.gif)

##Dev Dependencies

- Python 3.7.7
- watchdog
- pandas
- numpy
- psycopg2

## Setup

1) Create a virtual environment

``` 
python3 -m venv <env_name> 
``` 

2) Activate it:

``` 
source app/<env_name>/bin/activate 
``` 

3) Install the dependencies in the requirements.txt file:
``` 
pip3 install -r app/requirements.txt 
``` 

4) (Optional) Set your own configuration in the app/config.py file; leave the defaults if you run the postgres image I provided

#### Database

## Run

Launch it with the command:
``` 
python3 main.py 
``` 

## Answers to questions

1) Describe briefly the matching and reconciling method chosen.

    <br/>
    The csv files are read with the pandas library, extracting only the columns 'iswc', 'contributors' and 'title'.
<br>

2) We constantly receive metadata from our providers, how would you automatize the process?
    <br>
    The provided solution already offers some degree of automation since the system is always waiting for new files created inside the /data folder. However, a 