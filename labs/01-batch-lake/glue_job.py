import sys
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME", "INPUT_PATH", "OUTPUT_PATH"])
context = GlueContext(SparkContext.getOrCreate())
job = Job(context)
job.init(args["JOB_NAME"], args)
frame = context.spark_session.read.option("header", True).csv(args["INPUT_PATH"])
result = (frame.withColumn("email", F.lower(F.trim("email")))
          .withColumn("order_date", F.to_date("order_date"))
          .withColumn("amount", F.col("amount").cast("decimal(18,2)"))
          .dropDuplicates(["order_id"]))
result.write.mode("overwrite").partitionBy("order_date").parquet(args["OUTPUT_PATH"])
job.commit()

