## Testing

The OPAL team recommend that you test your code. If you'd like to run karma tests, OPAL ships with a function to give you a default karma config.

In your karma config just require('[[ path to opal ]]/config/karma_defaults.js')

The function takes in the files you want to include and runs karma tests on them.

If you want to run coverage tests, pass in the base directory your application and the files you want to run coverage on.

locally this will put a at the base directory of your application + '../../htmlcov/js/'.

On travis it would put it on at the base directory of your application + '/coverage'
