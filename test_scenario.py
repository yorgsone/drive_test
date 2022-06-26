import os
import pytest
from google_driver_class import google_driver
from equal_file_hashes import equal_file_hashes

GAC = 'GOOGLE_APPLICATION_CREDENTIALS'

@pytest.mark.parametrize("file_a,file_b, expected", [
    ('test_file.txt','test_file2.txt', False),
    ('test_file.txt', 'test_file.txt', True)
])
def test_equal_file_hashes(file_a, file_b, expected):
    assert equal_file_hashes(file_a, file_b) == expected

@pytest.fixture
def default_google_driver():
    return google_driver()


def test_credentials(default_google_driver):
    gd = default_google_driver
    creds_env = os.environ.get(GAC)

    assert (creds_env == None and gd == None)\
        or (not os.path.isfile(creds_env) and gd == None)\
        or (os.path.isfile(creds_env) and gd == None)\
        or gd != None

@pytest.mark.parametrize("failing_to_upload", [
    "",
    "filedoesntexist",
])
def test_failed_upload(default_google_driver, failing_to_upload):
    gd = default_google_driver
    if gd is None:
        return
    try:
        uploaded = gd.upload_file(failing_to_upload)
        if uploaded:
            assert False
    except FileNotFoundError:
        return

@pytest.mark.parametrize("to_upload", [
    "test_file.txt"
])
def test_upload(default_google_driver, to_upload):
    gd = default_google_driver
    if gd is None:
        return
    try:
        uploaded = gd.upload_file(to_upload)
        if not uploaded or not gd.is_last_file_uploaded:
            assert False
    except Exception:
        assert False

@pytest.mark.parametrize("to_download", [
    "test_file.txt"
])
def test_download_and_delete_from_drive(default_google_driver, to_download):
    gd = default_google_driver
    if gd is None:
        return
    try:
        uploaded = gd.upload_file(to_download)
        if not uploaded:
            return
        gd.download_last_file()
        if not os.path.isfile(gd.downloaded_file):
            assert False
        gd.delete_last_file()
    except Exception:
        assert False

@pytest.mark.parametrize("file, expected", [
    ("test_file.txt", True),
    ("", FileNotFoundError())
])
def test_scenario(default_google_driver, file, expected):
    gd = default_google_driver
    if gd is None:
        return

    try:
        uploaded = gd.upload_file(file)
        assert uploaded and gd.is_last_file_uploaded()
        gd.download_last_file()
        assert os.path.isfile(gd.downloaded_file)
        assert equal_file_hashes(file, gd.downloaded_file)
    except Exception as e:
        assert type(e) == type(expected)
