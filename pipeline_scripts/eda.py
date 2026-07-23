import pandas as pd
import numpy as np

df = pd.read_pickle('clean.pkl')
df = df.drop(columns=['square_footage'])  # 100% null - unusable, drop and document

print("=== Overview ===")
print("Total deals:", len(df))
print("Date range:", df['purchase_date'].min(), "-", df['purchase_date'].max())
print("Status counts:\n", df['deal_status'].value_counts())

print("\n=== Profitability ===")
print("Total actual profit:", df['actual_profit'].sum())
print("Median profit:", df['actual_profit'].median())
print("Win rate (profit>0):", (df['actual_profit']>0).mean())

print("\n=== By state (top 10 by count) ===")
by_state = df.groupby('state').agg(deals=('address','count'), total_profit=('actual_profit','sum'),
                                     avg_roi=('straight_roi','mean'), avg_dom=('days_on_market','mean')).sort_values('deals', ascending=False)
print(by_state.head(10))

print("\n=== By product type ===")
by_pt = df.groupby('product_type').agg(deals=('address','count'), total_profit=('actual_profit','sum'),
                                         avg_roi=('straight_roi','mean')).sort_values('deals', ascending=False)
print(by_pt)

print("\n=== By broker (top 10 by deal count) ===")
by_broker = df.groupby('broker').agg(deals=('address','count'), total_profit=('actual_profit','sum'),
                                       avg_roi=('straight_roi','mean')).sort_values('deals', ascending=False)
print(by_broker.head(10))

print("\n=== By year ===")
by_year = df.groupby('purchase_year').agg(deals=('address','count'), total_profit=('actual_profit','sum')).sort_index()
print(by_year)

print("\n=== Holding period vs profit correlation ===")
print(df[['holding_period_months','actual_profit','straight_roi','annualized_roi']].corr())

df.to_pickle('clean_final.pkl')
df.to_csv('real_estate_deals_clean.csv', index=False)
