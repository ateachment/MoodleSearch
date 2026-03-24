# 
# Run with command line parameters :
# python moodleCrawler -i yourIdentifier

def cutText(txt): # gets list of words an extract the first 18 of them
  wordlength = 18
  if txt == "":
    wordlist = txt.split(' ')
    if len(wordlist) > wordlength:
      return ' '.join(wordlist[:wordlength]) + " ..."
    else:
      return txt
  else:
     return txt

def scrapePage(link,linkText,shortText):
  print("SCRAPE_PAGE: ", linkText)
  short_txt = ""
  head = requests.head(link, allow_redirects=True, timeout=10)
  header = head.headers
  content_type = header.get('content-type')
  if content_type.__contains__("text/html"):        # follow only html content
    r = session.get(link)                           # Seiten aufrufen
    if r.ok:
      soup = bs4.BeautifulSoup(r.text,'html.parser')
      markUpPageContent=soup.find("div", {"id": "page-content"})
      if markUpPageContent is not None:  # link to source code etc.
        #for tag in markUpPageContent.select('form, navitem, gradingsummary'):      # get rid of forms
        #  tag.decompose()
        for tag in soup.select('span.nolink'):      # get rid of LaTeX formules
          tag.decompose()
        for tag in soup.select('div.mediaplugin'):  # get rid of Videos
          tag.decompose()
        for tag in soup.select('iframe'):           # get rid of iframes
          tag.decompose()
        for tag in soup.select('div.footer-content-popover'):  # get rid of Contents of question mark button
          tag.decompose()
        for tag in soup.select('div.drawer'):  # get rid of Contents of question mark button
          tag.decompose()

        for br in soup.select("br"):
            br.replace_with(" ")

        #print(markUpPageContent)
        paragraphs = markUpPageContent.find_all(['p','h1','h2','h3','h4','h5','h6'])   # Absätze
        if(paragraphs is not None):
          txt = ""
          short_txt = ""
          for paragraph in paragraphs:
            txt += paragraph.get_text() + ' '
            if(len(short_txt) < 50 ):
              short_txt += paragraph.get_text() + ' '
        rawTexts[-1] += ' ' + txt                                # add txt of page to last element of rawTexts
        shortTexts[-1] += [short_txt]         # add short_txt to last element of shortTexts
        results.append({
          "url": link,
          "title": linkText,
          "shortText": short_txt,
          "type": "page",
        })


def crawlPageLinks(activity, sectionname, shortText, rawText):

    global rawTexts, shortTexts, links
    link_page = activity.select_one("a.aalink")

    shortTextAddition = []
    rawTextAddition = ""
    if link_page:
        url = link_page["href"]
        if "/mod/page/view.php" in url:

            linkText = link_page.select_one(".instancename").contents[0].strip()
            links.append(url)

            shortTexts.append(shortText + [linkText])
            shortTextAddition = [sectionname] + [linkText]
            rawTextAddition = ' ' + linkText
            rawTexts.append(rawText + rawTextAddition)                     # append text to list rawTexts
            
            results.append({
              "url": url,
              "title": linkText,
              "shortText": "",
              "type": "section",
            })
            
            scrapePage(url,linkText,shortText + [sectionname] + [linkText])



    return shortTextAddition, rawTextAddition

def crawlSectionLinks(link_section, section, sectionname, shortText, rawText):
    global shortTexts, rawTexts

    links.append(link_section["href"])                    # append link to list links
    
    summarytext = section.find('div', attrs={'class':'summarytext'})
    if (summarytext is not None):
        summarytext = summarytext.get_text(strip=True, separator=" ")
        #print("SUMMARYTEXT=", summarytext)
        shortTextAddition = [sectionname] + [cutText(summarytext)]
        rawTextAddition = ' ' + sectionname + ' ' + summarytext
    else:
        shortTextAddition = [sectionname]
        rawTextAddition = ' ' + sectionname

    shortTexts.append(shortText + shortTextAddition)      # append shortText
    rawTexts.append(rawText + rawTextAddition)            # append text to list rawTexts
    
    results.append({
          "url": link_section["href"],
          "title": sectionname,
          "shortText": cutText(summarytext),
          "type": "section",
      })
    
    return shortTextAddition, rawTextAddition

