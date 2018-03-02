# Templates in Opal

Opal uses a mixture of Django and Angular templates.

### Angular and Django templates, living in harmony

Natively, both Angular and Django use the {{ ... }} syntax for interpolation in templates. In order for Opal to be compatible with both Django **and** Angular interpolation, we use the `[[ ... ]]` notation for Angular interpolation and the {{ ... }} syntax for Django interpolation, which allows us to include Django template interpolation in templates designed to be rendered by Angular on the client side.

```html
<!-- app_details_snippet.html -->

<!-- Django interpolation uses {{ ... }} --> 
{{ OPAL_BRAND_NAME }} 

<!-- Angular interpolation uses [[ ... ]] -->
[[ Opal_VERSION ]]
```

### Generic Template URL

On many occasions we simply want to fetch a template from the server in our Angular code
without any further processing. Opal provides a default catchall HTML template url which
will render .html files direct from disk.

```python
# opal.urls

url(r'templates/(?P<template_name>[a-z_/]+.html)', views.RawTemplateView.as_view())
```

So if our template is at `./myapp/templates/foo/bar.html`, then the url `/templates/foo/bar.html`
will return it.

### Over-riding Opal templates
Opal's built-in templates can help you be productive rapidly, and prototype an application quickly. However, as your application develops you are likely to need to over-ride Opal's templates.
    
#### How to over-ride a template
In general, if you want to override an Opal template, you simply place a file in your application with the same filename, and in the same relative location as that file in Opal's source code. The version in your application will then over-ride Opal's version.
    
For example if you want to over-ride the default form for the Demographics model, you create a new template: 

```
yourapp/
    templates/
        forms/
            demographic_form.html
```
    
#### How do I know which template I need to over-ride?
This is a good question. At the moment, you will need to look at the Opal source code and work out which template is being used. In general these templates are regularly named - for example in the example above, all core Opal models have a corresponding template in `/templates/forms/` and `/templates/detail/`.

#### Template 'inheritance'
Some templates explicitly 'inherit' from another template using the [standard Django templating syntax `extends`](https://docs.djangoproject.com/en/2.0/ref/templates/builtins/#extends)

```html
# yourapp/templates/patient_detail.html
{% extends patient_detail_base.html %}
```
Other templates have less 'explicit' inheritance from other templates, such as EpisodeCategory detail templates, which _also_ inherit from `patient_detail_base.html` but this is handled 'under the hood' and therefore it can be quite difficult to trace back up the inheritance tree and find the correct parent template to over-ride. At present the documentation around this 'implicit' inheritance is not as clear as we would like it to be, but expect this to improve over time.
