from aws_cdk.core import Construct, Stack
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_iam import Policy, PolicyStatement

from pointing_poker.aws.resources.sessions_table import session_table
from pointing_poker.aws.resources.api import graphql_api, pointing_poker_sources


class AppStack(Stack):
    def __init__(
        self,
        scope: Construct,
        res_id: str,
        asset_dir: str,
        graph_schema_path: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, res_id, **kwargs)

        self.table: Table = session_table(self, "sessions-table", **kwargs)

        self.api = graphql_api(
            self, "pointing-poker-graphql-api", graph_schema_path, **kwargs,
        )

        self.policy: Policy = Policy(
            self,
            "dynamodb-access-policy",
            policy_name="sessions-table-access",
            statements=[
                PolicyStatement(
                    actions=["dynamodb:*"],
                    resources=[
                        self.table.table_arn,
                        f"{self.table.table_arn}/index/id-index",
                    ],
                )
            ],
        )

        self.sources = pointing_poker_sources(
            self, self.api, self.policy, asset_dir, self.table.table_name
        )
