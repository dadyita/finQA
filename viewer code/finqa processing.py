import json

file_path = "../output/embedding_finQA_data.json"
data = json.load(open(file_path, 'r', encoding='utf8'))

filenames_dict = {}
output_data = {}
doc_id = 0
for example in data:
    filename = example['filename']

    filenames_dict[filename] = doc_id

    output_data[doc_id] = {}
    output_data[doc_id]["filename"] = filename
    output_data[doc_id]["question"] = [example['qa']["question"]]
    output_data[doc_id]["answer"] = [example['qa']["answer"]]
    output_data[doc_id]["formula_table"] = example["formula_table"]
    output_data[doc_id]["formula_text"] = example["formula_text"]
    output_data[doc_id]["formula_table_text"] = example["formula_table_text"]
    output_data[doc_id]["pre_text"] = example['pre_text']
    output_data[doc_id]["post_text"] = example['post_text']
    output_data[doc_id]["table"] = example['table']

    doc_id += 1

json.dump(output_data, open("../output/embedding_finQA_viewer.json", 'w', encoding='utf8'), indent=4)
