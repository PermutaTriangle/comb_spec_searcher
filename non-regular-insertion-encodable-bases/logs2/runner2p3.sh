#!/usr/bin/bash
#SBATCH --job-name=NRIE2p3

module load python/3.6.1

source ~/permenv/bin/activate

export PYTHONPATH='/users/home/henningu/lib/python3.6/site-packages/'

pwd

python3 run_batchp3.py
