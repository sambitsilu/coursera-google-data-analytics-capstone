import pandas as pd
df = pd.read_pickle('anon_final.pkl')

print("Total deals:", len(df))
print("Total profit:", df['actual_profit'].sum())
print("Median profit:", df['actual_profit'].median())
print("Win rate:", (df['actual_profit']>0).mean())

by_state = df.groupby('state').agg(deals=('deal_id','count'), total_profit=('actual_profit','sum'),
                                     avg_roi=('straight_roi','mean'), avg_dom=('days_on_market','mean')).sort_values('deals', ascending=False)
print("\nBy state:\n", by_state.head(8))

by_pt = df.groupby('product_type').agg(deals=('deal_id','count'), total_profit=('actual_profit','sum'),
                                         avg_roi=('straight_roi','mean')).sort_values('deals', ascending=False)
print("\nBy product type:\n", by_pt)

by_broker = df.groupby('broker').agg(deals=('deal_id','count'), total_profit=('actual_profit','sum'),
                                       avg_roi=('straight_roi','mean')).sort_values('deals', ascending=False)
print("\nTop brokers:\n", by_broker.head(6))

print("\nCorr holding period vs roi:\n", df[['holding_period_months','actual_profit','straight_roi','annualized_roi']].corr())
