import pandas as pd
import numpy as np
import re

df = pd.read_pickle('clean_final.pkl')

# ---------------------------------------------------------------
# 1. Drop the address entirely; replace with a synthetic deal ID.
#    Keep only state (already a separate column) for geography.
# ---------------------------------------------------------------
df = df.sort_values('purchase_date').reset_index(drop=True)
df.insert(0, 'deal_id', ['DEAL-' + str(i+1).zfill(3) for i in range(len(df))])
df = df.drop(columns=['address'])

# ---------------------------------------------------------------
# 2. Pseudonymize broker (highest deal count = Broker_01)
# ---------------------------------------------------------------
broker_order = df['broker'].value_counts(dropna=True).index.tolist()
broker_map = {name: f"Broker_{str(i+1).zfill(2)}" for i, name in enumerate(broker_order)}
df['broker'] = df['broker'].map(broker_map).fillna('Broker_Unknown')

# ---------------------------------------------------------------
# 3. Pseudonymize partnership (internal fund entities/individuals - most sensitive field)
# ---------------------------------------------------------------
partnership_order = df['partnership'].value_counts(dropna=True).index.tolist()
partnership_map = {name: f"Partner_{str(i+1).zfill(2)}" for i, name in enumerate(partnership_order)}
df['partnership'] = df['partnership'].map(partnership_map).fillna('Partner_Unknown')

# ---------------------------------------------------------------
# 4. Normalize seller_channel to a small set of real, non-identifying categories.
#    Many entries are messy data-entry (a person's or bank's name typed in
#    instead of the channel type) - bucket those into the closest real category
#    or OTHER, rather than pseudonymizing dozens of one-off values.
# ---------------------------------------------------------------
channel_map = {
    'AUCTION': 'AUCTION', 'TRUSTEE': 'TRUSTEE SALE', 'SHORTSALE': 'SHORT SALE',
    'HOMESEARCH': 'ONLINE MARKETPLACE', 'HUBZU': 'ONLINE MARKETPLACE',
    'BANK REO': 'BANK REO', 'ESTATE SALE': 'ESTATE SALE', 'EBAY': 'ONLINE MARKETPLACE',
    'REALTYBID': 'ONLINE MARKETPLACE', 'GSA': 'GOVERNMENT SALE', 'BROKER': 'BROKER REFERRAL',
    'NONE': 'OTHER/PRIVATE',
}
def norm_channel(v):
    if pd.isna(v):
        return np.nan
    v = str(v).strip().upper()
    if v in channel_map:
        return channel_map[v]
    return 'OTHER/PRIVATE'  # covers bank names, individual names, and rare entries
df['seller_channel'] = df['seller_channel'].apply(norm_channel)

# ---------------------------------------------------------------
# 5. Pseudonymize sourcing_vendor / closing_vendor consistently (shared mapping,
#    since the same vendor can appear in both columns)
# ---------------------------------------------------------------
vendor_values = pd.concat([df['sourcing_vendor'], df['closing_vendor']]).dropna()
vendor_order = vendor_values.value_counts().index.tolist()
vendor_map = {name: f"Vendor_{str(i+1).zfill(2)}" for i, name in enumerate(vendor_order)}
df['sourcing_vendor'] = df['sourcing_vendor'].map(vendor_map).fillna('Vendor_Unknown')
df['closing_vendor'] = df['closing_vendor'].map(vendor_map).fillna('Vendor_Unknown')

# ---------------------------------------------------------------
# 6. Drop free-text notes columns entirely - unstructured text is the highest-risk
#    field for leaking names/identifying deal specifics and isn't used quantitatively.
# ---------------------------------------------------------------
df = df.drop(columns=['notes', 'note_2'])

# ---------------------------------------------------------------
# 7. Reorder
# ---------------------------------------------------------------
front = ['deal_id','state','product_type','seller_channel','partnership','sourcing_vendor','closing_vendor','broker',
         'deal_status','purchase_date','sold_date','purchase_year','holding_period_months','days_on_market']
rest = [c for c in df.columns if c not in front]
df = df[front + rest]

print(df.shape)
print(df[['deal_id','broker','partnership','sourcing_vendor','closing_vendor','seller_channel']].head(8))

# Save mapping keys privately (NOT shipped to the user) in case re-identification audit is ever needed internally
df.to_pickle('anon_final.pkl')
df.to_csv('/home/claude/capstone/real_estate_deals_anonymized.csv', index=False)
print("\nBroker map size:", len(broker_map), "| Partnership map size:", len(partnership_map), "| Vendor map size:", len(vendor_map))
