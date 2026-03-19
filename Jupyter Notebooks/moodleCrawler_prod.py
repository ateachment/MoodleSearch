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
#     display_name: Python 3
#     name: python3
# ---

# %% [markdown] id="view-in-github" colab_type="text"
# <a href="https://colab.research.google.com/github/ateachment/MoodleSearch/blob/main/moodleCrawler_prod.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# %% [markdown] id="_eOGZGBMo1RR"
# Crawler for Moodle Courses
#

# %% colab={"base_uri": "https://localhost:8080/"} id="5C4I2-U9oWOh" outputId="fa534888-0702-489b-fce6-a8623ff6492b"
pip install HanTa # install lemmatizer of german language

# %% colab={"base_uri": "https://localhost:8080/"} id="vy0yCK5XUOqg" outputId="b786b978-a75a-4d4d-df77-483526c409bf"
import requests
import bs4
import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

from HanTa import HanoverTagger as ht
hannover = ht.HanoverTagger('morphmodel_ger.pgz')
from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np

# %% id="Yvhqsb-kuAAT"
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
stop.append('u.b')
stop.append('--')
stop.append('-')
stop.append('``')
stop.append("''")

# %% colab={"base_uri": "https://localhost:8080/"} id="6X_Z48OluFm0" outputId="bc7b41c2-c4cc-4032-8108-3c51d743416b"
base_url = 'https://eick-at.de/moodle/course/view.php?id=15#section-6'  # URL of the Moodle Course
r = requests.get(base_url)                                              # Http Request 
r


# %% id="gqlP7zDWuFm5"
soup = bs4.BeautifulSoup(r.text,'html5lib')

# %% id="5W7IHfpNuFm9"
headers = []                         
for url in soup.findAll("h3"):      # find sections
    headers.append(url)

# %% colab={"base_uri": "https://localhost:8080/"} id="buS--jRbWhaW" outputId="b1e03a39-9ee6-4e33-b162-ce9fdcd47123"
headers


# %% id="MJWjSV4PWotf"
def processText(txt):
  tokenized = nltk.tokenize.word_tokenize(txt)
  #print(tokenized)
  hannovered = [hannover.analyze(word)[0] for word in tokenized]
  #print(hannovered)
  processed = [w.lower() for w in hannovered if w not in stop]
  #print(processed)
  return processed



# %% colab={"base_uri": "https://localhost:8080/"} id="A9I9PI1auFnC" outputId="17b4d322-f52b-4863-e648-fbc1b042b829"
data = []                                      
for header in headers:                          # iterate sections
  # print(header)
  link = header.find('a').attrs['href']         # extract link of section
  txt = header.get_text()                       # extract text of section
  processed = processText(txt)                  # nlp of section text
  entry = [link, processed]                     # list entry with link and processed text
  print(entry)
  data.append(entry)                            # append entry in list data (nested lists)

  listTags = header.find_next_sibling('ul')     # pages, tasks, links ..
  for li in listTags:
    #print(li)
    link = li.find('a')
    txt2 = link.get_text().replace("Page","").replace("URL","").replace("Assignment","")
    if not("URL" in link.get_text()):
      link = link.attrs['href'] 
      
      r = requests.get(link)                    # Seiten aufrufen
      soup2 = bs4.BeautifulSoup(r.text,'html5lib')
      header2 = soup2.find('h2')                # Überschrift
      #print(header2)
      paragraphs = header2.find_all_next('p')   # Absätze
      txt = ""
      for paragraph in paragraphs:
        txt += paragraph.get_text()
      txt2 += txt
      #print(link,txt2)
      processed =processText(txt2)
      entry = [link, processed]
      print(entry)
      data.append(entry)



# %% [markdown] id="AnEogOIxVcnN"
#

# %% colab={"base_uri": "https://localhost:8080/", "height": 388} id="bS3JjzO67I5R" outputId="eafb479d-4910-4a48-a009-985331656e78"
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


# %% colab={"base_uri": "https://localhost:8080/"} id="EorQNc7vQZXY" outputId="91b5f1ea-9b20-4003-8d63-c2cbacb5f33f"
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


# %% id="Zt_jEv0nKFtB"
# set up a NumPy array with the specified dimension to contain the bag of words
n_words = len(vocab)
n_docs = len(data)
bag_o = np.zeros([n_docs,n_words])
# use loop function to add new row for each data of page. 
for ii in range(n_docs): 
    #call out the previous function 'bagofwords'. see the inputs: sentence and words
    bag_o[ii,:] = bagofwords(data[ii][1], vocab) 

# %% [markdown] id="pZHlKeXWt1Ju"
# Inverse document frequency

# %% id="zZfFS_vatzp-"
#initialize 2 variables representing the number of pages (numdocs) and the number of tokens/words (numwords)
numdocs, numwords = np.shape(bag_o)

#Changing into the tfidf formula as above
N = numdocs
term_frequency = np.empty(numwords)

#Count the number of documents the word appears in.
for word in range(numwords):
    term_frequency[word]=np.sum(bag_o[:,word]>0) 
idf = np.log(N/term_frequency)

# %% id="lvNFYPM0XVIa"
#initializs tfidf array
tfidf = np.empty([numdocs, numwords])

#loop through the pages, multiply term frequency (represented by bag of words) with idf
for doc in range(numdocs):
    tfidf[doc, :]=bag_o[doc, :]*idf

# %% id="kqumcsHHqYDg"
filename = "tfidf.npy"   # file extension has to be "npy"
np.save(filename,tfidf)  # numpy provides file functions
