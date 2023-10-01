import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from .user_agents import get_useragent

GOOGLE_SEARCH_URL = "https://www.google.com/search"


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def _get_search_results(term, num_results, lang, start, proxies, timeout):
    try:
        params = {
            "q": term,
            "num": num_results + 2,
            "hl": lang,
            "start": start,
        }
        resp = requests.get(
            GOOGLE_SEARCH_URL,
            headers={"User-Agent": get_useragent()},
            params=params,
            proxies=proxies,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.text
    except RequestException as e:
        print(f"Error: {e}")
        return None


def search(term, num_results=10, lang="en", proxy=None, advanced=False, timeout=5):
    escaped_term = requests.utils.quote(term)

    # Proxy
    proxies = {"https": proxy} if proxy else None

    # Fetch
    start = 0
    while start < num_results:
        html = _get_search_results(escaped_term, num_results - start, lang, start, proxies, timeout)
        if html is None:
            return

        soup = BeautifulSoup(html, "html.parser")
        result_blocks = soup.find_all("div", class_="g")
        
        if not result_blocks:
            start += 1

        for result in result_blocks:
            link = result.find("a", href=True)
            title = result.find("h3")
            description_box = result.find("div", class_="s")
            if description_box:
                description = description_box.text
                if link and title and description:
                    start += 1
                    if advanced:
                        yield SearchResult(link["href"], title.text, description)
                    else:
                        yield link["href"]

    # Sleep at the end of the search, if needed
    if start == 0:
        return

