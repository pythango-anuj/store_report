#Step1: Clone the project into the system by creating the local environment.

virtualenv venv
cd venv/scripts
./activate
git clone <Github repo link>


Step2: Install all the dependencies.

pip install -r requirements.txt


Step3: Run migrations to create the database tables.

python manage.py makemigrations
python manage.py migrate

Step4: Run commands created in apis folder to save the csv data to the respective models.

python manage.py <command name> 'your_google_drive_file_id' 'path_to_google_cloud_api_credentials_json_file.json'


Step5: Run the local server

python manage.py runserver


Now run the apis to get desired results
