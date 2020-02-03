from pony.orm import Required, Optional, Set, Json, \
                     composite_key as UNIQUE, PrimaryKey
from sakura.hub.mixins.dataflow import DataflowMixin
from sakura.hub.mixins.project import ProjectMixin
from sakura.hub.mixins.page import ProjectPageMixin
from sakura.hub.mixins.daemon import DaemonMixin
from sakura.hub.mixins.datastore import DatastoreMixin
from sakura.hub.mixins.database import DatabaseMixin
from sakura.hub.mixins.table import TableMixin
from sakura.hub.mixins.column import ColumnMixin
from sakura.hub.mixins.opclass import OpClassMixin
from sakura.hub.mixins.opinstance import OpInstanceMixin
from sakura.hub.mixins.link import LinkMixin
from sakura.hub.mixins.param import OpParamMixin
from sakura.hub.mixins.user import UserMixin
from sakura.hub.mixins.session import SessionMixin
from sakura.common.access import ACCESS_SCOPES

epoch = float

def define_schema(db):

    class User(db.Entity, UserMixin):
        login = PrimaryKey(str)
        email = Required(str, unique=True)
        password_salt = Required(bytes)
        password_hash = Required(bytes)
        first_name = Optional(str)
        last_name = Optional(str)
        creation_date = Optional(epoch)     # registration time/date
        gender = Optional(str)
        country = Optional(str)
        institution = Optional(str)
        occupation = Optional(str)          # work profile related
        work_domain = Optional(str)         # research topic
        privileges = Required(Json, default = [])
        requested_privileges = Required(Json, default = [])
        sessions = Set('Session')

    class Session(db.Entity, SessionMixin):
        id = PrimaryKey(int)
        user = Optional(User)
        timeout = Required(epoch)

    class Dataflow(db.Entity, DataflowMixin):
        access_scope = Required(int, default = ACCESS_SCOPES.private)
        grants = Required(Json, default = {})
        gui_data = Optional(str)
        metadata = Optional(Json, default = {})
        op_instances = Set('OpInstance')

    class Daemon(db.Entity, DaemonMixin):
        name = Required(str, unique=True)
        datastores = Set('Datastore')
        op_instances = Set('OpInstance')

    class OpClass(db.Entity, OpClassMixin):
        access_scope = Required(int, default = ACCESS_SCOPES.public)
        grants = Required(Json, default = {})
        repo = Required(Json)
        code_subdir = Required(str)
        metadata = Optional(Json, default = {})
        op_instances = Set('OpInstance')

    class OpInstance(db.Entity, OpInstanceMixin):
        daemon = Optional(Daemon)
        dataflow = Required(Dataflow)
        revision = Optional(Json, default = {})
        op_class = Required(OpClass)
        gui_data = Optional(str)
        uplinks = Set('Link')
        downlinks = Set('Link')
        params = Set('OpParam')

    class Link(db.Entity, LinkMixin):
        src_op = Required(OpInstance, reverse='downlinks')
        src_out_id = Required(int)
        dst_op = Required(OpInstance, reverse='uplinks')
        dst_in_id = Required(int)
        gui_data = Optional(str)

    class OpParam(db.Entity, OpParamMixin):
        op = Required(OpInstance, reverse='params')
        param_id = Required(int)
        value = Optional(Json)
        PrimaryKey(op, param_id)

    class Datastore(db.Entity, DatastoreMixin):
        daemon = Required(Daemon, reverse='datastores')
        host = Required(str)
        driver_label = Required(str)
        access_scope = Required(int, default = ACCESS_SCOPES.private)
        grants = Required(Json, default = {})
        metadata = Optional(Json, default = {})
        databases = Set('Database')

    class Database(db.Entity, DatabaseMixin):
        datastore = Required(Datastore)
        name = Required(str)
        access_scope = Required(int, default = ACCESS_SCOPES.private)
        grants = Required(Json, default = {})
        metadata = Optional(Json, default = {})
        tables = Set('DBTable')
        UNIQUE(datastore, name)

    class DBTable(db.Entity, TableMixin):
        database = Required(Database)
        name = Required(str)
        columns = Set('DBColumn')
        primary_key = Required(Json, default = [])
        foreign_keys = Required(Json, default = [])
        metadata = Optional(Json, default = {})
        UNIQUE(database, name)

    class DBColumn(db.Entity, ColumnMixin):
        table = Required(DBTable)
        col_id = Required(int)
        col_name = Required(str)
        col_type = Required(str)
        daemon_tags = Required(Json, default = [])
        user_tags = Required(Json, default = [])
        PrimaryKey(table, col_id)
        UNIQUE(table, col_name)

    class Project(db.Entity, ProjectMixin):
        access_scope = Required(int, default = ACCESS_SCOPES.private)
        grants = Required(Json, default = {})
        metadata = Optional(Json, default = {})
        pages = Set('ProjectPage')

    class ProjectPage(db.Entity, ProjectPageMixin):
        project = Required(Project)
        name = Required(str)
        content = Optional(str)
