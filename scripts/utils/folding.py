#!/usr/bin/env python3


def folding_phones(phon_phrase, phrase, folding_dict, language_code) :

    p = ' '.join([folding_dict[x].replace(":", " ") if x in folding_dict.keys() else x for x in phon_phrase.split(" ")])

    #below specific rules. Do same in French if necessary
    p = extrarules(phrase, p, language_code = language_code)
            
    return p


def extrarules(phrase, phon_phrase, language_code = "en-us"):
    #only english implemented yet.
    
    if language_code == "en-us" :
        p = phon_phrase.replace("Ə", "ə")
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
#------------------------------------------------------------------------

#careful, here the ":" in the key is a phoneme separator. 
en_folding_dict =    {
            "k":"k", "ɛ":"ɛ", "p":"p", "t":"t", "s":"s", "ɪ":"ɪ", "ŋ":"ŋ", "ɡ":"ɡ",
            "j":"j", "ʊ":"ʊ", "l":"l", "ə":"ə", "ɚ":"ə:ɹ","iː":"iː", "I":"iː", "ɔː":"ɔː","oː":"ɔː", "d":"d",
            "ɹ":"ɹ", "n":"n", "z":"z", "aɪ":"aɪ", "m":"m", "ɹ":"ɹ","ɔ":"ɑ", "ɑ":"ɑ", "æ":"æ",
            "oʊ":"oʊ", "ʌ":"ʌ","ɐ": "ʌ", "v":"v", "ɾ":"ɾ", "w":"w", "eɪ":"eɪ", "iə":"iə", "dʒ":"dʒ",
            "f":"f", "əl":"ə:l", "aʊ":"aʊ", "ɑːɹ":"ɑː:ɹ", "ɑː":"ɑː", "θ":"θ", "b":"b", "ɛɹ":"ɛ:ɹ",
            "uː":"uː", "h":"h", "tʃ":"tʃ", "ɜː":"ɜː", "ʃ":"ʃ" , "aɪə":"aɪ:ə", "ɔːɹ":"ɔː:ɹ",
            "ɔɪ":"ɔɪ", "aɪɚ":"aɪ:ə:ɹ", "ʒ":"ʒ", "ð":"ð", "ɪɹ":"ɪ:ɹ", "ʊɹ": "ʊ:ɹ", "x":"x", "ɑ̃":"ɛ", 
            "ɛ̃":"ɪ:n", "ʔ":"ʔ",  "n̩":"ə:n","oːɹ":"ɔː:ɹ","ᵻ" : "iː", "i":"ɪ", "ɬ": "l", "ç": "tʃ", "r":""
    }
