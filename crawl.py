import requests
from bs4 import BeautifulSoup, Comment
import time

def start(urls, settings): 
    # Define global variables used to store collected data
    global urls_list
    global history
    global output
    global domains
    domains = []
    history = []
    urls_list = urls
    output = {'parameters':[], 'comments':[], 'urls':[], 'hidden_forms':[]}
    get_domains_from_urls(urls)
    # Crawl until no new URLs are found
    i=0
    while len(urls_list) != 0:
        print(i)
        i+=1
        print(urls_list[0])
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
        # removes from output values that could cause errors - eg: None value
        #clean_output_urls()
        if not settings['no-params']:
            request.get_parameters()
        history.append(urls_list[0].strip())
        urls_list.pop(0)
        if settings['crawl']:
            request.add_new_urls()
        print(output)
        # Add delay?
        # time.sleep(settings['sleep'])
    print(output)
    print(history)

# Get the domains from user's input and store them in global variable 'domains'
def get_domains_from_urls(urls):
    for url in urls:
        domain: str = url.split('/')[2].split('?')[0].split('#')[0]
        if domain not in domains:
            domains.append(domain)

# removes from output values that could cause errors - eg: None value
'''def clean_output_urls():
    for url in output['urls']:
        if url == None:
            output['urls'].remove(url)
'''
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
            a_element_url: str = a_element.get('href')
            if a_element_url not in output['urls'] and a_element_url != None:
                output['urls'].append(a_element.get('href'))
        # Gets all <form> urls
        for form_element in self.soup.find_all('form'):
            form_element_url: str = form_element.get('action')
            if form_element_url not in output['urls'] and form_element_url != None:
                output['urls'].append(form_element_url)
            # Store forms in output['hidden_forms']
            # TODO: haven't checked yet if input is hidden or not
            if not self.no_forms:
                if form_element_url not in output['hidden_forms']:
                    output['hidden_forms'].append(form_element_url)
        # Gets all <link> urls
        for link_element in self.soup.find_all('link'):
            link_element_url: str = link_element.get('href')
            if link_element_url not in output['urls'] and link_element_url != None:
                output['urls'].append(link_element_url)
        # Gets all <script> urls
        for script_element in self.soup.find_all('script'):
            script_element_url: str = script_element.get('src')
            if script_element_url not in output['urls'] and script_element_url != None:
                output['urls'].append(script_element_url)
        # Gets all <img> urls
        for img_element in self.soup.find_all('img'):
            img_element_url: str = img_element.get('src')
            if img_element_url not in output['urls'] and img_element_url != None:
                output['urls'].append(img_element_url)
        # Gets all <svg> urls
        for svg_element in self.soup.find_all('svg'):
            svg_element_url: str = svg_element.get('src')
            if svg_element_url not in output['urls'] and svg_element_url != None:
                output['urls'].append(svg_element_url)

    # TODO: add info on where the parameters came from
    def get_parameters(self):
        for url in output['urls']:
            if '?' in url:
                parameters : str = url.split('?')[1].split('#')[0]
                output['parameters'] += parameters.split('&')

    def add_new_urls(self):
        for url in output['urls']:
            # TODO: better solution for relative links
            if 'http' not in url:
                url = 'https://' + domain + url
            domain: str = url.split('/')[2].split('?')[0].split('#')[0]
            #
            if domain in domains and url not in history:
                urls_list.append(url)