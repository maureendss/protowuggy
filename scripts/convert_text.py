#!/usr/bin/env python3

from phonemizer import phonemize
from phonemizer import separator
import nltk
import re
import pandas as pd
from tqdm import tqdm
import num2words
import ipapy
from collections import defaultdict
import pickle
import os

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




def phonemize_phrases(phrases, language_code='en-us', njobs=4, language_switch="remove-flags"):

    # phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = 'remove-flags', njobs=njobs)
    sep = separator.Separator(phone=' ', syllable='', word='/w ')
    phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = language_switch, separator = sep,  njobs=njobs) # here with word separator and space between phone

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

        
def phoneme_statistics(phonemised_phrases):

    all_counts = dict()
    for size in [3,4,5,6,7, 8, 9, 10]:
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
                seg = k[1:-1]
                struct = [get_phone_desc(x) for x in seg]
                if None in struct:
                    continue
                potential =  list(find_syllable_split(struct, syllable_list=syllable_list))
                if len(potential)>0:

                    for x in potential:
                        p_struct=x[0]
                        n1=seg[0:x[1]]
                        n2=seg[x[1]:]

                        form=' '.join([' '.join(n1), ' '.join(n2)])
                        form_bound=' '.join(k)
                        s = " | ".join([" ".join(p_struct[0])," ".join(p_struct[1])])
                        sy=" | ".join([" ".join(n1)," ".join(n2)])
                        w.append((form, form_bound, sy, s,v))
                        
                        
                            
            elif k.count('/w') == 1 and  k[0] != '/w' and k[-1] != '/w':
                
                struct = [get_phone_desc(x) for x in k]
                if None in struct:
                    continue #don't care when problems inphones 
                idx = [idx for idx, val in enumerate(struct) if val == "BOUND"][0]

                
                if ''.join(struct[0:idx]) in syllable_list and ''.join(struct[idx+1:]) in syllable_list :
                    n1 = k[0:idx] 
                    n2 = k[idx+1:]
                    seg = (n1, n2)

                    form=' '.join([' '.join(n1), ' '.join(n2)])
                    form_bound=' '.join(k)

                    sy=" | ".join([" ".join(n1)," ".join(n2)])
                    s = " | ".join([" ".join(struct[0:idx])," ".join(struct[idx+1:])]) 
                    nw.append((form, form_bound, sy, s, v))

                
                
                #That means we can create a protoword
                pass
            else:
                continue

    col=['form', 'form_bound','syll', 'structure', 'count']
    w_df = pd.DataFrame(w)
    nw_df = pd.DataFrame(nw)


    w_df.columns=col
    nw_df.columns=col

    return w_df, nw_df
# return w, nw


def match_w_nw(w_df, nw_df,n_perc=1):
    #match words and non words. 
    #1. get all common structures in w/nw
    w_struct = []
    nw_struct=[]
    for x in w_df['structure']:
        if x not in w_struct:
            w_struct.append(x)
    for x in nw_df['structure']:
        if x not in nw_struct:
            nw_struct.append(x)

            
    common_struct = [x for x in w_struct if x in nw_struct]
    print("{} potential syllable structures".format(len(common_struct)))

    #Trimming the dfs so that we can do our matches
    cond = w_df['form'].isin(nw_df['form'])
    w_df = w_df.drop(w_df[cond].index, inplace = False)
    cond = nw_df['form'].isin(w_df['form'])
    nw_df = nw_df.drop(nw_df[cond].index, inplace = False)
    

    #2. If form is same in both word and non word, remive!
    #2. for item in ..., get item of other
    #only do if same conosonant. 

    #threshold = n_freq of word_boundaries eg the lowest count of the hif=ghest 1% of words, regardless of structure

    hf_threshold = int(get_n_freq_phrases(w_df, n_perc=n_perc).tail(1)['count'])
    lf_threshold = int(get_n_freq_phrases(w_df,n_perc=n_perc, direction = "low").tail(1)['count'])
    
    high_freq = defaultdict(dict)
    
    low_freq=defaultdict(dict) 
    for structure in common_struct:
        high_freq[structure]=defaultdict(dict)
        low_freq[structure]=defaultdict(dict)

        w_tmp_df = w_df[w_df['structure'] == structure]
        nw_tmp_df = nw_df[nw_df['structure'] == structure]
        if len(w_tmp_df[w_tmp_df['count']>=hf_threshold])>1 and len(nw_tmp_df[nw_tmp_df['count']>=hf_threshold])>1 and len(w_tmp_df[w_tmp_df['count']>=lf_threshold])>1 and len(nw_tmp_df[nw_tmp_df['count']>=lf_threshold])>1 :
            high_freq[structure]['w'] = w_tmp_df[w_tmp_df['count']>=hf_threshold]
            high_freq[structure]['nw'] = nw_tmp_df[nw_tmp_df['count']>=hf_threshold]
            low_freq[structure]['w'] = w_tmp_df[w_tmp_df['count']>=lf_threshold]
            low_freq[structure]['nw'] = nw_tmp_df[nw_tmp_df['count']>=lf_threshold]

    #prune empty keys
    hf = dict( [(k,v) for k,v in high_freq.items() if len(v)>0])
    lf=dict( [(k,v) for k,v in low_freq.items() if len(v)>0])

    return hf,lf
    

