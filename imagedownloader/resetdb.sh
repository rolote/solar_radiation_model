#!/bin/sh

user=postgres
dbname="imagedownloader"

dropdb $dbname -U $user
createdb  $dbname -U $user

python2.7 manage.py syncdb
python2.7 manage.py migrate
