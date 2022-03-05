from requests import get
from bs4 import BeautifulSoup as bs


def fetch_url_meta(url: str = None):
    """fetch the meta title, desc, and banner url for target url or return None"""
    if url is None:
        return None

    r = get(url)
    content = r.content
    page = bs(content, "html.parser")
    meta_tags = page.find_all("meta")
    for tag in meta_tags:
        if tag.get("name") == "twitter:title":
            title = tag.get("content", "No title found")
        if tag.get("name") == "twitter:description":
            desc = tag.get("content", "No description found")
        if tag.get("name") == "twitter:image":
            banner = tag.get("content", None)

    return title, desc, banner
