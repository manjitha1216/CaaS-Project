from constructs import Construct
from aws_cdk import CfnOutput
from aws_cdk import RemovalPolicy
from aws_cdk import aws_secretsmanager as secretsmanager

from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    #aws_s3 as s3,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_rds as rds,
    aws_ec2 as ec2,
    RemovalPolicy

)

from constructs import Construct

from aws_cdk.aws_sns import (
    Topic  
)

from aws_cdk.aws_sqs import (
    Queue   
)

from aws_cdk.aws_sns_subscriptions import (
    SqsSubscription,
    EmailSubscription
)
from aws_cdk.aws_cloudwatch import (
    Alarm,
    Metric
)

from aws_cdk.aws_cloudwatch_actions import (
    AutoScalingAction,
    SnsAction
)


from aws_cdk import CfnOutput

from aws_cdk.aws_sns import (
    Topic  
)

from aws_cdk.aws_sqs import (
    Queue   
)

from aws_cdk.aws_sns_subscriptions import (
    SqsSubscription,
    EmailSubscription
)

from aws_cdk.aws_logs import (
    LogGroup,
    LogStream

)

class CombinationRdsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Prod_configs = self.node.try_get_context("envs")["Prod"]
        email_address = "nataliya.maroz@accenture.com"     
        
        eks_sns_topic = Topic(self, 'EKS SNS topic',display_name='EKS topic')
        rds_sns_topic = Topic(self, 'RDS SNS topic',display_name='RDS topic')

        eks_sqs_queue = Queue(self, 'EKSSQSQueue')
        rds_sqs_queue = Queue(self, 'RDSSQSQueue')
        
        eks_sns_topic.add_subscription(SqsSubscription(eks_sqs_queue))
        rds_sns_topic.add_subscription(SqsSubscription(rds_sqs_queue))
        
        eks_sns_topic.add_subscription(EmailSubscription(email_address))
        rds_sns_topic.add_subscription(EmailSubscription(email_address))


        #  Create a custome VPC
        custom_vpc = ec2.Vpc(
            self, "customvpc",
            ip_addresses= ec2.IpAddresses.cidr(Prod_configs['vpc_config']['vpc_cidr']),
            max_azs= 2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet", cidr_mask=Prod_configs["vpc_config"]["cidr_mask"], subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnet", cidr_mask=Prod_configs["vpc_config"]["cidr_mask"], subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            ])
        
        #Create an RDS Database
        myDB = rds.DatabaseInstance(self, 
                                    "MyDatabase",
                                    engine= rds.DatabaseInstanceEngine.MYSQL,
                                    vpc= custom_vpc,
                                    vpc_subnets= ec2.SubnetSelection(
                                        #subnet_type= ec2.SubnetType.PUBLIC,
                                        subnet_type= ec2.SubnetType.PRIVATE_ISOLATED,
                                    ),
                                    credentials= rds.Credentials.from_generated_secret("Admin"),
                                    #credentials=rds.Credentials.from_username('useradmin', password='admin'),
                                    #credentials=rds.Credentials.from_username_and_password('user_admin', 'user_password'),
                                    # credentials=rds.Credentials.from_generated_secret("Admin", # You can provide a secret name here
                                    #                   username='admin_user',
                                    #                   password=SecretValue.plain_text('admin_password')),
                                    instance_type= ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
                                                                       ec2.InstanceSize.MICRO),
                                    port= 3306,
                                    allocated_storage= 20,
                                    multi_az= True,
                                    removal_policy= RemovalPolicy.DESTROY,
                                    cloudwatch_logs_exports=['error', 'general', 'slowquery', 'audit'], #comment if db is not deployed
                                    deletion_protection= False,
                                    publicly_accessible= True
                                    )
        
        myDB.connections.allow_from_any_ipv4(
            ec2.Port.tcp(3306),
            description= "Open port for connection"
        )

        
        CfnOutput(self, "RDSInstanceArn", value=myDB.instance_arn)

        rds_cpu_alarm = Alarm(
            self, 'RDSCPUAlarm',
            metric=myDB.metric_cpu_utilization(),
            threshold=40,                   #triggered if the CPU utilization exceeds 90%.
            evaluation_periods=1,           #how many times the line will be crossed until alarm rings
            alarm_name='RDSCPUHighAlarm',
            actions_enabled=True
        )
        
        rds_db_connection_alarm = Alarm(
            self, 'RDSConnectionsEvent',
            metric=myDB.metric_database_connections(),
            threshold=50,                   #triggered if the CPU utilization exceeds 90%.
            evaluation_periods=1,           #how many times the line will be crossed until alarm rings
            alarm_name='RDSConnectionsEvent',
            actions_enabled=True
        )
        
      
        rds_cpu_alarm.add_alarm_action(SnsAction(rds_sns_topic)) #subscribe sns topic to cloudwatch alarm
        rds_db_connection_alarm.add_alarm_action(SnsAction(rds_sns_topic)) #subscribe sns topic to cloudwatch alarm
        
        
        rds_log_group = LogGroup(self, "RDSLogGroup",
                                  log_group_name="/rds/log/group",
                                  removal_policy=RemovalPolicy.DESTROY)

        rds_log_stream = LogStream(self, "RDSLogStream",
                                    log_group=rds_log_group,
                                    log_stream_name="rds_log_stream")
        
        # Step 4: Configure RDS to Use Log Streams (check AWS RDS documentation)

        # Output the CloudWatch Logs Log Group and Log Stream ARNs
        CfnOutput(self, "LogGroupArn", value=rds_log_group.log_group_name)
        CfnOutput(self, "LogStreamName", value=rds_log_stream.log_stream_name)
     
        #S3 Bucket Creation
        #logs_bucket = s3.Bucket(self, "LogsBucket")

        # Create Lambda function to send logs to S3
        logs_lambda_function = lambda_.Function(
            self,
            "LogsLambdaFunction",
            handler="lambda_handler.handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("lambda"),  # Update this path as needed
            environment={
                #"S3_BUCKET_NAME": logs_bucket.bucket_name,
                "LOG_GROUP_NAME": rds_log_group.log_group_name,
                "LOG_STREAM_NAME": rds_log_stream.log_stream_name,
            },
        )

        # Grant Lambda permissions to access CloudWatch Logs and write to S3
        rds_log_group.grant_read(logs_lambda_function)
        #logs_bucket.grant_write(logs_lambda_function)

        # Output the S3 bucket name
        #CfnOutput(self, "LogsBucketName", value=logs_bucket.bucket_name)         
        # eks_cpu_alarm = Alarm(
        #     self, 'EKSCPUAlarm',
        #     metric=,
        #     threshold=90,
        #     evaluation_periods=3,
        #     alarm_name='EKSCPUHighAlarm',
        #     actions_enabled=True
        # )
