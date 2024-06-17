import json
import argparse

parser = argparse.ArgumentParser(description="Reconstruct all_outputs dictionary from questions file and output queries file.")
parser.add_argument('--questions_filename', type=str, required=True, help="Path to the questions JSON file.")
parser.add_argument('--output_queries_filename', type=str, required=True, help="Path to the output queries text file.")
parser.add_argument('--output_filename', type=str, required=True, help="Path to the output JSON file.")
args = parser.parse_args()

with open(args.questions_filename, 'r') as f:
    questions = json.load(f)

with open(args.output_queries_filename, 'r') as f:
    output_queries = f.readlines()

output_queries = [query.strip() for query in output_queries]

all_outputs = {
    str(question["question_id"]): f"{query}\t----- bird -----\t{question['db_id']}"
    for question, query in zip(questions, output_queries)
}

with open(args.output_filename, 'w') as f:
    json.dump(all_outputs, f, indent=4)

print(f"json format output has been saved to {args.output_filename}")