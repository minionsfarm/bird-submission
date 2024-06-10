import sqlite3
import string
from collections import defaultdict

import transformers

from public.misc_utils import get_username


def load_tokenizer():
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        "public/data",
        cache_dir=f"/home/{get_username()}/cache",
        model_max_length=8192,
        padding_side="right",
        use_fast=False,
        split_special_tokens=False,
        trust_remote_code=True,
        use_auth_token=None,
    )
    return tokenizer


tokenizer = load_tokenizer()


def get_column_examples(conn, table):
    cur = conn.cursor()

    # Fetch column information including types
    cur.execute(f"PRAGMA table_info(`{table}`)")
    columns_info = cur.fetchall()
    columns_types = {col[1]: col[2] for col in columns_info}

    examples = defaultdict(lambda: defaultdict(int))
    cur.execute(f"SELECT * FROM `{table}` LIMIT 1000")
    columns = [description[0] for description in cur.description]
    rows = cur.fetchall()

    for row in rows:
        for c, data in zip(columns, row):
            if data is not None and type(data) not in {int, float}:
                if len(data) > 100:
                    continue
                if len(data) > 10:
                    # TODO(DK): maybe get rid of tokenizer dependency
                    tokens = tokenizer(data, add_special_tokens=False)
                    if len(data) / len(tokens["input_ids"]) < 2:
                        # print(
                        #     len(data) / len(tokens["input_ids"]),
                        #     len(data),
                        #     len(tokens["input_ids"]),
                        #     data,
                        # )
                        continue
            examples[c][data] += 1
    for c, ex in examples.items():
        if columns_types[c] == "BLOB":
            examples[c] = {}
        else:
            examples[c] = {
                k: v
                for k, v in sorted(ex.items(), key=lambda x: x[1], reverse=True)[:10]
                if k is not None and k != ""
            }

    return examples


def get_tables(conn):
    cur = conn.cursor()

    # Query the sqlite_master table for all table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")

    tables = []
    # Fetch all results
    for table in cur.fetchall():
        if table[0] == "sqlite_sequence":
            continue
        tables.append(table[0])
    return tables


with open("public/data/sqlite_keywords.txt") as f:
    keywords = set(f.read().splitlines())

allowed_chars = set(string.ascii_letters + string.digits + "_")


def is_keyword(name):
    if name.upper() in keywords:
        return True

    if name[0].isdigit():
        return True

    if not all(char in allowed_chars for char in name):
        return True

    return False


def quote_name(name):
    if is_keyword(name) or " " in name:
        return f'"{name}"'
    return name


def is_the_same(x, y):
    def normalize(x):
        return x.lower().replace(" ", "").replace("_", "")

    return normalize(x) == normalize(y)


def get_table_index(db, table):
    t_index = -1
    for i, table_orig in enumerate(db["table_names_original"]):
        if table_orig == table:
            t_index = i
            break
    assert t_index > -1

    return t_index


def get_primary_key(cur, table):
    # Query to get the table schema
    cur.execute(f"PRAGMA table_info({quote_name(table)});")
    columns = cur.fetchall()

    # Process each column
    primary_key = []
    for column in sorted(columns, key=lambda x: x[-1]):
        _, column_name, _, _, _, pk = column
        column_name_quoted = quote_name(column_name)
        if pk:
            primary_key.append(column_name_quoted)
    return primary_key


def get_to_cols(fks):
    to_cols = [fk[-1] for fk in fks if fk[-1] is not None]
    if to_cols:
        assert len(fks) == len(to_cols)
    return to_cols


def get_foreign_keys(cur, table):
    cur.execute(f"PRAGMA foreign_key_list({quote_name(table)});")
    fks = defaultdict(list)

    for fk in cur.fetchall():
        id_, seq, ref_table, from_col, to_col, _, _, _ = fk
        fks[id_].append((seq, ref_table, from_col, to_col))

    foreign_keys = []
    for id_ in fks:
        to_cols = get_to_cols(fks[id_])
        ref_tables = set()
        from_cols = []
        for seq, ref_table, from_col, _ in fks[id_]:
            ref_tables.add(ref_table)
            from_cols.append(from_col)
        assert len(ref_tables) == 1
        foreign_keys.append(
            {
                "ref_table": list(ref_tables)[0],
                "from_cols": [quote_name(c) for c in from_cols],
                "to_cols": [quote_name(c) for c in to_cols],
            }
        )
    return foreign_keys


