#! /bin/bash
aws cloudformation describe-stacks --stack-name sam-example-app > stack-output.json
