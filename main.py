from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, HttpError
import io
import tempfile
import os

DOWNLOADS_DIR = '.'


class google_driver():
    originalFileHash = None
    lastFile = None
    service = None

    def __new__(cls):
        try:
            cls.service = build('drive', 'v3')
            obj = super(google_driver, cls).__new__(cls)
            return obj
        except Exception as e:
            return None

    def upload_file(self, filename) -> bool:
        """uploads the file given and updates the class variable lastFile and returns True if successful"""
        file_metadata = {
            'name': filename,
            'mimeType': '*/*',
        }
        if not os.path.isfile(filename):
            lastFile = None
            originalFileHash = None
            print(f"{filename} does not exist")
            return False

        media = MediaFileUpload(filename,
                                mimetype=file_metadata['mimeType'],
                                resumable=True)
        try:
            file = self.service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()
            if file is not None:
                self.lastFile = (filename, file['id'])
                print(f"file {filename} uploaded")
        except Exception as e:
            print(f"Error while uploading file {filename}")
            return False
        return True

    def download_lastFile(self) -> str:
        """downloads the file that the last call to upload_file uploaded and returns the downloaded file's name"""
        if not self.isUploaded():
            return None

        with tempfile.NamedTemporaryFile(suffix='_'+self.lastFile[0], dir=DOWNLOADS_DIR, delete=False) as df:
            request = self.service.files().get_media(fileId=self.lastFile[1])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                df.write(fh.getbuffer())
            return df.name

    def isUploaded(self, fileId=None):
        if fileId is None:
            if self.lastFile is None:
                return None
            fileId = self.lastFile[1]
        try:
            metadata = self.service.files().get(fileId=fileId, fields='id').execute()
            return True
        except Exception:
            return False

    def list_files(self):
        pageToken = ''
        print('Files:')
        while pageToken is not None:
            try:
                results = self.service.files().list(
                    pageToken=pageToken, fields="nextPageToken, files(id, name)").execute()
            except Exception as e:
                print("failed to list google drive files", e)
                return
            items = results.get('files', [])
            if not items:
                print('No files found.')
                return
            for item in items:
                print(f"{item['name']} ({item['id']})")
            pageToken = results.get('nextPageToken')

    def delete_file(self, fileId=None):
        """deletes file with the given fileId from google Drive and if fileId is None, the lastFile is getting deleted"""
        if fileId is None:
            if self.lastFile is None:
                return
            fileId = self.lastFile[1]
        try:
            self.service.files().delete(fileId=fileId).execute()
            print(f"deleted {fileId}")
        except HttpError as error:
            print(f"An error occurred while deleting fileId: {fileId}", error)
