# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %% [markdown] colab_type="text" id="view-in-github"
# <a href="https://colab.research.google.com/github/ateachment/MoodleSearch/blob/main/moodleSearch_eval.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %% [markdown] id="_eOGZGBMo1RR"
# Lemmatisierung deutscher Sprache: 
# https://nickyreinert.de/blog/2020/12/09/einfuehrung-in-stemming-und-lemmatisierung-deutscher-texte-mit-python/
#
# Installation von HanoverTagger (wird :

# %% colab={"base_uri": "https://localhost:8080/"} id="5C4I2-U9oWOh" outputId="d407814c-c28a-43ca-9769-8bf3db7de93a"
# pip install HanTa 

# %% colab={"base_uri": "https://localhost:8080/"} id="vy0yCK5XUOqg" outputId="573bd949-f83d-4a70-b4d8-0f89cacdcf70"
import requests
import bs4
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt_tab')

from HanTa import HanoverTagger as ht
hannover = ht.HanoverTagger('morphmodel_ger.pgz')

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity # We will use this later to decide how similar two sentences are

# %% colab={"base_uri": "https://localhost:8080/"} id="Yvhqsb-kuAAT" outputId="29332e2c-3a48-4a93-e91e-70f3cf1bc236"
stop = nltk.corpus.stopwords.words('german')
# Add a few more stop words we would like to remove here
stop.append('daher')
stop.append('vieler')
stop.append('vielen')
stop.append('usw')
stop.append('bzw')
stop.append('etc')
stop.append('d.h.')
stop.append('u.a')
stop.append('z.b')
stop.append('--')
stop.append('-')
stop.append('.')  
stop.append('``')
stop.append("''")
stop

# %% [markdown] id="mYZu4r45HPUK"
# # Web Crawling

# %% colab={"base_uri": "https://localhost:8080/"} id="6X_Z48OluFm0" outputId="2272690b-bf80-426f-d806-009e1122b340"
session = requests.Session()
session.headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0"

base_url = 'https://moodle.eick-at.de/course/view.php?id=21'  # URL of the Moodle Course "test"
r = session.get(base_url, allow_redirects=True, timeout=10)   # Make a GET request to the URL and store the response in r
r



# %% id="gqlP7zDWuFm5"
#`r.text` contains the raw HTML returned when we made our GET request earlier. 
#`'html5lib'` tells BeautifulSoup that it is reading HTML information. 
soup = bs4.BeautifulSoup(r.text,'html5lib')
# script und style entfernen
for tag in soup(["script", "style"]):
    tag.decompose()
#print(soup.prettify()) # This will print the HTML in a more readable format. You can also just write `soup` to get the same result, but it is not as well formatted.



# %%
links = ["https://moodle.eick-at.de/course/view.php?id=21"]
rawTexts = ["Das ist ein kleiner Test u.a. zum moodle crawlen - keyword spezial"]
rawText = "Das ist ein kleiner Test u.a. zum moodle crawlen - keyword spezial"
shortTexts = [["Das ist ein kleiner Test u.a. zum moodle crawlen - keyword spezial"]]
shortText = ["Das ist ein kleiner Test u.a. zum moodle crawlen - keyword spezial"]

def scrapePage(link,linkText,shortText):
  short_txt = ""
  head = requests.head(link, allow_redirects=True)
  header = head.headers
  content_type = header.get('content-type')
  if content_type == "text/html; charset=utf-8":  # follow only html content
    r = session.get(link)                         # Seiten aufrufen
    #print(content_type, link)
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
        for tag in soup.select('div.drawer'):       # get rid of Contents of question mark button
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
              short_txt += paragraph.get_text()
        rawTexts[-1] += ' ' + txt                   # add txt of page to last element of rawTexts
        shortTexts[-1] += [short_txt]               # add short_txt to last element of shortTexts


# %%
def cutText(txt): # gets list of words an extract the first 18 of them
  wordlength = 18
  wordlist = txt.split(' ')
  if len(wordlist) > wordlength:
    return ' '.join(wordlist[:wordlength]) + " ..."
  else:
    return txt


# %%
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
              short_txt += paragraph.get_text()
        rawTexts[-1] += ' ' + txt                                # add txt of page to last element of rawTexts
        shortTexts[-1] += [short_txt]         # add short_txt to last element of shortTexts