def crawlCourse(link, shortText):
  r = session.get(link)
  #print(link)
  #print(r.status_code)
  if(r.ok):    # status_code 200
    soup = bs4.BeautifulSoup(r.text,'html5lib')
    #print(soup)
    for section in soup.select("ul[data-for='course_sectionlist'] > li.section"):

        # SECTION parser
        sectionname = section["data-sectionname"]

        link_section = section.select_one("h3.sectionname a")
        if link_section:
            shortTextAdditionSection, rawTextAdditionSection = crawlSectionLinks(link_section, section, sectionname, shortText, rawText)


        activitylist = section.select_one("ul[data-for='cmlist']")
        if not activitylist:
            continue
        

        for activity in activitylist.find_all("li", class_="activity", recursive=False):

            classes = activity.get("class", [])

            # normale Aktivität
            if "modtype_subsection" not in classes:
                shortTextAddition, rawTextAddition = crawlPageLinks(activity, sectionname, shortText + shortTextAdditionSection, rawText + rawTextAdditionSection)

            
            else:  # Subsection separat behandeln
                
                # SUBSECTION parser
                subsection = activity.select_one("li.section.delegated-section")
                if subsection:
                    subsection_name = subsection["data-sectionname"]

                    link_subsection = section.select_one("h4.sectionname a")
                    if link_subsection:
                        shortTextAdditionSubsection, rawTextAdditionSubsection = crawlSectionLinks(link_subsection, subsection, subsection_name, shortText + shortTextAdditionSection, rawText + rawTextAdditionSection)

                    for subactivity in subsection.select("li.activity"):
                        crawlPageLinks(subactivity, sectionname, shortText + shortTextAdditionSection + shortTextAdditionSubsection, rawText + rawTextAdditionSection + rawTextAdditionSubsection)

        
            



import settings
import requests
import bs4

session = requests.Session()
session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"

results = []
links = []
rawTexts = []
rawText = ""  # init rawText
shortTexts = []
input = ""  # comand line arg

def crawlMoodlePublicCourses():
  base_url = 'https://' + settings.uri2 + '/'
  r = session.get(base_url, allow_redirects=True, timeout=10)
  if(r.ok):
    soup = bs4.BeautifulSoup(r.text,'html5lib')
    courses = soup.find_all('div', attrs={"class":"coursebox"})
    #print(courses)
    for course in courses:
      link = course.find('a',attrs={'class':'aalink'})
      #print(link)
      uri = link.get_attribute_list('href')[0]        # extract uri of course
      coursename = link.get_text()
      #print(uri, coursename)
      summary = course.find('div', attrs={'class':'summary'})
      if summary is not None:
        summaryText = summary.get_text(strip=True, separator=" ")
      else:
        summaryText = ''
      # print("summary="+summary)
      links.append(uri)
      rawText = coursename + ' ' + summaryText
      rawTexts.append(rawText)
      shortText = [coursename, cutText(summaryText)]         # init shortText
      shortTexts.append(shortText)                 # append new shortText
      
      results.append({
          "url": uri,
          "title": coursename,
          "description": cutText(summaryText),
          "type": "course",
      })
      
      # print(uri, shortText)
      crawlCourse(uri, shortText)
      

