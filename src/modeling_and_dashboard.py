# modeling_and_dashboard.py
# Milestone 3: Modeling & Advanced Analysis for Netflix Content Analyzer
# This script will handle clustering, classification, feature importance, and dashboard setup.

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
if __name__ == "__main__":
    st.set_page_config(page_title="Netflix Content Analyzer Dashboard", layout="wide")
    st.title("Netflix Content Analyzer Dashboard")
    st.write("This dashboard displays clustering, classification, and feature importance analysis.")

    # Sidebar filters
    st.sidebar.header("Filter Data")
    all_countries = sorted(set([c for sublist in df['country_list'].apply(lambda x: eval(x) if pd.notnull(x) else []) for c in sublist]))
    all_genres = sorted(set([g for sublist in df['genre_list'].apply(lambda x: eval(x) if pd.notnull(x) else []) for g in sublist]))
    selected_country = st.sidebar.selectbox("Select Country", options=["All"] + all_countries)
    selected_genre = st.sidebar.selectbox("Select Genre", options=["All"] + all_genres)

    # Filter data based on sidebar
    filtered_df = df.copy()
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df['country_list'].apply(lambda x: selected_country in eval(x) if pd.notnull(x) else False)]
    if selected_genre != "All":
        filtered_df = filtered_df[filtered_df['genre_list'].apply(lambda x: selected_genre in eval(x) if pd.notnull(x) else False)]

    # Clustering Section
    with st.expander("Clustering Analysis", expanded=True):
        st.write("KMeans clustering groups Netflix titles by genre, duration, and ratings.")
        st.dataframe(cluster_summary)

        fig, ax = plt.subplots()
        sns.scatterplot(
            x=filtered_df['duration_int'],
            y=filtered_df['rating_encoded'],
            hue=filtered_df['cluster'],
            palette='tab10',
            alpha=0.7,
            ax=ax
        )
        ax.set_xlabel('Duration (min)')
        ax.set_ylabel('Rating (encoded)')
        ax.set_title('Clusters by Duration and Rating')
        st.pyplot(fig)

    # Classification Section
    with st.expander("Classification: Movie vs TV Show", expanded=True):
        st.write("Random Forest Classifier predicts content type based on features.")

        # Prepare features and target
        filtered_df['type_encoded'] = LabelEncoder().fit_transform(filtered_df['type'])
        features = ['genre_encoded', 'duration_int', 'rating_encoded']
        X = filtered_df[features].fillna(0)
        y = filtered_df['type_encoded']

        # Train/test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Random Forest
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        # Show metrics
        st.subheader("Classification Report")
        report = classification_report(y_test, y_pred, target_names=LabelEncoder().fit(filtered_df['type']).classes_, output_dict=True)
        st.dataframe(pd.DataFrame(report).transpose())

        st.subheader("Confusion Matrix")
        cm = confusion_matrix(y_test, y_pred)
        fig2, ax2 = plt.subplots()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=LabelEncoder().fit(filtered_df['type']).classes_, yticklabels=LabelEncoder().fit(filtered_df['type']).classes_, ax=ax2)
        ax2.set_xlabel('Predicted')
        ax2.set_ylabel('Actual')
        st.pyplot(fig2)

    # Feature Importance Section
    with st.expander("Feature Importance & Key Drivers", expanded=True):
        st.write("Feature importances from the Random Forest model help interpret which features drive content type predictions.")

        importances = clf.feature_importances_
        feature_names = features
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values(by='Importance', ascending=False)

        st.dataframe(importance_df)

        fig3, ax3 = plt.subplots()
        sns.barplot(x='Importance', y='Feature', data=importance_df, ax=ax3, palette='viridis')
        ax3.set_title('Feature Importances for Content Type Classification')
        st.pyplot(fig3)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    # Show metrics
    st.subheader("Classification Report")
    report = classification_report(y_test, y_pred, target_names=LabelEncoder().fit(df['type']).classes_, output_dict=True)
    st.dataframe(pd.DataFrame(report).transpose())


    st.subheader("Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    fig2, ax2 = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=LabelEncoder().fit(df['type']).classes_, yticklabels=LabelEncoder().fit(df['type']).classes_, ax=ax2)
    ax2.set_xlabel('Predicted')
    ax2.set_ylabel('Actual')
    st.pyplot(fig2)

    # --- Feature Importance Analysis ---
    st.header("Feature Importance & Key Drivers")
    st.write("Feature importances from the Random Forest model help interpret which features drive content type predictions.")

    importances = clf.feature_importances_
    feature_names = features
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)

    st.dataframe(importance_df)

    fig3, ax3 = plt.subplots()
    sns.barplot(x='Importance', y='Feature', data=importance_df, ax=ax3, palette='viridis')
    ax3.set_title('Feature Importances for Content Type Classification')
    st.pyplot(fig3)
