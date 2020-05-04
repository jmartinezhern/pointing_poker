from typing import Dict

from aws_cdk.core import Construct, Stack
from aws_cdk.aws_appsync import (
    GraphQLApi,
    Resolver,
    MappingTemplate,
    LambdaDataSource,
)

from aws_cdk.aws_iam import Policy
from aws_cdk.aws_lambda import Code, Function, Runtime


def lambda_data_source(
    scope: Construct,
    handler: str,
    field_name: str,
    type_name: str,
    api: GraphQLApi,
    code: Code,
    policy: Policy,
    environment: Dict[str, str],
) -> (Function, LambdaDataSource, Resolver):
    request_mapping: MappingTemplate = MappingTemplate.lambda_request(
        payload="$util.toJson($context.arguments)"
    )

    response_mapping: MappingTemplate = MappingTemplate.lambda_result()

    function: Function = Function(
        scope,
        f"{field_name}Lambda",
        code=code,
        runtime=Runtime("python3.7"),
        environment=environment,
        handler=f"pointing_poker.aws.controllers.sessions.{handler}",
    )

    policy.attach_to_role(function.role)

    source = api.add_lambda_data_source(f"{field_name}Source", "", function)

    resolver = Resolver(
        scope,
        f"{field_name}Resolver",
        api=api,
        data_source=source,
        field_name=field_name,
        type_name=type_name,
        request_mapping_template=request_mapping,
        response_mapping_template=response_mapping,
    )

    return function, source, resolver
