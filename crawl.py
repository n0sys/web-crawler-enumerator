import requests
from bs4 import BeautifulSoup, Comment
import re
import json
import os

def start(urls, settings): 
    # Define global variables used to store collected data
    # TODO: check local storage for use instead of global vars
    global urls_list
    global history
    global output
    global domains
    domains = []
    history = []
    urls_list = urls
    output = {'comments':[], 'urls':[], 'hidden_forms':[]}
    get_domains_from_urls(urls)
    # Crawl until no new URLs are found
    i=0
    while len(urls_list) != 0:
        print(i)
        i+=1
        print(urls_list[0]+'\n')
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

class Crawl():
    #TODO: change self.url if server returns 302 and change allow redirects to True in self.session
    def __init__(self, url, no_forms):
        self.url = url
        self.protocol = url.split('://')[0]
        self.domain = self.get_domain_from_url(self.url)
        self.relative_path = self.get_relative_path_from_url(self.url)
        self.session = requests.get(self.url, timeout=2.5, allow_redirects=False)
        self.soup = BeautifulSoup(str(self.session.content), 'html.parser')
        self.no_forms = no_forms
    
    # TODO: add info on where the comment came from
    # TODO: add /* */ comments 
    def get_comments(self):
        for comment in self.soup.find_all(string=lambda text: isinstance(text, Comment)):
            output['comments'].append(comment.extract())

    def get_urls(self):
        url_buffer: list = []
        # Gets all <form> urls
        for form_element in self.soup.find_all('form'):
            form_element_url: str = form_element.get('action')
            if form_element_url not in url_buffer:
                url_buffer.append(form_element_url)
            # TODO: haven't checked yet if input is hidden or not | store input values and not just URLs
            if not self.no_forms:
                if form_element_url not in output['hidden_forms']:
                    output['hidden_forms'].append(form_element_url)
        # Gets all <a> urls
        for a_element in self.soup.find_all('a'):
            a_element_url: str = a_element.get('href')
            if a_element_url not in url_buffer:
                url_buffer.append(a_element.get('href'))
        # Gets all <link> urls
        for link_element in self.soup.find_all('link'):
            link_element_url: str = link_element.get('href')
            if link_element_url not in url_buffer:
                url_buffer.append(link_element_url)
        # Gets all <script> urls
        for script_element in self.soup.find_all('script'):
            script_element_url: str = script_element.get('src')
            if script_element_url not in url_buffer:
                url_buffer.append(script_element_url)
        # Gets all <img> urls
        for img_element in self.soup.find_all('img'):
            img_element_url: str = img_element.get('src')
            if img_element_url not in url_buffer:
                url_buffer.append(img_element_url)
        # Gets all <svg> urls
        for svg_element in self.soup.find_all('svg'):
            svg_element_url: str = svg_element.get('src')
            if svg_element_url not in url_buffer:
                url_buffer.append(svg_element_url)
        #TODO: check for more url types
        # clean url buffer - bad values: None, # 
        clean_url_buffer = self.get_clean_urls(url_buffer)
        output['urls']+= clean_url_buffer

    # TODO: remove duplicate values from parameters
    # Format json: parameters={"https://google.com/asd":{"?i=":["asd","sd"],"?sd=":["sdd","qwee","sda"]}}
    def get_parameters(self):
        if os.stat(".wce/parameters.json").st_size != 0:
            with open(".wce/parameters.json") as parameters_file:
                parameters_json = json.load(parameters_file)
        else:
            parameters_json = {}
        for url in output['urls']:
            if '?' not in url:
                continue
            clean_url: str = self.get_clean_page(url)
            parameters: str = url.split('?')[1].split('#')[0]
            if clean_url not in parameters_json:
                parameters_json[clean_url] = {}
            for parameter in parameters.split('&'):
                parameter_split = parameter.split('=')
                if parameter_split[0] not in parameters_json[clean_url]:
                    parameters_json[clean_url][parameter_split[0]] = [parameter_split[1]]
                else:
                    parameters_json[clean_url][parameter_split[0]].append(parameter_split[1])     
        with open('.wce/parameters.json', 'w') as parameters_file:
            json.dump(parameters_json, parameters_file)

    def add_new_urls(self):
        for url in output['urls']:
            # doesn't add data urls to urls_list but keeps them in output urls
            if url[:4] == 'data':
                continue
            url_without_parameters = self.get_url_without_parameters(url)
            domain: str = url_without_parameters.split('/')[2]
            if domain in domains and url_without_parameters not in history and url_without_parameters not in urls_list:
                urls_list.append(url_without_parameters)
    
    # removes values from a list of urls that could cause errors 
    def get_clean_urls(self, urls):
        clean_urls: list = []
        for url in urls:
            # Remove None values
            if url == None or url == '':
                continue
            # TODO: better solution to detect relative links
            # adds protocol and domain to relative links
            # Matches urls that start with \\' when in html they are written as src='https://'
            if re.match("\\\\\'",url) != None:
                url = url.replace("\\'","")
            # matches http(s):// urls
            if re.match("https?\:\/\/[^.]+\.[^.]+",url) != None:
                clean_urls.append(url)
                continue
            # Matches data: urls
            if url[:4] == 'data':
                clean_urls.append(url)
                continue
            # Matches ../ and ./
            if re.match("\.\.?\/", url) != None:
                url = self.url + url
                clean_urls.append(url)
                continue
            # Matches /directory and not //web
            if re.match("\/[^/]", url) != None:
                url = self.url + url
                clean_urls.append(url)
                continue
            # Matches //
            if re.match("\/\/", url) != None:
                url = self.protocol + ':' + url
                clean_urls.append(url)
                continue
            #TODO: test if URL contains // other that protocol's one
        return clean_urls

    # Removes parameters and makes sure the URLs are written the same
    def get_clean_page(self, url):
        url_without_parameters = self.get_url_without_parameters(url)
        if url_without_parameters[-1] == '/':
            return url_without_parameters[:-1]
        return url_without_parameters
       
    #Get the domain of a given URL
    def get_domain_from_url(self, url):
        return url.split('/')[2].split('?')[0].split('#')[0]

    #returns the URL without parameters 
    def get_url_without_parameters(self, url):
        return url.split('?')[0].split('#')[0]

    #returns relative path of a url
    def get_relative_path_from_url(self, url):
        if url.count("/") < 3:
            return ""
        url_list = url.split('/')[3:]
        return '/'.join(url_list).split('?')[0].split('#')[0]