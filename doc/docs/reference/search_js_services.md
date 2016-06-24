# OPAL Core Search Javascript Services

## Filter

The Angular Service for saved filters. Maps to the model `opal.models.Filter`.

### save(attrs)

Save this filter with the attributes passed in. If there is no ID, this is taken to be a create.

### destroy()

Destroy this filter.

## filtersLoader

Loader service that will resolve with instantiated `Filter` objects for each of the current
user's filters.

## FilterResource

Angular $resource for Filter objects.
