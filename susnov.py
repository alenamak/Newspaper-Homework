import re
import os
import urllib.request
import lxml.html
from pymystem3 import Mystem

totalWords = 0
nextUrl = ''
mys = Mystem()

def makeDirectory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def fullURL(url):
    if url.find("://") == -1:
        if url[0] == '/':
            url = "http://susnov.ru" + url
        else:
            url = "http://susnov.ru/" + url
    return url
    
def urlContents(url):
    print("Getting %s..." % url)
    content = urllib.request.urlopen(url).read()
    content = content.decode('utf-8')
    return content
    
def parseContents(contents):
    global totalWords
    global nextURL
    
    html = lxml.html.fromstring(contents)
    elems = html.find_class('leading')
    
    for elem in elems:
        links = elem.findall('.//a');
        title = links[0].text
        url = links[0].get('href')
        
        m = re.search('\/([0-9]+)\-', url)
        articleId = m.group(1)
        
        published = elem.find_class('published')[0].text
        m = re.search('(([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})) ([0-9]{1,2}:[0-9]{1,2})', published)
        day = m.group(2)
        month = m.group(3)
        year = m.group(4)
        date = m.group(1)
        time = m.group(2)
        
        print("%s: %s, %s @ %s" % (articleId, url, date, time))

        paragraphs = elem.findall('.//p')
        
        text = ""
        articleWords = 0
        
        for paragraph in paragraphs:
            if paragraph.text:
                if len(text) >= 0:
                    text += u"\n\n"
                text += paragraph.text
                articleWords += paragraph.text.count(' ')
        
        totalWords += articleWords
        print(" %d words in this article (%d total)" % (articleWords, totalWords))
        print("")
        
        makeDirectory("Mystem-texts")        
        makeDirectory("texts")
        makeDirectory("texts/"+year)
        makeDirectory("texts/"+year+"/"+month)
        
        text_file = open("texts/"+year+"/"+month+"/"+articleId+'.txt', 'wb')
        text_file.write(text.encode("UTF-8"))
        mystfile = open("Mystem-texts/"+articleId+'.txt', 'w')        
        lemmas = mys.lemmatize(text)
        for item in lemmas:
            mystfile.write(item)
        text_file.close()
        mystfile.close()
        
        
    nextLink = html.find_class("pagination-next")[0].find('.//a')
    if nextLink is not None:
        nextURL = nextLink.get('href')
    else:
        nextURL = None
        
url = fullURL('/chitat-gazetu.html')
while totalWords <= 100000:
    contents = urlContents(url)
    parseContents(contents)
    if nextURL is None:
        break
    url = fullURL(nextURL)
    
