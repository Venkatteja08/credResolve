import pandas as pd

disp = pd.read_csv("collections_30k_dataset/call_dispositions.csv")
v_tel = pd.read_csv("collections_30k_dataset/vendor_telephony.csv")
calls = pd.read_csv("collections_30k_dataset/calls.csv")

print("Dispositions shape:", disp.shape)
print("Unique calls in dispositions:", disp['call_id'].nunique())

calls_disp = calls.merge(disp, on='call_id', how='left')
print("\nCalls call_status vs call_disposition code:")
print(pd.crosstab(calls_disp['call_status'], calls_disp['disposition_code'].fillna('NO_DISP')))

# Check if different vendors use different versions or disposition codes
calls_disp_vnd = calls_disp.merge(v_tel, left_on='vendor_id_x', right_on='vendor_id', how='left')
print("\nVendor Name vs Disposition Version:")
print(pd.crosstab(calls_disp_vnd['vendor_name'], calls_disp_vnd['disposition_version'].fillna('NONE')))

print("\nVendor Name vs Schema Version:")
print(pd.crosstab(calls_disp_vnd['vendor_name'], calls_disp_vnd['schema_version'].fillna('NONE')))
