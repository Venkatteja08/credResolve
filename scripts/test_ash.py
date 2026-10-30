import pandas as pd

ash = pd.read_csv("collections_30k_dataset/account_status_history.csv")
ash['event_at_dt'] = pd.to_datetime(ash['event_at'])
ash['recorded_at_dt'] = pd.to_datetime(ash['recorded_at'])
ash['month'] = ash['event_at_dt'].dt.to_period('M')

print("Status history event_at month vs status:")
print(pd.crosstab(ash['month'], ash['status']))

print("\nStatus history source vs status:")
print(pd.crosstab(ash['source'], ash['status']))

# Check if event_at and recorded_at have lag
ash['lag_hours'] = (ash['recorded_at_dt'] - ash['event_at_dt']).dt.total_seconds() / 3600.0
print("\nLag between recorded_at and event_at (hours):\n", ash['lag_hours'].describe())
print("Negative lag (recorded before event_at):", (ash['lag_hours'] < 0).sum())
