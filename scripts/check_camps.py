import pandas as pd

camps = pd.read_csv("collections_30k_dataset/campaigns.csv")
print("Target definitions:\n", camps['target_definition'].value_counts())
print("\nCross-tab strategy_version vs target_definition:\n", pd.crosstab(camps['strategy_version'], camps['target_definition']))
print("\nCross-tab strategy_version vs channel:\n", pd.crosstab(camps['strategy_version'], camps['channel']))
print("\nCampaign names by strategy:\n", camps.groupby('strategy_version')['campaign_name'].unique())