def get_key_maps(db_path):
    conn = sqlite3.connect(db_path)
    tables = [t for t in get_tables(conn) if t != "sqlite_sequence"]

    cur = conn.cursor()
    table_to_primary_key = {}
    for table in tables:
        table_to_primary_key[table] = get_primary_key(cur, table)

    table_to_foreign_keys = {}
    for table in tables:
        table_to_foreign_keys[table] = get_foreign_keys(cur, table)
        for foreign_keys in table_to_foreign_keys[table]:
            if not foreign_keys["to_cols"]:
                foreign_keys["to_cols"] = table_to_primary_key[
                    foreign_keys["ref_table"]
                ]
    return table_to_primary_key, table_to_foreign_keys


def get_unique_columns(cursor, table):
    # Query to get the table's unique and primary key constraints
    cursor.execute(f"PRAGMA index_list({quote_name(table)});")
    indexes = cursor.fetchall()
    unique_columns = set()
    # Track unique constraints
    for index in indexes:
        index_name = index[1]
        if index[2] == 1:  # Check if the index is unique
            cursor.execute(f"PRAGMA index_info({quote_name(index_name)});")
            for info in cursor.fetchall():
                unique_columns.add(quote_name(info[2]))
    return unique_columns


def get_table_definition_dict(db_path, db, column_examples):
    table_to_primary_key, table_to_foreign_keys = get_key_maps(db_path)

    conn = sqlite3.connect(db_path)
    tables = [t for t in get_tables(conn) if t != "sqlite_sequence"]
    fixed_tables = [x for x in db["table_names"] if x != "sqlite sequence"]
    assert len(tables) == len(fixed_tables)

    schema = {}

    cursor = conn.cursor()
    for table, fixed_table in zip(tables, fixed_tables):
        # Query to get the table schema
        cursor.execute(f"PRAGMA table_info({quote_name(table)});")
        columns = cursor.fetchall()

        t_index = get_table_index(db, table)

        fixed_columns = [x[1] for x in db["column_names"] if x[0] == t_index]
        assert len(columns) == len(fixed_columns)

        table_info = {
            "columns": [],
            "primary_key": table_to_primary_key.get(table, []),
            "foreign_keys": {},
            "fixed_name": None if is_the_same(table, fixed_table) else fixed_table,
        }

        for column, fixed_column in zip(columns, fixed_columns):
            _, column_name, column_type, _, _, pk = column
            examples = []
            if column_name in column_examples[table]:
                for ex in column_examples[table][column_name]:
                    if isinstance(ex, (float, int)):
                        break
                    if len(ex) > 30:
                        continue
                    if len(examples) > 1:
                        break
                    examples.append(ex.replace("\n", ""))

            table_info["columns"].append(
                {
                    "name": column_name,
                    "type": column_type,
                    "fixed_name": (
                        None if is_the_same(column_name, fixed_column) else fixed_column
                    ),
                    "examples": examples,
                }
            )

        for fk in table_to_foreign_keys[table]:
            if fk["ref_table"] not in table_info["foreign_keys"]:
                table_info["foreign_keys"][fk["ref_table"]] = []
            table_info["foreign_keys"][fk["ref_table"]].append(
                {
                    "mine": fk["from_cols"],
                    "foreign": fk["to_cols"],
                }
            )

        unique_columns = get_unique_columns(cursor, table)
        table_info["unique_columns"] = [
            uc for uc in sorted(unique_columns) if uc not in table_info["primary_key"]
        ]

        schema[table] = table_info

    conn.close()
    return schema


def create_in_memory_db(schema_sql):
    """Create an in-memory SQLite database and execute the provided schema SQL."""
    conn = sqlite3.connect(":memory:")  # Create an in-memory database
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    return conn
