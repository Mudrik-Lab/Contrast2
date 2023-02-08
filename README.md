# What is this
Contrast2 api repo

## About this project
Relevant docs:

* [parameters list](https://docs.google.com/spreadsheets/d/1ZrSEdJrwjikTdF_IJ3A6S6rGjU3UV7vx/edit#gid=1895565395)
* [structure](https://docs.google.com/document/d/11E_O41yWsau9-m7zqWexPv16NjtAX3u1/edit)

## Contributing


# Technology and setup
python 3.10
Django + drf + django-filter
DB in postgresql
Django configurations for settings file
Common practice middlewares (timezones, querycount)

## setup
### Setup for development

1. Python virtual environment:   
We are using poetry to manage the projects dependencies.   
   **Install Poetry** - https://python-poetry.org/docs/#installation
        

2. Get the code:    
Clone this project    
   ```
   git clone git@github.com:Mudrik-Lab/Contrast2.git
   ```
   

3. Install dependencies:    
enter projects directory and install dependencies using Poetry. Poetry will look for pyproject.toml file
    ```
    cd contrast-api
    poetry install
    ```
   And enter the virtual env created by Poetry:
   ```
   poetry shell
   ```
   
---
### From this point in the setup you should run the commands while you are inside the virtual env / poetry shell 

---

4. Database:    
We are currently using postgres. You need to set up a user,
   * After you have installed postgres, enter postgres cli client:    
   ```
   sudo su - postgres
   psql
   ```
   * create a database, a user and a role
    ```
    CREATE DATABASE contrast_api_db;
    CREATE USER contrast_api_user WITH PASSWORD 'contrast_api_pass';
    ALTER ROLE contrast_api_user SET client_encoding TO 'utf8';
    GRANT ALL PRIVILEGES ON DATABASE contrast_api_db TO contrast_api_user;
    ALTER ROLE contrast_api_user CREATEDB;
    ALTER DATABASE contrast_api_db OWNER TO contrast_api_user;
   ```
   * to exit postgres cli:   
   `Ctrl+D`
   
     and then exit superuser shell   
   `exit`
    * Now you can migrate the data:
   ```   
   python manage.py migrate   
   ```   

5. Create a superuser for yourself to start working
    ```
    python manage.py createsuperuser 
   ```

6. Run the dev server
    ```
   python manage.py runserver
   ```
 
### tests

```bash
poetry run python manage.py test
```
## Production

Ready to run as container (see dockerfile). Environment is determined by DJANGO_CONFIGURATION env variable
which maps to class in settings.py. Note that in non local dev environments DEBUG=False so django won't magically serve statics
You can use Nginx for that (before the django service, see, the [nginx.conf](deploy/nginx.conf) for a reference)
or install [whitenoise](https://whitenoise.evans.io/) and add it as a middleware. This is a common pattern for PAAS deployments

## Setup for use in local environment as a "black box"
e.g when you work on the frontend

```bash
docker-compose up
```
First run would be quite long because of docker building

Postgres has some issues currently with start order, so if you see errors in the logs,
just restart the compose a few times until it work


### CI
Depends on where you run, we support an initial github actions CI out of the box -declared [here](./.github/workflows/ci.yml) and 

## Not included libraries you might consider adding
* [Django nested inlines](https://github.com/s-block/django-nested-inline) for "nesting inlines" in the admin
* [Celery](https://docs.celeryq.dev/en/stable/) for async, scheduled or "out of request/response cycle" behavior
* [django admin reorder](https://pypi.org/project/django-modeladmin-reorder/) to customize the admin further