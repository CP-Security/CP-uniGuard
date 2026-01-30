## Installation

### Requirements

* Linux (tested on Ubuntu 20.04)
* Python 3.8+
* Anaconda or Miniconda
* PyTorch >= 1.12
* CUDA 11.7 or higher

### Create Anaconda Environment

In the directory of `CP-uniGuard`:

```bash
cd coperception
conda env create -f environment.yml
conda activate coperception
```

Or create environment manually:

```bash
conda create -n coperception python=3.8
conda activate coperception
```

### Install PyTorch with CUDA

```bash
conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia
```

### Install CoPerception Library

This installs and links `coperception` library to code in `./coperception` directory.

```bash
cd coperception
pip install -e .
```

### Dataset Preparation

Please download and unzip the [parsed detection dataset](https://drive.google.com/file/d/1ZM_JkugZHmTwkR1gwG8ZuFq0YBwPDcDV/view?usp=drive_link) of V2X-Sim 2.0.

The dataset should be organized as:

```
V2X-Sim-det/
├── train/
├── val/
└── test/
    ├── agent0/
    ├── agent1/
    ├── agent2/
    ├── agent3/
    ├── agent4/
    └── agent5/
        └── 19_0/
            ├── 0.npy
            └── ...
```

### Specifying Dataset Path

Update the dataset path in your commands using the `-d` or `--data` argument:

```bash
python cp_uniguard.py -d /path/to/V2X-Sim-det/test [other options]
```

Or modify the default value in `cp_uniguard.py`:

```python
parser.add_argument(
    "-d",
    "--data",
    default="/path/to/V2X-Sim-det/test",  # <-- Change this
    type=str,
    help="The path to the preprocessed sparse BEV training data",
)
```

### Specifying Model Checkpoint

Download the pre-trained model checkpoint and specify its path using the `--resume` argument:

```bash
python cp_uniguard.py --resume /path/to/checkpoint/epoch_49.pth [other options]
```

Default checkpoint location is configured in `cp_uniguard.py`:

```python
parser.add_argument(
    "--resume",
    default="../../ckpt/meanfusion/epoch_49.pth",
    type=str,
    help="The path to the saved model that is loaded to resume training",
)
```

**Available Checkpoints:**

| Checkpoint | Description |
|------------|-------------|
| `epoch_49.pth` | Victim model trained on clean data |
| `epoch_advtrain_49.pth` | Model with adversarial training (PGD) |

### Verify Installation

Run a quick test to verify the installation:

```bash
cd coperception/tools/det/
python cp_uniguard.py --robosac upperbound --scene_id 8
```

If the script runs without errors and produces detection results, the installation is successful.

---

## Troubleshooting

### GPU Out of Memory

Reduce batch size or use a GPU with more memory. CP-uniGuard is designed to run with `batch_size=1`.

### Multi-GPU Issues

Due to data synchronization issues, defense algorithms should run on a single GPU:

```bash
CUDA_VISIBLE_DEVICES=0 python cp_uniguard.py [options]
```

### Missing Dependencies

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install scipy shapely seaborn tqdm numpy torch torchvision
```
