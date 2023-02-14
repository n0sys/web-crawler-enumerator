import requests
from bs4 import BeautifulSoup, Comment

def start(urls, settings): 
    # Define global variables used to store data collected
    global urls_list
    global history
    global output
    urls_list = urls
    history= urls  
    output = {'parameters':[], 'comments':[], 'urls':[], 'hidden_inputs':[]}

    # Crawl until no new URLs are found
    while len(urls_list) != 0:
        request = Crawl(urls_list[0].strip())
        #TODO: check response status code
        # What to do based on user's request
        if settings['crawl']:
            request.add_new_urls()
        if not settings['no-params']:
            request.get_parameters()
        if not settings['no-comments']:
            request.get_comments()
        if not settings['no-urls']:
            request.get_urls()
        if not settings['no-inputs']:
            request.get_inputs()
        urls_list.pop(0)
        # Add delay?
        # time.sleep(settings['sleep'])
        #soup = BeautifulSoup(str(request.session.content), 'html.parser')
    print(output)

class Crawl():
    def __init__(self, url):
        self.url = url
        self.session = requests.get(self.url, timeout=2.5)
        self.soup = BeautifulSoup(str(self.session.content), 'html.parser')

    def get_parameters(self):
        pass
    
    def get_comments(self):
        for comment in self.soup.find_all(string=lambda text: isinstance(text, Comment)):
            output['comments'].append(comment.extract())

    def get_urls(self):
        for link in self.soup.find_all('a'):
            output['urls'].append(link.get('href'))

    def get_inputs(self):
        pass

    def add_new_urls(self):
        pass