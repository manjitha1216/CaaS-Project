from aws_cdk import CfnOutput
from aws_cdk import aws_ssm as ssm
from aws_cdk import RemovalPolicy
from aws_cdk import aws_secretsmanager as secretsmanager

from aws_cdk import (
    Duration,
    aws_eks as aws_eks,
    Stack,
    aws_ec2 as ec2,
    aws_iam as aws_iam,
    aws_rds as rds,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_lambda as lambda_,
    RemovalPolicy
    #aws_eks.HelmChartProps
   
    
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

class CdkEkStestStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        availability_zones = ['eu-central-1a', 'eu-central-1b']
        # Create a new VPC
        vpc = ec2.Vpc(self, 'Vpc',
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            vpc_name='eks-vpc',
            enable_dns_hostnames=True,
            enable_dns_support=True,
            availability_zones=availability_zones,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='eks-subnet-public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name='eks-subnet-private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name='eks-subnet-privateRDS',
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        #    #security group for node group
        # eks_nodegroup_security_group = ec2.SecurityGroup(
        #     self, 'MyNodegroupSecurityGroup',
        #     vpc=vpc,  # Use the VPC created earlier
        #     allow_all_outbound=True  # Adjust outbound rules based on your requirements
        # )

        # # Allow inbound connections on the HTTPS ports
        # eks_nodegroup_security_group.add_ingress_rule(
        #     peer=ec2.Peer.ipv4('0.0.0.0/0'),
        #     connection=ec2.Port.tcp(443),
        #     description='Allow inbound https connections'
        # )

        #  # Allow inbound connections on the SSH ports
        # eks_nodegroup_security_group.add_ingress_rule(
        #     peer=ec2.Peer.ipv4('0.0.0.0/0'),
        #     connection=ec2.Port.tcp(22),
        #     description='Allow inbound ssh connections'
        # )

        # # Creating cluster variable
        cluster = aws_eks.Cluster(
             self, 'EKS-Cluster',
             cluster_name='eks-cluster',
             version=aws_eks.KubernetesVersion.V1_28,
             vpc=vpc,
             default_capacity=0
         )
        
        
        #          # IAM Role for the node group
        # aws_eks.nodegroup_role = aws_iam.Role(
        #       self, 'NodegroupRole',
        #       assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
        #       managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSWorkerNodePolicy')]
        #   ) 

         # # Create the EKS node group
        aws_eks.nodegroup = cluster.add_auto_scaling_group_capacity(
             'Nodegroup',
             instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
             min_capacity=2,
             max_capacity=3,
             #role=aws_eks.nodegroup_role
             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
             #security_groups=eks_nodegroup_security_group
         )
        
        

        email_address = "nataliya.maroz@accenture.com"     
        
        eks_sns_topic = Topic(self, 'EKS SNS topic',display_name='EKS topic')
        rds_sns_topic = Topic(self, 'RDS SNS topic',display_name='RDS topic')

        eks_sqs_queue = Queue(self, 'EKSSQSQueue')
        rds_sqs_queue = Queue(self, 'RDSSQSQueue')
        
        eks_sns_topic.add_subscription(SqsSubscription(eks_sqs_queue))
        rds_sns_topic.add_subscription(SqsSubscription(rds_sqs_queue))
        
        eks_sns_topic.add_subscription(EmailSubscription(email_address))
        rds_sns_topic.add_subscription(EmailSubscription(email_address))
        # Create a security group for the RDS instance
        rds_security_group = ec2.SecurityGroup(
            self, 'RDSSecurityGroup',
            vpc=vpc,  # Use the VPC created earlier
            allow_all_outbound=True  # Adjust outbound rules based on your requirements
        )

        # Allow inbound connections on the MySQL port (e.g., 3306)
        rds_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4('0.0.0.0/0'), 
            connection=ec2.Port.tcp(3306),
            description='Allow inbound MySQL connections'
        )


        myDB = rds.DatabaseInstance(self, 
                                    "MyDatabase",
                                    engine= rds.DatabaseInstanceEngine.MYSQL,
                                    vpc= vpc,
                                    vpc_subnets= ec2.SubnetSelection(
                                        #subnet_type= ec2.SubnetType.PUBLIC,
                                        subnet_type= ec2.SubnetType.PRIVATE_ISOLATED,
                                    ),
                                    security_groups=[rds_security_group],
                                    credentials= rds.Credentials.from_generated_secret("Admin"),
                                    instance_type= ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3,
                                                                       ec2.InstanceSize.MICRO),
                                    port= 3306,
                                    allocated_storage= 20,
                                    multi_az= True,
                                    removal_policy= RemovalPolicy.DESTROY,
                                    cloudwatch_logs_exports=['error', 'general', 'slowquery', 'audit'], #comment if db is not deployed
                                    deletion_protection= False,
                                    publicly_accessible= False
                                    )

       # Helm chart for WordPress
        aws_eks.wordpress_chart = aws_eks.HelmChart(
            self, 'WordPressChart',
            chart='wordpress',
            release='wordpress',
            repository='https://charts.bitnami.com/bitnami',
            namespace='default',
            values={
                'mariadb.enabled': False,
                'externalDatabase.host': 'cdkeksteststack-mydatabase1e2517db-6ljxmdi3e6m6.ct48caeg4n7l.eu-central-1.rds.amazonaws.com',  # RDS endpoint
                'externalDatabase.user': 'Admin',   # RDS username
                'externalDatabase.password': '_aDI-xIbOhbyrEfbp-ih_PXprd2I5V', # RDS password
            },
            cluster=cluster
        )

        # Output the RDS endpoint for reference
        CfnOutput(self, 'RDS-Endpoint', value=myDB.db_instance_endpoint_address)

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
        rds_db_connection_alarm.add_alarm_action(SnsAction(rds_sns_topic))


        #S3 Bucket Creation
        #logs_bucket = s3.Bucket(self, "LogsBucket")

        # Create Lambda function to send logs to S3
        # logs_lambda_function = lambda_.Function(
        #     self,
        #     "LogsLambdaFunction",
        #     handler="lambda_handler.handler",
        #     runtime=lambda_.Runtime.PYTHON_3_8,
        #     code=lambda_.Code.from_asset("lambda"),  # Update this path as needed
        #     environment={
        #         "S3_BUCKET_NAME": logs_bucket.bucket_name,
        #         "LOG_GROUP_NAME": rds_log_group.log_group_name,
        #         "LOG_STREAM_NAME": rds_log_stream.log_stream_name,
        #     },
        # )

        # logs_lambda_function.role.add_to_policy(
        #         iam.PolicyStatement(
        #                 actions=["logs:DescribeLogGroups", "logs:DescribeLogStreams"],
        #                  resources=[rds_log_group.log_group_name, rds_log_stream.log_stream_name]
        #         )
        # )


        # Grant Lambda permissions to access CloudWatch Logs and write to S3
        #rds_log_group.grant_read(logs_lambda_function)
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
        