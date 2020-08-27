# works-single-view

This is the repository for the first part of the test assigned to me by BMAT. Once started, the system keeps searching for new files inside a configurable directory on the host; whenever a new csv file representing the musical work metadata is created, it is then processed and the information stored in a postgres database.

Here an example of the complete workflow:

![Works Single View Demo](demo/demo.gif)

## Setup

Create a virtual environment and activate it:

``` 
source app/<env_name>/bin/activate 
``` 

Install the dependencies in the requirements.txt file:

Open app/config.py and set your own configuration; you can leave the defaults if you run the postgres image I provided


## Run

Launch it with the command:
``` 
python3 main.py 
``` 

## Answers to questions

1) Describe briefly the matching and reconciling method chosen.

2) We constantly receive metadata from our providers, how would you automatize the process?

The provided solution already offers some degree of automation since the system is always waiting for new files created inside the /data folder. However, a 