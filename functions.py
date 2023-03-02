import json

# Get the domains from user's input and store them in global variable 'domains'
def get_domains_from_urls(urls):
    with open(".wce/crawling.json") as crawling_file:
        crawling_json = json.load(crawling_file)
    for url in urls:
        domain: str = url.split('/')[2].split('?')[0].split('#')[0]
        if domain not in crawling_json['domains']:
            crawling_json['domains'].append(domain)
    with open('.wce/crawling.json', 'w') as crawling_file:
        json.dump(crawling_json, crawling_file)

def output_results(settings):
    # Parameters
    if not settings['no-params']:
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
    if not settings['no-comments']:
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
    if not settings['no-forms']:
        with open(".wce/forms.json") as forms_file:
            forms_json = json.load(forms_file)
        print("\n----------------------")
        print("Forms found:")
        print("----------------------")
        for form in forms_json.keys():
            print('+',form)
        print("")