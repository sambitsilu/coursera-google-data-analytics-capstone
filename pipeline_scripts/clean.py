import pandas as pd
import numpy as np

df = pd.read_pickle('raw_selected.pkl')

# 1. Coerce error-string / blank columns to numeric, invalid -> NaN
numeric_cols = ['unleveraged_irr','leveraged_irr','bpo_value','bpo_variation','profit_estimate',
                 'profit_variation','rehab_estimate','rehab_actual_broker','rehab_differential',
                 'buy_side_cost_estimate','total_cost_estimate','square_footage']
for c in numeric_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

# 2. Standardize text fields
text_cols = ['state','seller_channel','product_type','partnership','sourcing_vendor','broker','closing_vendor']
for c in text_cols:
    df[c] = df[c].astype(str).str.strip().str.upper().replace({'NONE': np.nan, 'NAN': np.nan, '': np.nan})

# product_type has case inconsistencies seen earlier (sfr vs SFR, MUlti vs MULTI) - upper() handles that
df['product_type'] = df['product_type'].replace({'COMM': 'COMMERCIAL'})

# 3. Flags: convert 'X' -> True/blank -> False for under_contract_flag/listed_flag
for c in ['under_contract_flag','listed_flag']:
    df[c] = df[c].astype(str).str.strip().str.upper().eq('X')

# 4. Deal status derived field
df['deal_status'] = np.select(
    [df['under_contract_flag'], df['listed_flag'], df['sold_date'].notna()],
    ['Under Contract', 'Listed', 'Sold'],
    default='Unknown'
)

# 5. Flag extreme/implausible IRR values (near-zero holding period denominators blow up XIRR).
# Cap displayed IRR at a sane bound for analysis purposes; keep raw value in *_raw for transparency.
for c in ['unleveraged_irr','leveraged_irr']:
    df[c + '_raw'] = df[c]
    df.loc[df[c].abs() > 50, c] = np.nan  # >5000% treated as a broken/near-instant-flip IRR artifact

# 6. Recompute a clean holding period in months for readability
df['holding_period_months'] = (df['days_on_market'] / 30.44).round(1)

# 7. Profit margin sanity field
df['profit_margin_pct'] = np.where(df['total_cost'] > 0, df['actual_profit'] / df['total_cost'], np.nan)

# 8. Drop rows with no purchase price at all (shouldn't exist, but safety check)
before = len(df)
df = df[df['purchase_price'].notna() & (df['purchase_price'] > 0)]
print("dropped rows with no purchase price:", before - len(df))

# 9. Reorder columns sensibly
front = ['address','state','product_type','seller_channel','partnership','sourcing_vendor','broker',
         'deal_status','purchase_date','sold_date','purchase_year','holding_period_months','days_on_market']
rest = [c for c in df.columns if c not in front]
df = df[front + rest]

print(df.shape)
print(df.isna().sum().sort_values(ascending=False).head(20))
df.to_csv('real_estate_deals_clean.csv', index=False)
df.to_pickle('clean.pkl')
