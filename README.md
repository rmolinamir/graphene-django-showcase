# graphene-django-showcase
 Very basic graphene-django server setup with a PostgreSQL database & ubuntu vagrant machine.

# Local PostgreSQL setup

Django is a flexible framework for quickly creating Python applications. By default, Django applications are configured to store data into a lightweight SQLite database file. While this works well under some loads, a more traditional DBMS can improve performance in production.

In this guide, we’ll demonstrate how to install and configure PostgreSQL to use with your Django applications. We will install the necessary software, create database credentials for our application, and then start and configure a new Django project to use this backend.

## 1. Install the Components from the Ubuntu Repositories

Our first step will be install all of the pieces that we need from the repositories. We will install pip, the Python package manager, in order to install and manage our Python components. We will also install the database software and the associated libraries required to interact with them.

```
sudo apt-get update
sudo apt-get install python-pip python3-dev libpq-dev postgresql postgresql-contrib
```

## 2. Create a Database and Database User

By default, Postgres uses an authentication scheme called “peer authentication” for local connections. Basically, this means that if the user’s operating system username matches a valid Postgres username, that user can login with no further authentication.

During the Postgres installation, an operating system user named postgres was created to correspond to the postgres PostgreSQL administrative user. We need to change to this user to perform administrative tasks:

```
sudo su - postgres
```

You should now be in a shell session for the postgres user. Log into a Postgres session by typing:

```
psql
```

First, we will create a database for our Django project. Each project should have its own isolated database for security reasons. We will call our database myproject in this guide, but it’s always better to select something more descriptive. 
**Remember to end all commands at an SQL prompt with a semicolon.**

Create a database:

```
CREATE DATABASE hackernews;
```

Create a database user which we will use to connect to and interact with the database. Set the password to something strong and secure:

```
CREATE USER sample_user WITH PASSWORD 'sample_password';
```

Modify a few of the connection parameters for the user we just created. This will speed up database operations so that the correct values do not have to be queried and set each time a connection is established.

We are setting the default encoding to UTF-8, which Django expects. We are also setting the default transaction isolation scheme to “read committed”, which blocks reads from uncommitted transactions. Lastly, we are setting the timezone. By default, our Django projects will be set to use UTC:

```
ALTER ROLE sample_user SET client_encoding TO 'utf8';
ALTER ROLE sample_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sample_user SET timezone TO 'UTC';
```

Give our database user access rights to the database we created:

```
GRANT ALL PRIVILEGES ON DATABASE hackernews TO sample_user;
```

Exit the SQL prompt to get back to the postgres user’s shell session:

```
\q
```

Exit out of the postgres user’s shell session to get back to your regular user’s shell session:

```
exit
```

## 3. Install Django within a Virtual Environment

Follow this README guide based on a Django REST installation and setup: https://github.com/rmolinamir/django-rest-api/blob/master/README.md

### TODO: Update the guide to cover graphene-django GraphQL installation & setup

Requirements `requirements.txt` basic file:

```text
django==2.1.4
graphene-django==2.2.0
django-filter==2.0.0
django-graphql-jwt==0.1.5
postgres==3.0.0
psycopg2==2.8.4
```

## 4. Configure the Django Database Settings

Now that we have a project, we need to configure it to use the database we created.

Open the main Django project settings file located within the child project directory:

```
~/hackernews/hackernews/settings.py
```

Towards the bottom of the file, you will see a DATABASES section that looks like this:


```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

This is currently configured to use SQLite as a database. We need to change this so that our PostgreSQL database is used instead.

First, change the engine so that it uses the `postgresql_psycopg2` backend instead of the sqlite3 backend. For the NAME, use the name of your database. We also need to add login credentials. We need the username, password, and host to connect to. We’ll add and leave blank the port option so that the default is selected:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hackernews',
        'USER': 'sample_user',
        'PASSWORD': 'sample_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

## 5. Add a `settings.ini` file to hide important security credentials

1. Create a file somewhere on your server named `settings.ini`. I did this in `~/hackernews/hackernews/settings.ini`.

2. Add your config data to that file using the following format where the key could be an environmental variable and the value is a string. Note that you don't need to surround the value in quotes.

```ini
[section]
postgres_NAME=hackernews
postgres_USER=sample_user
postgres_PASSWORD=sample_password
```

3. Access these variables using python's `configparser` library. The code below could be in your Django project's `settings.py` file.

```python
from configparser import RawConfigParser

# Production ready environment variables for Django.
config = RawConfigParser()
config.read('hackernews/settings.ini')

postgres_NAME = config.get('section', 'postgres_NAME')
postgres_USER = config.get('section', 'postgres_USER')
postgres_PASSWORD = config.get('section', 'postgres_PASSWORD')
```

4. Update your database configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': postgres_NAME,
        'USER': postgres_USER,
        'PASSWORD': postgres_PASSWORD,
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

## 6. Migrate the Database and Test your Project

Now that the Django settings are configured, we can migrate our data structures to our database and test out the server.

We can begin by creating and applying migrations to our database. Since we don’t have any actual data yet, this will simply set up the initial database structure:

```python
python manage.py makemigrations
python manage.py migrate
```

After creating the database structure, we can create an administrative account by typing:

```python
python manage.py createsuperuser
```

You will be asked to select a username, provide an email address, and choose and confirm a password for the account.

Once you have an admin account set up, you can test that your database is performing correctly by starting up the Django development server:

```python
python manage.py runserver 0.0.0.0:8000
```

---

# Sources

1. [Digital Ocean - How To Use PostgreSQL with your Django Application on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04)
2. [joar - How to install psycopg2 with `pip` on Python?](https://stackoverflow.com/a/5450183/10246377)
3. [Braden Holt - Environment variables for Django](https://stackoverflow.com/a/49079880/10246377)