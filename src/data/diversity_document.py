import io, os, sys
from urllib.request import urlopen
import urllib.request
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import hashlib
import json
from socket import timeout
from bs4 import BeautifulSoup
from bs4.element import Comment
import warnings
from spacy.lang.en.stop_words import STOP_WORDS

class DiversityDocument:

    def __init__(self, attributes):
        self.attributes = attributes
        self.company_name = attributes['EmployerName']
        self.company_link = attributes['CompanyLinkToGPGInfo']
        hash_object = hashlib.md5(bytes(self.company_link, 'utf-8'))
        self.url_hash = hash_object.hexdigest()
        self.is_pdf = self.company_link.lower().endswith('pdf')
        self.file_path = os.path.join(os.getcwd(), '../data/raw/' + self.url_hash)
        self.clean_file_path = os.path.join(os.getcwd(), '../data/cleaned/' + self.url_hash + '.json')
        self.has_downloaded_file = os.path.isfile(self.file_path)
        self.has_downloaded_clean_file = os.path.isfile(self.clean_file_path)
        self.raw_text = self.load_text()
        self.clean_text = self.clean_text()

    def __str__(self):
        return "%s -- %s" % (self.company_name, self.company_link)

    def load_text(self):
        if self.has_downloaded_file:
            #print('Already downloaded %s -- %s' % (self.company_name, self.company_link))
            fh = open(self.file_path, "r", encoding="utf-8")
            return fh.read()
        else:
            return None

    def clean_text(self):
        if self.has_downloaded_clean_file:
            #print('Already downloaded clean text tokens for %s ' % (self.company_name))
            with open(self.clean_file_path, 'r') as f:
                doc = json.load(f)
            return doc
        else:
            return self.save_clean_text()

    def save_clean_text(self):
        if not self.raw_text:
            return None

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",category=DeprecationWarning)
            import spacy
            nlp = spacy.load('en')
            doc = nlp(self.raw_text)

            ents = doc.ents  # Named entities.
            # Keep only words (no numbers, no punctuation).
            # Lemmatize tokens, remove punctuation and remove stopwords.
            doc = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop and len(token) > 1]

            # Remove common words from a stopword list.
            doc = [token for token in doc if token not in STOP_WORDS]

            # Add named entities, but only if they are a compound of more than word.
            doc.extend([str(entity) for entity in ents if len(entity) > 1])
            with open(self.clean_file_path, 'w') as f:
                json.dump(doc, f)
            return doc

    def download(self):
        print('Downloading (%s)....' % (self.company_link))

        if self.is_pdf:
            self.raw_text = self.convert_pdf_to_txt(self.company_link)
        else:
            self.raw_text = self.convert_url_to_txt(self.company_link)

        if self.raw_text:
            open(self.file_path, 'wb').write(bytes(self.raw_text, 'utf-8'))
        return self.raw_text

    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def tag_links(self, element):
        if element.parent.name in ['a']:
            return True
        return False

    def convert_url_to_txt(self, url):
        if url == 'nan':
            return None
        try:
            html = urlopen(url, timeout=15)
            soup = BeautifulSoup(html, 'html.parser')
            texts = soup.findAll(text=True)
            visible_texts = filter(self.tag_visible, texts)
            #soup.find_all('a')
            return u" ".join(t.strip() for t in visible_texts)
        except (urllib.error.HTTPError, urllib.error.URLError) as error:
            print('Data not retrieved because %s\nURL: %s' % (error, url))
            return None
        except timeout:
            print('socket timed out - URL %s' % (url))
            return None
        except KeyboardInterrupt:
            raise
        except EOFError:
            raise
        except:
            print('Exception caught %s' % (sys.exc_info()[0]))
            return None


    def convert_pdf_to_txt(self, url):
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        #text = None

        try:
            f = urlopen(url, timeout=15).read()
            # Cast to StringIO object
            fp = io.BytesIO(f)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos = set()
            for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=False):
                interpreter.process_page(page)
            text = retstr.getvalue()
        except (urllib.error.HTTPError, urllib.error.URLError) as error:
            print('Data not retrieved because %s\nURL: %s' % (error, url))
            return None
        except timeout:
            print('socket timed out - URL %s' % (url))
            return None
        except KeyboardInterrupt:
            raise
        except EOFError:
            raise
        except:
            print('Exception caught %s' % (sys.exc_info()[0]))
            return None

        fp.close()
        device.close()
        retstr.close()
        return text
