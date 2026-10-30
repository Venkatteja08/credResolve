import pandas as pd
import pytz

calls = pd.read_csv("collections_30k_dataset/calls.csv", nrows=100)
print(calls[['call_id', 'event_at', 'timezone']].head(10))

def parse_to_ist(df, ts_col='event_at', tz_col='timezone'):
    # Vectorized / efficient conversion to Asia/Kolkata
    ts = pd.to_datetime(df[ts_col])
    # Group by timezone
    converted = pd.Series(index=df.index, dtype='datetime64[ns]')
    for tz_name, idx in df.groupby(tz_col).groups.items():
        if pd.isna(tz_name) or tz_name == '' or tz_name == 'None':
            tz_name = 'Asia/Kolkata'
        # Localize to given timezone, then convert to Asia/Kolkata
        # Note: if ts is naive, tz_localize then tz_convert
        s = ts.loc[idx]
        try:
            s_localized = s.dt.tz_localize(tz_name).dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
            converted.loc[idx] = s_localized
        except Exception as e:
            converted.loc[idx] = s
    return converted

calls['event_at_ist'] = parse_to_ist(calls)
calls['hour_raw'] = pd.to_datetime(calls['event_at']).dt.hour
calls['hour_ist'] = calls['event_at_ist'].dt.hour
print(calls[['call_id', 'event_at', 'timezone', 'event_at_ist', 'hour_raw', 'hour_ist']].head(10))
