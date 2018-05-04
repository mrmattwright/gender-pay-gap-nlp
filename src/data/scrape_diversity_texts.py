import pandas as pd
import numpy as np
import sys
from src.data.diversity_document import DiversityDocument
import spacy
nlp = spacy.load('en')
from gensim.models import Phrases
from gensim.corpora import Dictionary

df = pd.read_csv('data/external/2017-18stats.csv')
with open('data/external/download_whitelist.txt', 'r') as f:
    whitelist = [line.strip() for line in f]
df['CompanyLinkToGPGInfo'] = df['CompanyLinkToGPGInfo'].astype(str)

number_of_companies = len(df.index)
texts = list()
metadata = list()

for index, row in df.head(100).iterrows():
    percent_complete = ((index + 1) / number_of_companies) * 100
    print('%.2f percent complete' % (percent_complete))

    doc = DiversityDocument(row)

    if doc.url_hash in whitelist:
        continue

    if doc.raw_text is not None:
        texts.append(doc.raw_text)
        metadata.append(row.to_dict())

    if not doc.has_downloaded_file and not doc.company_link == 'nan':
        doc.download()
        if doc.raw_text is None:
            with open('data/external/download_whitelist.txt', 'a') as whitelist_file:
                whitelist_file.write(doc.url_hash + '\n')


processed_docs = []
for doc in nlp.pipe(texts, n_threads=4, batch_size=100):
    # Process document using Spacy NLP pipeline.

    ents = doc.ents  # Named entities.

    # Keep only words (no numbers, no punctuation).
    # Lemmatize tokens, remove punctuation and remove stopwords.
    doc = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]

    # Remove common words from a stopword list.
    #doc = [token for token in doc if token not in STOPWORDS]

    # Add named entities, but only if they are a compound of more than word.
    doc.extend([str(entity) for entity in ents if len(entity) > 1])

    processed_docs.append(doc)

docs = processed_docs
del processed_docs

# Add bigrams and trigrams to docs (only ones that appear 20 times or more).
bigram = Phrases(docs, min_count=20)
for idx in range(len(docs)):
    for token in bigram[docs[idx]]:
        if '_' in token:
            # Token is a bigram, add to document.
            docs[idx].append(token)


# Create a dictionary representation of the documents, and filter out frequent and rare words.
dictionary = Dictionary(docs)

# Remove rare and common tokens.
# Filter out words that occur too frequently or too rarely.
max_freq = 0.5
min_wordcount = 20
dictionary.filter_extremes(no_below=min_wordcount, no_above=max_freq)

_ = dictionary[0]  # This sort of "initializes" dictionary.id2token.

# Vectorize data.

# Bag-of-words representation of the documents.
corpus = [dictionary.doc2bow(doc) for doc in docs]

print('Number of unique tokens: %d' % len(dictionary))
print('Number of documents: %d' % len(corpus))
    #except Exception as e:
    #    print('Exception caught %s' % (sys.exc_info()[0]))
#
#corpus.add_texts(texts, metadatas=metadata, n_threads=4, batch_size=1000)
#corpus = textacy.Corpus('en', texts=iter(texts), metadatas=iter(metadata))
#src.data.textacy_helper.save_corpus(corpus, 'data/cleaned/2018_04_23_raw_gender_pay_gap')
