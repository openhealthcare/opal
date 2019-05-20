# Opal Settings

Opal applications provide a number of settings in the `settings.py` of your application.

## OPAL_AUTOCOMPLETE_SEARCH

Whether to enable autocomplete on search from the navbar. Defaults to False.

## OPAL_BRAND_NAME

The human readable form of your application name.
Displayed in the header by default.
Scaffolded applications start with whatever is passed in to `opal startproject`.

## OPAL_DEFAULT_SEARCH_FIELDS

Search fields that we look in by default when a user enters a search term.
Defaults to
```python
 [
    "demographics__hospital_number",
    "demographics__first_name",
    "demographics__surname"
]
```

## OPAL_LOG_OUT_DURATION

Opal will log users out if they have been inactive for greater than this value.
Scaffolded applications set this to 15 minutes by default. Unit is milliseconds.

## OPAL_LOGO_PATH

If `OPAL_LOGO_PATH` is set, the value is passed to the `{% static %}` templatetag to set the
`src` attribute of an image in the default application header and login screen.

## OPAL_FAVICON_PATH

If `OPAL_FAVICON_PATH` is set, the value is passed to the `{% static %}` templatetag
to set the `href` attribute for the favicon tag in the default application `<head>`

## VERSION_NUMBER

The version number of your application. Displayed in the header by default.
Scaffolded applications start at `<0.0.1`.

## DATE_DISPLAY_FORMAT

The format string to use when rendering dates using the `displayDate` Angular filter.
This defaults to `D MMM YYYY`.

Note that as formatting is performed by calling the Moment.js `.format()` method, the
date formatting syntax is neither Python `strftime` nor Django date formatting syntax.

For full details consult https://momentjs.com/docs/#/displaying/format/
