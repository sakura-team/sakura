class ProjectMixin:
    @classmethod
    def create_or_update(cls, project_id, **kwargs):
        project = cls.get(id = project_id)
        if project is None:
            project = cls(id = project_id, **kwargs)
        else:
            project.set(**kwargs)
        return project
    @classmethod
    def get_gui_data(cls, project_id):
        project = cls.get(id = project_id)
        if project == None:
            return None
        return project.gui_data
    @classmethod
    def set_gui_data(cls, project_id, gui_data):
        cls.create_or_update(project_id, gui_data = gui_data)
