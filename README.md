## installation
```
git clone https://github.com/minionsfarm/bird-submission.git
cd bird-submission
poetry install
```

## generation
```
# for dev
PYTHONPATH=$(pwd) poetry run python public/run.py --split dev --input_dir <INPUT_DIR> --dataset bird_dev --url=<URL>
# for test
PYTHONPATH=$(pwd) poetry run python public/run.py --split test --input_dir <INPUT_DIR> --dataset bird_test --url=<URL>
```
The <INPUT_DIR> should contain dev/ and test/ where dev/ contains dev_databases, dev.json, dev.sql, etc.
