import pandas as pd

disp = pd.read_csv("collections_30k_dataset/call_dispositions.csv")
calls = pd.read_csv("collections_30k_dataset/calls.csv")

calls_disp = calls.merge(disp, on='call_id', how='inner')
print("Total dispositions linked to calls:", len(calls_disp))
print("Calls status distribution for linked dispositions:")
print(calls_disp['call_status'].value_counts())
print("\nDispositions on NON-ANSWERED calls:")
non_ans = calls_disp[calls_disp['call_status'] != 'ANSWERED']
print(non_ans['disposition_code'].value_counts())

# What about disposition codes across versions?
print("\nDisposition codes by version:")
print(pd.crosstab(disp['disposition_code'], disp['disposition_version']))
