from pony.orm import Required, Optional, Set, Json, \
                     composite_key as UNIQUE, PrimaryKey
from sakura.hub.mixins.project import ProjectMixin
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

epoch = float

def define_schema(db):

    class User(db.Entity, UserMixin):
        login = PrimaryKey(str)
        email = Required(str, unique=True)
        password = Required(str)
        first_name = Optional(str)
        last_name = Optional(str)
        creation_date = Optional(epoch)     # registration time/date
        gender = Optional(str)
        country = Optional(str)
        institution = Optional(str)
        occupation = Optional(str)          # work profile related
        work_domain = Optional(str)         # research topics
        ds_admin_of = Set('Datastore')
        ds_rw = Set('Datastore')
        ds_ro = Set('Datastore')
        db_rw = Set('Database')
        db_ro = Set('Database')
        db_owner_of = Set('Database')
        db_contact_of = Set('Database')

    class Project(db.Entity, ProjectMixin):
        gui_data = Optional(str)
        op_instances = Set('OpInstance')

    class Daemon(db.Entity, DaemonMixin):
        name = Required(str, unique=True)
        connected = Required(bool, default = False)
        op_classes = Set('OpClass')
        datastores = Set('Datastore')

    class OpClass(db.Entity, OpClassMixin):
        daemon = Required(Daemon, reverse='op_classes')
        name = Required(str)
        short_desc = Required(str)
        tags = Optional(Json, default = [])
        icon = Required(str)
        op_instances = Set('OpInstance')
        UNIQUE(daemon, name)

    class OpInstance(db.Entity, OpInstanceMixin):
        project = Optional(Project) # TODO: should be required
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
        online = Required(bool)
        host = Required(str)
        driver_label = Required(str)
        admin = Optional(User, reverse = 'ds_admin_of')
        users_rw = Set(User, reverse = 'ds_rw')
        users_ro = Set(User, reverse = 'ds_ro')
        databases = Set('Database')

    class Database(db.Entity, DatabaseMixin):
        datastore = Required(Datastore)
        name = Required(str)
        db_name = Required(str)
        short_desc = Optional(str)
        creation_date = Optional(epoch)
        tags = Optional(Json, default = [])
        owner = Optional(User, reverse = 'db_owner_of')
        users_rw = Set(User, reverse = 'db_rw')
        users_ro = Set(User, reverse = 'db_ro')
        contacts = Set(User, reverse = 'db_contact_of')
        tables = Set('DBTable')
        UNIQUE(datastore, db_name)
        UNIQUE(datastore, name)

    class DBTable(db.Entity, TableMixin):
        database = Required(Database)
        name = Required(str)
        db_table_name = Required(str)
        short_desc = Optional(str)
        creation_date = Optional(epoch)
        columns = Set('DBColumn')
        UNIQUE(database, db_table_name)
        UNIQUE(database, name)

    class DBColumn(db.Entity, ColumnMixin):
        table = Required(DBTable)
        col_name = Required(str)
        col_type = Required(str)
        db_col_name = Required(str)
        daemon_tags = Required(Json, default = [])
        user_tags = Required(Json, default = [])
        UNIQUE(table, db_col_name)
        UNIQUE(table, col_name)
