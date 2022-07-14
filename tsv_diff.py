
"""
diff tsv files
"""
import csv
import json
import os
from deepdiff import DeepDiff

# paths to files
file1 = '/Users/sachinraj/PycharmProjects/pythonProject7/temp/hcmutation.tsv'
file2 = '/Users/sachinraj/PycharmProjects/pythonProject7/temp/hcmutation2.tsv'


#File Loading
file_array1 = []
file_array2 = []
with open(file1) as csv_file:
    csv_reader1 = csv.DictReader(csv_file, delimiter="\t")
    for row in csv_reader1:
        file_array1.append(row)
with open(file2) as csv_file:
    csv_reader2 = csv.DictReader(csv_file, delimiter="\t")
    for row in csv_reader2:
        file_array2.append(row)


#Sorting records
sort_fields = ["Sample ID","Gene Name"] # add all field you link to sort
for field in sort_fields:
    filearray1 = sorted(file_array1,
                        key=lambda item: item[field], reverse=True)
    filearray2 = sorted(file_array2,
                          key=lambda item: [field], reverse=True)


# DeepDiff
difference = DeepDiff(file_array1, file_array2)

result = json.dumps(json.loads(difference.to_json()), indent=4)

print(result)
