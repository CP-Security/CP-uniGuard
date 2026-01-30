## Experiment Guide for CP-uniGuard

This document describes how to run different defense mechanisms and evaluations using `cp_uniguard.py`.

---

### Baseline Evaluations

#### Upperbound (Clean Collaboration with All Agents)

Evaluate performance when all agents are benign and collaborate:

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac upperbound --scene_id 8
```

#### Upperbound with Partial Collaboration

Evaluate with a subset of collaborators (clean environment):

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac upperbound --scene_id 8 --robosac_k 3 --partial_upperbound
```

#### Lowerbound (Ego-only)

Evaluate without any collaboration (ego agent only):

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac lowerbound --scene_id 8
```

#### No Defense (Attacked Baseline)

Evaluate under attack without any defense mechanism:

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac no_defense \
    --scene_id 8 \
    --number_of_attackers 2 \
    --adv_iter 15 \
    --adv_method pgd \
    --eps 0.5
```

---

### CP-uniGuard Defense Mechanisms

#### 1. ROBOSAC (Original Sampling-based Defense)

Random sampling consensus defense with step budget:

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac robosac_mAP \
    --scene_id 8 \
    --number_of_attackers 2 \
    --step_budget 5 \
    --box_matching_thresh 0.3
```

**Key Parameters:**
- `--step_budget`: Maximum sampling attempts per frame
- `--box_matching_thresh`: IoU threshold for consensus verification (default: 0.3)

#### 2. PASAC (Progressive Agent Selection with Adaptive Consensus)

Recursive binary splitting with online adaptive threshold:

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac pasac_mAP \
    --scene_id 8 \
    --number_of_attackers 2 \
    --box_matching_thresh 0.3 \
    --adaptive_alpha 0.2 \
    --adaptive_gamma 0.02 \
    --adaptive_window_size 30 \
    --initial_threshold 0.3
```

**Key Parameters:**
- `--adaptive_alpha`: Smoothing factor for threshold updates (default: 0.2)
- `--adaptive_gamma`: Depth adjustment parameter (default: 0.02)
- `--adaptive_window_size`: Maximum sliding window size (default: 30)
- `--adaptive_min_window_size`: Minimum samples before threshold update (default: 5)
- `--initial_threshold`: Initial consensus threshold (default: 0.3)

#### 3. Linear Agent Selection

Linear testing of each agent with adaptive threshold:

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac linear_mAP \
    --scene_id 8 \
    --number_of_attackers 2 \
    --adaptive_alpha 0.2 \
    --adaptive_gamma 0.02 \
    --initial_threshold 0.3
```

#### 4. Fix Attackers Scenario

Fixed attackers across frames (attackers don't change):

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac fix_attackers \
    --scene_id 8 \
    --number_of_attackers 2 \
    --step_budget 5 \
    --fix_attackers
```

---

### Attacker Configuration

Common parameters for configuring attacks:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--number_of_attackers` | Number of malicious agents | 1 |
| `--adv_method` | Attack type: pgd, bim, cw-l2 | pgd |
| `--adv_iter` | Attack iterations | 15 |
| `--eps` | Perturbation magnitude | 0.5 |
| `--pert_alpha` | Step size for perturbation | 0.1 |
| `--ego_loss_only` | Only use ego loss for attack | False |

---

### Scene and Agent Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--scene_id` | Target scene ID(s) | [8] |
| `--sample_id` | Start from specific frame | None |
| `--ego_agent` | Ego agent ID | 1 |
| `--num_agent` | Total number of agents | 6 |
| `--no_cross_road` | Exclude RSU/crossroad | False |
| `--use_history_frame` | Use previous frame as reference | False |

---

### Performance Evaluation

#### Validation of PASAC/ROBOSAC Algorithm

Evaluate success rate of finding benign collaborators:

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --log --robosac robosac_validation \
    --number_of_attackers 2 \
    --robosac_k 3
```

#### Detection Performance (mAP)

All defense modes above produce mAP metrics. Check logs for:
- Local mAP@0.5 and mAP@0.7 per agent
- Average mAP across all agents
- Success rate of consensus finding
- Average sampling steps per frame

#### FPS and Latency Measurement

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py --robosac performance_eval
```

---

### Logging

Add `--log` to save results. Log files are saved in:

```
coperception/ckpt/<checkpoint_dir>/log_epoch{}_scene{}_ego{}_{}attackers_{MODE}_{TIME}_initial_threshold_{}.txt
```

Example log analysis metrics:
- `Sampling STEP MEAN`: Average steps to find consensus
- `Success Rate`: Percentage of frames with successful consensus
- `mAP@0.5` and `mAP@0.7`: Detection accuracy

---

### Example Workflow

Complete evaluation pipeline for a scenario with 2 attackers:

```bash
cd coperception/tools/det/

# 1. Upperbound (best case)
python cp_uniguard.py --log --robosac upperbound --scene_id 8

# 2. Lowerbound (worst case)
python cp_uniguard.py --log --robosac lowerbound --scene_id 8

# 3. No Defense (baseline under attack)
python cp_uniguard.py --log --robosac no_defense --scene_id 8 --number_of_attackers 2

# 4. ROBOSAC
python cp_uniguard.py --log --robosac robosac_mAP --scene_id 8 --number_of_attackers 2 --step_budget 5

# 5. PASAC (our proposed method)
python cp_uniguard.py --log --robosac pasac_mAP --scene_id 8 --number_of_attackers 2

# 6. Linear Selection
python cp_uniguard.py --log --robosac linear_mAP --scene_id 8 --number_of_attackers 2
```

Compare results across different methods to evaluate defense effectiveness.
