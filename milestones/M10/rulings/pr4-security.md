---
# M10 PR 4 (#57), the close. Security's key over the one Security path this
# PR touches: infra/security/app.py, the calls destination's policy, which is
# PR 2's again (the platform account as principal, nothing narrower) because
# CloudWatch Logs refused PR 3's narrowing twice on 2026-10-18; and, in
# words, the Unsure items this seat carried into the close (pr3.md B to J,
# pr2.md C, K, M, N, O, pr2-security.md A to D, pr1.md L) and what stands in
# AWS after the close. Product's file is pr4.md; Engineering's (with the
# cold review) pr4-engineering.md; the Data Owner's pr4-data-owner.md.
ruling: pr4-security
seat: Security
authorises:
  - infra/security/app.py
  - milestones/M10/rulings/pr4-security.md
evidence:
  - SPEC/00-overview.md#8-M10
  - SPEC/10-public-caller.md
  - milestones/M10/rulings/pr2-security.md
  - milestones/M10/rulings/pr3-security.md
  - milestones/M10/rulings/pr3.md
  - evals/history/14ab792156f585c9010275e6b6be3f687cee22c6.json
  - https://github.com/andaro74/agentkeel/actions/runs/39143365127
  - https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutDestinationPolicy.html
  - https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutResourcePolicy.html
pr: 57
---

# Ruling: M10 PR 4, Security

Ruled by andaro74 as Security, 2026-10-18, as written. A deploy made on this file before it reads "Ruled by" is
recorded below as one (M09 finding 4; pr3.md Unsure G).

## Security F3 stands: the calls destination admits the platform account, not the execution role

PR 3 set the destination policy's principal to
`arn:aws:iam::581208540944:role/agentkeel-cfn-exec` (`99e6807`,
`pr3-security.md` row 6), answering the security read's F3: once the
subscriber role trusted Logs on the platform account's behalf, any
principal in that shared account holding `logs:PutSubscriptionFilter`
could subscribe any log group to `agentkeel-calls`, and a line naming
`festival-desk` from any log group would land under
`calls/agents/festival-desk/`, where the reader cannot tell it from a
door's line.

That narrowing cannot be deployed. Two deploys of the security stack from
CloudShell on 2026-10-18, each as a CLI-synthesised template, each rolled
back:

| Policy | CloudWatch Logs refused it with |
|---|---|
| PR 3's: `Principal: {AWS: <the role's ARN>}` | "Principal section of policy contains ARN instead of account ID" (`e05095c` records it) |
| `Principal: {AWS: 581208540944}` with `Condition: ArnEquals aws:PrincipalArn: <the role's ARN>` | "Only aws:PrincipalOrgID and aws:PrincipalOrgPaths condition keys are allowed" (`0ebfdbd` records it) |

A destination policy names accounts, or an organisation by
`aws:PrincipalOrgID` or `aws:PrincipalOrgPaths`, and nothing narrower
(`PutDestinationPolicy`, read 2026-10-18: "authorizes cross-account users";
its one example is an account id; `forceUpdate` exists for the move from
accounts to an organisation id; the "no other condition" rests on the
service's own error text, quoted above). So `main` at `f05405f` holds a
security stack that cannot be deployed as written, and the deployed stack is
PR 2's policy, the rollback target of both attempts; `pr3-security.md`'s
"deployed by hand after this file is ruled" and pr3.md Unsure F's "admits
the execution role alone" did not come to pass. This PR makes the tree say
what is deployed: `Sid: ThePlatformAccountsDoorsSubscribe`, `Principal:
{AWS: 581208540944}`, `logs:PutSubscriptionFilter`, the one destination ARN,
no condition; the test holds the whole statement by equality and, on the
real synth, the account and no condition. The CLI synth of this branch
equals the deployed template by the owner's read in CloudShell (the diff is
not in the tree; `pr4.md` Unsure), so no deploy is made in PR 4.

