python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --no-input
# python manage.py createsuperuser
# python manage.py loadcsv ../data/ingredients.csv Ingredient
python3 manage.py loadcsv ingredients.csv Ingredient