def crawlMoodleCategoryWithLogin():  # subsection
  base_url = 'https://' + settings.uri + '/'
  r = session.get(base_url, allow_redirects=True, timeout=10)
  if(r.ok):
    urlLogin = r.url
    #print(urlLogin)
    #print(r.cookies)
    soup = bs4.BeautifulSoup(r.text,'html5lib')
    url = soup.find('input', {'name': 'url'}).get('value')

    values = {'url': url, 'timezone': '', 'skin': 'sp', 'user2': settings.user2, 'user': settings.user, 'password': settings.password} # password is needed
    r = session.post(urlLogin, values)   # login
    if(r.ok):
      soup = bs4.BeautifulSoup(r.text,'html5lib')
      urlCourses = "https://" + settings.uri + "/course/index.php?categoryid=" + str(settings.categoryid)
      r = session.get(urlCourses)
      if(r.ok):
        soup = bs4.BeautifulSoup(r.text,'html5lib')
        #print(soup)
        courses = soup.find_all('div', attrs={"class":"course-description"})
        #print(courses[2])
        for course in courses:
          #link = course.find('div', attrs={'class':'course-name'}).find('div', attrs={'class':'coursename'}).find('a',attrs={'class':'aalink'}).get_attribute_list('href')[0]        # extract link of course
          link = course.find('div', attrs={'class':'course-name'}).find('div', attrs={'class':'coursename'}).find('a',attrs={'class':'aalink'})
          uri = link.get_attribute_list('href')[0]        # extract uri of course
          coursename = link.get_text()
          #print(uri, coursename)
          summary = course.find('div', attrs={'class':'summary'}).get_text(strip=True, separator=" ")
          # print("summary="+summary)
          links.append(uri)
          rawTexts.append(coursename + ' ' + summary)
          shortText = [coursename, cutText(summary)]         # init shortText
          shortTexts.append(shortText)                 # append new shortText
          #print(uri, shortText)
          
          results.append({
            "url": uri,
            "title": coursename,
            "description": cutText(summary),
            "type": "course",
          })
          
          crawlCourse(uri, shortText)

import sys, getopt
def app(argv):
  global input
  try:
    opts, args = getopt.getopt(argv,"h:i:",["input="])
  except getopt.GetoptError:
    print('test.py -i <input>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('test.py -i <input>')
      sys.exit()
    elif opt in ("-i", "--input"):
      input = arg
  if(input == "eick-at"):
    crawlMoodlePublicCourses()
  elif(input == "wvs-ffm"):
    crawlMoodleCategoryWithLogin()
  else:
    print("Input is '" + input + "'. Has to be: '" + settings.identifier + "' or '" + settings.identifier2 + "'.")
    print("For example: moodleCrawler.py -i eick-at")
    sys.exit(2)

if __name__ == "__main__":
   app(sys.argv[1:])


import requests
import bs4
import nltk



import re             # regular expression
import cloudpickle as pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity # We will use this later>
from nltk.stem.snowball import GermanStemmer
from nltk.corpus import stopwords

stop = nltk.corpus.stopwords.words('german')
# Add a few more stop words we would like to remove here
stop.append('daher')
stop.append('vieler')
stop.append('vielen')
stop.append('usw')
stop.append('bzw')
stop.append('etc')



stemmer = GermanStemmer()
analyzer = TfidfVectorizer(strip_accents="unicode").build_analyzer()
stop = set(stopwords.words('german')).union(set(stopwords.words('english')))  # combine german and english stop words

def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc) if w not in stop and re.match( r'\b[a-zA-ZäöüÄÖÜß]{2,}\b', w)) # exclude stopwords, numbers and stemm
                                                                                                                  # but includes german umlauts


tf = TfidfVectorizer(decode_error="strict", strip_accents="unicode", analyzer=stemmed_words)
tf_fit = tf.fit_transform(rawTexts)

picklesDir="data/"
filenameLinks = os.path.join(picklesDir, "links_" + input + ".pickle")
filenameShortTexts = os.path.join(picklesDir, "shortTexts_" + input  + ".pickle")
filenameTf = os.path.join(picklesDir, "tf_" + input + ".pickle")
filenameTf_fit = os.path.join(picklesDir, "tf_fit_" + input + ".pickle")
filenameResults = os.path.join(picklesDir, "results_" + input  + ".pickle")


with open(filenameLinks, "wb") as fp:
  pickle.dump(links, fp)
with open(filenameShortTexts, "wb") as fp:
  pickle.dump(shortTexts, fp)
with open(filenameTf, "wb") as fp:
  pickle.dump(tf, fp)
with open(filenameTf_fit, "wb") as fp:
  pickle.dump(tf_fit, fp)
with open(filenameResults, "wb") as fp:
  pickle.dump(results, fp)

print(len(links)),print(len(rawTexts),print(len(shortTexts),print(len(results))))
