import time

from bs4 import BeautifulSoup
import requests


def parser(url):

    request = requests.get(url)
    bs = BeautifulSoup(request.text, "html.parser")
    links = bs.find("span", class_="page-title-count-wQ7pG")
    number = int(links.get_text().replace("\xa0", ""))
    links = bs.find_all("a", class_="link-link-MbQDP link-design-default-_nSbv title-root-zZCwT iva-item-title-py3i_ title-listRedesign-_rejR title-root_maxHeight-X6PsH")
    i = 1
    final_links = []
    for link in links:
        final_links.append("https://www.avito.ru" + link["href"])
        if i == 3:
            break
        else:
            pass
        i += 1
    return number, final_links
