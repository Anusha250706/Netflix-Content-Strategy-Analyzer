# dashboard_matplotlib.py
# Dashboard for Netflix Content Analyzer using pandas and matplotlib (no Streamlit)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import os

# Load data
csv_path = 'data/netflix_cleaned.csv'
df = pd.read_csv(csv_path)

# --- Clustering ---
df['main_genre'] = df['genre_list'].apply(lambda x: eval(x)[0] if pd.notnull(x) and len(eval(x)) > 0 else 'Unknown')
le_genre = LabelEncoder()
df['genre_encoded'] = le_genre.fit_transform(df['main_genre'])
le_rating = LabelEncoder()
df['rating_encoded'] = le_rating.fit_transform(df['rating'].astype(str))
X_cluster = df[['genre_encoded', 'duration_int', 'rating_encoded']].fillna(0)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)
kmeans = KMeans(n_clusters=4, random_state=42)
df['cluster'] = kmeans.fit_predict(X_scaled)

# --- Clustering Plot ---
plt.figure(figsize=(8,6))
sns.scatterplot(x=df['duration_int'], y=df['rating_encoded'], hue=df['cluster'], palette='tab10', alpha=0.7)
plt.xlabel('Duration (min)')
plt.ylabel('Rating (encoded)')
plt.title('Clusters by Duration and Rating')
plt.legend(title='Cluster')
plt.tight_layout()
plt.savefig('outputs/cluster_scatter.png')
plt.close()

# --- Classification ---
df['type_encoded'] = LabelEncoder().fit_transform(df['type'])
features = ['genre_encoded', 'duration_int', 'rating_encoded']
X = df[features].fillna(0)
y = df['type_encoded']
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

# --- Classification Report ---
report = classification_report(y_test, y_pred, target_names=LabelEncoder().fit(df['type']).classes_)
with open('outputs/classification_report.txt', 'w') as f:
    f.write(report)

# --- Confusion Matrix ---
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=LabelEncoder().fit(df['type']).classes_, yticklabels=LabelEncoder().fit(df['type']).classes_)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.tight_layout()
plt.savefig('outputs/confusion_matrix.png')
plt.close()

# --- Feature Importance ---
importances = clf.feature_importances_
feature_names = features
importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=False)
importance_df.to_csv('outputs/feature_importance.csv', index=False)
plt.figure(figsize=(6,3))
sns.barplot(x='Importance', y='Feature', data=importance_df, palette='viridis')
plt.title('Feature Importances for Content Type Classification')
plt.tight_layout()
plt.savefig('outputs/feature_importance.png')
plt.close()

print('All analysis complete. Plots and reports saved in outputs/.')
