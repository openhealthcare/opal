# Theming your Opal application

Opal applicatoins ship with a basic theme that is good enough to use in production,
but we expect that most applications will wish to customise the look and feel.
Accordingly, we support a range of different theming options.

## Basic Options

Basic theming comes in the form of settings which can be tweaked.
You can give your application a different name, logo, and set the version number.

## Overriding CSS and templates

You can override the CSS to change the core colours et cetera, and there are some
key templates that you can tweak.

### Changing the home page.

By default, the home page of an opal application simply renders the `welcome.html`
template.

## Form styles

Opal defaults to using Bootstrap `form-horizontal` style widgets. That means that the
label is rendered on the same line as the form widget. You can change this to the
vertical (default Bootstrap style )for an individual form widget by passing the `style`
argument:

```html
{% input field="Demographics.first_name" style="vertical" %}
```

## Custom Themes

Comprehensive re-skins likely require you to write your own Opal theme. You can
do this within an application directly, or if you definitely have a theme you
want to use in multiple applications, you can write a theme plugin.

### Example themes

We have created a number of example themes for Opal. These are intended to demonstrate
the possibilities rather than for production use.

* [Slack Skin](http://github.com/openhealthcare/opal-slacktheme)
* [Google Inbox Skin](http://github.com/openhealthcare/opal-inboxtheme)
