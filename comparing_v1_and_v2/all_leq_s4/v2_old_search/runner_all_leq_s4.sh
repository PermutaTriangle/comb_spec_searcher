#!/usr/bin/bash
#SBATCH --job-name=MIMICK_OLD_all_leq_s4

module load python/3.6.1

source ~/permenv/bin/activate

export PYTHONPATH='/users/home/henningu/lib/python3.6/site-packages/'

pwd

python3 run_batch.py
