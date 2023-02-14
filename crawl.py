import requests
from bs4 import BeautifulSoup, Comment

def start(urls, settings): 
    # Define global variables used to store data collected
    global urls_list
    global history
    global output
    history: list= []
    urls_list: list = urls 
    output = {'parameters':[], 'comments':[], 'urls':[], 'hidden_forms':[]}

    # Crawl until no new URLs are found
    while len(urls_list) != 0:
        history.append(urls_list[0].strip())
        request = Crawl(urls_list[0].strip(),
            settings['no-forms']
            )
        #TODO: check response status code
        # What to do based on user's request
        if not settings['no-comments']:
            request.get_comments()
        #TODO: add js web suppport - if site requires js, wont load with requests library
        request.get_urls()
        if not settings['no-params']:
            request.get_parameters()
        history.append(urls_list[0].strip())
        urls_list.pop(0)
        if settings['crawl']:
            request.add_new_urls()
        # Add delay?
        # time.sleep(settings['sleep'])
    print(output)

class Crawl():
    def __init__(self, url, no_forms):
        self.url = url
        self.session = requests.get(self.url, timeout=2.5)
        self.soup = BeautifulSoup(str(self.session.content), 'html.parser')
        self.no_forms = no_forms
    
    # TODO: add info on where the comment came from
    # TODO: add /* */ comments 
    def get_comments(self):
        for comment in self.soup.find_all(string=lambda text: isinstance(text, Comment)):
            output['comments'].append(comment.extract())

    def get_urls(self):
        # Gets all <a> urls
        for a_element in self.soup.find_all('a'):
            output['urls'].append(a_element.get('href'))
        # Gets all <form> urls
        for form_element in self.soup.find_all('form'):
            form_element_url: str = form_element.get('action')
            if form_element_url not in output['urls']:
                output['urls'].append(form_element_url)
            # Store forms in output['hidden_forms']
            # TODO: haven't checked yet if input is hidden or not
            if not self.no_forms:
                if form_element_url not in output['hidden_forms']:
                    output['hidden_forms'].append(form_element_url)
        # Gets all <link> urls
        for link_element in self.soup.find_all('link'):
            link_element_url: str = link_element.get('href')
            if link_element_url not in output['urls']:
                output['urls'].append(link_element_url)
        # Gets all <script> urls
        for script_element in self.soup.find_all('script'):
            script_element_url: str = script_element.get('src')
            if script_element_url not in output['urls']:
                output['urls'].append(script_element_url)
        # Gets all <img> urls
        for img_element in self.soup.find_all('img'):
            img_element_url: str = img_element.get('src')
            if img_element_url not in output['urls']:
                output['urls'].append(img_element_url)
        # Gets all <svg> urls
        for svg_element in self.soup.find_all('svg'):
            svg_element_url: str = svg_element.get('src')
            if svg_element_url not in output['urls']:
                output['urls'].append(svg_element_url)

    # TODO: add info on where the parameters came from
    def get_parameters(self):
        for url in output['urls']:
            if '?' in url:
                parameters : str = url.split('?')[1].split('#')[0]
                output['parameters'] += parameters.split('&')

    def add_new_urls(self):
        for url in output['urls']:
            pass
