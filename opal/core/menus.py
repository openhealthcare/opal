"""
Helpers for constructing extensible menus in Opal applications
"""
import warnings

warnings.simplefilter('once', DeprecationWarning)


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
        warnthem = """
Declaring Opal menu items as python dicts will no longer work in Opal 0.9.0.

Menu items should be instances of opal.core.menus.MenuItem

You should convert {0}

Please consult the Opal documentation on menus for more information.
"""
        for item in app_items:
            if isinstance(item, MenuItem):
                self.items.append(item)
            else:
                self.items.append(MenuItem(**item))
                warnings.warn(warnthem.format(item), DeprecationWarning,
                              stacklevel=2)

        for plugin in plugins.OpalPlugin.list():
            for item in plugin.menuitems:
                if isinstance(item, MenuItem):
                    self.items.append(item)
                else:
                    self.items.append(MenuItem(**item))
                    warnings.warn(warnthem.format(item), DeprecationWarning,
                                  stacklevel=2)

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
