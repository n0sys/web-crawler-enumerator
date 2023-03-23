import json
import re

# Get the domains from user's input either a string or a list -> returns a list of domains
def get_domains_from_urls(urls):
    input_is_str: bool = False
    # When passing a string instead of a line
    if isinstance(urls, str):
        urls = [urls]
        input_is_str = True
    for url in urls:
        domains_list: list = []
        # stores site address as www.example.come
        site: str = url.split('/')[2].split('?')[0].split('#')[0]
        if site == 'localhost':
            domains_list.append(site)
            continue
        # if site is not localhost
        # reversed the string bcz re matches pattern by search left-to-right 
        domain: str = re.findall("[^.*]+\.[^.*]+",site[::-1])[0][::-1]
        domains_list.append(domain)
    if input_is_str:
        return domains_list[0]
    return domains_list
    
def output_results(settings):
    # Parameters
    if not settings['no-params']:
        with open(".wce/parameters.json") as parameters_file:
            parameters_json = json.load(parameters_file)
        print("\n----------------------")
        print("Parameters found")
        print("----------------------")
        for url in parameters_json.keys():
            print("[+] " + url )
            for urls_parameter in parameters_json[url]:
                print('\t?' + urls_parameter + '=' )
                print('', end="\t\t")
                for urls_parameter_value in parameters_json[url][urls_parameter]:
                    print(urls_parameter_value, end="\t ")
                print("")
    # Comments
    if not settings['no-comments']:
        with open(".wce/comments.json") as comments_file:
            comments_json = json.load(comments_file)
        print("\n----------------------")
        print("Comments found:")
        print("----------------------")
        for url in comments_json.keys():
            if comments_json[url] == []:
                continue
            print("[+] "+ url + ":")
            for comment in comments_json[url]:
                print("\t", comment)
    # URLs 
    print("\n----------------------")
    print("URLs found:")
    print("----------------------")
    with open(".wce/urls.json") as urls_file:
        urls_json = json.load(urls_file)
    for url in urls_json.keys():
        print('[+]',url)
    # Forms
    if not settings['no-forms']:
        with open(".wce/forms.json") as forms_file:
            forms_json = json.load(forms_file)
        print("\n----------------------")
        print("Forms found:")
        print("----------------------")
        for form in forms_json.keys():
            print('[+]',form)
        print("")