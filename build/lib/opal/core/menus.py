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

        return (self.template_name == other.template_name and
                self.activepattern == other.activepattern and
                self.href == other.href and
                self.icon == other.icon and
                self.display == other.display and
                self.index == other.index)

    def __ne__(self, other):
        if not isinstance(other, MenuItem):
            return NotImplemented

        return not self == other


class Menu(object):

    def __init__(self, user=None):
        self.user = user
        self.items = []

        from opal.core import application, plugins
        app = application.get_app()

        # If we don't += this here, we start appending to the
        # list attached to the active Application class.
        # Which is suboptimal.
        app_items = app.get_menu_items(user=self.user)
        for item in app_items:
            self.items.append(item)

        for plugin in plugins.OpalPlugin.list():
            for item in plugin.menuitems:
                self.items.append(item)

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
