import base64
import os.path

import urllib3
import shutil
import gdown


def google_drive_download(model_drive_id: str, destination_file: str):
    # Make sure the base directory for destination file exists
    base_dir = os.path.dirname(destination_file)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    drive_link = f"https://drive.google.com/uc?id={model_drive_id}"
    gdown.download(drive_link, destination_file, quiet=False)


def onedrive_download(link: str, destination_file: str):
    download_url = create_onedrive_directdownload(link)
    http = urllib3.PoolManager()

    with open(destination_file, 'wb') as outfile:
        r = http.request('GET', download_url, preload_content=False)
        shutil.copyfileobj(r, outfile)
        outfile.close()
        r.release_conn()


def create_onedrive_directdownload(onedrive_link: str) -> str:
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/', '_').replace('+', '-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl
