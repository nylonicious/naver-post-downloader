import asyncio
import re
from json import loads as loadjson
from pathlib import Path
from sys import version_info
from urllib.parse import unquote, urlparse

import aiohttp


async def queue_downloads(url):
    title = urlparse(url).query.split('volumeNo=')[1].split('&')[0]
    desired_path = Path.cwd() / title
    desired_path.mkdir(parents=False, exist_ok=True)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            text = await response.text()
            for item in text.split("data-linkdata=\'")[1:]:
                linkdata = loadjson(item.split("\'>\n")[0])
                if 'src' in linkdata:
                    picture_url = linkdata['src']
                    picture_id = unquote(urlparse(picture_url).path.split('/')[-1])
                    picture_name = re.sub('[<>:\"/|?*]', ' ', picture_id).strip()
                    picture_path = desired_path / picture_name
                    if not picture_path.is_file():
                        await download(session, picture_url, picture_path)
                else:
                    print(f"Error string does not include 'src' {linkdata}")


async def download(session, picture_url, picture_path):
    async with session.get(picture_url) as r:
        if r.status == 200:
            picture_path.write_bytes(await r.read())
            print(f'Downloaded {picture_url}')
        else:
            print(f'Error {r.status} while getting request for {picture_url}')


def main():
    urlinput = input('Enter post URL: ')
    asyncio.run(queue_downloads(urlinput))


if __name__ == '__main__':
    assert version_info >= (3, 7), 'Script requires Python 3.7+.'
    main()
