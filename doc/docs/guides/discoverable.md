# Opal Discoverable Features

Opal makes extensive use of the case of discoverable features. These are pieces of
composable functionality that can be implemented by any plugin or application,
simply by declaring a class with the appropriate fields and methods implemented. (Details
of exactly which fields and methods vary by feature.)

### Defining Discoverable Features

The only thing required for a discoverable feature, is that it defines the name of
the module in which it should expect to find instances.

    from opal.core import discoverable

    class MyFeature(discoverable.DiscoverableFeature):
        module_name = 'myfeature'


This now gives us access to various interfaces which come with the library. We can access
all subclasses of `MyFeature` by calling `MyFeature.list()` - which will look through all
Django apps in our application, and look for a module named `myfeature.py`. The `list()`
method then returns any subclasses of `MyFeature`.

### Slugs and Display Names

We often want to define human and machine readable strings to name our features. Display
names are intended for people - feel free to include spaces, numbers and punctuation. Slugs
are intended for machines - so no spaces, numbers, hyphens, periods or other punctuation. By
default, if there is a display name and no explicit slug, we will 'slugify' the display name.

    class MyNameFeature(MyFeature):
        display_name = 'Hello World'

    print MyNameFeature.get_slug()
    # 'hello_world'

    class MySlugFeature(MyFeature):
        slug = 'this_is_a_slug'

    print MySlugFeature.get_slug()
    # 'this_is_a_slug'

### Retrieving Subclasses

Once we define a `display_name` or `slug` for subclasses of our feature, we can then fetch them via
the `get()` api.

    class RedFeature(MyFeature):
        slug = 'red_feature'

    MyFeature.get('red_feature') # -> RedFeature


### Sortable Features

We can make our feature sortable via an `order` property by including
 `discoverable.SortableFeature` as a parent class. This will ensure that `MyFeature.list()`
 respects the `.order` number of any subclass.


    class MyFeature(discoverable.DiscoverableFeature,
                     discoverable.SortableFeature):
         module_name = 'myfeature'

    class ThirdFeature(MyFeature):
        order = 3

    class FirstFeature(MyFeature):
        order = 1

    class SecondFeature(MyFeature):
        order = 2

    for f in MyFeature.list():
        print f.order, f

    # <class '*.*.FirstFeature'>, 1
    # <class '*.*.SecondFeature'>, 2
    # <class '*.*.ThirdFeature'>, 3


### Restrictable Features

We can ensure that only particular users can access a feature by including
 `discoverable.RestrictableFeature` as a parent class, and implementing the `visible_to`
 classmethod on any restricted subclasses.

     class MyFeature(discoverable.DiscoverableFeature, discoverable.RestrictableFeature):
         module_name = 'myfeature'

 For instance, a feature that was only visible to superusers could be implemented like this:

     class SuperuserFeature(MyFeature):

         @classmethod
         def visible_to(klass, user):
             return user.is_superuser

### Validating Features

Sometimes we wish to validate features so that we don't cause unintended consequences when
we implement subclasses of them. This is available via the `is_valid` classmethod. For instance,
if we wanted to implement a "Bomb" feature, which blew up every time the blow_up attribute was
true, we could to this as follows:

    class BombFeature(discoverable.DiscoverableFeature):
        module_name = 'bombs'
        blow_up = False

        @classmethod
        def is_valid(klass):
            if klass.blow_up == True:
                from opal.core.exceptions import InvalidDiscoverableFeatureError
                raise InvalidDiscoverableFeatureError('BLOWING UP')


    class Threat(BombFeature): pass
    # That's fine.

    class Detonate(BombFeature):
        blow_up = True
    # InvalidDiscoverableFeatureError: BLOWING UP

### Abstract Features

Sometimes we want to declare an abstract feature - something with reusable functionality
that isn't itself a new feature. We would rather not have our abstract feature show up
when we `list()` our base feature - because it's simply a programming convenience. This
is made simple by using `opal.utils.AbstractBase`.

        class A(discoverable.DiscoverableFeature):
            module_name = 'a'

        class AA(A, AbstractBase): pass

        class B(A): pass

        class C(AA): pass

        class D(AA): pass


        A.list()
        # [B, C, D]
