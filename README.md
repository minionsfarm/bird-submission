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
./prepare-eval.sh
# models and adapters will be at /home/$(whoami)/models and /home/$(whoami)/adapters

# Download a docker
# In case of a docker permission problem, run `sudo usermod -aG docker $USER`
# and exit the terminal and open a new one.
docker pull minions.azurecr.io/bird

# sudo is required to create /etc/docker/daemon.json
sudo ./create-deamon.sh
```

## generation
```
# for dev (about 1 hour)
./run-eval.sh dev small <INPUT_DIR> <OUTPUT_DIR>
# for test (about 6 hours)
./run-eval.sh test small <INPUT_DIR> <OUTPUT_DIR>
./run-eval.sh test large <INPUT_DIR> <OUTPUT_DIR>

# e.g.
./run-eval.sh dev small /home/azureuser/datasets/bird /home/azureuser/output
```
The <INPUT_DIR> should contain dev/ and test/ where dev/ contains dev_databases, dev.json, dev.sql, etc.
Both <INPUT_DIR> and <OUTPUT_DIR> should start with /home/$(whoami)

NOTE:
```
dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
dateutil/zoneinfo/__init__.py:26: UserWarning: I/O error(2): No such file or directory
```
is expected to get printed. Not a problem.
