echo "Deployment started ..."
nohup python random_data_generator.py >random_data_generator.out &
echo "Starting random data generator started"
python manage.py makemigrations
python manage.py migrate
echo "Completed migrations"
nohup python monitor.py > monitor.out &
echo "Started folder monitoring"

python manage.py runserver 0.0.0.0:8000
