release: python manage.py migrate && python manage.py load_atlas_data
web: gunicorn contrast_api.wsgi --log-file -
