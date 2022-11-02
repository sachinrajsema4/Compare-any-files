import csv
import json
from deepdiff import DeepDiff
import os

#1 Add Input data here in Stage Vs Prod - Mutation & Summary Files:
file1 = '/Users/sachinraj/PycharmProjects/project_diff_file/temp/HC/prod_summary_hc_minus.tsv'
file2 = '/Users/sachinraj/PycharmProjects/project_diff_file/temp/HC/stage_summary_hc_minus.tsv'
output_file_name = "v2_summary_diff_results"
file_pk = "Sample ID"
file_delimiter = "\t"


# array sorting
def json_array_sort(j_array, sort_key):
    return sorted(j_array, key=lambda item: item[sort_key], reverse=True)


# nested objected selector for json objects
def nested_object_selector(array, pk):
    return [o[pk] for o in array]


# simple_list_pattern_counter
def pattern_counter(array):
    patterns_count = []
    for o in unique(array):
        patterns_count.append({o: array.count(o)})
    return patterns_count


# load json to csv
def json_csv_loader(data_input, output_o):
    count = 0
    with open("result/" + output_o, "w") as file:
        csv_writer = csv.writer(file, delimiter=file_delimiter)
        for item_x in data_input:
            if count == 0:
                # Writing headers of CSV file
                header = item_x.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(item_x.values())


# Read CSV to JSON Object convert function
def csv_json_reader(file, sort_key):
    array = []

    with open(file, encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=file_delimiter)
        for lines in csv_reader:
            array.append(lines)
    return json_array_sort(array, sort_key)


# Select unique list
def unique(list1):
    list_set = set(list1)
    return list(list_set)


# Processing Starts  here:
# 0 File reading :
array1 = csv_json_reader(file1, file_pk)
array2 = csv_json_reader(file2, file_pk)

# 1 finding common
common = []

for x in array1:
    if x in array2:
        common.append(x)

for y in array2:
    if y not in common:
        if y in array1:
            common.append(y)

# 2 Identifying mismatches

array1_mismatch = []
array2_mismatch = []

for item in array1:
    if item not in common:
        array1_mismatch.append(item)
    else:
        pass
for item in array2:
    if item not in common:
        array2_mismatch.append(item)
    else:
        pass

# 3 Identifying the missing Sample ID b/w files i.e. Sample ID is the pk here:

pk_column1 = [item[file_pk] for item in array1_mismatch]
pk_column2 = [item[file_pk] for item in array2_mismatch]

array1_miss = []
array2_miss = []

for item in pk_column1:
    if item not in pk_column2:
        array2_miss.append(item)

for item in pk_column2:
    if item not in pk_column1:
        array1_miss.append(item)

final_message = "Comparison Completed" if len(array1_mismatch) == len(array2_miss) and len(
    array2_mismatch) == len(array1_miss) else "Investigation Needed"

output = f"""
{"-" * 100}
Comparison Result:
{"-" * 100} \n
#1 {len(common)} Common records found between {os.path.basename(file1)} & {os.path.basename(file2)}\n. See below:
\t\t\t{json.dumps(common, indent=4)}\n
#2 Missing {file_pk}s:
\ti) {len(array1_miss)} {file_pk} from {os.path.basename(file2)} were not in {os.path.basename(file1)}. See below:
\t\t\t{json.dumps(array1_miss, indent=4)} \n
\tii) {len(array2_miss)} {file_pk} from {os.path.basename(file1)} were not in {os.path.basename(file2)}. See below:
\t\t\t{json.dumps(array2_miss, indent=4)} \n
{"-" * 100}
"""
summary = f"""
Observation: {final_message} 
Summary of Results:
\t1\t{len(common)} Common records found between {os.path.basename(file1)} & {os.path.basename(file2)}
\t2\tMissing {file_pk}s:
\t\ti) {len(array1_miss)} {file_pk} from {os.path.basename(file2)} were not in {os.path.basename(file1)} 
\t\tii) {len(array2_miss)} {file_pk} from {os.path.basename(file1)} were not in {os.path.basename(file2)}
"""

# Logic for further clean up
# remove array1_miss from array2_mismatch
# remove array2_miss from array1_mismatch

array1_investigate = []
array2_investigate = []

for dicts in array1_mismatch:
    for key, value in dicts.items():
        if key == "Sample ID" and value not in array2_miss:
            array1_investigate.append(dicts)

for dicts in array2_mismatch:
    for key, value in dicts.items():
        if key == "Sample ID" and value not in array1_miss:
            array2_investigate.append(dicts)

pk_column1_sel = nested_object_selector(array1_investigate, file_pk)
pk_column2_sel = nested_object_selector(array2_investigate, file_pk)

array1_pattern = pattern_counter(pk_column1_sel)
array2_pattern = pattern_counter(pk_column2_sel)

additional_info = f"""
Additional information:
\t\tTo check patterns for unmatched files : 
\t\t>\tpatterns found for {os.path.basename(file1)}:\n\t\t - {array1_pattern}
\t\t>\tpatterns found for {os.path.basename(file2)}:\n\t\t - {array2_pattern}

\t\t\tPending Manual intervention for : 
\t\t> {len(array1_investigate)} records in {os.path.basename(file1)}  - records posted in file: pending_review_{os.path.basename(file1)}
\t\t> {len(array2_investigate)} records in {os.path.basename(file2)}  - records posted in pending_review_{os.path.basename(file1)}
{"-" * 100}
""" if final_message == "Investigation Needed" else f"{'-' * 100}"

#printing outputs
with open(f"result/{output_file_name}", "wt") as f:
    f.write(summary+additional_info+output)
if final_message == "Investigation Needed":
    json_csv_loader(array1_investigate, "pending_review_" + os.path.basename(file1))
    json_csv_loader(array2_investigate, "pending_review_" + os.path.basename(file2))

# 4 Sort and deepdiff if items remain :
# sort data by primary key
# array1 = json_array_sort(array1, file_pk)
# array2 = json_array_sort(array2, file_pk)

# # # Loading modified file
# json_csv_loader(array1, os.path.basename(file1))
# json_csv_loader(array2, os.path.basename(file2))

# # result
# line_num = 1
#
# print(missing_patterns1)
# print(missing_patterns2)
# for x, y in zip(array1, array2):
#     line_num += 1
#     difference = DeepDiff(x, y)
#     result = json.dumps(json.loads(difference.to_json()), indent=4)
#     print("-" * 100)
#     print("Sample_name :", x[file_pk], ',', "on line :", line_num, "\n", result)
#     print("-" * 100)
