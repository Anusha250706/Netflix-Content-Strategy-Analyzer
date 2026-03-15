import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load data
df = pd.read_csv('data/netflix_cleaned.csv')

# Explode country_list and genre_list for analysis
df['country_list'] = df['country_list'].apply(lambda x: eval(x) if pd.notnull(x) else [])
df['genre_list'] = df['genre_list'].apply(lambda x: eval(x) if pd.notnull(x) else [])
df_exploded = df.explode('country_list').explode('genre_list')

# Key drivers: Top genres by country
country_genre = df_exploded.groupby(['country_list', 'genre_list']).size().reset_index(name='count')
top_genres_by_country = country_genre.sort_values(['country_list', 'count'], ascending=[True, False])
top_genres_by_country = top_genres_by_country.groupby('country_list').head(3)
top_genres_by_country.to_csv('outputs/top_genres_by_country.csv', index=False)

# Plot: Top 5 countries and their top genres
top_countries = df_exploded['country_list'].value_counts().head(5).index.tolist()
plt.figure(figsize=(10,6))
for country in top_countries:
    subset = top_genres_by_country[top_genres_by_country['country_list'] == country]
    plt.bar(subset['genre_list'], subset['count'], label=country)
plt.xlabel('Genre')
plt.ylabel('Count')
plt.title('Top Genres in Top 5 Countries')
plt.legend()
plt.tight_layout()
plt.savefig('outputs/top_genres_in_top_countries.png')
plt.close()

# Key drivers: Top countries by genre
genre_country = df_exploded.groupby(['genre_list', 'country_list']).size().reset_index(name='count')
top_countries_by_genre = genre_country.sort_values(['genre_list', 'count'], ascending=[True, False])
top_countries_by_genre = top_countries_by_genre.groupby('genre_list').head(3)
top_countries_by_genre.to_csv('outputs/top_countries_by_genre.csv', index=False)

# Plot: Top 5 genres and their top countries
top_genres = df_exploded['genre_list'].value_counts().head(5).index.tolist()
plt.figure(figsize=(10,6))
for genre in top_genres:
    subset = top_countries_by_genre[top_countries_by_genre['genre_list'] == genre]
    plt.bar(subset['country_list'], subset['count'], label=genre)
plt.xlabel('Country')
plt.ylabel('Count')
plt.title('Top Countries in Top 5 Genres')
plt.legend()
plt.tight_layout()
plt.savefig('outputs/top_countries_in_top_genres.png')
plt.close()

print('Key driver analysis for content availability across countries and genres complete. Results saved in outputs/.')