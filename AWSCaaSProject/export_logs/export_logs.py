# import boto3
# import os
# import datetime

# GROUP_NAME = "/aws/rds/instance/awscaasprojectstack-mydatabase1e2517db-ljeqsyoosnfl/error"
# DESTINATION_BUCKET = "logsbucketmanjitha"
# PREFIX = "Cloudwatchlogstest"
# NDAYS = 1
# nDays = int(NDAYS)


# currentTime = datetime.datetime.now()
# StartDate = currentTime - datetime.timedelta(days=nDays)
# EndDate = currentTime - datetime.timedelta(days=nDays - 1)


# fromDate = int(StartDate.timestamp() * 1000)
# toDate = int(EndDate.timestamp() * 1000)

# BUCKET_PREFIX = os.path.join(PREFIX, StartDate.strftime('%Y{0}%m{0}%d').format(os.path.sep))


# def lambda_handler(event, context):
#     client = boto3.client('logs')
#     response = client.create_export_task(
#          logGroupName=GROUP_NAME,
#          fromTime=fromDate,
#          to=toDate,
#          destination=DESTINATION_BUCKET,
#          destinationPrefix=BUCKET_PREFIX
#         )
#     print(response)

# import boto3
# import os
# import gzip
# from io import BytesIO
# from aws_cdk import Duration
# def handler(event, context):
#     log_group_name = os.environ['LOG_GROUP_NAME']
#     s3_bucket_name = os.environ['S3_BUCKET_NAME']
#     s3_key_prefix = os.environ['S3_KEY_PREFIX']
#     client = boto3.client('logs')
#     s3_client = boto3.client('s3')
#     # Retrieve the log events using CloudWatch Logs Insights query
#     query = 'fields @timestamp, @message | sort @timestamp desc | limit 5'
#     response = client.start_query(
#         logGroupName=log_group_name,
#         startTime=int((context.aws_request_initiator['time'] - Duration.minutes(2)).timestamp()),
#         endTime=int(context.aws_request_initiator['time'].timestamp()),
#         queryString=query,
#     )
#     query_id = response['queryId']
#     # Wait for the query to complete
#     while True:
#         query_status = client.get_query_results(queryId=query_id)
#         if query_status['status'] == 'Complete':
#             break
#     # Extract and export log events to S3
#     results = query_status['results']
#     log_data = '\n'.join(['\t'.join([field['value'] for field in row]) for row in results])
#     s3_key = f'{s3_key_prefix}{context.aws_request_initiator["time"].isoformat()}.log.gz'
#     with BytesIO() as gzipped_data:
#         with gzip.GzipFile(fileobj=gzipped_data, mode='w') as gz:
#             gz.write(log_data.encode('utf-8'))
#         gzipped_data.seek(0)
#         s3_client.put_object(Body=gzipped_data, Bucket=s3_bucket_name, Key=s3_key)