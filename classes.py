import requests
from bs4 import BeautifulSoup, Comment
import re
import os
import json
import functions
from urllib.parse import unquote

class Crawl():
    #TODO: change self.url if server returns 302 and change allow redirects in self.session
    def __init__(self, url, no_forms):
        self.url = unquote(url)
        self.protocol = url.split('://')[0]
        self.session = requests.get(self.url, timeout=2.5, allow_redirects=False)
        self.soup = BeautifulSoup(str(self.session.content), 'html.parser')
        self.no_forms = no_forms
    
    # Directly adds urls to json files | Adds urls to urls.json and forms to forms.json
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
            # TODO: store input values and not just URLs
            if not self.no_forms:
                # Store form url in dictionary with None as value (cz not needed for now)
                clean_form_url = self.get_clean_url(form_element_url)
                if clean_form_url is None:
                    continue
                if clean_form_url not in forms_json:
                    forms_json[clean_form_url] = None
        if not self.no_forms:
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
        # removes bad values from url_buffer | returns a list of cleaned urls
        clean_urls: list = self.get_clean_urls(url_buffer)
        # add urls to urls.json
        if os.stat(".wce/urls.json").st_size != 0:
            with open(".wce/urls.json") as urls_file:
                urls_json = json.load(urls_file)
        else:
            urls_json = {}
        for clean_url in clean_urls:
            if clean_url not in urls_json.keys():
                urls_json[clean_url] = None
        with open('.wce/urls.json', 'w') as urls_file:
            json.dump(urls_json, urls_file)
        
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
                try:
                    key: str = parameter_split[0]
                    value: str = parameter_split[1]
                    # initiate the key if it didnt exist in page's dictionary
                    if key not in parameters_json[clean_url]:
                        parameters_json[clean_url][key] = []
                    # add value to the key if the value doesnt already exist
                    if value not in parameters_json[clean_url][key]:
                        parameters_json[clean_url][key].append(value) 
                except IndexError:
                    pass
        with open('.wce/parameters.json', 'w') as parameters_file:
            json.dump(parameters_json, parameters_file)

    def add_new_urls(self):
        with open(".wce/urls.json") as urls_file:
            urls_json = json.load(urls_file)
        with open(".wce/crawling.json") as crawling_file:
            crawling_json = json.load(crawling_file)
        for url in urls_json.keys():
            # doesn't add data urls to urls_to_visit but keeps them in output urls
            if url[:4] == 'data':
                continue
            url_without_parameters = self.get_url_without_parameters(url)
            try:
                extension: str = url_without_parameters.split('/')[-1].split('.')[-1]
                if extension == 'js' or extension == 'css' or extension == 'txt'\
                 or extension == 'png' or extension == 'jpg' or extension == 'gif':
                    continue
            except IndexError:
                pass
            domain: str = functions.get_domains_from_urls(url)
            if domain in crawling_json['domains'] and url_without_parameters not in crawling_json['history']\
             and url_without_parameters not in crawling_json['urls_to_visit']:
                crawling_json['urls_to_visit'].append(url_without_parameters)
        with open('.wce/crawling.json', 'w') as crawling_file:
            json.dump(crawling_json, crawling_file)
    
    # removes values from a list of urls that could cause errors
    def get_clean_urls(self, urls):
        clean_urls: list = []
        for url in urls:
            # This value is used to check if a URL is good or not | If its true then add url to urls_json if not ignore it
            is_good_url: bool = False
            # Remove None values
            if url == None or url == '':
                continue
            # decode url
            url = unquote(url)
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
                if self.url[-1] == '/':
                    url = self.url[:-1] + url
                else:
                    url = self.url + url
                is_good_url = True
            # Matches //
            if re.match("\/\/", url) != None:
                url = self.protocol + ':' + url
                is_good_url = True
            # url is bad, go to the next one
            if not is_good_url:
                continue
            # if the url is good and its not already in urls_json, add it as key
            if url not in clean_urls:
                # for now keep value as None as we dont need it | might need it later
                clean_urls.append(url)
        return clean_urls

    def get_clean_url(self, url):
        # Remove None values
        if url == None or url == '':
            return None
        # adds protocol and domain to relative links
        # Matches urls that start with \\' This happens when they are written as src='https://'
        if not re.match("\\\\\'",url) is None:
            url = url.replace("\\'","")
        # Matches ../ and ./
        if not re.match("\.\.?\/", url) is None:
            url = self.url + url
        # Matches /directory and not //web
        if not re.match("\/[^/]", url) is None:
            url = self.url + url
        # Matches //
        if not re.match("\/\/", url) is None:
            url = self.protocol + ':' + url
        return url

    # Removes parameters and makes sure the URLs are written the same
    def get_clean_page(self, url):
        url_without_parameters = self.get_url_without_parameters(url)
        if url_without_parameters[-1] == '/':
            return url_without_parameters[:-1]
        return url_without_parameters

    #returns the URL without parameters 
    def get_url_without_parameters(self, url):
        return url.split('?')[0].split('#')[0]