import csv
from django.core.management.base import BaseCommand
from apis.models import PollDetails
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime
from django.utils import timezone
import io

class Command(BaseCommand):
    help = 'Ingest data from Google Drive link into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_id', type=str, help='Google Drive file ID')
        parser.add_argument('credentials_file', type=str, help='Path to the service account credentials JSON file')

    def handle(self, *args, **options):
        file_id = options['file_id']
        credentials_file = options['credentials_file']

        # Authenticate with Google Drive API using service account credentials
        credentials = service_account.Credentials.from_service_account_file(credentials_file)
        drive_service = build('drive', 'v3', credentials=credentials)

        # Get the file content from Google Drive
        request = drive_service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        # Process the file_content and ingest data into the database
        self.ingest_data_from_csv(file_content.getvalue().decode('utf-8'))

    def ingest_data_from_csv(self, csv_content):
        # Process the CSV content and save data into the database
        reader = csv.reader(csv_content.splitlines())
        headers = next(reader)
        PollDetails.objects.all().delete()
        for row in reader:
            store_id, status, timestamp_utc = row
            timestamp_utc = timezone.make_aware(datetime(2023, 1, 22, 12, 9, 39, 388884), timezone.utc)
            PollDetails.objects.create(store_id=store_id, timestamp_utc=timestamp_utc, status=status)
