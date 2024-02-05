#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_ek_stest.cdk_ek_stest_stack import CdkEkStestStack


app = cdk.App()
CdkEkStestStack(app, "CdkEkStestStack")

app.synth()
