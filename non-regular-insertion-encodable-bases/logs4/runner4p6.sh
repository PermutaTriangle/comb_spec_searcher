#!/usr/bin/bash
#SBATCH --job-name=NRIE4p6

module load python/3.6.1

source ~/permenv/bin/activate

export PYTHONPATH='/users/home/henningu/lib/python3.6/site-packages/'

pwd

python3 run_batchp6.py
