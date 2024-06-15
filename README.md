## installation
```
git clone https://github.com/minionsfarm/bird-submission.git
cd bird-submission
# NOTE: If az is not installed, please install az first.
# sudo is required to create /etc/docker/daemon.json
sudo ./prepare-eval.sh
```

## generation
```
# for dev
./run-eval.sh dev small <INPUT_DIR> <OUTPUT_DIR>
# for test
./run-eval.sh test small <INPUT_DIR> <OUTPUT_DIR>
./run-eval.sh test large <INPUT_DIR> <OUTPUT_DIR>
```
The <INPUT_DIR> should contain dev/ and test/ where dev/ contains dev_databases, dev.json, dev.sql, etc.
Both <INPUT_DIR> and <OUTPUT_DIR> should start with /home/$(whoami)
