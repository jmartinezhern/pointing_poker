from time import time

from aws_cdk.aws_appsync import CfnApiKey, GraphQLApi
from aws_cdk.core import Construct
from aws_cdk.aws_iam import Policy
from aws_cdk.aws_lambda import Code

from pointing_poker.aws.resources.data_source import lambda_data_source


def graphql_api(scope: Construct, res_id: str, schema_path: str, **kwargs):
    api = GraphQLApi(
        scope,
        res_id,
        name="Pointing Poker API",
        schema_definition_file=schema_path,
        **kwargs
    )

    api_key = CfnApiKey(
        scope, "apiKey", api_id=api.api_id, expires=int(time() + (365 * 24 * 60 * 60)),
    )

    return api, api_key


def pointing_poker_sources(
    scope: Construct, api: GraphQLApi, policy: Policy, asset_dir: str, table_name: str
):
    lambda_env = {"SESSIONS_TABLE_NAME": table_name}

    code: Code = Code.from_asset(asset_dir)

    return list(
        map(
            lambda field_definition: lambda_data_source(
                scope,
                field_definition[0],
                field_definition[1],
                field_definition[2],
                api,
                code,
                policy,
                lambda_env,
            ),
            [
                ("create_session", "createSession", "Mutation"),
                ("join_session", "joinSession", "Mutation"),
                ("leave_session", "leaveSession", "Mutation"),
                ("session", "session", "Query"),
                ("participant", "participant", "Query"),
                ("set_vote", "setVote", "Mutation"),
                ("start_voting", "startVoting", "Mutation"),
                ("set_reviewing_issue", "setReviewingIssue", "Mutation"),
                ("stop_voting", "stopVoting", "Mutation"),
                ("close_session", "closeSession", "Mutation"),
            ],
        )
    )
