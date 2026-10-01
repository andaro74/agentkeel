# infra/grafana

Grafana panel 1, the registry (Security; SPEC/06 section 6, R1 in
`milestones/M06/feasibility.md` section 8). Three parts, each with one seat
and one path:

- `panel1.json`: the dashboard. Panel 1 has one target, the Athena data
  source `registry`, reading `agentkeel-registry` and nothing else.
  `validate` refuses any other source or table (S4's query reader,
  `src/validate/panel.py`). `build.panel_not_in_registry` compares the rows
  Grafana returns with a registry scan (S4's other reader, BLOCK 3).
- `app.py`, the stack `AgentkeelGrafana`: Athena's DynamoDB connector (AWS's
  published one, pinned, with a role that reads the registry alone), its
  data catalog `agentkeel_registry`, the workgroup `agentkeel-grafana`, a
  one-day scratch bucket, and the role the workspace assumes.
- The workspace, made by hand (below). Amazon Managed Grafana, Identity
  Center authentication. Identity Center is already on in this account (an
  organisation instance since 2024-07-23, no permission sets, no users,
  read 2026-09-30); the workspace adds one user and one application
  assignment and no permission set.

Cost (read 2026-09-30): $9 a month for the one editor, $5 a month for the
observer's service account in a month it reads, Athena about nothing at a
10 MB minimum per query. A 90-day trial covers up to five users if the
account has not used it.

## By hand, during M06 PR 2, in this order

As the admin in the agent account (581208540944), after the bootstrap
stack's redeploy has made `agentkeel-registry`:

```sh
aws sts get-caller-identity          # 581208540944
cd infra/grafana && npx aws-cdk@2 diff
npx aws-cdk@2 deploy                  # needs CAPABILITY_IAM and CAPABILITY_AUTO_EXPAND (the connector)
aws cloudformation describe-stacks --region us-west-2 --stack-name AgentkeelGrafana \
  --query "Stacks[0].Outputs" --output table
```

`cdk diff` shows only new resources: one bucket, two roles, the connector
application, one data catalog, one workgroup. Anything else is a stop.

Then the workspace, in the console (Amazon Managed Grafana, us-west-2):

1. Create workspace `agentkeel`. Authentication: **AWS IAM Identity
   Center**. Permission type: **customer managed**, role
   `agentkeel-grafana-workspace` (the stack's output). Data sources: none
   (the one below is added by hand). Network access: public. Grafana
   version: the newest offered.
2. In IAM Identity Center, create the user `andaro74` and assign it to the
   workspace as **Admin**.
3. Sign in to the workspace. Add the data source **Amazon Athena**, with
   **uid `registry`**: authentication "Workspace IAM role", region
   us-west-2, data catalog `agentkeel_registry`, database `default`,
   workgroup `agentkeel-grafana`. Save and test. As done on 2026-10-01:
   - The form gives a new data source a random uid, so it is made through
     the API with a temporary Admin service account's token (one day),
     deleted after step 5:
     `POST /api/datasources` with `{"name":"registry","uid":"registry","type":"grafana-athena-datasource","access":"proxy","jsonData":{"authType":"ec2_iam_role","defaultRegion":"us-west-2","catalog":"agentkeel_registry","database":"default","workgroup":"agentkeel-grafana"}}`.
   - The Athena plugin is not installed in a new workspace: the data source
     is saved but its page reads "Data source not found" until **Amazon
     Athena** is installed (Administration, Plugins; plugin management on
     in the workspace's configuration options).
4. Import `infra/grafana/panel1.json` as a dashboard. Panel 1 lists
   `refagent` once refagent's deploy at PR 2's merge has written its row.
5. Create a service account `agentkeel-observer`, role **Viewer**, and a
   token for it (the longest expiry offered; Managed Grafana caps it at 30
   days, so a token is made again before PR 3's run if it has lapsed).
   Store it in `agentkeel` as the secret `AGENTKEEL_GRAFANA_TOKEN`, and the
   workspace URL as the variable `AGENTKEEL_GRAFANA_URL`. `evals.yml` hands
   both to `scripts/observe_template.py`, which posts panel 1's own query to
   `/api/ds/query`.

## What this does not do

- Panel 2 (the verdict history) is cut to M07 (SPEC/06 section 9, cut 1).
- No gate reads the workspace's data source settings: a data source whose
  uid is `registry` but which reads something else would pass `validate`.
  The rows it returns are what `build` compares with a registry scan, so a
  row that is not in the registry still reads as F6.4 fired.
- No seeded case attempts the connector reading a table other than the
  registry; its role names the registry alone.
