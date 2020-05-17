![CD](https://github.com/jmartinezhern/pointing_poker/workflows/CD/badge.svg)
![CI](https://github.com/jmartinezhern/pointing_poker/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/jmartinezhern/pointing_poker/branch/master/graph/badge.svg)](https://codecov.io/gh/jmartinezhern/pointing_poker)
[![BCH compliance](https://bettercodehub.com/edge/badge/jmartinezhern/pointing_poker?branch=master)](https://bettercodehub.com/)

# Pointing Poker

Pointing Poker is a simple back-end for a [Pointing Poker app](https://pointingpoker.app). The current implementation is based on AWS Lambda, Dynamodb, and AppSync.

The front-end implementation can be found [here](https://github.com/jmartinezhern/pointing-poker-web-app).

# Deploying

## Prerequisites

Pointing poker using the AWS CDK to deploy to CloudFormation. Follow the [AWS documentation](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html) to configure your account and setup the CDK. 

## CDK Deploy

To deploy, run:

```shell script
cdk deploy
```

This will deploy a CloudFormation to the region of your choice. Follow the [AppSync documentation](https://docs.aws.amazon.com/appsync/latest/devguide/quickstart.html) to fetch the endpoint and configure API Key.

You can also use the [AWS CLI](https://aws.amazon.com/cli/) to fetch the API information.

```shell script
aws appsync list-graphql-apis
```
