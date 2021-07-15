# protowuggy
protolexicon task for speech representation models

conda env create -f environment.yml

## Phonemising

module load espeak
module load mbrola
module load festival

1. Create a file with phonemised items.
2. Want tokeep the punctuation 
`phonemize -l fr-fr -b espeak tmp_small.txt -o phones.txt --language-switch remove-flags`

