
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def extract_job_description(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Please provide a valid HTTP(S) URL.")

    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "ResumeTailor/1.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that aren't useful job-description content.
    for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)

    if len(text) < 200:
        raise ValueError(
            "Too little text extracted. The page may require JavaScript "
            "or a login, or it may block automated requests."
        )

    return text[:30_000]  # Limit input size
