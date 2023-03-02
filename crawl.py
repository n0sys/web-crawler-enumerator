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
    global domains
    domains = []
    history = []
    urls_list = urls
    # Get the domains from user's input and store them in global variable 'domains'
    get_domains_from_urls(urls)
    # Crawl until no new URLs are found
    # TODO: issue in output urls (found when visiting http://localhost/dashboard)
    while len(urls_list) != 0:
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
        if not settings['no-params']:
            request.get_parameters()
        history.append(urls_list[0].strip())
        urls_list.pop(0)
        if settings['crawl']:
            request.add_new_urls()
        # Add delay?
        # time.sleep(settings['sleep'])
    output_results()

# Get the domains from user's input and store them in global variable 'domains'
def get_domains_from_urls(urls):
    for url in urls:
        domain: str = url.split('/')[2].split('?')[0].split('#')[0]
        if domain not in domains:
            domains.append(domain)

def output_results():
    # Parameters
    with open(".wce/parameters.json") as parameters_file:
        parameters_json = json.load(parameters_file)
    print("\n----------------------")
    print("Parameters found")
    print("----------------------")
    for url in parameters_json.keys():
        print("Parameters found in " + url +':')
        for urls_parameter in parameters_json[url]:
            print('+ ?' + urls_parameter + '=')
            for urls_parameter_value in parameters_json[url][urls_parameter]:
                print(urls_parameter_value, end="\t ")
            print("")
        print("")
    # Comments
    with open(".wce/comments.json") as comments_file:
        comments_json = json.load(comments_file)
    print("\n----------------------")
    print("Comments found:")
    print("----------------------")
    for url in comments_json.keys():
        if comments_json[url] == []:
            continue
        print("Comments found in "+ url + ':')
        for comment in comments_json[url]:
            print('+ '+ comment)
    # URLs 
    print("\n----------------------")
    print("URLs found:")
    print("----------------------")
    with open(".wce/urls.json") as urls_file:
        urls_json = json.load(urls_file)
    for url in urls_json.keys():
        print('+',url)
    # Forms
    with open(".wce/forms.json") as forms_file:
        forms_json = json.load(forms_file)
    print("\n----------------------")
    print("Hidden forms found:")
    print("----------------------")
    for form in forms_json.keys():
        print('+',form)
    print("")

