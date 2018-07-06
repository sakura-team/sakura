from sakura.common.cache import Cache
from sakura.hub.db import db_session_wrapper
from sakura.hub.context import get_context

SESSIONS_CLEANUP_DELAY = 6   # seconds

def sessions_cleanup():
    with db_session_wrapper():
        get_context().sessions.cleanup()

def plan_cleanup():
    planner_greenlet = get_context().planner
    planner_greenlet.plan(SESSIONS_CLEANUP_DELAY, sessions_cleanup)
    Cache.plan_cleanup(planner_greenlet)