**What stands, named (security-reviewer F1 on this PR, accepted by
name).** Any principal in the platform account (a shared account) holding
`logs:PutSubscriptionFilter` on a log group may subscribe it to the calls
destination, and the stream partitions each line by its own `agent` field;
nothing in `src/` or `scripts/` reads a batch's `logGroup` or `owner`. The
reader copies no line whose `agent` is not the prefix it was read under
(PR 2's F1 repair), which stops a line filed under the wrong agent, not a
forged line filed under the right one. No seeded case shows a foreign
subscription refused, because none is refused: pr3.md Unsure F is closed as
**not held, standing**, not as answered. And the narrowing PR 3 asked for
would not have closed it either (security-reviewer N2): the execution
role's own `PutSubscriptionFilter` reaches `/aws/lambda/agentkeel-*-door-*`,
the door functions' own log groups, so a template rendered under that role
could subscribe one and a printed line carrying an `agent` field would land
under that agent's prefix; the deploy plane's templates are held by
`ruling-cited` and this review, not by IAM. F3's remedy was partial, and is
recorded as such.

The routes, none built at M10:

1. **A dedicated account for the doored agents** (SPEC/00 §2's landing
   zone, R3). The account id is then the narrowing Logs allows, the trust
   already pairs per account, and the destination policy as deployed is
   exact. Complete for this path; a second platform account with every
   bootstrap grant re-homed; `platform-architect`'s deferred-item note is
   where it goes.
2. **Partition by the source, not the line.** `DataMessageExtraction` off
   so the batch's `logGroup` and `owner` survive; the prefix keyed on
   `/agentkeel/doors/<agent>/access` and on that pattern alone (so a door
   Lambda's own group does not match either); `from_raw` and the observer
   reading the batch shape. A Data Owner ruling on the record's shape goes
   with it (SPEC/10 §11 R5), and a seeded case (a line from another log
   group) before it is called working.
3. **A service control policy** in the organisation denying
   `logs:PutSubscriptionFilter` on the destination ARN for every principal
   but the execution role (`aws:PrincipalArn`): the one preventive control
   the shared account allows. Needs Organizations over `581208540944`,
   which nothing in the tree shows.
4. **A detective read**: the observer lists the platform account's
   subscription filters whose destination is `agentkeel-calls`, and `build`
   reads a record as not held when any log group outside
   `/agentkeel/doors/*/access` subscribes; a read-only
   `logs:DescribeSubscriptionFilters` grant on the eval role. The same read
   answers N6 below.

Until one is built, a record under `calls/agents/<name>/` is evidence that a
line naming `<name>` reached the destination from the platform account, and
the door's own records are told from a forgery by the request id the owner
wrote in the run file, which the observer steps each record by. That is what
row 10's cell rests on at M10, and the explainer says so.

## Accepted by name at the close (security-reviewer N6)

The destination policy lives in the security account, and no
platform-account principal can edit it. What a platform-account principal
can do is stop the records: the execution role may put a second filter or
repoint `DoorCalls` through a template (it cannot delete it, the deploy
boundary's `logs:Delete*`), and an account admin may delete it outright.
Either leaves `calls/` empty for that door, and row 10 reads the run unread,
not held; nothing reads that the filter is present. Accepted by name as
`pr2-security.md` accepted the same for the stream; route 4 is the read
that would name it.

## The by-hand deploys of 2026-10-18, before this file

Both refused deploys were attempted from this branch's two commits before
any ruling file carried them: M09 finding 4 and pr3.md Unsure G again,
recorded here. Neither changed the account: each rolled back to PR 2's
policy, which `pr2-security.md` ruled. Ruling this file makes the attempts
ruled. No further deploy is owed for M10's close.

## The Unsure items this seat carried, each disposed

| From | Item | Disposition |
|---|---|---|
| pr3 B | `logs:PutResourcePolicy` and the six log-delivery grants reach the whole shared account; `aws:ViaAWSService` untried | **Standing, accepted by name** (`pr3-security.md`). Not tried at the close: the only reader is a door deploy, and no throwaway door was deployed in PR 4. The deploy boundary caps none of them. Security, at the next door deploy or a dedicated account |
| pr3 C | `logs:DeleteLogDelivery` not granted | **Standing**, unmeasured: no doored agent has been retired. The first retirement of a doored agent (M07's `rollout: retired` path) is where it is read; a `DELETE_FAILED` there is a Security repair, not a finding of claim 10 |
| pr3 D | `RetainExceptOnCreate` on the pool has not fired | **Standing**, not described as working. The 55 orphans were deleted by hand; no failed first deploy has run since the repair |
| pr3 E | A subject removed from `callers` keeps its user and credential in the pool | **Standing**; the docstring says so (PR 3 F5). Tool Owner on removal semantics, Security on the retained credential; a `rollout: retired` or a `callers` removal in festival-desk is where it is read |
| pr3 F | The destination admits the execution role alone; no seeded case shows another principal refused | **Not held, standing**: F3 above. The narrowing is not deployable and would have been partial; the four routes are named |
| pr3 G | The by-hand deploys preceded their ruling | PR 3's were ruled on 2026-10-17; this PR's two refused attempts are recorded above and ruled by this file |
| pr3 H | `time_epoch_ms` carries seconds | Engineering, standing (`pr4-engineering.md`): the reader reads either unit by its size; the live lines read as 2026-10-18 on this run's envelope |
| pr3 I | The quota test measures the template, not an intrinsic's rendered length | Engineering, standing. 1,106 characters of room in the default policy |
| pr3 J | Whether `logs:PutResourcePolicy` takes a resource | **Read at the close** in the API reference (2026-10-18): the action takes an optional `resourceArn`, "currently only supports LogGroup ARN"; an account holds "a maximum of 10 policies without resourceARN and one per LogGroup resourceARN"; its policies apply to AWS service principals only. So the grant on `*` is what the vended delivery's account-level policy needs, and the sentence "none of which takes a resource" in `infra/bootstrap/app.py`'s DoorGrants reason is not exact: `PutResourcePolicy` can be scoped to a log group, though API Gateway's delivery writes the account-level one. The sentence is corrected at the next Security PR that touches the bootstrap; not in a close. Standing |
| pr2 C, O | The door's two functions run outside the platform VPC | **Standing**, accepted by name (`pr2-security.md` F7). Unchanged by the run |
| pr2 K | The log groups and the subscription are retained | **Recorded**; festival-desk's three log groups and its subscription stand |
| pr2 M | `DROPPED_KEYS`: whether the drop list is the whole of what public evidence must not carry, re-read at the first live record | **Re-read on this run's envelope with the Data Owner** (`pr4-data-owner.md`): what the live access-log lines and the bypass's data event carried, what was dropped, what reached the envelope. Security's part: nothing on the envelope names an address, a user agent, a key id, a principal id, a session context or a TLS detail; the bypass's principal ARN is on it by design (the run file states it) |
| pr2 N | Whether Cognito evaluates the agent tag on the handlers' pool actions | **Answered by the deploy**: run 39076739413 built the pool, the two clients and the user under the tag-held grants, `UPDATE_COMPLETE`; no refusal at Cognito. The API's grants stay untagged (`/apis/*`), accepted at PR 2 |
| pr2-security A | Whether the access log records a refused stranger with the authoriser's context and a no-token 401 with its request id | **Answered by the run**: the stranger's line names `stranger` and its issuer pool; the no-token line is the API's 401 with its request id. The envelope reads both (`pr4.md`) |
| pr2-security B | Whether the subscription's delivery lands under `calls/agents/<name>/` within N, through the bucket's lock | **Answered by the run**, after PR 3's trust repair: each line's object is under the prefix, within N by the envelope's reading; Firehose's put passed the lock |
| pr2-security C | Cognito and the agent tag | As pr2 N |
| pr2-security D | The probe with a quote and a newline in a claimed username, read back from `calls/` | **Not made.** No such call was in the run file, and none is added at a close. Standing; the authoriser clips what it writes (PR 2 F1) and a test holds the clipping, which is the only reading of it |
| pr1 L | The stranger's throwaway pool is made and deleted outside the repository, recorded by no observer | The pool `us-west-2_rXaZjWjO5` issued the stranger's token (the live line names it). Its deletion is the owner's word; no observer reads it. Recorded |
| this PR, security-reviewer N4 | Neither destination test asserts `RoleArn` is the subscriber role or `TargetArn` the stream | Engineering, standing (`pr4-engineering.md`): one line each at the next Engineering PR; not in a close |

## What stands in AWS after the close

Nothing is deleted without a Security ruling. festival-desk's door stands
as deployed by run 39076739413: the HTTP API (`ohw3eeegoa`), the pool
`us-west-2_f8kyzKF0P` with its two clients and the user `lantern-desk`, the
authoriser and proxy functions, the three log groups and the subscription
to `agentkeel-calls`; the runtime in JWT mode admitting the door's client.
In the security account: the destination, the Firehose and the `calls/`
statements as PR 2 ruled them. The bypass role `m10-bypass` in the platform
account and the stranger's pool are the owner's to confirm deleted; neither
is read by anything here (`pr4.md` Unsure). The failed deploy runs'
artifacts stand.

## Seat report: security-reviewer on PR 4 (verbatim)

Dispositions: F1 accepted by name above; F2 is this file; N1 settled by
`git show 917601d:infra/security/app.py` (the Sid at PR 2 was
`ThePlatformAccountsDoorsSubscribe`, the same; recorded in `pr4.md`); N2
taken into F3's text above; N3 the guide's URL and read date are in this
file's `evidence`, not edited into `infra/` at a close; N4 Engineering,
standing; N5 "stands" kept, "held" not written; N6 accepted by name above.

> Security seat report: M10 PR 4 (the close), branch m10-pr4 against f05405f. A draft for the PR body, not a ruling.
>
> Read: infra/security/app.py:478-512; tests/test_containment_stacks.py:259-329; infra/bootstrap/app.py:425-450, 886-932; infra/construct/governed_agent.py:99, 711-717; milestones/M10/rulings/pr3-security.md, pr3.md Unsure B-J, pr2-security.md:82-97 and :142; SPEC/10 line 403. This session has no shell, so I could not run `git diff` or `git show 917601d`. For question 1 I used the PR 2 security report's verbatim quote of the PR 2 policy and the PR 2 test, not the commit itself. No workflow, key policy, egress rule or evidence store changes here, so checks 1, 4, 5 and 6 have nothing new to read.
>
> **1. Is it PR 2's policy?**
> - NOTE 1. What is on the branch: `"Sid": "ThePlatformAccountsDoorsSubscribe", "Effect": "Allow", "Principal": {"AWS": AGENT_ACCOUNT}, "Action": "logs:PutSubscriptionFilter", "Resource": f"arn:aws:logs:{REGION}:{SECURITY_ACCOUNT}:destination:{CALLS_DESTINATION}"` (app.py:505-509), no Condition. pr2-security.md:142 quotes PR 2 as `Principal: {AWS: AGENT_ACCOUNT}`, `logs:PutSubscriptionFilter`, the one destination ARN, and PR 2's test (test_containment_stacks.py:266-268, under the "M10 PR 2" header) asserts the same Sid, action and resource by whole-statement equality. Principal, action, resource match. The Sid I could not read at 917601d; settle with `git show 917601d:infra/security/app.py | grep -n Sid` in the PR body. Security rules.
>
> **2. The forgery path, now that the destination cannot narrow**
> - FINDING 1. The path F3 named is live and this PR records it rather than closes it. The destination admits the account root (app.py:507), which delegates to every principal in 581208540944 holding `logs:PutSubscriptionFilter` on the destination ARN; the stream partitions on the line's `.agent` (app.py:471) and keeps only the message (app.py:469). Nothing in `src/` or `scripts/` reads `logGroup` or `owner` (grep: none), so a reader cannot tell a foreign line from a door's. The comment says this plainly (app.py:502-503). What would settle it is one of the routes below, or an accepted-by-name sentence in the ruling. Security rules; the Data Owner rules the record's shape if route (b) is taken.
> - NOTE 2. Narrowing to the execution role would not have closed it either. The role's own `PutSubscriptionFilter` reaches `/aws/lambda/agentkeel-*-door-*` (bootstrap app.py:896-898), which the door functions write to under `ItsOwnLogStreams`. A template could subscribe a door Lambda's own log group, and a `print()` line with an `agent` field would land under that agent's prefix. The deploy plane's templates are gated by `ruling-cited` and this review, not by IAM. F3's remedy was partial; say so in pr4-security.md.
> - Route (a), a dedicated agent account: the account id is then the narrowing, and the trust at app.py:486-488 already pairs per account. Honest and complete for this path. Cost: a second platform account, every bootstrap grant re-homed; a later milestone, not PR 4.
> - Route (b), partition by source log group: needs `DataMessageExtraction` off (app.py:469) so the CloudWatch envelope's `logGroup` and `owner` survive, a jq query that maps `/agentkeel/doors/<agent>/access` to the prefix, and `from_raw`/the observer to read the envelope shape. Closes the "foreign log group under a door's prefix" case but not NOTE 2 (a door Lambda's group still matches the exec role's grant unless the jq accepts only `/agentkeel/doors/*/access`). Record shape changes: Data Owner rules (SPEC/10 §11 R5).
> - Route (c), a third: a service control policy in the organisation denying `logs:PutSubscriptionFilter` on the destination ARN for every principal but the execution role (`aws:PrincipalArn`). The only preventive control the shared account allows; needs Organizations over 581208540944, which I cannot see from the tree. Security rules.
> - Route (d), detective: the observer lists the platform account's subscription filters whose destination is `agentkeel-calls` and `build` names a record as not held when any log group outside `/agentkeel/doors/*/access` subscribes. Needs a read-only `logs:DescribeSubscriptionFilters` grant on the eval role. Engineering builds; Security rules the grant.
>
> **3. The comment's claims about CloudWatch Logs**
> - NOTE 3. app.py:499-502 states two refusals as observed error text, each dated, and the stack's rollback. Both match the observed refusals the brief gives. The Logs guide ("Cross-account cross-Region subscriptions", Step 1: Create a destination; PutDestinationPolicy API) shows the destination policy with an account id as principal and names `aws:PrincipalOrgID` for an organisation; I do not recall the guide listing `aws:PrincipalOrgPaths` or an explicit "no other condition" sentence, so the comment's "any condition but" rests on the service's own error, which it quotes. Nothing untrue found. Settle by adding the guide URL and read date to the comment, as app.py:482 does for the trust.
> - FINDING 2. The comment cites `milestones/M10/rulings/pr4-security.md` (app.py:504) and the file is not in the tree (rulings/ holds pr1 to pr3-security only). PR 2's F6 again. Settle: commit the DRAFT with `pr:` this PR's number before it opens; it must also record that pr3-security.md:40-41 ("the destination policy narrowed ... is deployed by hand after this file is ruled") and pr3.md Unsure F ("admits the execution role alone") did not come to pass. Security writes; Product's `ruling-cited` reads it.
>
> **4. The tests**
> - NOTE 4. test_containment_stacks.py:266-268 asserts the whole statement by equality, so no wildcard, no list of principals and no Condition can pass it; :328-329 asserts `Principal == {"AWS": "581208540944"}`, `"Condition" not in allow` and the action on the real synth. That holds what matters. Gap: neither test asserts the destination's `RoleArn` is the subscriber role (app.py:495) or its `TargetArn` the stream (app.py:496); a destination pointed at another role or stream would pass both. One `assert destination["RoleArn"]`/`TargetArn` line settles it. Engineering writes; Security rules.
> - NOTE 5. The comment at test :324-325 says "The account, and nothing wider, stands." True of the template; it has not fired on a seeded case (no refused subscription from another account has been made). Keep "stands", do not write "held".
>
> **5. Switched off from inside the platform account?**
> - NOTE 6. The destination policy lives in the security account; no platform-account principal can edit it, and the security stack is deployed by hand from CloudShell by whoever holds admin there. What a platform-account principal can do: delete or replace the door's subscription filter (`DoorCalls`, governed_agent.py:714). The execution role cannot delete it (deploy boundary `logs:Delete*`, bootstrap app.py:446) but can put a second filter or repoint it through a template; an account admin can delete it outright. Either stops records silently: `calls/` reads empty and row 10 reads unread, as pr2-security.md:124 already says for the stream. No reader checks the filter is present (grep: nothing reads `DescribeSubscriptionFilters`). Route (d) above is the same read. Security rules whether this is accepted by name.
>
> Deploy: none in this PR, per the brief; I do not propose one. The claim that the synthesised template equals the deployed one is the owner's read and is not in the tree; the PR body should carry the diff command and its empty output.
>
> BLOCK: 0 · FINDING: 2 · NOTE: 6
