import time
from sakura.common.access import GRANT_LEVELS
from sakura.common.errors import APIRequestError
from sakura.hub.context import get_context
from sakura.hub.access import pack_gui_access_info, parse_gui_access_info
from sakura.hub.mixins.bases import BaseMixin

class ProjectMixin(BaseMixin):
    def pack(self):
        return dict(
            project_id = self.id,
            **self.metadata,
            **pack_gui_access_info(self)
        )
    def get_full_info(self):
        # start with general metadata
        result = self.pack()
        # note: we consider that pages are part of project 'metadata' (not 'content').
        # that is why the required grant level below is 'list' (not 'read').
        # this allows all users (even if not logged in) to view pages of public
        # projects.
        if self.get_grant_level() >= GRANT_LEVELS.list:
            # add pages
            result['pages'] = sorted((page.pack() for page in self.pages),
                                     key=lambda p: p['page_id'])
        return result
    def describe(self):
        return "'%(name)s' project" % dict(
            name = self.metadata['name']
        )
    @classmethod
    def create_project(cls, creation_date = None, **kwargs):
        context = get_context()
        if not context.user_is_logged_in():
            raise APIRequestError('Please log in first!')
        # set a creation_date if missing
        if creation_date is None:
            creation_date = time.time()
        # parse access info from gui
        kwargs = parse_gui_access_info(**kwargs)
        # instanciate project
        project = cls()
        # update attributes
        project.update_attributes(
            creation_date = creation_date,
            **kwargs
        )
        # record owner
        project.owner = context.user.login
        # add a 'Main' page
        context.pages.create_page(project, 'Main')
        # return project id
        context.db.commit()
        return project.id
    def create_page(self, page_name):
        context = get_context()
        return context.pages.create_page(self, page_name)
    def delete_project(self):
        self.assert_grant_level(GRANT_LEVELS.own,
                'Only owner is allowed to delete this project.')
        # delete this project
        self.delete()
