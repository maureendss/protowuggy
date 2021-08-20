#!/usr/bin/env python3

from phonemizer import phonemize
from phonemizer import separator
from utils import folding
import nltk
import pandas as pd
from tqdm import tqdm
import num2words
import ipapy
from collections import defaultdict
import pickle
import os, re, time, warnings, sys


def convert_num_to_words(utterance, language_code = 'en'):
      utterance = ' '.join([num2words.num2words(i, lang=language_code) if i.isdigit() else i for i in utterance.split()])
      return utterance

    #normalise digits, 

def checkString(string):
    if string:
        return any(c.isalpha() for c in string)
    else:
        return False

#--------- Based on code by XN and Gwendal ----------------------
def extrarules(phrase, phon_phrase, language_code = "en-us"):
    #only english implemented yet.
    
    if language_code == "en-us" :

        #-------------------------------------------------------------
        #règle nasale 
        if "ɔ̃" in phon_phrase and len(phrase.split(" ")) == len(phon_phrase.split(" ")) :
            for pw, w in zip(phon_phrase.split(" "), phrase.split(" ")):
                if "ɔ̃" in pw :
                    p = pw.replace("ɔ̃", "ɑː n" if match(r".*n$", word) else "ə n t")
                else:
                    p = pw.replace("ɔ̃", "ɑː n")
                    warnings.warn("Replaced {} by {}, could be an error".format(pw, p))
        #-------------------------------------------------------------

        #soupcon to soupson
        if 's uː p k ə n /w ' in phon_phrase :
            p = phon_phrase.replace('s uː p k ə n /w', 's uː p s ə n')
            
                                                    
        p = phon_phrase
    else:
        p = phon_phrase
    return p
#----------------------------------------------------------------


def text_to_phrases(text, language_code='en-us'):
    # Turn text into phrases based on punctuation and lines.
    # TODO : MDS - take care of unicode. 
    punc_separators = "[;:,.!?¡¿—…\"«»“”]|(\s')"
    phrases = []
    with open(text, 'r', encoding="utf-8") as infile:
        raw_lines = infile.read().split('\n\n')

    lines = []
    for l in raw_lines : 
        x = l.replace('\n', ' ')
        lines.extend(nltk.tokenize.sent_tokenize(x))
    for l in lines :
        phrases.extend([convert_num_to_words(p, language_code = language_code) for p in re.split(punc_separators, l.strip()) if checkString(p)]) #check not empty
    return phrases



def phonemize_phrases(phrases,  language_code='en-us', njobs=4, language_switch="keep-flags", preserve_punctuation=True):

    # phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = 'remove-flags', njobs=njobs)
    sep = separator.Separator(phone=' ', syllable='', word='/w ')

    phon = phonemize(phrases,language=language_code, backend='espeak', language_switch = language_switch, separator = sep,  njobs=njobs , preserve_punctuation=preserve_punctuation) # here with word separator and space between phone

    if len(phrases) != len(phon):
        print(len(phrases), len(phon))
        print(phrases)
        print(phon)
        raise ValueError("Length of input phrases and output phonemised phrases differ")
    return phon

def phonemisation_process(text, language_code="en-us", njobs=10, language_switch = "keep-flags", preserve_punctuation=True):

    lines = text_to_phrases(text, language_code=language_code)

    sys.setrecursionlimit(5000)
    
    # 2 . Phonemisation
    print("Phonemizing {} phrases".format(len(lines)))
    start_time = time.time()
    print(len(lines))
    phon_phrases = phonemize_phrases(lines, language_code=language_code, njobs=njobs, language_switch=language_switch, preserve_punctuation=preserve_punctuation)
    print("--- Phonemisation took %s seconds ---" % (round((time.time() - start_time), 3)))

    df = pd.DataFrame(list(zip(lines,phon_phrases)), columns = ["phrase", "phonemised_phrase_no_folding"])

    return df



def postprocessing(df, folding_dict, language_code="en-us") :



    #1 Folding
    print('Folding phones')
    df['phonemised_phrase'] = df.apply(lambda r : folding.folding_phones(r['phonemised_phrase_no_folding'], r["phrase"], folding_dict, language_code), axis=1)

    #2. Any language flag?
    print('Any language flag?')
    df['foreign_flag'] = df.apply(lambda r : True if  re.search('\(\w*\)', r['phonemised_phrase']) else False, axis=1)
    df['phonemised_phrase'] = df.apply(lambda r : re.sub('\(\w*\)\s', ' ', r['phonemised_phrase']), axis=1)

    #3. Any phones not in phone set?
    print('Any unauthorised token?')
    authorised_tokens = [r for r in folding_dict.values()]+["/w"]
    df['external_phones'] = df.apply(lambda r : [x for x in r['phonemised_phrase'].split() if  x not in authorised_tokens], axis=1)
    
    return df




if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text_file", help="path to the input text file")
    parser.add_argument('output_dir')
    parser.add_argument("--n_job",type=int, help="number of jobs for phonemizer", default=50)
    parser.add_argument("--language_code", default='en-us')
    
    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    print("Phonemising {}".format(args.text_file))
    if "en" in args.language_code :
    
        folding_dict=folding.en_folding_dict
    else:
        raise ValueError("No folding dictionary existing yet for language code {}".format(args.language_code))


        
    print("creating output dir in {}".format(args.output_dir))
    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    outfile = os.path.join(args.output_dir, 'phon_phrases.pkl')
    print(outfile)
    if not os.path.isfile(outfile):
        print("....Loading text and phonemising phrases")
        df = phonemisation_process(args.text_file, language_code=args.language_code, njobs=args.n_job)
        with open(outfile, 'wb') as out:
            pickle.dump(df, out)
    else:
        with open(outfile, 'rb') as f:
            df = pickle.load(f)

    outfile = os.path.join(args.output_dir, 'phon_phrases_processed.pkl')
    if not os.path.isfile(outfile):
        print("...postprocessing phon_phrases")
        phon_phrases = postprocessing(df, folding_dict, language_code=args.language_code)
        print('...done with postprocessing')

        with open(outfile, 'wb') as out:
            pickle.dump(df, out)
    else:
        with open(outfile, 'rb') as f:
            df = pickle.load(f)

    print("-----------DONE------------")
