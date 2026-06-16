import requests


class NewsSource:

    def __init__(self, name, url, category):
        self.name = name
        self.url = url
        categorys = category.split(',')
        categorys = [x.strip() for x in categorys]
        self.category = categorys
    def get_news(self):
        response = requests.get(self.url, headers={'User-Agent': 'dagNieuws/1.0'})
        return response.text