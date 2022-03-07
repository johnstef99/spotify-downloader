from requests import get
from bs4 import BeautifulSoup

from spotdl.lyrics.lyric_base import LyricBase
from spotdl.lyrics.exceptions import LyricsNotFoundError

import logging
logger = logging.getLogger(__name__)


user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
}


class Genius(LyricBase):
    """
    Fetch lyrics from Genius.

    Examples
    --------
    + Fetching lyrics for *"Tobu - Cruel"*:

        >>> from spotdl.lyrics.providers import Genius
        >>> genius = Genius()
        >>> lyrics = genius.from_query("tobu cruel")
        >>> print(lyrics)
    """

    def from_query(self, query: str, linesep="\n", timeout=None):
        logger.debug(
            'Fetching lyrics for the search query on "{}".'.format(query))
        return self.get_lyrics_genius(query)

    def get_lyrics_genius(self, query: str) -> str:
        """
        `str` `query` : query to search at genius.com
        RETURNS `str`: Lyrics of the song.
        Gets the lyrics of the song.
        """
        headers = {
            "Authorization": "Bearer alXXDbPZtK1m2RrZ8I4k2Hn8Ahsd0Gh_o076HYvcdlBvmc0ULL1H8Z8xRlew5qaG",
        }
        headers.update(user_agent)

        api_search_url = "https://api.genius.com/search"
        search_query = query

        api_response = get(api_search_url, params={
                           "q": search_query}, headers=headers)
        if not api_response.ok:
            return ""
        api_json = api_response.json()

        try:
            song_id = api_json["response"]["hits"][0]["result"]["id"]
        except (IndexError, KeyError):
            return ""

        song_api_url = f"https://api.genius.com/songs/{song_id}"
        api_response = get(song_api_url, headers=headers)
        if not api_response.ok:
            return ""
        api_json = api_response.json()

        song_url = api_json["response"]["song"]["url"]
        genius_page = get(song_url, headers=user_agent)
        if not genius_page.ok:
            return ""

        soup = BeautifulSoup(genius_page.text.replace(
            "<br/>", "\n"), "html.parser")
        lyrics_div = soup.select_one("div.lyrics")

        if lyrics_div is not None:
            return lyrics_div.get_text().strip()

        lyrics_containers = soup.select(
            "div[class^=Lyrics__Container]")
        lyrics = "\n".join(con.get_text()
                           for con in lyrics_containers)
        return lyrics.strip()
