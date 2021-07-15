#!/usr/bin/env python3

from phonemizer import phonemize
from phonemizer import separator
import nltk
import re
import pandas as pd
from tqdm import tqdm
import num2words
import ipapy


def convert_num_to_words(utterance, language_code = 'en'):
      utterance = ' '.join([num2words.num2words(i, lang=language_code) if i.isdigit() else i for i in utterance.split()])
      return utterance

    #normalise digits, 


def text_to_phrases(text, language_code='en-us'):
    # Turn text into phrases based on punctuation and lines.
    # TODO : MDS - take care of unicode. 
    punc_separators = '[;:,.!?¡¿—…"«»“”]'
    phrases = []
    with open(text, 'r', encoding="utf-8") as infile:
        for l in infile :
            phrases.extend([convert_num_to_words(p, language_code = language_code) for p in re.split(punc_separators, l.strip()) if checkString(p)]) #check not empty
    return phrases




def phonemize_phrases(phrases, language_code='en-us', njobs=4):

    # phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = 'remove-flags', njobs=njobs)
    sep = separator.Separator(phone=' ', syllable='', word='/w ')
    phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = 'remove-flags', separator = sep,  njobs=njobs) # here with word separator and space between phone

    if len(phrases) != len(phon):
        raise ValueError("Length of input phrases and output phonemised phrases differ")
    return phon


#def simplify_phones



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



# def phoneme_statistics(phonemised_phrases, wordbounds=True):

#     if wordbounds: #one item is one boundary. Don"t care about utterances anymore
#         phrases = []
#         for utt in phonemised_phrases:
#             for x in utt.split('/w'):
#                 if x.strip():
#                     phrases.append(x.strip())

#     else:
#         phrases = []
#         for utt in phonemised_phrases:
#             x = utt.replace('/w ', '')
#             phrases.append(x.strip())
                
        
#     all_counts = dict()
#     for size in [2,3,4,5,6]:
#         counts = nltk.FreqDist()
#         for sent in phrases:
#             counts.update(nltk.ngrams(nltk.tokenize.word_tokenize(sent), size))
#         all_counts[size]=counts
#     #find a way to get the syllables
#     return all_counts


def phoneme_statistics(phonemised_phrases):

    # #if wordbound
    # n = 4
    # for sent in phrases :
    #     for i in range(len(sent)-n+1):
    #         counts.update(sent[i:i+n])
        
    all_counts = dict()
    for size in [3,4,5,6,7, 8, 9]:
        counts = nltk.FreqDist()
        for sent in phonemised_phrases:
            counts.update(nltk.ngrams(nltk.tokenize.word_tokenize(sent), size))
        all_counts[size]=counts
    #find a way to get the syllables
    return all_counts


def get_valid_ngrams(phoneme_count_dict, syllable_list=['V', 'CV', 'VC', 'CVC', 'CCV', 'CCCV', 'CVCC']):
    # V CV VC CVC CCV CCCV CVCC''' #CAREFUL NOT TO COUNT TWICE
    w = [] #list of tuples of form (phoneme_list, count, syllable structure
    nw =[] 

    for size in phoneme_count_dict.keys() :
        for k,v in phoneme_count_dict[size].items():
            if k[0] == '/w' and k[-1] == '/w' and k.count('/w') == 2 :
                #That means that  word boundaires on both sides and not in middle, we can create a real word.
                seg = k[1:-2]
                struct = [get_phone_desc(x) for x in seg]
                if None in struct:
                    continue
                potential =  list(find_syllable_split(struct, syllable_list=syllable_list))
                if len(potential)>0:

                    for x in potential:
                        p_struct=x[0]
                        p_seg=seg[0:x[1]],seg[x[1]:] 
                        w.append((p_seg, p_struct,v)) 

            
            elif k.count('/w') == 1 and  k[0] != '/w' and k[-1] != '/w':
                
                struct = [get_phone_desc(x) for x in k]
                if None in struct:
                    continue #don't care when problems inphones 
                idx = [idx for idx, val in enumerate(struct) if val == "BOUND"][0]

                
                if ''.join(struct[0:idx]) in syllable_list and ''.join(struct[idx+1:]) in syllable_list :
                    n1 = k[0:idx] 
                    n2 = k[idx+1:]
                    seg = (n1, n2)
                    nw.append(((n1,n2), (struct[0:idx], struct[idx+1:]), v))

                
                
                #That means we can create a protoword
                pass
            else:
                continue

    col=['segments', 'structure', 'count']
    w_df = pd.DataFrame(w)
    nw_df = pd.DataFrame(nw)


    w_df.columns=col
    nw_df.columns=col

    return w_df, nw_df
    # return w, nw



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
    if phone_string == '/w':
        return "BOUND"
    elif phone_string not in ipapy.UNICODE_TO_IPA :
        return None
    elif ipapy.UNICODE_TO_IPA[phone_string].is_consonant :
        return "C"
    elif ipapy.UNICODE_TO_IPA[phone_string].is_vowel :
        return "V"
    else:
        return None

    
def checkString(string):
    return any(c.isalpha() for c in string)


def find_syllable_split(l,syllable_list=['V', 'CV', 'VC', 'CVC', 'CCV', 'CCCV', 'CVCC']):
    a = []
    for i in range(1, len(l)):
        n1=l[0:i]
        n2=l[i:]
        if ''.join(n1) in syllable_list and ''.join(n2) in syllable_list:
            yield ((n1, n2), i)
        
# def split_list_into_list(l, l_separator):
#     # using list comprehension + zip() + slicing + enumerate()
#     # Split list into lists by particular value
#     size = len(l)
#     idx_list = [idx + 1 for idx, val in enumerate(l) if val == l_separator]
#     res = [l[i: j-1] for i, j in zip([0] + idx_list, idx_list + ([size+1] if idx_list[-1] != size else [size])) if len(l[i: j-1])>0]

#     return res


#def split_structure(list):
    
#works if i can split the string into two structures following the ... . :
## V CV VC CVC CCV CCCV CVCC

                        
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text_file", help="path to the input text file")
    parser.add_argument("n_job", help="number of jobs for phonemizer", default=1)
    pars.add_argument(language_code, default='en-us')
    parser.parse_args()
    args, leftovers = parser.parse_known_args()



    #phrases = text_to_phrases('tmp.txt', language_code='fr-fr')
    # phon_phrases = phonemize_phrases(phrases, language_code='fr-fr', njobs=8)
    #phon_dict = phoneme_statistics(phon_phrases)
    #w_df, nw_df = get_valid_ngrams(phon_dict)

