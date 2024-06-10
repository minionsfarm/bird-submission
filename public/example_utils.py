from collections import defaultdict


def get_examples_from_table(conn, table):
    cur = conn.cursor()

    # Fetch column information including types
    cur.execute(f"PRAGMA table_info(`{table}`)")
    columns_info = cur.fetchall()

    examples = defaultdict(set)
    for col in columns_info:
        if "char(" in col[2].lower() or col[2] == "TEXT":
            rows = cur.execute(f"SELECT `{col[1]}` FROM `{table}`")
            for row in rows:
                for c in row:
                    if c in {"", None}:
                        continue
                    if len(c) > 50:
                        continue
                    examples[col[1]].add(c)
    for c in examples:
        examples[c] = sorted(examples[c])
    return examples
