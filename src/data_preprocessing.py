# ==============================
# Netflix Content Strategy Analyzer
# ==============================

"""
PROJECT SCOPE:
This project aims to analyze Netflix's content dataset to understand 
content distribution, growth trends, genre popularity, rating patterns, 
and country-level contributions. The objective is to extract meaningful 
business insights that can help understand Netflix's content strategy.

The analysis includes:
- Data cleaning and preprocessing
- Normalization of categorical features (genre, country)
- Exploratory Data Analysis (EDA)
- Feature engineering (Content Length Category, Original vs Licensed)
- Visualization of insights

SUCCESS METRICS:
The project will be considered successful if:

1. The dataset is cleaned (missing values handled, duplicates removed).
2. Categorical features such as genre and country are normalized.
3. Visualizations clearly show:
   - Content growth over time
   - Distribution of genres
   - Distribution of ratings
   - Distribution of content type (Movies vs TV Shows)
   - Country-level content contribution
4. Derived features are created:
   - Content Length Category
   - Original vs Licensed classification
5. All visualizations are saved successfully in the outputs folder.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ------------------------------
# 1. Load Dataset
# ------------------------------
df = pd.read_csv("data/netflix_titles.csv")

print("Dataset Loaded Successfully!")
print(df.head())

# Create output folder for saving visualizations
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# ------------------------------
# 2. Data Cleaning
# ------------------------------

# Remove duplicates
df.drop_duplicates(inplace=True)

# Fill missing values
df.fillna("Unknown", inplace=True)

# Convert date_added to datetime
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

print("\nData Cleaning Completed!")

# ------------------------------
# 3. Normalize Categorical Features
# ------------------------------

# Normalize Genres
df['listed_in'] = df['listed_in'].str.split(',')
df = df.explode('listed_in')
df['listed_in'] = df['listed_in'].str.strip()

# Normalize Countries
df['country'] = df['country'].str.split(',')
df = df.explode('country')
df['country'] = df['country'].str.strip()

print("Categorical Features Normalized!")

# ------------------------------
# 4. Content Type Analysis
# ------------------------------

plt.figure()
sns.countplot(data=df, x='type')
plt.title("Movies vs TV Shows on Netflix")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/content_type.png")
plt.close()

# ------------------------------
# 5. Rating Distribution
# ------------------------------

plt.figure()
sns.countplot(data=df, x='rating', order=df['rating'].value_counts().index)
plt.title("Distribution of Ratings on Netflix")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig("outputs/rating_distribution.png")
plt.close()

# ------------------------------
# 6. Top 10 Countries
# ------------------------------

country_counts = df['country'].value_counts().head(10)

plt.figure()
country_counts.plot(kind='bar')
plt.title("Top 10 Content Producing Countries")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/top_countries.png")
plt.close()

# ------------------------------
# 7. Content Added Per Year
# ------------------------------

df['year_added'] = df['date_added'].dt.year
year_counts = df['year_added'].value_counts().sort_index()

plt.figure()
year_counts.plot(kind='line')
plt.title("Content Added Per Year")
plt.tight_layout()
plt.savefig("outputs/content_per_year.png")
plt.close()

# ------------------------------
# 8. Top 10 Genres
# ------------------------------

genre_counts = df['listed_in'].value_counts().head(10)

plt.figure()
genre_counts.plot(kind='bar')
plt.title("Top 10 Genres on Netflix")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/top_genres.png")
plt.close()

# ------------------------------
# 9. Feature Engineering
# ------------------------------

# Content Length Category
def categorize_duration(duration):
    if "min" in duration:
        minutes = int(duration.split()[0])
        if minutes < 60:
            return "Short Movie"
        elif minutes < 120:
            return "Medium Movie"
        else:
            return "Long Movie"
    elif "Season" in duration:
        seasons = int(duration.split()[0])
        if seasons == 1:
            return "Single Season Show"
        else:
            return "Multi-Season Show"
    else:
        return "Unknown"

df['Content_Length_Category'] = df['duration'].apply(categorize_duration)

# Original vs Licensed (simple assumption)
df['Original_vs_Licensed'] = df['title'].apply(
    lambda x: "Original" if "Netflix" in x else "Licensed"
)

# ------------------------------
# 10. Visualization of Derived Features
# ------------------------------

plt.figure()
sns.countplot(data=df, x='Content_Length_Category',
              order=df['Content_Length_Category'].value_counts().index)
plt.title("Content Length Category Distribution")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/content_length_category.png")
plt.close()

plt.figure()
sns.countplot(data=df, x='Original_vs_Licensed')
plt.title("Original vs Licensed Content")
plt.tight_layout()
plt.savefig("outputs/original_vs_licensed.png")
plt.close()

print("\nAll Visualizations Saved in 'outputs' folder!")
print("Project Execution Completed Successfully!")