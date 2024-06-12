import logging
import os
import sqlite3
import time
from collections import defaultdict
from datetime import datetime
from datetime import timezone
from zoneinfo import ZoneInfo

import requests
from absl import app
from absl import flags

from public import db_utils
from public import example_utils
from public import io_utils

logging.basicConfig(level=logging.INFO)

FLAGS = flags.FLAGS

flags.DEFINE_string("split", None, "dev or test")
flags.DEFINE_string("dataset", None, "bird_dev or bird_test")
flags.DEFINE_string("input_dir", None, "The input_dir that contains dev/ and test/")
flags.DEFINE_string("url", "http://localhost:8080", "The endpoint")
flags.DEFINE_boolean("do_setup", True, "")

VERSION = "2.0.0"

# for submission
_SPLITS = ["dev", "test"]
_DATASETS = [
    "bird_dev",
    "bird_test",
    "bird_dev_level1",
    "bird_dev_level2",
    "bird_dev_level3",
    "bird_dev_tiny",
]
# # for development
# _DATASETS = [
#     "bird_dev",
#     "bird_dev_level1",
#     "bird_dev_level2",
#     "bird_dev_level3",
#     "bird_dev_tiny",
# ]
# _SPLITS = ["dev"]


def get_db_path(db_dir, split, db_id):
    filepath = os.path.join(db_dir, split, f"{split}_databases/{db_id}/{db_id}.sqlite")
    assert os.path.exists(filepath), f"{filepath} doesn't exist"
    return filepath


def get_db(db_dir, split, db_id):
    filepath = get_db_path(db_dir, split, db_id)
    conn = sqlite3.connect(filepath)
    conn.text_factory = lambda x: x.decode("utf-8", "ignore")
    return conn


def load_db_id_to_db(db_dir, split):
    dbs = io_utils.read_file(os.path.join(db_dir, split, f"{split}_tables.json"))
    return {db["db_id"]: db for db in dbs}


def get_db_id_to_names(input_dir, split):
    db_id_to_db = {}
    for table in load_db_id_to_db(input_dir, split).values():
        table_names = table["table_names_original"]
        column_names = defaultdict(list)
        for table_index, column_name in table["column_names_original"]:
            if table_index == -1:
                continue
            if table_names[table_index] == "sqlite_sequence":
                continue
            column_names[table_index].append(column_name)
        db_id_to_db[table["db_id"]] = []

        for key, val in column_names.items():
            db_id_to_db[table["db_id"]].append(
                {"table": table_names[key], "columns": val}
            )
    return db_id_to_db


def prepare_schemas(input_dir, output_dir, split):
    schemas_filename = os.path.join(output_dir, split, "schemas_dict.json")
    # Create schemas_dict.json
    if not os.path.exists(schemas_filename):
        db_id_to_db = load_db_id_to_db(input_dir, split)
        examples = defaultdict(dict)
        for db_id in db_id_to_db:
            conn = get_db(input_dir, split, db_id)
            for table in db_utils.get_tables(conn):
                examples[db_id][table] = db_utils.get_column_examples(conn, table)

        schemas = []
        for db_id, db in db_id_to_db.items():
            db_path = get_db_path(input_dir, split, db_id)
            schemas.append(
                {
                    "schema": db_utils.get_table_definition_dict(
                        db_path, db, examples[db_id]
                    ),
                    "db_id": db_id,
                }
            )
        io_utils.write_file(schemas_filename, schemas)


def prepare_examples(input_dir, output_dir, split):
    exmaples_filename = os.path.join(output_dir, split, "examples.json.gz")
    # Dump examples.json.gz
    if not os.path.exists(exmaples_filename):
        db_id_to_db = load_db_id_to_db(input_dir, split)
        examples = {}
        for db_id in db_id_to_db:
            examples[db_id] = {}
            conn = get_db(input_dir, split, db_id)
            tables = db_utils.get_tables(conn)
            for table in tables:
                examples[db_id][table] = example_utils.get_examples_from_table(
                    conn, table
                )
        io_utils.write_file(exmaples_filename, examples)


