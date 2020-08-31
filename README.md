# works-single-view

## Table of Contents

- [Description](#description)
- [Dependencies](#dependencies)
- [Setup](#setup)
- [Usage](#usage)
- [Questions](#questions)

## Description

This is the repository for the first part of the test assigned to me by BMAT. 

Once started, the software:
1) processes every csv file already inside the data directory
2) waits for new csv files created inside the same directory

Further details regarding the file processing are provided in the answers section. To start the matching and reconciling activity just drag and drop the appropriate csv metadata file inside the data directory; here an example of the workflow:

![Works Single View Demo](demo/demo.gif)


The logic is divided among four main objects with different responsibilities:

- `Watcher`: its task is to wait for new events inside a configurable folder on the host filesystem and then pass them to the handler object that it instantiates (in this case a file system handler)  
- `FileSystemHandler`: concrete handler that responds to csv creation events only. If the new file passes the check, it is then passed to the processor object for the matching and reconcile task
- `Processor`: object responsible for the matching and reconcile task from a csv formatted as the provided metadata file `works_metadata.csv`
- `DB`: utility class that handles the interaction with the database

### Table structure

The main (and only) table is called `works_single_view` and it contains the following columns:

- ID: primary key, integer   
- ISWC: character varying(20), I set an  `unique` constraint on it
- CONTRIBUTORS: array of text
- TITLE: text
- CREATED_AT: timestamp without timezone
- MODIFIED_AT: timestamp without timezone

## Dependencies

- Python 3.7.7
- Pip >= 19.2.3
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
pip install -r app/requirements.txt 
``` 

4) Set the necessary configuration in the app/config.py file:
```
src_path = 'absolute/path/to/app/data'
DB_HOST = 'localhost' 
DB_PORT = 5432
DB_NAME = 'bmat'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
```
`src_path` is the folder used by the watcher to register new events, i.e the folder in which the csv files are dropped. The other variables are used to connect to the database.

### Database
Here I provide the SQL instruction to create the table works_single_view used by the software; use it in the SQL tool in pgAdmin or as a query statement in pgsql:
``` 
CREATE TABLE public.works_single_view
(
    id serial,
    iswc character varying(20) COLLATE pg_catalog."default",
    contributors text[] COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default",
    created_at timestamp without time zone DEFAULT now(),
    modified_at timestamp without time zone DEFAULT now(),
    CONSTRAINT works_single_view_pkey PRIMARY KEY (id),
    CONSTRAINT iswc UNIQUE (iswc)
)
``` 

## Run

Launch it with the command:
``` 
python3 main.py 
``` 
A logging message should notify that the system is watching the configured folder.
## Questions

1) <b>Describe briefly the matching and reconciling method chosen.</b>
I considered the iswc code the most important piece of information contained inside the csv file, since it is an international standard and identifies each musical work uniquely. So I decided to discard the `sources` and `id` columns because not relevant to the data structure of the musical work. The columns `title` and `contributors` are considered instead, but their value can be null. The matching and reconciling method is described below:
    1) The csv file is read with the pandas library, extracting the columns containing the 'iswc', 'contributors' and 'title' values into the list `data`; this list contains all values as they are in the original csv file
    2) the iswc without duplicates and null values are stored in the `iswcs` list
    3) for each iswc inside the `iswcs` list, the following steps are executed:
        1) the list containing the indices of all its occurrences inside the `data` list is obtained
        2) using the list computed at 1), the string containing all the related contributors are extracted from `data`, separated as single strings and then added to a set; this set will contain the complete list of the contributors for the current musical work without duplicates (it will contain an empty string if no contributors are found)
        3) the title is extracted scanning all the occurrences of `data` and taking the first non-empty value that is found (or empty string if no one exists)
        4) an `INSERT` query is appended to the `query` string, using the values taken from the preceeding steps
    4) all the extracted data is inserted in the database as a single transaction using the `queries` string composed by the iteration of point 3) <br/>
- Note 1: in case of same contributors with different names (as in the case of 'Edward Sheeran' and 'Edward Christopher Sheeran'), the corresponding entry will contain them both
- Note 2: I decided to write an unpsert query that updates the contributors of the record if the entry with the given iswc already exists instead of discarding it 
<br>

2) <b>We constantly receive metadata from our providers, how would you automatize the process?</b>
    <br>
    The provided solution can be considered already automatic as long as everything runs locally, i.e. on a single machine. However, given that the providers are external actors and can have different requirements, the things that I would do to turn the current implementation into a reliable automatic solution are the following: 
    
    1) I would discuss with the provider the possibility to use a file sharing service (like Google Drive, Dropbox or S3 on AWS) or an FTP server
    2) instead of placing the file containing the metadata on a local folder, the provider would upload it on such a service (let's call it shared folder) following a given time schedule, for example each day at the same hour. 
    3) I would modify the observation part of my solution, changing from a file system based polling to a set of authorized API requests to the shared folder; in particular, the software would: 
        1) list all csv files contained in the shared folder
        2) download and process only the files created in the last 24 hours. The parameters necessary to access the shared folder (for example all the endpoints and the secrets) would be added to the settings file inside the application
    4) I would sync the activation of the metadata ingestion according to the time schedule set by the provider; the way in which I would realize it would be different if the software runs inside a serverless environment, like AWS Lamba, or inside a dedicated server
