"""
Helpers for constructing extensible menus in Opal applications
"""


class MenuItem(object):

    def __init__(self, **kwargs):
        self.template_name = kwargs.get('template_name', "")
        self.activepattern = kwargs.get('activepattern', "")
        self.href          = kwargs.get('href', "")
        self.icon          = kwargs.get('icon', "")
        self.display       = kwargs.get('display', "")
        self.index         = kwargs.get('index', 100)

    def __repr__(self):
        return u"<Opal MenuItem href: '{0}'>".format(self.href)

    def __eq__(self, other):
        if not isinstance(other, MenuItem):
            return NotImplemented

        return all([self.template_name == other.template_name,
                    self.activepattern == other.activepattern,
                    self.href == other.href,
                    self.icon == other.icon,
                    self.display == other.display,
                    self.index == other.index])

    def __ne__(self, other):
        if not isinstance(other, MenuItem):
            return NotImplemented

        return not self == other

    def for_user(self, user):
        return True


class Menu(object):

    def __init__(self, user=None):
        self.user = user
        self.items = []

        from opal.core import application, plugins
        app = application.get_app()

        # If we don't += this here, we start appending to the
        # list attached to the active Application class.
        # Which is suboptimal.
        self.items = app.get_menu_items(self.user)

        for plugin in plugins.OpalPlugin.list():
            self.items.extend(plugin.get_menu_items(self.user))

    def __iter__(self):

        # sorting of menu item is done withan index
        # property (lower = first), if they don't
        # have an index or if there are multiple with the
        # same index then its done alphabetically

        def alphabetic(x):
            return x.display

        def index_sorting(x):
            return x.index

        items = sorted(sorted(self.items, key=alphabetic), key=index_sorting)

        return (i for i in items)