# %%
def crawlPageLinks(activity, sectionname, shortText, rawText):
    print("CRAWL_PAGE_LINKS", sectionname)
    global rawTexts, shortTexts, links
    link_page = activity.select_one("a.aalink")
    #print("CRAWL_PAGE_LINKS: ", link_page)
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

            print("LINK_PAGE=", url)
            print("LINK_TEXT=", linkText)

            scrapePage(url,linkText,shortText + [sectionname] + [linkText])
            
            #print("global shortTexts: ", shortTexts)
            #print("lokal shortText: ", shortText)
            #print("global rawTexts: ", rawTexts)
        else:
            print("Link_Page (ignored, no page link): ", url)   
    return shortTextAddition, rawTextAddition


# %%
def crawlSectionLinks(link_section, section, sectionname, shortText, rawText):
    print("\nCRAWL_SECTION_LINKS :", sectionname)
    global shortTexts, rawTexts

    #print("Parameter: ", sectionname, shortText)
    #print("CRAWL_SECTION_LINKS: ", link_section)
    print("LINK_SECTION=", link_section["href"])
    links.append(link_section["href"])                    # append link to list links
    
    summarytext = section.find('div', attrs={'class':'summarytext'})
    if (summarytext is not None):
        summarytext = summarytext.get_text(strip=True, separator=" ")
        print("SUMMARYTEXT=", summarytext)
        shortTextAddition = [sectionname] + [cutText(summarytext)]
        rawTextAddition = ' ' + sectionname + ' ' + summarytext
    else:
        shortTextAddition = [sectionname]
        rawTextAddition = ' ' + sectionname

    shortTexts.append(shortText + shortTextAddition)      # append shortText
    rawTexts.append(rawText + rawTextAddition)            # append text to list rawTexts
    #print("global shortTexts: ", shortTexts)
    #print("lokal shortText: ", shortText)
    print("global rawTexts: ", rawTexts)
    return shortTextAddition, rawTextAddition


# %% id="5W7IHfpNuFm9"
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

        

# %%
crawlCourse(base_url, shortText)


# %% id="MJWjSV4PWotf"
def processText(txt):
  tokenized = nltk.tokenize.word_tokenize(txt)
  #print(tokenized)
  hannovered = [hannover.analyze(word)[0] for word in tokenized]
  #print(hannovered)
  processed = [w.lower() for w in hannovered if w not in stop]
  #print(processed)
  return processed



# %%
data = []    
i = 0
for rawText in rawTexts:
    #print(i, "RAW_TEXT=", rawText)
    print(i,"Link=", links[i], "\nRAW_TEXT=", rawText)
    print("SHORT_TEXT[i]=", shortTexts[i])
    processedText = processText(rawText)
    data.append((links[i], processedText))
    i += 1

print("DATA=", data)

# %% colab={"base_uri": "https://localhost:8080/", "height": 388} id="bS3JjzO67I5R" outputId="c0e0c0f4-3936-4aff-f2a5-bd8a4163e8ec"
import matplotlib.pyplot as plt
def plot_hist(data):
    entry_lengths = [len(entry[1]) for entry in data]
    fig = plt.figure(figsize=(6, 6)) 
    plt.xlabel('Eintraglänge')
    plt.ylabel('Anzahl der Einträge')
    plt.hist(entry_lengths, bins=20)
    plt.show()
    return entry_lengths
entry_lengths = plot_hist(data)


# %% [markdown] id="q87hHeZyDRMv"
# Bag of words

# %% id="UQlsfmIe7M7x"
# calculate frequency of words
def map_book(hash_map, tokens):
    if tokens is not None:
        for word in tokens:
            # Word Exist?
            if word in hash_map:
                hash_map[word] = hash_map[word] + 1
            else:
                hash_map[word] = 1

        return hash_map
    else:
        return None
        
def make_hash_map(data):  
    hash_map = {}
    for entry in data:
        hash_map = map_book(hash_map, entry[1])
    return hash_map


# define a function frequent_vocab with the following input: word_freq and max_features
def frequent_vocab(word_freq, max_features): 
    counter = 0  #initialize counter with the value zero
    vocab = []   # create an empty list called vocab
    # list words in the dictionary in descending order of frequency
    for key, value in sorted(word_freq.items(), key=lambda item: (item[1], item[0]), reverse=True): 
       #loop function to get the top (max_features) number of words
        if counter<max_features: 
            vocab.append(key)
            counter+=1
        else: break
    return vocab


# %% colab={"base_uri": "https://localhost:8080/"} id="EorQNc7vQZXY" outputId="11e60a90-4b38-41e0-d07b-90435b13d290"
hash_map = make_hash_map(data) #create hash map (words and frequency) from tokenized dataset

vocab=frequent_vocab(hash_map, 1000)  # adjust second Parameter
print(hash_map)
print(vocab)


