"""
Tools for downloading APKs from APKPure
"""

import io
import logging
from typing import Optional, BinaryIO

import requests
from tqdm import tqdm
from DrissionPage import SessionPage
from DrissionPage.errors import ElementNotFoundError

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


def get_file_size(url: str) -> Optional[int]:
    """
    Get the size of the file at the given URL.

    Args:
        url (str): URL of the file.

    Returns:
        Optional[int]: Size of the file in bytes, or None if the size cannot be determined.
    """
    response = requests.head(url, headers=HEADERS, timeout=10)
    content_length = response.headers.get("Content-Length")
    return int(content_length) if content_length is not None else None


def download_single(keywords: str) -> Optional[BinaryIO]:
    """
    Download a single APK from APKPure

    Args:
        keywords (str): Search keywords

    Returns:
        BinaryIO: Downloaded file pointer
    """
    page = SessionPage()
    keywords = "%20".join(keywords.strip().split())
    url = f"https://apkpure.net/search?q={keywords}"
    page.get(url)
    try:
        first_info = page.ele(".first-info").attr("href")
    except ElementNotFoundError as e:
        logging.log(logging.WARNING, e)
        return
    page.get(f"{first_info}/download")

    try:
        dismiss_btn = page.ele("#dismiss-button")
        dismiss_btn.click()
    except ElementNotFoundError:
        pass

    download_link = page.ele(".apk").ele(".download-btn").attr("href")

    file_size = get_file_size(download_link)

    response = requests.get(download_link, stream=True, timeout=300, headers=HEADERS)
    response.raise_for_status()

    file_stream = io.BytesIO()

    if file_size:  # If file size is known
        with tqdm(
            total=file_size, unit="B", unit_scale=True, desc="Downloading"
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    file_stream.write(chunk)
                    pbar.update(len(chunk))
    else:  # If file size is not known
        for chunk in response.iter_content(chunk_size=8192):
            file_stream.write(chunk)

    file_stream.seek(0)
    return file_stream
