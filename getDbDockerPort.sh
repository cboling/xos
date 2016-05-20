#!/bin/bash
#
# Simple script to get port for postgreql database container.  Trying to do this
# with just the 'make'  $shell  directive is a bit cumbersome

docker inspect --format '{{ .NetworkSettings.Ports }}' $1 2>/dev/null | awk -F"[ }]" '{print $2}'