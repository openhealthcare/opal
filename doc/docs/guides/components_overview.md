The OPAL ecosystem comprises several types of components - let's take a look at how they all
hang together.

### Core OPAL framework

The core OPAL framework provides common patterns for writing clinical facing transactional 
applications. It is an opinionated approach, and amongst many other things, it gives you 
authentication and login mechanisms, hooks for integration with other clinical systems, a 
foundational [Clinical Data Model](datamodel.md), self-documenting, open JSON APIs for your 
data, a [Permission framework](roles_and_permissions.md) and a pattern library for UX 
components.

In addition to this, OPAL also provides some very common functionality as part of the core
framework, such as Search, rendering lists of patients, viewing the detail and history of
episodes of care, as well as multi-user realtime updates.

### Plugins

OPAL plugins are intended to provide high quality generic, composable, re-usable chunks of 
functionality that can be "dropped in" to an application. For example, installing the 
[Analytics](https://github.com/openhealthcare/opal-analytics) plugin allows you to integrate
your application with Google or Piwik Analytics with a minimum of fuss. The 
[Referral](https://github.com/openhealthcare/opal-referral) plugin provides the plumbing for 
building complex inter-team referrals within an institution.

Plugins have a [rich plugin API](plugins.md) they can hook into to aid the seamlessness, and
many examples can be found by inspecting the source of [existing plugins](plugins_list.md). 
This includes defining patient Flows through the system, adding to the core JSON API, ovrerriding
templates, adding patient Actions, as well as much more.

TODO: Write the Plugin Tutorial

### Applications

An application is the collection of configuration and bespoke functionality that would be 
provided to an individual institution - e.g. it's the thing that you would look to deploy.

Example applications include [elCID](https://github.com/openhealthcare/elcid) - a for managing
infection patients, or [OPAL-Renal](https://github.com/openhealthcare/opal-renal) - an MDT & 
handover tool for Renal wards. 

A hospital might have multiple services running on one `Application`, or multiple `Applications`
that integrate with one another.

## Opinionated but Pluggable

OPAL is an Opinionated Framework. It expects the developer to structure code in a 
certain way. 

OPAL expects features to be implemented as single page Angular.js applications, with the server
mostly figuring as an API endpoint for reading and writing data.

TODO: Expand on this

That said, the technology stack of Django, Angular & Bootstrap allows the confident user a huge
degree of flexibility when writing their own applications and plugins. 

For instance, there is nothing to _stop_ a developer from implementing a part of the functionality 
in some other Javascript framework, and simply calling the [JSON API](json_api.md). However, by
doing so, the developer will lose a large collection of pre-existing libraries, conventions et cetera.
While possible, this approach is not likely to be officially supported in the medium term..
