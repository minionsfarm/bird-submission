## machine spec
```
Azure
Standard_NC96ads_A100_v4 (4 A100 80GB)
1T SSD
Ubuntu-based HPC and AI (Ubuntu-HPC 2204 - x64 Gen2) - base image
```

## installation
```
git clone https://github.com/minionsfarm/bird-submission.git
cd bird-submission
# NOTE: you need at least 200GB of free disk
./prepare-eval.sh
# models and adapters will be at /home/$(whoami)/models and /home/$(whoami)/adapters

# Download a docker (three steps)
sudo usermod -aG docker $USER # step 1
# Step 2. exit the terminal and open a new one
docker pull minions.azurecr.io/bird # step 3

# sudo is required to create /etc/docker/daemon.json
sudo ./create-daemon.sh

# Download evaluation data: bird/dev and bird/test
```

## generation
```
# eval takes about 1 hour with small and 6 hours with large.
# for dev
./run-eval.sh dev small <INPUT_DIR> <OUTPUT_DIR>
# for test
./run-eval.sh test small <INPUT_DIR> <OUTPUT_DIR>
./run-eval.sh test large <INPUT_DIR> <OUTPUT_DIR>

# e.g.
./run-eval.sh dev small /home/azureuser/datasets/bird /home/azureuser/output

NOTE: If you encounter `docker: Error response from daemon: unknown or invalid runtime name: nvidia.`
run `sudo systemctl restart docker`
```
The <INPUT_DIR> should contain dev/ and test/ where dev/ contains dev_databases, dev.json, dev.sql, etc.
Both <INPUT_DIR> and <OUTPUT_DIR> should start with /home/$(whoami)

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
