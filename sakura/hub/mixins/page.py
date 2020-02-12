from sakura.hub.context import get_context
from sakura.hub.mixins.bases import BaseMixin
from sakura.common.access import GRANT_LEVELS
from sakura.common.errors import APIRequestError, APIObjectDeniedError

class ProjectPageMixin(BaseMixin):
    def pack(self):
        return dict(
            project_id = self.project.id,
            page_id = self.id,
            page_name = self.name,
            page_content = self.content
        )
    @property
    def grants(self):
        return self.project.grants
    @property
    def access_scope(self):
        return self.project.access_scope
    def describe(self):
        return "'%(name)s' page" % dict(
            name = self.name
        )
    @classmethod
    def create_page(cls, project, page_name):
        context = get_context()
        if not context.user_is_logged_in():
            raise APIRequestError('Please log in first!')
        if project.get_grant_level() < GRANT_LEVELS.write:
            raise APIObjectDeniedError('Access denied')
        # instanciate page
        page = cls(project = project, name = page_name, content = '')
        # return page id
        context.db.commit()
        return page.id
    def update_page(self, page_name=None, page_content=None):
        if self.project.get_grant_level() < GRANT_LEVELS.write:
            raise APIObjectDeniedError('Access denied.')
        if page_name is not None:
            self.name = page_name
        if page_content is not None:
            self.content = page_content
    def delete_page(self):
        if self.project.get_grant_level() < GRANT_LEVELS.write:
            raise APIObjectDeniedError('Access denied.')
        if len(self.project.pages) == 1:
            raise APIRequestError('Project has a single page, cannot delete it.')
        self.delete()
