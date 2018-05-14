from src.data.diversity_document import DiversityDocument
from gensim.models import Phrases
from gensim.corpora import Dictionary
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

class DiversityUtils:
    def __init__(self, attributes):
        self.attributes = attributes

    @classmethod
    def iter_diversity_data(cls, df_divers):
        with open('../data/external/download_whitelist.txt', 'r') as f:
            whitelist = [line.strip() for line in f]

        number_rows = df_divers.shape[0]
        counter = 0
        for index, row in df_divers.iterrows():
            counter = counter + 1
            percent_complete = (counter / number_rows) * 100

            if counter % 100 == 0:
                #clear_output(wait=True)
                print('%.2f percent complete' % (percent_complete))

            doc = DiversityDocument(row)

            if doc.url_hash in whitelist:
                continue

            if not doc.has_downloaded_file and not doc.company_link == 'nan':
                doc.download()
                if doc.raw_text is None:
                    with open('../data/external/download_whitelist.txt', 'a') as whitelist_file:
                        whitelist_file.write(doc.url_hash + '\n')

            if doc.raw_text is not None and doc.clean_text is not None:
                yield doc.clean_text

        print('Processing Finished: 100%')

class CorpusDiversity(object):
    def __init__(self, df):
        self.df = df
        self.dictionary = Dictionary(DiversityUtils.iter_diversity_data(df))

    def __iter__(self):
        for doc in DiversityUtils.iter_diversity_data(self.df):
            # tokenize each message; simply lowercase & match alphabetic chars, for now
            yield self.dictionary.doc2bow(doc)

#    def __len__(self):
#        return len(self.dictionary)

class CorpusSentenceDiversity(object):
    def __init__(self, df):
        self.df = df
        self.dictionary = Dictionary(DiversityUtils.iter_diversity_data(df))

    def __iter__(self):
        for doc in DiversityUtils.iter_diversity_data(self.df):
            # tokenize each message; simply lowercase & match alphabetic chars, for now
            yield doc

class LabeledLineSentence(object):
    def __init__(self, df):
       self.df = df
    def __iter__(self):
        for label, doc in DiversityUtils.iter_diversity_data(self.df):
            yield TaggedDocument(words=doc,tags=list(label))
