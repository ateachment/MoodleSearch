# Run with command line parameters :
# python moodleCrawler -i yourIdentifier

def cutText(txt): # gets list of words an extract the first 18 of them
  wordlength = 18
  wordlist = txt.split(' ')
  if len(wordlist) > wordlength:
    return ' '.join(wordlist[:wordlength]) + " ..."
  else:
    return txt

def scrapePage(link,linkText,shortText):
  r = session.get(link)                         # Seiten aufrufen
  short_txt = ""
  if(r.ok):
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
      paragraphs = markUpPageContent.find_all_next(['p','h1','h2','h3','h4','h5','h6'])   # Absätze
      if(paragraphs is not None):
        txt = ""
        short_txt = ''
        for paragraph in paragraphs:
          txt += paragraph.get_text() + ' '
          if(len(short_txt) < 50 ):
            short_txt += ' ' + paragraph.get_text()
        txt2 = linkText + ' ' + txt
      rawTexts.append(txt2)                         # append txt of page to rawTexts
      shortTexts.append(shortText + [short_txt])         # append short_txt
      # print(txt2)

def crawlCourse(link, shortText):
  r = session.get(link)
  #print(r.status_code)
  if(r.ok):    # status_code 200
    soup = bs4.BeautifulSoup(r.text,'html5lib')
    #print(soup)
    for section in soup.findAll('li',{'class':'section'}):            #    ('h3',{'class':'sectionname'}):  # iterate sections
      #print(section)
      section_id = section.attrs['id']
      #print(section_id)
      sectionname = section.find('h3',{'class':'sectionname'}).get_text(strip=True, separator=" ")
      #print(sectionname)

      link2 = link + "#" + section_id         # calculate link of section
      links.append(link2)                                   # append link to list links
      # extract text of section
      #print(sectionname)
      rawTexts.append(sectionname)                          # append text to list rawTexts

      #print(link2, shortTexts[-1])
      summarytext = section.find('div', attrs={'class':'summarytext'})
      if (summarytext is not None):
        summarytext = summarytext.get_text(strip=True, separator=" ")
        shortTexts.append(shortText + [sectionname] + [cutText(summarytext)])          # append shortText
      else:
        shortTexts.append(shortText + [sectionname])          # append shortText
      #print(summarytext)
      #print(shortText[-1])

      markUpLink = section.find('a', attrs={'class':'aalink'})
      #print(markUpLink)
      if(markUpLink is not None):
        link3 = markUpLink.attrs['href']
        if(link3 is not None):
          markUpName = markUpLink.span
          if not("Link/URL" in markUpName.get_text()):
            for s in markUpName.select('span'):
              s.extract()
            linkText = markUpName.get_text()
            # print(link3)
            # print(linkText)
            links.append(link3)
            scrapePage(link3,linkText,shortText + [sectionname] + [linkText])



import settings
import requests
import bs4

session = requests.Session()
session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"

links = []
rawTexts = []
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
      rawTexts.append(coursename + ' ' + summaryText)
      shortText = [coursename, cutText(summaryText)]         # init shortText
      shortTexts.append(shortText)                 # append new shortText
      print(uri, shortText)
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
          crawlCourse(uri, shortText)

import sys, getopt
def main(argv):
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
    sys.exit(2)

if __name__ == "__main__":
   main(sys.argv[1:])


import requests
import bs4
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

import numpy as np
import pandas as pd
import re             # regular expression
import pickle
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
analyzer = TfidfVectorizer().build_analyzer()
stop += stopwords.words('german') + stopwords.words('english')

def stemmed_words(doc):
    return (stemmer.stem(w) for w in analyzer(doc) if w not in stop and re.match( r'\b[a-zA-Z]{2,}\b', w)) # exclude stopwords, numbers and stemm


tf = TfidfVectorizer(decode_error="replace", analyzer=stemmed_words)
tf_fit = tf.fit_transform(rawTexts)

picklesDir="data/"
filenameLinks = os.path.join(picklesDir, "links_" + input + ".pickle")
filenameShortTexts = os.path.join(picklesDir, "shortTexts_" + input  + ".pickle")
filenameTf = os.path.join(picklesDir, "tf_" + input + ".pickle")
filenameTf_fit = os.path.join(picklesDir, "tf_fit_" + input + ".pickle")

with open(filenameLinks, "wb") as fp:
  pickle.dump(links, fp)
with open(filenameShortTexts, "wb") as fp:
  pickle.dump(shortTexts, fp)
with open(filenameTf, "wb") as fp:
  pickle.dump(tf, fp)
with open(filenameTf_fit, "wb") as fp:
  pickle.dump(tf_fit, fp)
