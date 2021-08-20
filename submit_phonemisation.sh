#!/bin/bash

#SBATCH --job-name=phonemisation
#SBATCH --output=logs/phonemisation-%A-%a.out
#SBATCH --error=logs/phonemisation-%A-%a.err
#SBATCH --nodes=1
#SBATCH --cpus-per-task=10
#SBATCH --time=05:00:00
#SBATCH --array=0-1000%30 #should go to 6000 but max is 1001


shopt -s globstar

root_dir_text=/scratch1/projects/InfTrain/dataset/text

lang="EN"

njobs=10

## HERE TO CHANGE ##
startArray=0 #all starts of job arrays to go up to 6000 as the maxArray Size is 1001.
#startArray=5000
#possible values should be 0 1000 2000 3000 4000 5000

echo "Starting at value $startArray "

mkdir -p logs

root_dir_phonemisation=${root_dir_text}/phonemisation
phonemised_data=

module load espeak
conda activate protowuggy

export PYTHONPATH=$PYTHONPATH:/scratch2/mde/projects/protowuggy/scripts


if [ ! -f text/${lang}_text_list.txt ]; then
    for text in ${root_dir_text}/$lang/**/*.txt; do
        echo $text >> text/${lang}_text_list.txt
    done;
fi

id=$(expr $SLURM_ARRAY_TASK_ID + $startArray)
text=$(sed -n "$id"p text/${lang}_text_list.txt)
echo $SLURM_ARRAY_TASK_ID
echo $text

dirname=${text%.txt}
phon_dir=$root_dir_text/phonemisation/$lang/${dirname#"$root_dir_text/$lang/"}
phon_dir=text/phonemisation/$lang/${dirname#"$root_dir_text/$lang/"}
mkdir -p $phon_dir

if [ -f $text ] && [ ! -f ${phon_dir}/phon_phrases_processed.pkl ]; then
    echo "-------------------"
    echo "Phonemising $text"
    echo "-------------------"
    echo " "
    srun python scripts/preprocessing.py --n_job $njobs --language_code en-us $text $phon_dir --language_code en-us ;
else
    echo "/// $text already phonemised or path not found ///";
fi
