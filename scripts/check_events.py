import pandas as pd
import numpy as np

print("=== CHECKING CATEGORICAL VALUES ACROSS TABLES ===")

calls = pd.read_csv("collections_30k_dataset/calls.csv", low_memory=False)
print("\nCalls status:\n", calls['call_status'].value_counts(dropna=False))
print("\nCalls direction:\n", calls['direction'].value_counts(dropna=False))

attempts = pd.read_csv("collections_30k_dataset/call_attempts.csv", low_memory=False)
print("\nAttempt status:\n", attempts['attempt_status'].value_counts(dropna=False))
print("Attempt no min/max/quantiles:\n", attempts['attempt_no'].describe())

ptp = pd.read_csv("collections_30k_dataset/promises_to_pay.csv", low_memory=False)
print("\nPTP status:\n", ptp['status'].value_counts(dropna=False))
print("\nPTP source:\n", ptp['source'].value_counts(dropna=False))

wa = pd.read_csv("collections_30k_dataset/whatsapp_events.csv", low_memory=False)
print("\nWhatsApp event_type:\n", wa['event_type'].value_counts(dropna=False))
print("WhatsApp template_code:\n", wa['template_code'].value_counts(dropna=False))

sms = pd.read_csv("collections_30k_dataset/sms_events.csv", low_memory=False)
print("\nSMS event_type:\n", sms['event_type'].value_counts(dropna=False))
print("SMS template_code:\n", sms['template_code'].value_counts(dropna=False))

fv = pd.read_csv("collections_30k_dataset/field_visits.csv", low_memory=False)
print("\nField visit outcome:\n", fv['outcome'].value_counts(dropna=False))
print("Field visit visit_type:\n", fv['visit_type'].value_counts(dropna=False))

comp = pd.read_csv("collections_30k_dataset/complaints.csv", low_memory=False)
print("\nComplaints type:\n", comp['complaint_type'].value_counts(dropna=False))
print("Complaints severity:\n", comp['severity'].value_counts(dropna=False))
print("Complaints source:\n", comp['source'].value_counts(dropna=False))
