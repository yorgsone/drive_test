import os
import pytest
from google_driver_class import google_driver
from equal_file_hashes import equal_file_hashes

GAC = 'GOOGLE_APPLICATION_CREDENTIALS'

def test_credentials():
    gd = google_driver()
    creds_env = os.environ.get(GAC)

    assert  (creds_env == None and gd == None)\
            or (not os.path.isfile(creds_env) and gd == None)\
            or (os.path.isfile(creds_env) and gd == None)\
            or gd != None

@pytest.mark.parametrize("failing_to_upload", [
    "",
    "filedoesntexist",
])
def test_failed_upload(failing_to_upload):
    gd = google_driver()
    if gd is None:
        return
    try:
        uploaded = gd.upload_file(failing_to_upload)
        if uploaded:
           assert False 
    except FileNotFoundError:
        return

@pytest.mark.parametrize("to_upload", [
    "a_test_file.txt",
])
def test_upload(to_upload):
    gd = google_driver()
    if gd is None:
        return
    try:
        uploaded = gd.upload_file(to_upload)
        if not uploaded or not gd.is_last_file_uploaded:
            assert False
    except Exception:
        assert False

