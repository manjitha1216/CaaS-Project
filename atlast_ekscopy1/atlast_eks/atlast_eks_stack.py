from aws_cdk import (
    aws_eks as aws_eks,
    Stack,
    aws_ec2 as ec2,
    aws_iam as aws_iam,
    core,
   
    
)
from constructs import Construct

class AtlastEksStack(Stack):

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
                )
            ]
        )
       
          

        # Create an IAM Role to be assumed by admins
        masters_role = aws_iam.Role(
            self,
            'EksMastersRole',
            assumed_by=aws_iam.AccountRootPrincipal() 
        )

        # Attach an IAM Policy to that Role so users can access the Cluster
        masters_role_policy = aws_iam.PolicyStatement(
            actions=['eks:DescribeCluster'],
            resources=['*'],  # Adjust the resource ARN if needed
        )
        masters_role.add_to_policy(masters_role_policy)
        cluster.aws_auth.add_masters_role(masters_role)

        # Add the user to the cluster's admins
        admin_user = aws_iam.User.from_user_arn(self, "AdminUser",user_arn="arn:aws:iam::757516528332:user/cdk-project")
        cluster.aws_auth.add_user_mapping(admin_user, groups=["system:masters"])

        # Output the EKS cluster name
        core.CfnOutput(
        self,
        'ClusterNameOutput',
        value=cluster.cluster_name,
        )

        #Output the EKS master role ARN
        core.CfnOutput(
        self,
        'ClusterMasterRoleOutput',
        value=masters_role.role_arn,
        description="IAM Role ARN for EKS cluster administrator",  # Add a description for clarity
        )


        # Creating cluster variable
        cluster = aws_eks.Cluster(
            self, 'EKS-Cluster',
            cluster_name='eks-cluster',
            version=aws_eks.KubernetesVersion.V1_26,
            vpc=vpc,
            default_capacity=0
        )


                # IAM Role for the node group
        aws_eks.nodegroup_role = aws_iam.Role(
            self, 'NodegroupRole',
            assumed_by=aws_iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSWorkerNodePolicy')]
        )
        
        # Create the EKS node group
        aws_eks.nodegroup = cluster.add_auto_scaling_group_capacity(
            'Nodegroup',
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            desired_size=1,
            min_size=1,
            max_size=3,
            role=aws_eks.nodegroup_role
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
                'externalDatabase.host': 'combinationrdsstack-mydatabase1e2517db-gbxfhlthnpqm.ct48caeg4n7l.eu-central-1.rds.amazonaws.com',  # RDS endpoint
                'externalDatabase.user': 'Admin',   # RDS username
                'externalDatabase.password': ',I3UNDYk8d5MPyQ8,XFosr60hMgwn9', # RDS password
            }
        )


        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "AtlastEksQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
