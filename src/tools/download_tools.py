import base64
import urllib3
import shutil
import gdown


def google_drive_download(link: str, destinaton_file: str):
    gdown.download(link, destinaton_file, quiet=False)


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
