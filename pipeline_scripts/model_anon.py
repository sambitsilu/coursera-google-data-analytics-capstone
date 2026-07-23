import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

df = pd.read_pickle('anon_final.pkl')

features_num = ['purchase_price','rehab_and_interest','total_cost','loan_amount','purchase_year']
features_cat = ['state','product_type','seller_channel']

model_df = df[features_num + features_cat + ['actual_profit']].dropna(subset=['actual_profit'])
model_df['loan_amount'] = model_df['loan_amount'].fillna(0)
model_df = model_df.dropna(subset=features_num)
model_df['is_profitable'] = (model_df['actual_profit'] > 0).astype(int)

for c in features_cat:
    counts = model_df[c].value_counts()
    rare = counts[counts < 5].index
    model_df[c] = model_df[c].where(~model_df[c].isin(rare), 'OTHER')

X = model_df[features_num + features_cat]
y = model_df['is_profitable']

preprocess = ColumnTransformer([
    ('num', 'passthrough', features_num),
    ('cat', OneHotEncoder(handle_unknown='ignore'), features_cat)
])
pipe = Pipeline([('prep', preprocess), ('rf', RandomForestClassifier(n_estimators=300, max_depth=5, class_weight='balanced', random_state=42))])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
pipe.fit(X_train, y_train)
pred = pipe.predict(X_test)
proba = pipe.predict_proba(X_test)[:,1]
print(classification_report(y_test, pred))
print("ROC AUC:", roc_auc_score(y_test, proba))
cv_scores = cross_val_score(pipe, X, y, cv=5, scoring='roc_auc')
print("5-fold CV ROC AUC: mean=%.3f std=%.3f" % (cv_scores.mean(), cv_scores.std()))

ohe = pipe.named_steps['prep'].named_transformers_['cat']
cat_names = ohe.get_feature_names_out(features_cat)
all_names = features_num + list(cat_names)
importances = pipe.named_steps['rf'].feature_importances_
imp_df = pd.Series(importances, index=all_names).sort_values(ascending=False)
print("\nTop feature importances:\n", imp_df.head(10))
imp_df.to_csv('feature_importance_clf_anon.csv')