class Crawl():
    #TODO: change self.url if server returns 302 and change allow redirects in self.session
    def __init__(self, url, no_forms):
        self.url = url
        self.protocol = url.split('://')[0]
        self.domain = self.get_domain_from_url(self.url)
        self.relative_path = self.get_relative_path_from_url(self.url)
        self.session = requests.get(self.url, timeout=2.5, allow_redirects=False)
        self.soup = BeautifulSoup(str(self.session.content), 'html.parser')
        self.no_forms = no_forms
    
    # TODO: add /* */ comments 
    def get_comments(self):
        if os.stat(".wce/comments.json").st_size != 0:
            with open(".wce/comments.json") as comments_file:
                comments_json = json.load(comments_file)
        else:
            comments_json = {}
        if self.url not in comments_json:
            comments_json[self.url] = []
        for comment in self.soup.find_all(string=lambda text: isinstance(text, Comment)):
            comments_json[self.url].append(comment.extract())
        with open('.wce/comments.json', 'w') as comments_file:
            json.dump(comments_json, comments_file)

    def get_urls(self):
        url_buffer: list = []
        # Gets all <form> urls
        if not self.no_forms:
            if os.stat(".wce/forms.json").st_size != 0:
                with open(".wce/forms.json") as forms_file:
                    forms_json = json.load(forms_file)
            else:
                forms_json = {}
        for form_element in self.soup.find_all('form'):
            form_element_url: str = form_element.get('action')
            if form_element_url not in url_buffer:
                url_buffer.append(form_element_url)
            # TODO: haven't checked yet if input is hidden or not | store input values and not just URLs
            if not self.no_forms:
                if form_element_url not in forms_json:
                    forms_json[form_element_url] = None
        with open('.wce/forms.json', 'w') as forms_file:
            json.dump(forms_json, forms_file)
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
        # cleans urls and adds them to urls.json
        self.get_clean_urls(url_buffer)

    # Format json: parameters={"https://google.com/asd":{"?i=":["asd","sd"],"?sd=":["sdd","qwee","sda"]}}
    def get_parameters(self):
        # if parameters.json is not empty, load content 
        if os.stat(".wce/parameters.json").st_size != 0:
            with open(".wce/parameters.json") as parameters_file:
                parameters_json = json.load(parameters_file)
        else:
            parameters_json = {}
        # extract parameters and save them to parameters json file
        with open(".wce/urls.json") as urls_file:
            urls_json = json.load(urls_file)
        for url in urls_json.keys():
            if '?' not in url:
                continue
            clean_url: str = self.get_clean_page(url)
            parameters: str = url.split('?')[1].split('#')[0]
            if clean_url not in parameters_json:
                parameters_json[clean_url] = {}
            for parameter in parameters.split('&'):
                parameter_split = parameter.split('=')
                # initiate parameter if it didnt exist in page's dictionary
                if parameter_split[0] not in parameters_json[clean_url]:
                    parameters_json[clean_url][parameter_split[0]] = []
                # add value to the parameter if the value doesnt already exist
                if parameter_split[1] not in parameters_json[clean_url][parameter_split[0]]:
                    parameters_json[clean_url][parameter_split[0]].append(parameter_split[1])    
        with open('.wce/parameters.json', 'w') as parameters_file:
            json.dump(parameters_json, parameters_file)

    def add_new_urls(self):
        with open(".wce/urls.json") as urls_file:
            urls_json = json.load(urls_file)
        for url in urls_json.keys():
            # doesn't add data urls to urls_list but keeps them in output urls
            if url[:4] == 'data':
                continue
            url_without_parameters = self.get_url_without_parameters(url)
            domain: str = url_without_parameters.split('/')[2]
            if domain in domains and url_without_parameters not in history and url_without_parameters not in urls_list:
                urls_list.append(url_without_parameters)
    
    # removes values from a list of urls that could cause errors 
    def get_clean_urls(self, urls):
        if os.stat(".wce/urls.json").st_size != 0:
            with open(".wce/urls.json") as urls_file:
                urls_json = json.load(urls_file)
        else:
            urls_json = {}
        for url in urls:
            #TODO: test if URL contains '//' other than protocol's ones
            # This value is used to check if a URL is good or not | If its true then add url to urls_json if not ignore it
            is_good_url: bool = False
            # Remove None values
            if url == None or url == '':
                continue
            # TODO: better solution to detect relative links
            # adds protocol and domain to relative links
            # Matches urls that start with \\' This happens when they are written as src='https://'
            if re.match("\\\\\'",url) != None:
                url = url.replace("\\'","")
                is_good_url = True
            # matches http(s):// urls
            if re.match("https?\:\/\/[^.]+\.[^.]+",url) != None:
                is_good_url = True
            # Matches data: urls
            if url[:4] == 'data':
                is_good_url = True
            # Matches ../ and ./
            if re.match("\.\.?\/", url) != None:
                url = self.url + url
                is_good_url = True
            # Matches /directory and not //web
            if re.match("\/[^/]", url) != None:
                url = self.url + url
                is_good_url = True
            # Matches //
            if re.match("\/\/", url) != None:
                url = self.protocol + ':' + url
                is_good_url = True
            # url is bad, go to the next one
            if is_good_url == False:
                continue
            # if the url is good and its not already in urls_json, add it as key
            if url not in urls_json.keys():
                # for now keep value as None as we dont need it | might need it later
                urls_json[url] = None
        with open('.wce/urls.json', 'w') as urls_file:
            json.dump(urls_json, urls_file)

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