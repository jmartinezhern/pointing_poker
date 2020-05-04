from aws_cdk.core import Construct

from aws_cdk.aws_dynamodb import Attribute, AttributeType, BillingMode, Table


def session_table(scope: Construct, res_id: str, **kwargs) -> Table:
    table = Table(
        scope,
        res_id,
        partition_key=Attribute(name="sessionID", type=AttributeType.STRING),
        sort_key=Attribute(name="id", type=AttributeType.STRING),
        time_to_live_attribute="ttl",
        billing_mode=BillingMode.PAY_PER_REQUEST,
        **kwargs
    )

    table.add_global_secondary_index(
        index_name="id-index",
        partition_key=Attribute(name="id", type=AttributeType.STRING),
    )

    return table
