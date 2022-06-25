from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload,HttpError
import io
import tempfile

DOWNLOADS_DIR = '.'

class google_driver():
    def __init__(self):
        self.lastFile = None
        self.service = build('drive', 'v3')
    
    def upload_file(self, filename):
        file_metadata = {
        'name': filename,
        'mimeType': '*/*',
        }
        media = MediaFileUpload(filename,
                    mimetype=file_metadata['mimeType'],
                    resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        if file is not None:
            self.lastFile = (filename, file['id'])
    
    def download_lastFile(self) -> str:
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
                print("Download %d%%." % int(status.progress() * 100))
            return df.name

    def isUploaded(self, fileId=None):
        if fileId is None:
            if self.lastFile is None:
                return None
            fileId = self.lastFile[1]
        try:
            metadata = self.service.files().get(fileId=fileId, fields='id').execute()
            return True
        except Exception as err:
            return False
    
    def listOrDeleteFiles(self, delete=False):
        results = self.service.files().list(
        pageSize=100, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))
            if delete:
                try:
                    self.service.files().delete(fileId=item['id']).execute()
                except HttpError as error:
                    print('An error occurred: ', error)

driver = google_driver()
driver.listFiles()