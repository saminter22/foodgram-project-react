python manage.py makemigrations
python manage.py migrate --noinput
python manage.py collectstatic --noinput
# python manage.py createsuperuser
# python manage.py loadcsv ../data/ingredients.csv Ingredient
python manage.py loadcsv ingredients.csv Ingredient