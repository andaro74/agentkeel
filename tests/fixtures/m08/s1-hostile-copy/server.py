"""The hostile copy's server. The template's `server.py` unchanged but for the
import shim (`from . import agent`), which is a platform-owned file. The
attempts are all in `agent.py`; nothing here is hostile, and the platform
check reads neither (SPEC/08 §1). A fixture: never run in agentkeel.
"""
from __future__ import annotations

from . import agent  # the hostile agent.py beside it

# The real server body is the template's; it is shipped unchanged and is not
# reproduced in the fixture. At deploy time the platform's own server.py form
# is what runs; this file stands for the agent repository's copy, which the
# platform check reads for existence only.
handler = agent.answer
