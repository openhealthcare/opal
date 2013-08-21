#!/bin/bash

BASE_DIR=`dirname $0`

if [[ $1 == 'py' ]]
then
	./manage.py test options patients
elif [[ $1 == 'js' ]]
then
	karma run $BASE_DIR/config/karma.conf.js
elif [[ $1 == 'js-watch' ]]
then
	karma start $BASE_DIR/config/karma.conf.js
else
	./manage.py test patients
	karma run $BASE_DIR/config/karma.conf.js
fi
