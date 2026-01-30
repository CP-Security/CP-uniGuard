#!/bin/bash
export CUDA_VISIBLE_DEVICES=2

Number_of_Attackers=1


nohup python cp_uniguard.py --log \
    --robosac linear_mAP  \
    --adv_iter 15 \
    --number_of_attackers $Number_of_Attackers \
    --adv_method pgd \
    --initial_threshold 0.5 \
     > linear_run_$(date +%m%d_%H%M%S).log 2>&1 &
