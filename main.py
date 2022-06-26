from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, HttpError
import io
import tempfile
import os
import hashlib

DOWNLOADS_DIR = '.'

def compare_files(a, b) -> bool:
    """computes the hash of each file and compares them
    returns True if they are the equal"""
    BUF_SIZE = 4096

    a_hashed = hashlib.sha1()
    b_hashed = hashlib.sha1()
   
    with open(a, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            a_hashed.update(data)
    
    with open(b, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            b_hashed.update(data)
    print(a_hashed.hexdigest() , b_hashed.hexdigest())
    return a_hashed.hexdigest() == b_hashed.hexdigest()

class google_driver():
    last_file = None
    downloaded_file = None
    service = None

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
            self.downloaded_file

    def download_last_file(self) -> str:
        """downloads the file that the last call to upload_file uploaded and returns the downloaded file's name"""
        if not self.is_uploaded():
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
            return df.name

    def is_uploaded(self):
        if self.last_file is None:
            return False
        try:
            metadata = self.service.files().get(fileId=self.last_file[1], fields='id').execute()
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
        except HttpError as error:
            print(f"An error occurred while deleting fileId: {self.last_file[1]}", error)

    def delete_file(self, fileId)->bool:
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

gd = google_driver()
gd.upload_file('filepath_to_be_uploaded')
all_files = gd.list_files()
print(all_files)
gd.download_last_file()
if compare_files(gd.last_file[0], gd.downloaded_file):
    print("a == b")
else:
    print("a != b")
gd.delete_last_file()