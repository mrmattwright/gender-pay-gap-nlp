import pickle
from cytoolz import itertoolz
from textacy import Corpus
from spacy.util import get_lang_class


def save_corpus(corpus, fname):
    # save the spacy_lang data as the first element
    to_save = [corpus.spacy_lang.meta]
    to_save.extend([doc.spacy_doc for doc in corpus])

    pickle_dump(to_save, fname)


def load_corpus(fname):
    loaded = pickle_load(fname)

    spacy_lang_meta = loaded[0]
    spacy_docs = loaded[1:]

    first_spacy_doc, spacy_docs = itertoolz.peek(spacy_docs)

    spacy_lang = get_lang_class(spacy_lang_meta['lang'])(vocab=first_spacy_doc.vocab,
                                                         meta=spacy_lang_meta)

    for name in spacy_lang_meta['pipeline']:
        spacy_lang.add_pipe(spacy_lang.create_pipe(name))

    corpus = Corpus(spacy_lang, docs=spacy_docs)
    return corpus


class MacOSFile(object):

    def __init__(self, f):
        self.f = f

    def __getattr__(self, item):
        return getattr(self.f, item)

    def read(self, n):
        # print("reading total_bytes=%s" % n, flush=True)
        if n >= (1 << 31):
            buffer = bytearray(n)
            idx = 0
            while idx < n:
                batch_size = min(n - idx, 1 << 31 - 1)
                # print("reading bytes [%s,%s)..." % (idx, idx + batch_size), end="", flush=True)
                buffer[idx:idx + batch_size] = self.f.read(batch_size)
                # print("done.", flush=True)
                idx += batch_size
            return buffer
        return self.f.read(n)

    def write(self, buffer):
        n = len(buffer)
        # print("writing total_bytes=%s..." % n, flush=True)
        idx = 0
        while idx < n:
            batch_size = min(n - idx, 1 << 31 - 1)
            # print("writing bytes [%s, %s)... " % (idx, idx + batch_size), end="", flush=True)
            self.f.write(buffer[idx:idx + batch_size])
            # print("done.", flush=True)
            idx += batch_size


def pickle_dump(obj, file_path):
    with open(file_path, "wb") as f:
        return pickle.dump(obj, MacOSFile(f), protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(MacOSFile(f))