# %% id="kus5yifih-9q"
# define a function bagofwords with the following input: page and words
def bagofwords(data, vocab):
    # frequency word count
    bag = np.zeros(len(vocab)) #create a NumPy array made up of zeroes with size len(words)
    # loop through data and add value of 1 when token is present in the tweet
    for sw in data:
        for i,word in enumerate(vocab):
            if word == sw: 
                bag[i] += 1
                
    return np.array(bag) # return the bag of word for one page


# %% colab={"base_uri": "https://localhost:8080/"} id="6T8b-f4UjonJ" outputId="d62a4a73-d4a3-4201-d9f5-51ab3f5c4f58"
test = ['subsection']
bagofwords(test, vocab)

# %% id="Zt_jEv0nKFtB"
# set up a NumPy array with the specified dimension to contain the bag of words
n_words = len(vocab)
n_docs = len(data)
bag_o = np.zeros([n_docs,n_words])
# use loop function to add new row for each data of page. 
for ii in range(n_docs): 
    #call out the previous function 'bagofwords'. see the inputs: sentence and words
    bag_o[ii,:] = bagofwords(data[ii][1], vocab) 

# %% colab={"base_uri": "https://localhost:8080/"} id="KZh_YmARpKw-" outputId="7d7354fd-382f-40de-ea36-be3458cfc0cc"
bag_o.shape

# %% [markdown] id="pZHlKeXWt1Ju"
# Inverse document frequency

# %% colab={"base_uri": "https://localhost:8080/"} id="zZfFS_vatzp-" outputId="0191abcc-fd3d-43e7-ac92-cbaa5644deff"
#initialize 2 variables representing the number of pages (numdocs) and the number of tokens/words (numwords)
numdocs, numwords = np.shape(bag_o)

#Changing into the tfidf formula as above
N = numdocs
term_frequency = np.empty(numwords)

#Count the number of documents the word appears in.
for word in range(numwords):
    term_frequency[word]=np.sum(bag_o[:,word]>0) 
print(term_frequency)
idf = np.log(N/term_frequency)
print(idf)

# %% id="lvNFYPM0XVIa"
#initializs tfidf array
tfidf = np.empty([numdocs, numwords])

#loop through the pages, multiply term frequency (represented by bag of words) with idf
for doc in range(numdocs):
    tfidf[doc, :]=bag_o[doc, :]*idf

# %% colab={"base_uri": "https://localhost:8080/"} id="Hw4X28HLunqf" outputId="6bf12448-ab91-4ec6-ed26-cb159a2faf85"
tfidf.shape

# %% colab={"base_uri": "https://localhost:8080/"} id="psVdAxNMwESb" outputId="865a8c1d-80e9-477f-c3a5-27f774de54cf"
print (tfidf)

# %% [markdown] id="bwDDac3d6GNy"
# This data can be saved so that it does not have to be determined each time with web crawling and NLP (could be done as a task once a day).

# %% id="_5Shtx-I6ojA"
filename = "tfidf.npy"   # file extension has to be "npy"
np.save(filename,tfidf)  # numpy provides file functions

# %% [markdown] id="QV68a3IRAkBt"
# The data can be loaded by this:

# %% id="Il36TN8iAYqO"
tfidf=np.load(filename)

# %% colab={"base_uri": "https://localhost:8080/"} id="kwMQCpAq02ZL" outputId="24bb09a6-3c72-4526-9be0-41d68204375c"
# search string
search='subsection, two'

processed = processText(search)
print(processed)
search_vector = bagofwords(processed, vocab)
print(search_vector)

#calculate tfidf 
term_frequency = np.empty(numwords)

#Count the number of documents the search word appears in.
for word in range(numwords):
    term_frequency[word]=np.sum(search_vector[word]>0) 
print(term_frequency)

#initializs tfidf array
search_tfidf = np.empty([numwords])

#multiply term frequency (represented by bag of words) with idf
search_tfidf = term_frequency * idf

print(search_tfidf)

# %% colab={"base_uri": "https://localhost:8080/"} id="6m3hCEhvIjh0" outputId="575a8aaf-4298-418b-8512-1da1aa6b2a69"
#comparision with search vector without tfidf
comparisons = cosine_similarity(tfidf, search_vector.reshape(1,-1))
print(comparisons)
#comparision with tfdif search vector => better results
comparisons = cosine_similarity(tfidf, search_tfidf.reshape(1,-1))
print(comparisons)

# %% colab={"base_uri": "https://localhost:8080/"} id="D1qKH9vXJW8u" outputId="5507c2d5-cb95-4117-b880-0404bc3eee75"
print("search word: ", search)
# best result
print("Best result:", data[comparisons.argmax()][0])

print("All results:")
for i, score in enumerate(comparisons):
    print(score, data[i][0])
