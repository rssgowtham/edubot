import requests
from bs4 import BeautifulSoup

def isInvalidSite(text):
    exclude_sites = ["youtube.com", "news", "books."]
    for i in exclude_sites:
        if i in text:
            return True
    return False

def isImpLink(link):
    imp_sites = ["geeksforgeeks", "tutorialspoint", "wikipedia", "javatpoint", "studytonight", "math-shortcut-tricks", "w3schools"]
    for i in imp_sites:
        if i in link:
            return True
    return False

def getLinksAreaOfPageFromUrl(url):
    searched_page = requests.get(url)
    soup = BeautifulSoup(searched_page.content, 'html.parser')
    link_areas = soup.find_all("div", {"class": "ZINbbc xpd O9g5cc uUPGi"})
    try:
        alt_text_area = soup.find_all("div", {"class": "MUxGbd v0nnCb lyLwlc"})
    except Exception as e:
        alt_text_area = []
    finally:
        return link_areas, alt_text_area

def getSiteTitleAndLink(link_area):
    site_title = link_area.find("div", {"class": "BNeawe vvjwJb AP7Wnd"})
    link_area = link_area.find("div", {"class": "BNeawe UPmit AP7Wnd"})
    return site_title, link_area

def changeCharacterInLink(link):
    link = link.text
    modifiedLink = ""
    for i in link:
        # print(i)
        if i == '›':
            modifiedLink += '/'
        elif i== '›':
            modifiedLink += '/'
        elif i != ' ' and i!='›':
            modifiedLink += i
    if "http" != link[0:4]:
        modifiedLink = "http://" + modifiedLink
    return modifiedLink

def getValidLinks(link_areas):
    pdf_flag = 0
    pdf_link = ""
    pdf_title = ""
    links_data = ""
    for link_area in link_areas:
        link_area = link_area.find("a")
        if link_area is not None:
            site_title, link = getSiteTitleAndLink(link_area)
            if link is not None and link.text != "" and not isInvalidSite(link.text):
                if site_title is None or type(site_title) == str:
                    site_title = "\n"
                else:
                    site_title = site_title.text
                link = changeCharacterInLink(link)
                if(pdf_flag<2):
                    if(site_title[:5].lower() == "[pdf]"):
                        pdf_link = link
                        pdf_title = site_title
                        pdf_flag = 2
                elif(pdf_flag==0):
                    if(isImpLink(link)):
                        pdf_link = link
                        pdf_title = site_title
                        pdf_flag = 1
                # links.append(link)
                # site_titles.append(site_title)
                links_data =  links_data + site_title + "\n" + link + "\n\n"
    return links_data, pdf_link, pdf_title

def getLinksOfGoogleSearch(text):
    url = "https://google.com/search?q=" + text
    link_areas, alt_text_area = getLinksAreaOfPageFromUrl(url)
    try:
        if alt_text_area:
            if "Showing" not in alt_text_area[0].text:
                alt_text_link = alt_text_area[0].find("a")
                alt_text = alt_text_link.find("i").text
                url = "https://google.com/search?q=" + alt_text
                link_areas, alt_text_area = getLinksAreaOfPageFromUrl(url)
    except:
        pass
    links_data, pdf_link, pdf_title = getValidLinks(link_areas)
    return links_data, pdf_link, pdf_title

def getValidWikiLink(link_areas):
    site_title = None
    link = None
    for link_area in link_areas:
        link_area = link_area.find("a")
        if link_area is not None:
            site_title, link = getSiteTitleAndLink(link_area)
            if link is not None and link.text != "" and not isInvalidSite(link.text):
                break

    if site_title is None or type(site_title) == str:
        site_title = "\n"
    else:
        site_title = site_title.text
    if link is None:
        link = ""
    else:
        link = changeCharacterInLink(link)
    return link, site_title

def getWikiLink(text):
    url = "https://google.com/search?q=" + text
    link_areas, alt_text_area = getLinksAreaOfPageFromUrl(url)
    try:
        if alt_text_area:
            if "Showing" not in alt_text_area[0].text:
                alt_text_link = alt_text_area[0].find("a")
                alt_text = alt_text_link.find("i").text
                url = "https://google.com/search?q=" + alt_text
                link_areas, alt_text_area = getLinksAreaOfPageFromUrl(url)
    except:
        pass
    pdf_link, pdf_title = getValidWikiLink(link_areas)
    return pdf_link, pdf_title



def getDifferentLinks(text_list):
    text_wise_links = []
    text_wise_link_titles = []
    pdf_links = []
    pdf_titles = []
    for text in text_list:
        try:
            links_data, pdf_link, pdf_title = getLinksOfGoogleSearch(text)
            if(pdf_link==""):
                pdf_link, pdf_title = getWikiLink(text + "wikipedia")
            if links_data != "":
                text_wise_links.append(links_data)
            pdf_links.append(pdf_link)
            pdf_titles.append(pdf_title)
        except Exception as e:
            print(e)
            continue
    return text_wise_links, pdf_links, pdf_titles

# links, pdf_link, pdf_title = getDifferentLinks(["voice", "datastructures"])
# print(links[0])
# print(links[1])
# print(pdf_link[0])
# print(pdf_link[1])