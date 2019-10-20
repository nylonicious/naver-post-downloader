import asyncio
import re
from json import loads as loadjson
from pathlib import Path
from sys import version_info
from urllib.parse import unquote, urlparse

import aiohttp


class NaverDownloader:
    def __init__(self, url):
        self.session = None
        asyncio.run(self.queue_downloads(url))

    async def queue_downloads(self, url):
        title = urlparse(url).query.split('volumeNo=')[1].split('&')[0]
        desiredpath = Path.cwd() / title
        if not desiredpath.exists():
            desiredpath.mkdir(parents=True)
        timeout = aiohttp.ClientTimeout(total=60)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as self.session:
            async with self.session.get(url) as response:
                text = await response.text()
                for i in text.split("data-linkdata=\'")[1:]:
                    linkdata = loadjson(i.split("\'>\n")[0])
                    if 'src' in linkdata:
                        picture_url = linkdata['src']
                        picture_id = unquote(urlparse(picture_url).path.split('/')[-1])
                        picture_name = re.sub('[<>:\"/|?*]', ' ', picture_id).strip()
                        picture_path = desiredpath / picture_name
                        if not desiredpath.is_file():
                            await self.download(picture_url, picture_path)
                    else:
                        print(f"Error string does not include 'src' {linkdata}")

    async def download(self, picture_url, picture_path):
        async with self.session.get(picture_url) as r:
            if r.status == 200:
                with open(picture_path, 'wb') as f:
                    print(f'Downloading {picture_url}')
                    f.write(await r.read())
            else:
                print(f'Error {r.status} while getting request for {picture_url}')


def main():
    urlinput = input('Enter post URL: ')
    NaverDownloader(urlinput)


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
