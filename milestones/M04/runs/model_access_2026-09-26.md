# Model access and lifecycle, 2026-09-26

A record, not evidence (P11): commands the human ran with their own
credentials in account 581208540944, us-west-2, before M04 PR 1's first
commit, and their output as printed, carriage returns stripped. Read by
SPEC/04 §2 (the candidates) and §5 (S5's date). Nothing gates on this
file.

## 1. Which pinned models answer a call

`scripts/check_model_access.py` makes one Converse call per pin with
`maxTokens: 1`.

```
$ uv run python scripts/check_model_access.py --role agent --role m04_equivalent_swap --role m04_cheaper_swap --role m04_breaking_swap --role m04_deprecation_plant | tr -d '\r'
ok      agent                      us.anthropic.claude-sonnet-4-6
ok      m04_equivalent_swap        us.anthropic.claude-sonnet-4-5-20250929-v1:0
ok      m04_cheaper_swap           us.anthropic.claude-haiku-4-5-20251001-v1:0
REFUSED m04_deprecation_plant      us.anthropic.claude-sonnet-4-20250514-v1:0
        ResourceNotFoundException: Access denied. This Model is marked by provider as Legacy and you have not been actively using the model in the last 30 days. Please 
ok      m04_breaking_swap          us.meta.llama3-1-8b-instruct-v1:0
4 of 5 pinned models answered in us-west-2
```

## 2. Where each candidate's profile routes

```
$ for p in us.anthropic.claude-sonnet-4-5-20250929-v1:0 us.anthropic.claude-haiku-4-5-20251001-v1:0 us.meta.llama3-1-8b-instruct-v1:0; do aws bedrock get-inference-profile --region us-west-2 --inference-profile-identifier "$p" --query 'models[].modelArn' --output text | tr -d '\r'; done
arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0   arn:aws:bedrock:us-east-2::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0   arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0
arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0    arn:aws:bedrock:us-east-2::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0    arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-haiku-4-5-20251001-v1:0
arn:aws:bedrock:us-east-1::foundation-model/meta.llama3-1-8b-instruct-v1:0      arn:aws:bedrock:us-east-2::foundation-model/meta.llama3-1-8b-instruct-v1:0      arn:aws:bedrock:us-west-2::foundation-model/meta.llama3-1-8b-instruct-v1:0
```

All three route to the three regions `PROFILE_REGIONS` already names
(`infra/bootstrap/app.py`). Adding them to the eval role adds models, not
regions.

## 3. Lifecycle

```
$ aws bedrock get-foundation-model --region us-west-2 --model-identifier anthropic.claude-sonnet-4-20250514-v1:0 --query 'modelDetails.modelLifecycle' | tr -d '\r'
{
    "status": "LEGACY",
    "startOfLifeTime": "2025-05-22T00:00:00+00:00",
    "endOfLifeTime": "2026-10-14T08:00:00+00:00",
    "legacyTime": "2026-04-14T08:00:00+00:00",
    "publicExtendedAccessTime": "2026-07-14T08:00:00+00:00"
}

$ for m in anthropic.claude-sonnet-4-6 anthropic.claude-sonnet-4-5-20250929-v1:0 anthropic.claude-haiku-4-5-20251001-v1:0 meta.llama3-1-8b-instruct-v1:0; do echo "$m"; aws bedrock get-foundation-model --region us-west-2 --model-identifier "$m" --query 'modelDetails.modelLifecycle' --output json | tr -d '\r'; done
anthropic.claude-sonnet-4-6
{
    "status": "ACTIVE",
    "startOfLifeTime": "2026-02-17T18:00:00+00:00"
}
anthropic.claude-sonnet-4-5-20250929-v1:0
{
    "status": "ACTIVE",
    "startOfLifeTime": "2025-09-29T00:00:00+00:00"
}
anthropic.claude-haiku-4-5-20251001-v1:0
{
    "status": "ACTIVE",
    "startOfLifeTime": "2025-10-15T17:00:00+00:00"
}
meta.llama3-1-8b-instruct-v1:0
{
    "status": "ACTIVE",
    "startOfLifeTime": "2024-07-23T08:00:00+00:00"
}
```

Read in us-west-2 only; every profile above routes to three regions,
and the lifecycle of the model in us-east-1 and us-east-2 was not read
(threshold-owner note 14 on PR 1).

Bedrock gives `endOfLifeTime` only for the `LEGACY` model. refagent's
`deprecated_after` stays null: no date is announced for Sonnet 4.6
(SPEC/04 §2).
