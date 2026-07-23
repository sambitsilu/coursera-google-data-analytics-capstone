import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

df = pd.read_pickle('clean_final.pkl')

# Target: actual_profit. Only use features known at PURCHASE time (no data leakage from sale-side columns)
features_num = ['purchase_price','rehab_and_interest','total_cost','loan_amount','purchase_year']
features_cat = ['state','product_type','seller_channel']

model_df = df[features_num + features_cat + ['actual_profit']].dropna(subset=['actual_profit'])
# fill numeric NaNs (e.g. loan_amount NaN = cash deal = 0)
model_df['loan_amount'] = model_df['loan_amount'].fillna(0)
model_df = model_df.dropna(subset=features_num)

# collapse rare states/product types into 'OTHER' to avoid overfitting on one-hot sparsity
for c in features_cat:
    counts = model_df[c].value_counts()
    rare = counts[counts < 5].index
    model_df[c] = model_df[c].where(~model_df[c].isin(rare), 'OTHER')

X = model_df[features_num + features_cat]
y = model_df['actual_profit']

preprocess = ColumnTransformer([
    ('num', 'passthrough', features_num),
    ('cat', OneHotEncoder(handle_unknown='ignore'), features_cat)
])

pipe = Pipeline([('prep', preprocess), ('rf', RandomForestRegressor(n_estimators=300, max_depth=6, random_state=42))])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipe.fit(X_train, y_train)
pred = pipe.predict(X_test)

print("n samples:", len(model_df))
print("Test R2:", r2_score(y_test, pred))
print("Test MAE:", mean_absolute_error(y_test, pred))
print("Baseline MAE (predict mean):", mean_absolute_error(y_test, [y_train.mean()]*len(y_test)))

# feature importances
ohe = pipe.named_steps['prep'].named_transformers_['cat']
cat_names = ohe.get_feature_names_out(features_cat)
all_names = features_num + list(cat_names)
importances = pipe.named_steps['rf'].feature_importances_
imp_df = pd.Series(importances, index=all_names).sort_values(ascending=False)
print("\nTop feature importances:\n", imp_df.head(12))

imp_df.to_csv('feature_importance.csv')
