# Templates in Opal

Opal uses a mixture of Django and Angular templates.

### Angular and Django templates, living in harmony

Natively, both Angular and Django use the {{ ... }} syntax for interpolation in
templates. In order for Opal to be compatible with both Django **and** Angular
interpolation, we use the `[[ ... ]]` notation for Angular interpolation and
the {{ ... }} syntax for Django interpolation, which allows us to include
Django template interpolation in templates designed to be rendered by Angular on
the client side.

```html
<!-- app_details_snippet.html -->

<!-- Django interpolation uses {{ ... }} -->
{{ OPAL_BRAND_NAME }}

<!-- Angular interpolation uses [[ ... ]] -->
[[ OPAL_BRAND_NAME ]]
```

### Generic Template URL

On many occasions we want to fetch a template from the server in our Angular code
without any further processing. Opal provides a default catchall HTML template url which
will render .html files direct from disk.

```python
# opal.urls

url(r'templates/(?P<template_name>[a-z_/]+.html)', views.RawTemplateView.as_view())
```

So if our template is at `./myapp/templates/foo/bar.html`, then the url
`/templates/foo/bar.html` will return it.

### Overriding Opal templates

Opal's built-in templates can help you be productive rapidly, and prototype an
application quickly. However, as your application develops you are likely to
need to override Opal's templates.

#### How to override a template

In general, if you want to override an Opal template, you will need to place a file
in your application with the same filename, and at the same relative location
as that file in Opal's source code. The Django template loader system will then
select the file from your application rather than the file in the Opal templates
directory.

For example if you want to override the default form for the Demographics
model, you create a new template:

```
yourapp/
    templates/
        forms/
            demographic_form.html
```

#### How do I know which template I need to override?

You will need to look at the templates in the Opal source
code and work out which one is being used.

Templates related to the display or editing of **subrecords**, are named
according to the [API name](../reference/subrecords.md#subrecordget_api_name) of the subrecord
and can be found in `./templates/forms` or `./templates/records/`.

For instance, the demographics form is located in `./templates/forms/demographics_form.html` and
the display template for a demographics instance is located in
`./templates/records/demographics.html`.

Templates related to **form widgets** are found in `./templates/_helpers` and named after the
type of widget they represent. For instance, the template for the `{% input %}`
templatetag is found at `./templates/_helpers/input.html`

Once logged in, the **main layout** of the application is provided by the template at
`./templates/opal.html`. By default, this simply extends
`./templates/app_layouts/layout_base.html`.

The **patient detail** page is provided by the template at `./templates/patient_detail.html`. By
default this uses the page layout from `./templates/patient_detail_base.html`.

The detail template for an **episode** of any given episode category is set on the
[category class](../reference/episode_categories.md#episodecategorydetail_template).
