import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_pickle('anon_final.pkl')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})

by_year = df.groupby('purchase_year')['actual_profit'].sum()
fig, ax = plt.subplots(figsize=(7,4))
ax.bar(by_year.index.astype(str), by_year.values/1000, color='#2c5f8a')
ax.set_ylabel('Total profit ($ thousands)'); ax.set_xlabel('Purchase year')
ax.set_title('Total realized profit by acquisition year')
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('chart_profit_by_year_anon.png', dpi=150); plt.close()

by_state = df.groupby('state').agg(deals=('deal_id','count'), avg_roi=('straight_roi','mean')).sort_values('deals', ascending=False).head(8)
fig, ax1 = plt.subplots(figsize=(7,4))
ax1.bar(by_state.index, by_state['deals'], color='#2c5f8a', label='Deal count')
ax1.set_ylabel('Number of deals')
ax2 = ax1.twinx()
ax2.plot(by_state.index, by_state['avg_roi']*100, color='#d9782d', marker='o', label='Avg straight ROI %')
ax2.set_ylabel('Average straight ROI (%)')
ax1.set_title('Deal volume and average ROI by state (top 8 by volume)')
fig.legend(loc='upper right', bbox_to_anchor=(0.9,0.88))
plt.tight_layout(); plt.savefig('chart_state_roi_anon.png', dpi=150); plt.close()

pt_order = df['product_type'].value_counts().head(6).index
fig, ax = plt.subplots(figsize=(7,4))
data = [df.loc[df['product_type']==pt,'straight_roi'].dropna()*100 for pt in pt_order]
ax.boxplot(data, tick_labels=pt_order, showfliers=False)
ax.set_ylabel('Straight ROI (%)'); ax.set_title('ROI distribution by property type (top 6 by deal count)')
plt.xticks(rotation=20); plt.tight_layout()
plt.savefig('chart_roi_by_type_anon.png', dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(7,4))
ax.scatter(df['holding_period_months'], df['actual_profit']/1000, alpha=0.6, color='#2c5f8a')
ax.set_xlabel('Holding period (months)'); ax.set_ylabel('Actual profit ($ thousands)')
ax.set_title('Holding period vs. realized profit'); ax.axhline(0, color='gray', linewidth=0.8)
plt.tight_layout(); plt.savefig('chart_holding_vs_profit_anon.png', dpi=150); plt.close()

imp = pd.read_csv('feature_importance_clf_anon.csv', index_col=0).iloc[:,0].head(8).sort_values()
fig, ax = plt.subplots(figsize=(7,4))
ax.barh(imp.index, imp.values, color='#2c5f8a')
ax.set_title('Top predictors of deal profitability (Random Forest)')
ax.set_xlabel('Feature importance')
plt.tight_layout(); plt.savefig('chart_feature_importance_anon.png', dpi=150); plt.close()
print("done")
