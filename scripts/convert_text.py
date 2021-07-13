#!/usr/bin/env python3

from phonemizer import phonemize
from phonemizer import separator
import nltk
import re
from tqdm import tqdm
import ipapy
def text_to_phrases(text):
    # Turn text into phrases based on punctuation and lines.
    # TODO : MDS - take care of unicode. 
    punc_separators = ';:,.!?¡¿—…"«»“”'
    phrases = []
    with open(text, 'r', encoding="utf-8") as infile:
        for l in infile :
            phrases.extend([p for p in re.split('[?.,]', l.strip()) if checkString(p)]) #check not empty
    return phrases




def phonemize_phrases(phrases, language_code='en-us', njobs=4):

    # phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = 'remove-flags', njobs=njobs)
    sep = separator.Separator(phone=' ', syllable='', word='/w ')
    phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = 'remove-flags', separator = sep,  njobs=njobs) # here with word separator and space between phone

    if len(phrases) != len(phon):
        raise ValueError("Length of input phrases and output phonemised phrases differ")
    return phon

def word_statistics(phrases):
    
    # turn into words (tokens)
    from nltk import ngrams, FreqDist
    from nltk.tokenize import word_tokenize
    all_counts = dict()
    size=2
    all_counts[size] = FreqDist(ngrams(word_tokenize(data), size))
    all_counts[size] = FreqDist([ngrams(word_tokenize(ph), 2) for ph in p])
    #def protoword_statistics(ngram_size=2
    counts = nltk.FreqDist()   
    for sent in phrases:
        counts.update(nltk.ngrams(nltk.tokenize.word_tokenize(sent), 2))



def phoneme_statistics(phonemised_phrases, wordbounds=True):

    if wordbounds: #one item is one boundary. Don"t care about utterances anymore
        phrases = []
        for utt in phonemised_phrases:
            for x in utt.split('/w'):
                if x.strip():
                    phrases.append(x.strip())

    else:
        phrases = []
        for utt in phonemised_phrases:
            x = utt.replace('/w ', '')
            phrases.append(x.strip())
                
        
    all_counts = dict()
    for size in [2,3,4,5,6]:
        counts = nltk.FreqDist()
        for sent in phrases:
            counts.update(nltk.ngrams(nltk.tokenize.word_tokenize(sent), size))
        all_counts[size]=counts
    #find a way to get the syllables
    return all_counts



# def get_syllables(phon_phrase):
#     '''phon_phraserase: string
#     We consider a syllable is either consonant(s) + vowel(s) or vowel + consonant
#     or that tehy are cut by word boundaries - ??
#     FOllowing these syllabification rules : 
#     V CV VC CVC CCV CCCV CVCC'''

#     phones = phon_phrase.strip().split(' ')
#     phones_type = [get_phone_desc(x) for x in phones]
#     syllables = []
#     i=0
    
#     while i < len(phon_phrase):
#         start = i
#         bound = False
#         while bound = False:

#             if phones[i] == "/w":
#                 i+=1
#                 bound=true

#             #V
#             if phones_type[i] == "V" and phones[i+1] == "/w":
#                 i+=2
#                 bound=true

#             #CV
#             if phones_type[i] == "C" and phones_type[i+1] == "V" and phones[i+2] == "/w":
#                 i+=3
#                 bound=true
                

            
#         if start != end:
#             syllables.append[phon_phrase[start:i]
        
      

    
    

#def get_phoneme_boundaries:


def get_phone_desc(phone_string):
    if phone_string not in ipapy.UNICODE_TO_IPA :
        return None
    if ipapy.UNICODE_TO_IPA[phone_string].is_consonant :
        return "C"
    elif ipapy.UNICODE_TO_IPA[phone_string].is_vowel :
        return "V"
    else:
        return None

    
def checkString(string):
    return any(c.isalpha() for c in string)    
                        
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text_file", help="path to the input text file")
    parser.add_argument("n_job", help="number of jobs for phonemizer", default=1)
    pars.add_argument(language_code, default='en-us')
    parser.parse_args()
    args, leftovers = parser.parse_known_args()



    #phrases = text_to_phrases('tmp.txt')
    # phon_phrases = phonemize_phrases(phrases, language_code='fr-fr', njobs=8)
    #phon_wb = phoneme_statistics(phon_phrases)
    #phon_nwb = phoneme_statistics(phon_phrases, wordbounds=False)
