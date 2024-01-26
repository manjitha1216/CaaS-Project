#!/usr/bin/env python3

import aws_cdk as cdk

from cdktest.cdktest_stack import CdktestStack


app = cdk.App()
CdktestStack(app, "CdktestStack")

app.synth()
