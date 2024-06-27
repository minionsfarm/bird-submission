## machine spec
```
Azure
Standard_NC96ads_A100_v4 (4 A100 80GB)
1T SSD
Ubuntu-based HPC and AI (Ubuntu-HPC 2204 - x64 Gen2) - base image
```

## prep
```
# Step 1: launch an instance with minions.azurecr.io/bird_v2

# Step 2: mount data and get into docker
# Our program expects <WORK_DIR> to contain bird/ which contain dev/ and test/.
# e.g. /home/dokook/something/bird/dev/dev.json then <WORK_DIR> should be /home/dokook/something
docker run --gpus all -v <WORK_DIR>:/home/root -it minions.azurecr.io/bird_v2

# The following should print nothing if data is mounted in the expected path.
# If it complains, remount the data.
./bird-submission/sanity_check.sh

# download models and adapters at /home/root/models and /home/root/adapters
./bird-submission/prepare-eval.sh
```

## generation and eval
```
# eval takes about 1 hour with small and 6 hours with large on dev.
# for dev
./bird-submission/run-inference.sh dev small
# for test
./bird-submission/run-inference.sh test small
./bird-submission/run-inference.sh test large

# all output will be at /home/root/output (inside docker) <BIRD_DATASET_DIR>/output (outside docker)
```

NOTE:
```
None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.
Special tokens have been added in the vocabulary, make sure the associated word embeddings are fine-tuned or trained.
I0615 05:05:27.268593 140542925115392 run.py:154] version: 3.0.0

dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
```
is expected to get printed. Not a problem.

