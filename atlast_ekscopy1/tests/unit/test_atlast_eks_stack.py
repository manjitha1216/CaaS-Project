import aws_cdk as core
import aws_cdk.assertions as assertions

from atlast_eks.atlast_eks_stack import AtlastEksStack

# example tests. To run these tests, uncomment this file along with the example
# resource in atlast_eks/atlast_eks_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AtlastEksStack(app, "atlast-eks")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
