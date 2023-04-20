from bs4 import BeautifulSoup
import requests
import asyncio


# Парсим ссылку, забираем первые 3 результата.
async def avparser(url):
    while True:
        request = requests.get(url)
        print(request.status_code)
        bs = BeautifulSoup(request.text, "html.parser")
        links = bs.find_all("a", class_="link-link-MbQDP link-design-default-_nSbv title-root-zZCwT iva-item-title-py3i_ title-listRedesign-_rejR title-root_maxHeight-X6PsH")
        titles = bs.find_all("h3", class_="title-root-zZCwT iva-item-title-py3i_ title-listRedesign-_rejR title-root_maxHeight-X6PsH text-text-LurtD text-size-s-BxGpL text-bold-SinUO")
        prices = bs.find_all("span", class_="price-text-_YGDY text-text-LurtD text-size-s-BxGpL")
        try:
            links[0] is None
            break
        except IndexError:
            await asyncio.sleep(5)

    i = 1
    b = 1
    j = 1
    final_links = []
    final_titles = []
    final_prices = []
    for link in links:
        final_links.append("https://www.avito.ru" + link["href"])
        if i == 3:
            break
        else:
            pass
        i += 1
    for title in titles:
        final_titles.append(title.getText())
        if b == 3:
            break
        else:
            pass
        b += 1
    for price in prices:
        final_prices.append(price.getText().replace('\xa0', ''))
        if j == 3:
            break
        else:
            pass
        j += 1
    return final_links, final_titles, final_prices
