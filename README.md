# django_server
Python Django project for users to store their movies collections.

----
## Requirements

1. Install python version 3

2. Install dependent packags using requirements.txt
`pip3 install Django`

## Environment variables

1. Add following environment variables
`demo_client`
`demo_client_secret`
`mysql_host`
`mysql_user`
`mysql_password`
`mysql_db`

## Mysql Database setup

1. Update the mysql configurations in settings.py

2. Create mysql database with the name specified in the mysql configurations
`python3 manage.py migrate movie_collections`

## Server

1. Start the Django server in port 8000 
`python3 manage.py runserver 0.0.0.0:8000`
