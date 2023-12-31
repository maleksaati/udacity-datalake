import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format
import pyspark.sql.types as t

def create_spark_session():
    """Create Spark Session.

    Args:
        no args.

    Returns:
        spark session object.

    """
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4") \
        .getOrCreate()
    return spark


def process_song_data(spark, input_data, output_data):
    """read (songs, artists) data from s3, and write it to datalake s3 (parquet)

    Args:
        spark: spark session.
        input_data: source of songs data.
        output_data: songs parqet output location.

    Returns:
        no returns.

    """
    # get filepath to song data file
    song_data =  os.path.join(input_data , 'song_data/A/B/C/*.json')

    # read song data file
    df = spark.read.json(song_data)

    # extract columns to create songs table
    songs_table = df.select(['song_id', 'title', 'artist_id', 'year', 'duration'])
    songs_table = songs_table.dropDuplicates(['song_id'])

    # write songs table to parquet files partitioned by year and artist
    songs_table.show(5)
    songs_table.write.mode("overwrite").partitionBy("year", "artist_id").parquet(output_data + 'songs')

    # extract columns to create artists table
    artists_table = df.select('artist_id', 'artist_latitude', 'artist_longitude', 'artist_location', 'artist_name')
    artists_table = artists_table.dropDuplicates(['artist_id'])

    # write artists table to parquet files
    artists_table.show(5)
    artists_table.write.mode('overwrite').parquet(output_data + "artists")


def process_log_data(spark, input_data, output_data):
    """read log data from s3, and extract 3 tables (users, timetable, songsplay), and write output to datalake s3 (parquet)

    Args:
        spark: spark session.
        input_data: source of songs data.
        output_data: songs parqet output location.

    Returns:
        no returns.
    """
        
    # get filepath to log data file
    log_data = os.path.join(input_data, "log_data/*/*/*.json")

    # read log data file
    df = spark.read.json(log_data) 
    
    # filter by actions for song plays
    df = df.filter(df.page == 'NextSong') 

    # extract columns for users table    
    users_table = df.select('firstName', 'lastName', 'gender', 'level', 'userId')
    users_table = users_table.dropDuplicates(['userId'])
    # write users table to parquet files
    users_table.show(5)
    users_table.write.mode('overwrite').parquet(output_data + 'users')
     
    # create timestamp column from original timestamp column
    get_timestamp = udf(lambda x: str(int(int(x)/1000.0)))
    df = df.withColumn('timestamp', get_timestamp(df['ts']))

    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: str(datetime.fromtimestamp(int(x)/1000.0)))
    df = df.withColumn('datetime',get_datetime(df['ts']))


    # extract columns to create time table
    time_table = df.select('ts', 'timestamp','datetime')
    time_table = time_table.withColumn("hour", hour(time_table.datetime))
    time_table = time_table.withColumn("dayofmonth", dayofmonth(time_table.datetime))
    time_table = time_table.withColumn("weekofyear", weekofyear(time_table.datetime))
    time_table = time_table.withColumn("month", month(time_table.datetime))
    time_table = time_table.withColumn("year", year(time_table.datetime))

    
    # write time table to parquet files partitioned by year and month
    time_table.show(5)
    time_table.write.partitionBy('year','month').parquet(os.path.join(output_data,'timetable'),'overwrite')


    # read in song data to use for songplays table
    song_df = spark.read.parquet(output_data + "songs")

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = df.join(song_df, df.song == song_df.title, how='inner')
    songplays_table.show(5)
    songplays_table = songplays_table.select(
                                col("datetime").alias("start_time"),col("userId").alias("user_id"),"level","song_id","artist_id", \
                                col("sessionId").alias("session_id"), col("location"), col("userAgent").alias("user_agent"), year('datetime').alias('year'),
                                        month('datetime').alias('month'))

    # write songplays table to parquet files partitioned by year and month
    songplays_table.show(5)
    songplays_table.write.parquet(output_data + "songplays", mode="overwrite", partitionBy=["year","month"])


def main():
    config = configparser.ConfigParser()
    config.read('dl.cfg')



    os.environ['AWS_ACCESS_KEY_ID']=config['AWS']['AWS_ACCESS_KEY_ID']
    os.environ['AWS_SECRET_ACCESS_KEY']=config['AWS']['AWS_SECRET_ACCESS_KEY']

    spark = create_spark_session()

    input_data = "s3a://udacity-dend/"
    output_data = "s3a//songsdatalake10/"
    
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)




if __name__ == "__main__":
    main()