# Upgrades: what arrives in your repository, and what you do

For a developer or a seat holder of an agent made from the template. You
never edit a pipeline to take an upgrade: your repository has none. The
platform opens a pull request in your repository, and you read it and
merge it.

**What has run, as this page is written (M07 PR 3): no upgrade.** The
parts below are built and tested against planted cases in the platform's
own repository. No agent has yet taken an upgrade. One agent repository
made from the template has merged its first pull request; its first
deploy failed in the platform's own pipeline and is repaired at M07 PR 3.
The upgrades are made after that merges, and this page is corrected at
the close if they show it wrong.

## The three kinds

| Kind | What sets it off | What the pull request changes |
|---|---|---|
| Platform | The platform re-makes the template from a later version of itself | In `manifest.yaml`, `platform_version` and `guardrail`; and `server.py` and `__init__.py` |
| Retirement | The organisation's owner asks for your agent to be retired, or your model is within 30 days of being switched off by its maker and you have not moved | One line in `manifest.yaml`: `rollout: retired` |
| Model | Applies to the platform's own reference agent only, at M07. An agent from the template keeps the model its manifest names | Nothing in your repository |

Each arrives as a **draft** pull request, opened by the platform's App
`agentkeel-upgrades`, from a branch named `platform-upgrade/<version>` or
`platform-retire`. It is opened once. If you close it, it is not opened
again.

## What you do

1. Read it. The description says what changed and why.
2. Wait for the platform check. It runs on a schedule, within a few
   minutes, as it does on every pull request.
3. When the check has passed, mark the pull request ready and merge it.
   Use a merge commit, as for any change.

That is all. After the merge the platform deploys your agent again, as it
does after any merge. For a retirement it removes your agent instead.

## What you do not do

- **Do not push to the platform's branch.** If a person's commit is on an
  upgrade pull request, the platform's record says the upgrade needed a
  manual edit. If the upgrade is wrong for your agent, close it and tell
  the platform's owner.
- **Do not copy the change by hand into another pull request.** Same
  reason.
- **Do not add a workflow.** Nothing in your repository asks for the
  platform check; it comes to you.

## A platform upgrade: minor or major

The description says which.

- **Minor:** your repository passes the platform's check as it stands at
  the new version. Merge the upgrade when you can.
- **Major:** your repository does **not** pass the check at the new
  version as it stands. The description lists the checks that refuse it.
  The upgrade pull request brings the platform's own files up to date;
  if the refusal is about your own files (a seat, a golden, your data),
  fix those in a pull request of your own.

The upgrade touches only the files the platform owns. Your `agent.py`,
`prompt.txt`, `tools/`, `data/`, `goldens/` and every other line of your
manifest are yours and stay as they are. In `manifest.yaml` your comments
and every other field are kept byte for byte.

To see what an upgrade would change before it arrives, from a clone of
`andaro74/agentkeel` and of the template:

```sh
make upgrade AGENT=path/to/your-repo PLATFORM=path/to/agent-template
```

It prints the files that would change. It opens nothing.

## A retirement

Read this one carefully. **It is one-way.**

Merging it means: at the next deploy run the platform removes your
agent's runtime, and your agent stops answering. Nothing restores it. If
you later set `rollout` back, the platform deploys a new runtime at a new
address; the old one stays gone.

What is kept: your repository; the agent's row in the registry, which
then says when it was retired; its past answers and the signed copy of
what was deployed, in the audit bucket; its key, its table and its logs.
The audit bucket locks each record for one day. After that the records
are kept by the security account's own rules, not by a lock.

If your agent should not be retired, close the pull request.

A retirement changes one line and must stay one line. When the platform
retires your agent it is built to compare your manifest with the one it
last deployed, and to refuse if anything but `rollout` differs. No
retirement has run yet. So do not change
another field in the retirement pull request, and do not merge another
manifest change just before it: let that change deploy first. If your
agent's last deploy failed, it cannot be retired until a deploy succeeds.

## How long it takes

The platform looks for agents to upgrade every 15 minutes. Its three
limits, which a late step misses and nobody moves:

| Step | Limit |
|---|---|
| From the platform's new version to the pull request in your repository | 4,500 seconds (75 minutes) |
| From your merge to your agent deployed again | 3,600 seconds (one hour) |
| From your merge of a retirement to the runtime removed | 3,600 seconds (one hour) |

## If something looks wrong

- The pull request is not from `agentkeel-upgrades[bot]`: it is not the
  platform's. Do not merge it as an upgrade.
- It changes a file other than the ones in the table above: close it and
  tell the platform's owner. The platform's own check for this is in
  `scripts/platform_upgrade.py`; it has been tested on a planted case and
  has not yet run on a real repository.
- The platform check does not arrive: it runs every five minutes, and
  GitHub can delay a schedule when it is busy.
