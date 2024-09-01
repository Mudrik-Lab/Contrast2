# What is this
Contrast api repo

## About this project
Relevant docs:

* [parameters list](https://docs.google.com/spreadsheets/d/1ZrSEdJrwjikTdF_IJ3A6S6rGjU3UV7vx/edit#gid=1895565395)
* [structure](https://docs.google.com/document/d/11E_O41yWsau9-m7zqWexPv16NjtAX3u1/edit)

## Licensing

We believe in open-science!
The data is licensed under  CC-BY-SA-4.0 creative commons open license
and the [code here under the GNU GPLv3 open source license](./LICENSE)

## Contributing
see [CONTRIBUTING](./CONTRIBUTING.md)

# Technology and setup
python 3.10
Django + drf + django-filter
DB is postgresql
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


5. To load the pre-existing data you need to: 
   6. 
      * [Download this file](https://docs.google.com/spreadsheets/d/180WivImbqDv6MBabsHIt2dqvHKS-xDZz/edit?usp=sharing&ouid=115553053451052458030&rtpof=true&sd=true)
      in .xlsx format for **ConTrast**, or
      * [Download this file](https://docs.google.com/spreadsheets/d/16icOOS2XWvFel80k9Gw3pC-r3EsaOi-U/edit?usp=drive_link&ouid=115553053451052458030&rtpof=true&sd=true) in .xlsx format for **UnConTrast**
   7.
      * Save the file in
      ``` /studies/data``` directory for **ConTrast**, or
      * Save the file in
      ``` /uncontrast_studies/data``` directory for **UnConTrast**
   8. 
      * Run this command for **ConTrast**:

         ```
          python manage.py load_historic_data 
        ```
      * Run this command for **UnConTrast**:

         ```
          python manage.py load_uncon_data 
         ```   
Note: if you need to do this in bash (for example when migrating on the server):
      1. Copy the file to your drive and temporarily allow open access to viewer to view
      2. Follow the technique [here](https://chemicloud.com/blog/download-google-drive-files-using-wget/)
6. Create a superuser for yourself to start working
   ```
    python manage.py createsuperuser 
   ```
7. Run the dev server
    ```
   python manage.py runserver
   ```
 
### tests

```bash
poetry run python manage.py test
```
## Production

Currently this project is deployed to Heroku, via [github actions ci](./.github/workflows/ci.yml) 


## Setup for use in local environment as a "black box"
e.g when you work on the frontend

```bash
docker-compose up --build

# or to run in the background
docker-compose up -d --build

# You might drop --build, in case no changes in the poetry.lock file, but I'd suggest not to 
```
First run would be quite long because of docker building

Postgres has some issues currently with start order, so if you see errors in the logs,
just restart the compose a few times until it work

For doing the initial data load while running in compose:

After copying the file as above, and after verifying compose up --build as above

```bash
docker exec -it web_contrast_api python manage.py load_historic_data
# This runs the load, but inside the already running containers
```
### CI

As part of deploying this app we also deploy a [separately build react app](https://github.com/Mudrik-Lab/ContrastFront), and serve it from the django project
with django-spa. 

### Linting and formatting

With [ruff](https://github.com/astral-sh/ruff), not automated yet as part of CI

```bash
ruff check . --fix
ruff format
```

We're using `ruff format` for formatting please adjust prs accordingly