def get_n_freq_phrases(df, n_perc=1, direction="high"):
    # if direction is low, and n_perc = 1, then we take the 1% less frequent

    #n is dependent on length of dataset
    n=int(round(n_perc*len(df)/100))
    if direction == "high":
        n_freq = df.sort_values(by=["count"], ascending=False).head(n)
    elif direction =="low":
        n_freq = df.sort_values(by=["count"], ascending=True).head(n)
    return n_freq

    
#--UTILS--------------------------------------------------------------------------

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
        
                       
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text_file", help="path to the input text file")
    parser.add_argument('output_dir')
    parser.add_argument("--n_job", help="number of jobs for phonemizer", default=50)
    parser.add_argument("--language_code", default='en-us')
    
    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    print("creating output dir in {}".format(args.output_dir))
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)
        
    if not os.path.isfile(os.path.join(args.output_dir, 'phrases.pkl')):
        print("....Loading text")
        phrases = text_to_phrases(args.text_file, language_code=args.language_code)
        with open(os.path.join(args.output_dir, 'phrases.pkl'), 'w') as outfile:
            pickle.dump(phrases, outfile)
    else:
        with open(os.path.join(args.output_dir, 'phrases.pkl'), 'rb') as f:
            phrases = pickle.load(f)


            
    if not os.path.isfile(os.path.join(args.output_dir, 'phon_phrases.pkl')):
        print("...phonemizing phrases")
        phon_phrases = phonemize_phrases(phrases, language_code=args.language_code, njobs=args.n_job)
        print('...done with phonemization')
        with open(os.path.join(args.output_dir, 'phon_phrases.pkl'), 'wb') as outfile:
            pickle.dump(phon_phrases, outfile)
    else:
        with open(os.path.join(args.output_dir, 'phon_phrases.pkl'), 'rb') as f:
            phon_phrases = pickle.load(f)

    phon_dict = phoneme_statistics(phon_phrases)
    w_df, nw_df = get_valid_ngrams(phon_dict)
    hf, lf = match_w_nw(w_df, nw_df)

    with open(os.path.join(args.output_dir, 'stats.pkl'), 'wb') as f:
        pickle.dump([phon_dict, (w_df, nw_df), (hf, lf)], outfile)
    # shoudl cat all text into one.

    #
    #phrases = text_to_phrases('tmp.txt', language_code='fr-fr')
    # phon_phrases = phonemize_phrases(phrases, language_code='fr-fr', njobs=8)
    #phon_dict = phoneme_statistics(phon_phrases)
    #w_df, nw_df = get_valid_ngrams(phon_dict)
    # hf, lf = match_w_nw(w_df, nw_df)


    #find /gpfsscratch/rech/cfs/commun/dataset/text/EN/LibriVox/ -type f  -exec cat {} + > $SCRATCH/all_EN.txt
