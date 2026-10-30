import pandas as pd

accounts = pd.read_csv("collections_30k_dataset/accounts.csv")
print("Total accounts:", len(accounts))
print("Total principal amount:", accounts['principal_amount'].sum())
print("Total outstanding amount:", accounts['outstanding_amount'].sum())
print("Mean outstanding per account:", accounts['outstanding_amount'].mean())

payments = pd.read_csv("collections_30k_dataset/payments.csv")
payments_succ = payments[payments['payment_status'] == 'SUCCESS'].drop_duplicates('payment_reference')
print("Total net settled recovery (Jan - Aug):", payments_succ['amount'].sum())
print("Total net settled payments count:", len(payments_succ))
print("Mean recovery per payment:", payments_succ['amount'].mean())
