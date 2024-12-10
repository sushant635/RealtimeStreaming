import pyspark
from pyspark.sql import SparkSession 
from pyspark.sql.types import StructType,StructField,StringType,FloatType
from pyspark.sql.functions import col,from_json,udf,when
from config.config import config
import time
import openai
from transformers import pipeline



def sentiment_analysis(comment: str) -> str:
    if comment:
        print(comment)
        
        # Load pre-trained sentiment analysis pipeline
        classifier = pipeline("sentiment-analysis")
        
        # Classify sentiment
        result = classifier(comment)
        label = result[0]['label']

        # Map labels to POSITIVE, NEGATIVE, or NEUTRAL
        if "positive" in label.lower():
            sentiment = "POSITIVE"
        elif "negative" in label.lower():
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        
        return sentiment
    return "Empty"




def start_streaming(spark):
    topic = 'customers_review'  
    while True:
        try:
            stream_df = (spark.readStream.format("socket")
                        .option("host", "0.0.0.0")
                            .option("port", 9999)
                            .load()
                        )
            schema = StructType([
                StructField('review_id',StringType()),
                StructField('user_id',StringType()),
                StructField('business_id',StringType()),
                StructField('stars',FloatType()),
                StructField('date',StringType()),
                StructField('text',StringType())
            ])
            stream_df = stream_df.select(from_json(col('value'),schema).alias('data')).select(("data.*"))
            # query = stream_df.writeStream.outputMode("append").format('console').options(truncate=False).start()
            # query = stream_df.writeStream.outputMode("append").format("console").start()

            sentiment_analysis_udf = udf(sentiment_analysis,StringType())

            stream_df = stream_df.withColumn('feedback',when(col('text').isNotNull(),sentiment_analysis_udf(col('text')))
                                             .otherwise(None)
                                             )

            

            kafka_df = stream_df.selectExpr("CAST(review_id AS STRING) as key","to_json(struct(*)) AS value")

            query = (kafka_df.writeStream
                        .format('kafka')
                        .option("kafka.bootstrap.servers",config['kafka']['bootstrap.servers'])
                        .option("kafka.security.protocol",config['kafka']['security.protocol'])
                        .option("kafka.sasl.mechanism",config['kafka']['sasl.mechanisms'])
                        .option('kafka.sasl.jaas.config',
                                'org.apache.kafka.common.security.plain.PlainLoginModule required username="{username}"'
                                'password="{password}";'.format(
                                    username = config['kafka']['sasl.username'],
                                    password =config['kafka']['sasl.password']
                                ))
                        .option('checkpointLocation','/tmp/checkpoint')
                        .option('topic',topic)
                        .start()
                        .awaitTermination()

            )

            # query.awaitTermination()


        except Exception as e:
            print(f'Exception encounterd :{e}. Retrying in 10 seconds')
            time.sleep(10)



if __name__ == "__main__":
    spark_conn = SparkSession.builder.appName("SocketstreamConsume").getOrCreate()

    start_streaming(spark_conn)
