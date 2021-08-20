#!/usr/bin/env

# Allocated resources are NOT SHARED across the jobs. They represent
# resources allocated for each job in the array.
#SBATCH --output=res%A_%a
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40

conda activate protowuggy
bash scripts/convert_text.py "all_EN.txt" "all_EN" --n_job 40 --language_code 'en-us'
