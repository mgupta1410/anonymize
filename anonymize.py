import spacy
import pickle
import re

class Anonymize:
    def __init__(self, tags_to_anon, custom_tags_to_anon=None):
        self.tags_to_anon = tags_to_anon
        self.custom_tags_to_anon = custom_tags_to_anon
        self.mapping = {}
        
        self.nlp = spacy.load('en')
        
        self.nlp = spacy.load('en')

        punctuation = '!"#$%&\'*+,.:;<=>?[\\]^_`{|}~'
        rp = re.compile(re.escape(punctuation))
        ri = re.compile(r'[\s{}]+'.format(re.escape(punctuation)))

        def custom_tokenizer(nlp):
            return spacy.tokenizer.Tokenizer(nlp.vocab, infix_finditer=ri.finditer, suffix_search=rp.search, prefix_search=rp.search)

        self.nlp.tokenizer = custom_tokenizer(self.nlp)
    
    def tokenize(self, string):
        return [token.text for token in self.nlp(string)]
    
    def get_anon_string(self, string):
        anon_tokens = []
        doc = self.nlp(string)
        
        for i, token in enumerate(doc):
            key = token.text
            
            custom_tag, custom_bio = self.get_custom_tag(token.text, self.custom_tags_to_anon)
            
            if token.ent_type_ in self.tags_to_anon or custom_tag is not None:
                if key not in self.mapping:
                    # give priority to custom tag
                    tag = custom_tag if custom_tag is not None else token.ent_type_
                    bio = custom_bio if custom_tag is not None else token.ent_iob_
                    value = "{0}-{1}-{2}".format(tag, bio, str(len(self.mapping)))
                    self.mapping[key] = value
                else:
                    value = self.mapping[key]
                    
                anon_tokens.append(value)
            else:
                anon_tokens.append(key)
        return ' '.join(anon_tokens)
    
    def get_custom_tag(self, token, tags):
        # COURSE
        
        for tag in set(tags):
            if tag == 'COURSE':
                cont_alpha = 0
                cont_digit = 0
                for char in token:
                    if char.isupper():
                        cont_alpha += 1
                    else:
                        break
                for char in token[::-1]:
                    if char.isdigit():
                        cont_digit += 1
                    else:
                        break
                if cont_alpha and cont_digit and cont_alpha + cont_digit == len(token):
                    return tag, 'B'
            
            if tag == 'CONTACT':
                #print("HERE", tag, tags)
                regex = '(([\)]??[\+](\d\d?)[-\.\)]??)??[\(]??\d{3}[\)]??[-\.]??([\(]??\d{3}[\)]??[-\.]??)?[\(]??\d{4}[\)]?)'
                pattern = re.compile(regex)
                obj = pattern.search(token)
                if obj is not None:
                    
                    span = obj.span()
                    if span[0] == 0 and span[1] == len(token):
                        return tag, 'B'
            
            if tag == 'EMAIL':
                regex = '([a-zA-Z.\-0-9]?)+\@[a-zA-Z.\-0-9]*'
                pattern = re.compile(regex)
                obj = pattern.search(token)
                if obj is not None:
                    span = obj.span()
                    if span[0] == 0 and span[1] == len(token):
                        return tag, 'B'
                    
        return None, None
                


    def save_mapping(self, filepath):
         pickle.dump(self.mapping, open( filepath, "wb" ))
            
    def load_mapping(self, filepath=None):
        if filepath is not None:
            self.mapping = pickle.load(open( filepath, "rb" ))
        return self.mapping