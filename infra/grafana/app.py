"""Grafana's reach into the registry, AgentkeelGrafana (Security seat; SPEC/06 section 6, R1).

Deployed by the human with admin in the agent account (581208540944), by
hand, after `infra/bootstrap/` has made `agentkeel-registry`:

    cd infra/grafana && npx aws-cdk@2 diff && npx aws-cdk@2 deploy

Panel 1 reads the registry through **Athena**, an AWS data source in Amazon
Managed Grafana, and Athena reads DynamoDB through its **DynamoDB
connector**, a Lambda function AWS publishes in the Serverless Application
Repository. Neither is a custom plugin (SPEC/00 section 13: Grafana's job
excludes "anything custom"); the Enterprise DynamoDB plugin is $45 a user a
month on top of the licence (milestones/M06/feasibility.md section 8, R1).
What this stack makes:

- **one bucket** for the connector's spill (`spill/`) and the workgroup's
  results (`results/`), each kept one day, TLS only, public access blocked;
- **the connector's role**, passed to the published application as
  `LambdaRole` so that its own role is never made: the published role reads
  every DynamoDB table in the account, and this account holds other
  projects' tables. This one scans and describes `agentkeel-registry` alone;
- **the connector** (`AthenaDynamoDBConnector`, a pinned version) as
  `agentkeel-registry-connector`, and the Athena data catalog
  `agentkeel_registry` that names it;
- **the workgroup** `agentkeel-grafana`, its results location enforced;
- **the workspace's role**, `agentkeel-grafana-workspace`, which Managed
  Grafana assumes (this account only) to run panel 1's query: Athena in that
  workgroup and catalog, the connector's invoke, and the bucket's prefixes.

The workspace itself, its Identity Center user and its Athena data source
(uid `registry`, this workgroup, this catalog) are made by hand
(`README.md`). Panel 1's query is `infra/grafana/panel1.json`, which
`validate` holds to the registry alone (S4's query reader).
"""

from __future__ import annotations

import os
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_athena as athena
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sam as sam
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

REGION = "us-west-2"
ACCOUNT = "581208540944"
REGISTRY_TABLE = "agentkeel-registry"  # infra/bootstrap/app.py, REGISTRY_TABLE
CONNECTOR = "agentkeel-registry-connector"
CATALOG = "agentkeel_registry"  # panel1.json's connectionArgs.catalog
WORKGROUP = "agentkeel-grafana"
WORKSPACE_ROLE = "agentkeel-grafana-workspace"
# AWS's published connector, pinned. Read from the Serverless Application Repository on 2026-09-30
# (`aws serverlessrepo get-application`): 2026.33.1, its parameters as used below.
CONNECTOR_APP = "arn:aws:serverlessrepo:us-east-1:292517598671:applications/AthenaDynamoDBConnector"
CONNECTOR_VERSION = "2026.33.1"


class GrafanaStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        bucket = s3.Bucket(
            self, "Scratch", bucket_name=f"agentkeel-grafana-{ACCOUNT}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL, enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED, object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            lifecycle_rules=[s3.LifecycleRule(expiration=cdk.Duration.days(1))],
            removal_policy=cdk.RemovalPolicy.DESTROY, auto_delete_objects=False,
        )  # fmt: skip
        registry = f"arn:aws:dynamodb:{REGION}:{ACCOUNT}:table/{REGISTRY_TABLE}"
        function = f"arn:aws:lambda:{REGION}:{ACCOUNT}:function:{CONNECTOR}"

        connector_role = iam.Role(
            self, "ConnectorRole", role_name=f"{CONNECTOR}-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="agentkeel: Athena's DynamoDB connector reads agentkeel-registry and nothing else.",
        )  # fmt: skip
        connector_role.add_to_policy(iam.PolicyStatement(
            sid="ReadTheRegistryOnly",
            actions=["dynamodb:DescribeTable", "dynamodb:Scan", "dynamodb:Query", "dynamodb:PartiQLSelect"],
            resources=[registry],
        ))  # fmt: skip
        connector_role.add_to_policy(iam.PolicyStatement(
            sid="ListTablesTakesNoResource", actions=["dynamodb:ListTables"], resources=["*"]))
        connector_role.add_to_policy(iam.PolicyStatement(
            sid="ItsOwnSpill",
            actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket", "s3:GetBucketLocation",
                     "s3:GetLifecycleConfiguration"],
            resources=[bucket.bucket_arn, bucket.arn_for_objects("spill/*")],
        ))  # fmt: skip
        connector_role.add_to_policy(iam.PolicyStatement(
            sid="TheQueryItAnswers", actions=["athena:GetQueryExecution"],
            resources=[f"arn:aws:athena:{REGION}:{ACCOUNT}:workgroup/{WORKGROUP}"],
        ))  # fmt: skip
        connector_role.add_to_policy(iam.PolicyStatement(
            sid="ItsOwnLogs", actions=["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
            resources=[f"arn:aws:logs:{REGION}:{ACCOUNT}:log-group:/aws/lambda/{CONNECTOR}:*"],
        ))  # fmt: skip

        connector = sam.CfnApplication(
            self, "Connector",
            location=sam.CfnApplication.ApplicationLocationProperty(
                application_id=CONNECTOR_APP, semantic_version=CONNECTOR_VERSION),
            parameters={"AthenaCatalogName": CONNECTOR, "SpillBucket": bucket.bucket_name, "SpillPrefix": "spill",
                        "LambdaRole": connector_role.role_arn, "LambdaMemory": "512", "LambdaTimeout": "120"},
        )  # fmt: skip

        catalog = athena.CfnDataCatalog(
            self, "Catalog", name=CATALOG, type="LAMBDA", parameters={"function": function},
            description="agentkeel: the registry, through Athena's DynamoDB connector (panel 1).",
        )  # fmt: skip
        catalog.node.add_dependency(connector)

        athena.CfnWorkGroup(
            self, "WorkGroup", name=WORKGROUP, recursive_delete_option=True,
            description="agentkeel: panel 1's queries, and nothing else.",
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                enforce_work_group_configuration=True, publish_cloud_watch_metrics_enabled=True,
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    output_location=f"s3://{bucket.bucket_name}/results/",
                    encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
                        encryption_option="SSE_S3"))),
        )  # fmt: skip

        workspace = iam.Role(
            self, "WorkspaceRole", role_name=WORKSPACE_ROLE,
            assumed_by=iam.ServicePrincipal("grafana.amazonaws.com", conditions={
                "StringEquals": {"aws:SourceAccount": ACCOUNT},
                "ArnLike": {"aws:SourceArn": f"arn:aws:grafana:{REGION}:{ACCOUNT}:/workspaces/*"}}),
            description="agentkeel: what Managed Grafana runs panel 1's query as.",
        )  # fmt: skip
        workspace.add_to_policy(iam.PolicyStatement(
            sid="PanelOnesQueryInItsWorkgroupAndCatalog",
            actions=["athena:StartQueryExecution", "athena:GetQueryExecution", "athena:GetQueryResults",
                     "athena:StopQueryExecution", "athena:GetWorkGroup", "athena:GetDataCatalog",
                     "athena:ListDatabases", "athena:GetDatabase", "athena:ListTableMetadata",
                     "athena:GetTableMetadata"],
            resources=[f"arn:aws:athena:{REGION}:{ACCOUNT}:workgroup/{WORKGROUP}",
                       f"arn:aws:athena:{REGION}:{ACCOUNT}:datacatalog/{CATALOG}"],
        ))  # fmt: skip
        workspace.add_to_policy(iam.PolicyStatement(
            sid="ListingTakesNoResource",
            actions=["athena:ListWorkGroups", "athena:ListDataCatalogs"], resources=["*"]))
        workspace.add_to_policy(iam.PolicyStatement(
            sid="TheConnector", actions=["lambda:InvokeFunction"], resources=[function]))
        workspace.add_to_policy(iam.PolicyStatement(
            sid="TheResultsAndTheSpill",
            actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:GetBucketLocation"],
            resources=[bucket.bucket_arn, bucket.arn_for_objects("results/*"), bucket.arn_for_objects("spill/*")],
        ))  # fmt: skip
        cdk.CfnOutput(self, "WorkspaceRoleArn", value=workspace.role_arn)
        cdk.CfnOutput(self, "WorkGroupName", value=WORKGROUP)
        cdk.CfnOutput(self, "CatalogName", value=CATALOG)


app = cdk.App(outdir=os.environ.get("CDK_OUTDIR") or str(Path(__file__).parent / "cdk.out"))
stack = GrafanaStack(
    app, "AgentkeelGrafana",
    env=cdk.Environment(account=ACCOUNT, region=REGION),
    description="agentkeel M06: Grafana's reach into the registry through Athena. Security seat.",
    synthesizer=cdk.LegacyStackSynthesizer(),  # the account is not CDK-bootstrapped in us-west-2
)
REASONS = {
    "Scratch/Resource": [(
        "AwsSolutions-S1",
        "SPEC/06 §6 (R1): a scratch bucket for the connector's spill and Athena's results, each kept one "
        "day; nothing in it is evidence, and server access logs would need a second bucket that nothing reads.",
    )],
    "ConnectorRole/DefaultPolicy/Resource": [(
        "AwsSolutions-IAM5",
        "SPEC/06 §6 (R1): dynamodb:ListTables takes no resource-level permission; the spill is "
        "spill/* in this stack's own bucket, whose keys the connector writes per query; the log group's "
        "streams are named by Lambda. The table grant is agentkeel-registry by ARN.",
    )],
    "WorkspaceRole/DefaultPolicy/Resource": [(
        "AwsSolutions-IAM5",
        "SPEC/06 §6 (R1): ListWorkGroups and ListDataCatalogs take no resource-level permission; "
        "results/* and spill/* are this stack's bucket's prefixes, whose keys Athena writes per query.",
    )],
}
for path, rules in REASONS.items():
    NagSuppressions.add_resource_suppressions_by_path(
        stack, f"AgentkeelGrafana/{path}", [{"id": rule, "reason": reason} for rule, reason in rules])
cdk.Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
