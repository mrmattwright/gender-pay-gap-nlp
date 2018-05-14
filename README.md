# gender-pay-gap-nlp

You can download all the gender pay gap figures from the [gov.uk website](https://gender-pay-gap.service.gov.uk/viewing/download). One of the fields is the url to the companies diversity reports, some are web pages, some are pdfs.

This project downloads that content and performs a series of experiments to see if we can find out any patterns, topics or differences between what people score on gender pay gap statistics and how they talk about the subject.

Authors note; None of this is empirical evidence, it's more of a fun exploration of the topic. We can't draw any concrete conclusions . I'm sure that won't some journalist from doing so though. Sigh.

With that enormous caveat out of the way let's dive headlong into some of the experiments then.


## Topic Analysis

**Notebook:** [lda_viz.ipynb](notebooks/lda_viz.ipynb)

**Goal:** The idea here is have a look at the key topics talked about and group then automatically into topic areas. For this we used LDA and LDAViz to examine the results.

**How:**
Uses LDA to automatically group a 'good' and 'bad' corpus into groups, then you can compare which topics 'good' and 'bad' companies talk about.

![LDA Viz](images/ldaviz1.png)

**Results:**
Ok, but hard to tell

## Word Similarity

**Notebook:** [word_similarity.ipynb](notebooks/word_similarity.ipynb)


**Goal:** To see if companies use the same sorts of language around certain words. Do good companies use the word 'community' in a different way to bad companies for example.

**How:** Builds two word2vec models, one on a corpus of 'good' scoring diversity documents, another on a corpus of 'bad' diversity documents then does a little set math to see what words related to a choosen word that only 'good' people mention and the reverse to see what words are used exclusively by those that score badly in diversity.

**Results**
Some examples.


## Document Similarity

**Notebook:** Notebook: [document_similarity.ipynb](notebooks/document_similarity.ipynb)

**Goal:**
Work in Progress

**How:**
Uses doc2vec.

**Results**
