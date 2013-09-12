#!/bin/sh

user=postgres
dbname="imagedownloader"
python=/usr/local/bin/python2.7

dropdb $dbname -U $user
createdb  $dbname -U $user

$python manage.py syncdb
$python manage.py migrate
