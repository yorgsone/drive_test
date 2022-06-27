import os
import io
import tempfile
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, HttpError

DOWNLOADS_DIR = '.'


class google_driver():
    last_file = None  # tuple (file name, fileId)
    downloaded_file = None  # just the path of the downloaded file
    service = None  # the client for the google api

    def __new__(cls):
        try:
            cls.service = build('drive', 'v3')
            obj = super(google_driver, cls).__new__(cls)
            return obj
        except Exception as e:
            return None

    def upload_file(self, filename) -> bool:
        """uploads the file given and updates the class variable last_file and returns True if successful"""
        file_metadata = {
            'name': os.path.basename(os.path.normpath(filename)),
            'mimeType': '*/*',
        }
        if not os.path.isfile(filename):
            self.last_file = None
            self.downloaded_file = None
            raise FileNotFoundError

        media = MediaFileUpload(filename,
                                mimetype=file_metadata['mimeType'],
                                resumable=True)
        try:
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()
            self.last_file = (filename, file['id'])
            print(f"file {filename} uploaded")
            return True
        except Exception as e:
            print(f"Error while uploading file {filename}")
            return False
        finally:
            self.downloaded_file = None

    def download_last_file(self):
        """downloads the file that the last call to upload_file uploaded and sets the downloaded_file var to the file's name"""
        if not self.is_last_file_uploaded():
            raise 'last_file is None'

        with tempfile.NamedTemporaryFile(suffix='_'+os.path.basename(os.path.normpath(self.last_file[0])), dir=DOWNLOADS_DIR, delete=False) as df:
            request = self.service.files().get_media(fileId=self.last_file[1])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                df.write(fh.getbuffer())
            self.downloaded_file = df.name

    def is_last_file_uploaded(self):
        if self.last_file is None:
            return False
        try:
            metadata = self.service.files().get(
                fileId=self.last_file[1], fields='id').execute()
            return True
        except Exception:
            return False

    def list_files(self) -> list:
        """returns a list of tuples of all the files in the drive if successful and None if not |  (filename , fileId) format)"""
        pageToken = ''
        all_files_on_drive = []

        while pageToken is not None:
            try:
                results = self.service.files().list(
                    pageToken=pageToken, fields="nextPageToken, files(id, name)").execute()
            except Exception as e:
                print(e)
                return None
            items = results.get('files', [])
            if not items:
                print('No files found.')
                break
            for item in items:
                print(f"{item['name']} ({item['id']})")
                all_files_on_drive.append((item['name'], item['id']))
            pageToken = results.get('nextPageToken')
        return all_files_on_drive

    def delete_last_file(self):
        """deletes last_file from google Drive"""
        if self.last_file is None:
            raise 'last_file is None'
        try:
            self.service.files().delete(fileId=self.last_file[1]).execute()
            print(f"deleted {self.last_file[1]}")
        except Exception as e:
            print(f"An error occurred while deleting fileId: {self.last_file[1]}", e)

    def delete_file(self, fileId) -> bool:
        """given a fileId, deletes a file from google drive and return True if successful"""
        if fileId == '' or fileId == None:
            return False
        try:
            self.service.files().delete(fileId=fileId).execute()
            print(f"deleted {fileId}")
            return True
        except HttpError as error:
            print(f"An error occurred while deleting fileId: {fileId}", error)
            return False
