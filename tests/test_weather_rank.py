import pytest


@pytest.mark.asyncio
async def test_get_map() -> None:
    import re

    import httpx
    from bs4 import BeautifulSoup, Tag

    url = ''
    async with httpx.AsyncClient() as ctx:
        res = await ctx.get(
            'http://www.nmc.cn/publish/observations/hourly-temperature.html'
        )
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            img_element: Tag | None = soup.select_one('.imgblock > img')
            if img_element:
                img_url: str | list[str] | None = img_element.get('src')
                if isinstance(img_url, str):
                    url = img_url
    url_pattern = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$')
    assert url_pattern.match(url), f"URL '{url}' is not a valid web link"