def execute_query(query, input_dir, split, db_id):
    connection = get_db(input_dir, split, db_id)
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        return cursor.fetchmany(2)
    except Exception as e:
        return f"MinionsSQLGenerationError: {str(e)}"
    finally:
        connection.close()


def main(argv):
    del argv

    assert FLAGS.split in {
        "dev",
        "test",
    }, "--split dev or --split test should be provided"
    assert (
        FLAGS.dataset in _DATASETS
    ), "--dataset bird_dev or --dataset bird_test should be provided"
    assert FLAGS.input_dir, "--input_dir <input_dir> that contains dev/ and test/"
    logging.info(f"version: {VERSION}")

    input_dir = FLAGS.input_dir
    output_dir = "outputs"
    for split in _SPLITS:
        split_dir = os.path.join(input_dir, split)
        assert os.path.exists(split_dir), f"{split_dir} doesn't exist"
        prepare_schemas(input_dir, output_dir, split)
        prepare_examples(input_dir, output_dir, split)

    split = FLAGS.split
    schemas_filename = os.path.join(output_dir, split, "schemas_dict.json")
    schemas = io_utils.read_file(schemas_filename)
    logging.info(f"schemas {len(schemas)}, {schemas_filename}")

    exmaples_filename = os.path.join(output_dir, split, "examples.json.gz")
    examples = io_utils.read_file(exmaples_filename)

    questions_filename = os.path.join(input_dir, split, f"{split}.json")
    questions = io_utils.read_file(questions_filename)
    logging.info(f"questions {len(questions)}")

    tables_filename = os.path.join(input_dir, split, f"{split}_tables.json")
    tables = io_utils.read_file(tables_filename)
    logging.info(f"tables {len(tables)}")

    # initial setup
    if FLAGS.do_setup or split == "test":
        r = requests.post(
            f"{FLAGS.url}/api/initial-setup",
            headers={"Content-Type": "application/json"},
            json={
                "schemas_dict": schemas,
                "examples": examples,
                "split": split,
                "questions": questions,
                "tables": tables,
                "version": VERSION,
            },
        )
        if r.status_code != 200:
            raise Exception("initial setup went wrong", r.status_code)

    # start pinging the server
    dataset = FLAGS.dataset
    logging.info(f"dataset: {dataset}")

    query_data = []
    for nth_try in range(4):
        logging.info(f"nth_try: {nth_try}")
        request_id = (
            datetime.now(timezone.utc)
            .astimezone(ZoneInfo("America/Los_Angeles"))
            .strftime("%m%d_%H%M%S")
        )
        request_args = {
            "request_id": request_id,
            "split": split,
            "dataset": dataset,
            "nth_try": nth_try,
            "query_data": query_data,
            "version": VERSION,
        }
        r = requests.post(
            f"{FLAGS.url}/api/request-generation",
            headers={"Content-Type": "application/json"},
            json=request_args,
        )
        r_json = r.json()
        r_json_to_print = r_json.copy()
        r_json_to_print["query_data"] = None
        logging.info(f"request-generation: {r_json_to_print}")
        if r.status_code != 200:
            raise Exception("request-generation went wrong", r.status_code)

        while True:
            r = requests.post(
                f"{FLAGS.url}/api/retrieve-generation",
                headers={"Content-Type": "application/json"},
                json=request_args,
            )
            r_json = r.json()
            r_json_to_print = r_json.copy()
            r_json_to_print["query_data"] = None
            logging.info(f"retrieve-generation: {r_json_to_print}")
            if r.status_code != 200:
                raise Exception("retrieve-generation went wrong", r.status_code)
            response = r.json()
            if response["status"] == "completed":
                break

            # TODO: change the sleep time
            time.sleep(60)

        # update query_data
        query_data = response.get("query_data", [])
        for q in query_data:
            outputs = []
            for query in q["query"]:
                output = execute_query(
                    query,
                    input_dir,
                    split,
                    q["db_id"],
                )
                outputs.append(output)
            q["output"] = outputs


    # Store the final results
    io_utils.write_file(
        f"outputs/{split}/output.sql",
        "\n".join([q["query"][0] for q in query_data]),
    )
    logging.info(f"SQL generation is Done. Find the sql file here: outputs/{split}/output.sql")


if __name__ == "__main__":
    app.run(main)
