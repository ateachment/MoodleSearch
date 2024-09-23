from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def stemmed_words(doc):
    import nltk
    from nltk.corpus import stopwords
    from sklearn.feature_extraction.text import TfidfVectorizer
    from nltk.stem.snowball import GermanStemmer
    import re                                               # regular expression
    stop = nltk.corpus.stopwords.words('german')
    analyzer = TfidfVectorizer().build_analyzer()
    stemmer = GermanStemmer()
    stop += stopwords.words('german') + stopwords.words('english')
    return (stemmer.stem(w) for w in analyzer(doc) if w not in stop and re.match( r'\b[a-zA-Z]{2,}\b', w)) # exclude stopwords, numbers and stemm



@app.route('/', methods=['GET'])
def index():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    import json

    jsonData = json.loads(request.json)
    print(jsonData)
    search = jsonData['search']
    input = jsonData['i']

    
    # search terms
    if(search is not None):
        import cloudpickle as pickle
        from sklearn.metrics.pairwise import cosine_similarity
        import os

        picklesDir="data/"
        filenameLinks = os.path.join(picklesDir, "links_" + input + ".pickle")
        filenameShortTexts = os.path.join(picklesDir, "shortTexts_" + input  + ".pickle")
        filenameTf = os.path.join(picklesDir, "tf_" + input + ".pickle")
        filenameTf_fit = os.path.join(picklesDir, "tf_fit_" + input + ".pickle")

        with open(filenameLinks, "rb") as fp:   # Unpickling
            linksLoaded = pickle.load(fp)
        with open(filenameShortTexts, "rb") as fp:   # Unpickling
            shortTextsLoaded = pickle.load(fp)
        with open(filenameTf, 'rb') as fp:
            tf_loaded = pickle.load(fp)
        with open(filenameTf_fit, 'rb') as fp:
            tf_fit_loaded = pickle.load(fp)

        search_list = []
        search_list.append(search)
        search_tf_fit = tf_loaded.transform(search_list)
        cosinus_similarities = cosine_similarity(search_tf_fit, tf_fit_loaded)

        sorted_similarities = sorted(((value, index) for index, value in enumerate(cosinus_similarities[0])), reverse=True)

        #output
        list = [{"shortText": shortTextsLoaded[similarity[1]], "link": linksLoaded[similarity[1]], "similarity": similarity[0], "index": similarity[1]} for similarity in sorted_similarities[:10] if(similarity[0] > 0)]
        print(json.dumps(list))
        return jsonify(list)
    

if __name__ == '__main__':
    app.run()
