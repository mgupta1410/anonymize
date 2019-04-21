import spacy
import pickle

nlp = spacy.load('en')

class Anonymize:
    def __init__(self, tags_to_anon):
        self.tags_to_anon = tags_to_anon
        self.mapping = {}
    
    def get_anon_string(self, string):
        anon_tokens = []
        doc = nlp(string)
        for i, token in enumerate(doc):
            key = token.text
            if token.ent_type_ in self.tags_to_anon:
                if key not in self.mapping:
                    value = "{0}-{1}-{2}".format(token.ent_type_, token.ent_iob_, str(len(self.mapping)))
                    self.mapping[key] = value
                else:
                    value = self.mapping[key]
                anon_tokens.append(value)
            else:
                anon_tokens.append(key)
        return ' '.join(anon_tokens)
    
    def save_mapping(self, filepath):
         pickle.dump(self.mapping, open( filepath, "wb" ))
            
    def load_mapping(self, filepath=None):
        if filepath is not None:
            self.mapping = pickle.load(open( filepath, "rb" ))
        return self.mapping