import pandas as pd
import numpy as np

print("="*60)
print("PART 2A: DUPLICATE PAYMENTS DEEP DIVE")
print("="*60)
p = pd.read_csv("collections_30k_dataset/payments.csv", low_memory=False)
print("Total rows:", len(p))
print("Exact duplicate rows:", p.duplicated().sum())
print("Duplicates by payment_id:", p['payment_id'].duplicated().sum())
print("Duplicates by payment_reference:", p['payment_reference'].duplicated().sum())

# Examine payment reference duplicates
ref_counts = p['payment_reference'].value_counts()
dup_refs = ref_counts[ref_counts > 1].index
print(f"Number of payment_references appearing >1 time: {len(dup_refs)}")

sample_dups = p[p['payment_reference'].isin(dup_refs[:5])].sort_values('payment_reference')
print("\nSample duplicate references:\n", sample_dups[['payment_id', 'account_id', 'event_at', 'payment_reference', 'amount', 'payment_status', 'payment_method', 'provider_id']])

# Are there duplicate references with mixed statuses? E.g. FAILED then SUCCESS, or double SUCCESS?
dup_df = p[p['payment_reference'].isin(dup_refs)]
print("\nStatus distribution within duplicated references:")
print(dup_df.groupby('payment_reference')['payment_status'].nunique().value_counts())
print("\nCross-tab of statuses for duplicated references:")
status_pairs = dup_df.groupby('payment_reference')['payment_status'].unique().apply(lambda x: tuple(sorted(x))).value_counts()
print(status_pairs)

# How much money is double counted if counting all SUCCESS rows with same payment_reference?
succ_dups = dup_df[dup_df['payment_status'] == 'SUCCESS']
succ_dup_refs = succ_dups['payment_reference'].value_counts()
multi_succ = succ_dup_refs[succ_dup_refs > 1]
print(f"\nReferences with MULTIPLE 'SUCCESS' entries: {len(multi_succ)}")
double_counted_amount = succ_dups[succ_dups['payment_reference'].isin(multi_succ.index)]
print("Total rows in multi-SUCCESS:", len(double_counted_amount))
print("Extra amount inflated by duplicate SUCCESS rows:", double_counted_amount.groupby('payment_reference')['amount'].apply(lambda s: s.iloc[1:].sum()).sum())


print("\n" + "="*60)
print("PART 2C: TIMEZONE PROBLEMS")
print("="*60)
# Check timezone strings and offsets across calls, vendor_telephony, agent_sessions, accounts
calls = pd.read_csv("collections_30k_dataset/calls.csv", low_memory=False)
print("Calls timezones:\n", calls['timezone'].value_counts(dropna=False))
v_tel = pd.read_csv("collections_30k_dataset/vendor_telephony.csv")
print("\nVendor telephony timezones:\n", v_tel[['vendor_id', 'vendor_name', 'timezone', 'status']])
sessions = pd.read_csv("collections_30k_dataset/agent_sessions.csv", low_memory=False)
print("\nAgent sessions timezones:\n", sessions['timezone'].value_counts(dropna=False))
accs = pd.read_csv("collections_30k_dataset/accounts.csv", low_memory=False)
print("\nAccounts timezones:\n", accs['timezone'].value_counts(dropna=False))

# Check how calls event_at parses:
print("\nSample call event_at strings:\n", calls['event_at'].head())
# Check call hour distribution by timezone:
calls['hour'] = pd.to_datetime(calls['event_at']).dt.hour
print("\nCall hour distribution by timezone column:")
print(calls.groupby(['timezone', 'hour']).size().unstack(fill_value=0))


print("\n" + "="*60)
print("PART 2D: VENDOR MAPPING & DISPOSITION CHANGES")
print("="*60)
disp = pd.read_csv("collections_30k_dataset/call_dispositions.csv", low_memory=False)
print("Disposition version by month:")
disp['month'] = pd.to_datetime(disp['event_at']).dt.to_period('M')
print(disp.groupby(['month', 'disposition_version']).size().unstack(fill_value=0))
print("\nDisposition codes across versions:")
print(disp.groupby(['disposition_version', 'disposition_code']).size().unstack(fill_value=0))


print("\n" + "="*60)
print("PART 2E: AGENT IDENTITY PROBLEMS")
print("="*60)
ag = pd.read_csv("collections_30k_dataset/agents.csv", low_memory=False)
print("Agents total rows:", len(ag))
print("Unique agent_id:", ag['agent_id'].nunique())
print("Unique employee_code:", ag['employee_code'].nunique())
print("Unique agent_name:", ag['agent_name'].nunique())
# How are agent_id and employee_code mapped?
emp_to_agents = ag.groupby('employee_code')['agent_id'].nunique()
print("Employee codes mapped to >1 agent_id:", (emp_to_agents > 1).sum())
print("Distribution of agent_ids per employee code:\n", emp_to_agents.value_counts())
agent_to_emp = ag.groupby('agent_id')['employee_code'].nunique()
print("Agent_ids mapped to >1 employee code:", (agent_to_emp > 1).sum())
print("Distribution of employee codes per agent_id:\n", agent_to_emp.value_counts())
