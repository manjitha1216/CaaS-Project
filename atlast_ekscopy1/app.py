import os

from aws_cdk import core as cdk
from atlast_eks.atlast_eks_stack import AtlastEksStack

AWS_ACCOUNT = os.environ["AWS_ACCOUNT"]
AWS_REGION = os.environ["AWS_REGION"]


app = cdk.App()

# Capture the instance of AtlastEksStack
eks_stack = AtlastEksStack(
    app, "AtlasEksStack",
    env=cdk.Environment(account=AWS_ACCOUNT, region=AWS_REGION),



   # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html 
)


app.synth()
