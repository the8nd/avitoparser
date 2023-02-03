from bs4 import BeautifulSoup
import requests


# Парсим ссылку, забираем первые 3 результата.
def parser(url):
    while True:
        request = requests.get(url)
        bs = BeautifulSoup(request.text, "html.parser")
        links = bs.find_all("a", class_="link-link-MbQDP link-design-default-_nSbv title-root-zZCwT iva-item-title-py3i_ title-listRedesign-_rejR title-root_maxHeight-X6PsH")

        try:
            links[0] is None
            break
        except IndexError:
            pass

    i = 1
    final_links = []
    for link in links:
        final_links.append("https://www.avito.ru" + link["href"])
        if i == 3:
            break
        else:
            pass
        i += 1
    return final_links
