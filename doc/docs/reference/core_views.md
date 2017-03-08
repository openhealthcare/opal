# opal.core.views

Opal provides a number of helper functions and classes for working with Django views.

## opal.core.views.LoginRequiredMixin

A Mixin class that can be used with a view to ensure that we require users to be
logged in in order to access the view.

```python
class MyView(LoginRequiredMixin, View):
    pass
```

## opal.core.views.json_response

Returns a Django HTTPResponse instance with the data argument serialized using the
correct serialization class.

```python
json_response(data, status_code=200):
```
