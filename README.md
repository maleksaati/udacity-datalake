## Project: Data Lake

#### Introduction

A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

the aim of this project is to build an ETL pipeline for a data lake hosted on S3. 
1- load data from S3.
2- process the data into analytics tables using Spark.
3- and load them back into S3. 

## Project Datasets

You'll be working with two datasets that reside in S3. Here are the S3 links for each:

-   Song data:  `s3://udacity-dend/song_data`
-   Log data:  `s3://udacity-dend/log_data`

## Run Instructions:

1.  Setup an AWS EMR that has one master and n nodes.
2. Copy etp.py and dl.cfg into EMR master
3. submit etl.py
```
    /usr/bin/spark-submit --master yarn ./etl.py
```