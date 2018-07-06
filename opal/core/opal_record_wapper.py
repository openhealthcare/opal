class OpalRecordWrapper(object):
    """
    An OpalRecordWrapper is a wrapper between a record, either a subrecord,
    an episode or a patient and something that wants to extract data from it.

    It lets us override fields on a model while providing a consistent
    interface.

    We can override fields either by passing them in or by overriding them
    as class attributes
    """
    model = None
    api_name = None
    display_name = None
    icon = None
    template = None
    is_singleton = None

    def __init__(
        self,
        model=None,
        api_name=None,
        display_name=None,
        icon=None,
        template=None,
        is_singleton=None
    ):
        self.model = model or self.model
        self.api_name = api_name or self.api_name
        self.display_name = display_name or self.display_name
        self.icon = icon or self.icon
        self.template = template or self.template
        if is_singleton is not None:
            self.is_singleton = is_singleton

    def get_api_name(self):
        return self.api_name or (self.model and self.model.get_api_name())

    def get_display_name(self):
        return self.display_name or (
            self.model and self.model.get_display_name()
        )

    def get_icon(self):
        return self.icon or (self.model and self.model.get_icon())

    def get_template(self):
        return self.template or (
            self.model and self.model.get_display_template()
        )

    def singleton(self):
        if self.is_singleton is None and self.model:
            return getattr(self.model, "_is_singleton", False)

        return self.is_singleton
