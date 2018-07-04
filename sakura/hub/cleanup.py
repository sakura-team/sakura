from sakura.hub.db import db_session_wrapper
from sakura.hub.context import get_context

CLEANUP_DELAY = 6   # seconds

def cleanup():
    with db_session_wrapper():
        get_context().sessions.cleanup()

def plan_cleanup():
    get_context().planner.plan(CLEANUP_DELAY, cleanup)
