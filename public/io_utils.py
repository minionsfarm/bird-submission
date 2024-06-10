import gzip
import json
import os


def read_file(filename):
    if filename.endswith(".json"):
        with open(filename) as f:
            return json.load(f)
    elif filename.endswith(".json.gz"):
        with gzip.open(filename, "rt") as f:
            return json.load(f)
    elif filename.endswith(".gz"):
        with gzip.open(filename, "rt") as f:
            return f.read().splitlines()
    else:
        with open(filename) as f:
            return f.read().splitlines()


def write_file(filename, data):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    if filename.endswith(".json.gz"):
        with gzip.open(filename, "wt") as g:
            json.dump(data, g, indent=4)
    elif filename.endswith(".gz"):
        with gzip.open(filename, "wt") as g:
            if isinstance(data, dict):
                json.dump(data, g, indent=4)
            else:
                g.write(data)
    elif filename.endswith(".json"):
        with open(filename, "w") as g:
            json.dump(data, g, indent=4)
    else:
        with open(filename, "w") as g:
            g.write(data)
