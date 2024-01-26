from constructs import Construct
from aws_cdk import CfnOutput
from aws_cdk import RemovalPolicy

from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    #aws_sns as sns,
    #aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources,
    aws_rds as rds,
    aws_ec2 as ec2,
    RemovalPolicy

)

class CdktestStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        Prod_configs = self.node.try_get_context("envs")["Prod"]
        bucket = s3.Bucket(self, "mybucket")
        
        #crate queue
        queue = sqs.Queue(
            self, "SQSLambdaQueue",
            visibility_timeout=Duration.seconds(300),
        )

        #create our lambda function
        sqs_lambda = lambda_.Function(self, "SQSLambda",
                                      handler='lambda_handler.handler',
                                      runtime=lambda_.Runtime.PYTHON_3_10,
                                      code=lambda_.Code.from_asset('lambda'))
        # Create our event source
        sqs_event_source = lambda_event_sources.SqsEventSource(queue)

        #Add SQS event source to Lambda
        sqs_lambda.add_event_source(sqs_event_source)


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
                                        subnet_type= ec2.SubnetType.PUBLIC,
                                    ),
                                    credentials= rds.Credentials.from_generated_secret("Admin"),
                                    instance_type= ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
                                                                       ec2.InstanceSize.MICRO),
                                    port= 3306,
                                    allocated_storage= 80,
                                    multi_az= False,
                                    removal_policy= RemovalPolicy.DESTROY,
                                    deletion_protection= False,
                                    publicly_accessible= True
                                    )
        
        myDB.connections.allow_from_any_ipv4(
            ec2.Port.tcp(3306),
            description= "Open port for connection"
        )

        
        CfnOutput(self, 
                  "db_endpoint",
                  value= myDB.db_instance_endpoint_address)





        '''#Create RDS instance
        rds_instance = DatabaseInstance(
            self, "RDSInstance",
            engine=DatabaseInstanceEnine.mysql(version='5.7'),
            instance_class='db.t2.micro',
            master_username='admin',
            master_user_password=core.SecretValue.plain_text('password')
        )'''

        """topic = sns.Topic(
            self, "CdktestTopic"
        )"""

        #topic.add_subscription(subs.SqsSubscription(queue))
