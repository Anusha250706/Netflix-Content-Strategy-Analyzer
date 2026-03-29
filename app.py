import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Netflix Content Strategy Analyzer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# CUSTOM CSS - DARK NETFLIX STYLE
# -------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0b0b0f;
        color: #f5f5f5;
    }

    [data-testid="stSidebar"] {
        background-color: #111111;
    }

    section[data-testid="stSidebar"] div, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    .main-title {
        font-size: 40px;
        font-weight: 800;
        color: #E50914;
        margin-bottom: 0;
    }

    .sub-title {
        font-size: 18px;
        color: #d1d5db;
        margin-top: 0;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .insight-box {
        background: #16181d;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        margin-bottom: 12px;
        border-left: 5px solid #E50914;
        color: #f5f5f5;
    }

    .footer-text {
        text-align: center;
        color: #9ca3af;
        font-size: 14px;
        margin-top: 20px;
    }

    div[data-testid="metric-container"] {
        background-color: #16181d;
        border: 1px solid #262730;
        padding: 14px;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.35);
    }

    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div {
        color: #ffffff !important;
    }

    .stExpander {
        background-color: #16181d !important;
        border-radius: 10px !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: #16181d;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown('<p class="main-title">🎬 Netflix Content Strategy Analyzer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Interactive dashboard to explore global streaming trends by year, genre, country, ratings, and content type.</p>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/netflix_titles.csv")
    return df

df = load_data()

# -------------------------------------------------
# DATA CLEANING
# -------------------------------------------------
df["country"] = df["country"].fillna("Unknown")
df["rating"] = df["rating"].fillna("Unknown")
df["duration"] = df["duration"].fillna("Unknown")
df["listed_in"] = df["listed_in"].fillna("Unknown")
df["director"] = df["director"].fillna("Unknown")
df["cast"] = df["cast"].fillna("Unknown")
df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
df["year_added"] = df["date_added"].dt.year
df["month_added"] = df["date_added"].dt.month_name()
df = df.drop_duplicates()

def content_length_category(duration):
    duration = str(duration)
    if "min" in duration:
        try:
            mins = int(duration.split()[0])
            if mins < 60:
                return "Short Movie"
            elif mins <= 120:
                return "Medium Movie"
            else:
                return "Long Movie"
        except:
            return "Unknown"
    elif "Season" in duration:
        try:
            seasons = int(duration.split()[0])
            if seasons == 1:
                return "1 Season"
            elif seasons <= 3:
                return "2-3 Seasons"
            else:
                return "4+ Seasons"
        except:
            return "Unknown"
    return "Unknown"

df["Content Length Category"] = df["duration"].apply(content_length_category)

def extract_duration_value(duration):
    try:
        return int(str(duration).split()[0])
    except:
        return None

df["duration_value"] = df["duration"].apply(extract_duration_value)
df["main_genre"] = df["listed_in"].apply(lambda x: str(x).split(",")[0].strip())

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.markdown("## 🎛 Dashboard Filters")
st.sidebar.write("Use these filters to interact with the Netflix dataset.")

year_list = sorted(df["release_year"].dropna().unique())
selected_years = st.sidebar.multiselect("Select Release Year", year_list, default=year_list)

type_list = sorted(df["type"].dropna().unique())
selected_types = st.sidebar.multiselect("Select Content Type", type_list, default=type_list)

country_list = sorted(df["country"].dropna().unique())
selected_countries = st.sidebar.multiselect("Select Country", country_list, default=country_list)

genre_list = sorted(set(g.strip() for sub in df["listed_in"].dropna().str.split(",") for g in sub))
selected_genres = st.sidebar.multiselect("Select Genre", genre_list, default=genre_list)

rating_list = sorted(df["rating"].dropna().unique())
selected_ratings = st.sidebar.multiselect("Select Rating", rating_list, default=rating_list)

# -------------------------------------------------
# FILTER DATA
# -------------------------------------------------
filtered_df = df[
    (df["release_year"].isin(selected_years)) &
    (df["type"].isin(selected_types)) &
    (df["country"].isin(selected_countries)) &
    (df["rating"].isin(selected_ratings))
]

filtered_df = filtered_df[
    filtered_df["listed_in"].apply(
        lambda x: any(g in [i.strip() for i in str(x).split(",")] for g in selected_genres)
    )
]

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please change your filter values.")
    st.stop()

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------
total_titles = filtered_df.shape[0]
total_movies = filtered_df[filtered_df["type"] == "Movie"].shape[0]
total_tvshows = filtered_df[filtered_df["type"] == "TV Show"].shape[0]
top_country = filtered_df["country"].value_counts().idxmax()
top_genre = filtered_df["main_genre"].value_counts().idxmax()

st.markdown('<p class="section-title">📊 Dashboard Summary</p>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Titles", total_titles)
k2.metric("Movies", total_movies)
k3.metric("TV Shows", total_tvshows)
k4.metric("Top Country", top_country)
k5.metric("Top Genre", top_genre)

# -------------------------------------------------
# CHART 1 + 2
# -------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    growth_data = filtered_df["release_year"].value_counts().sort_index().reset_index()
    growth_data.columns = ["Release Year", "Count"]

    fig_growth = px.line(
        growth_data,
        x="Release Year",
        y="Count",
        markers=True,
        title="Content Growth Over Release Years",
        color_discrete_sequence=["#E50914"],
        template="plotly_dark"
    )
    fig_growth.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_growth, use_container_width=True)

with c2:
    type_counts = filtered_df["type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]

    fig_type = px.pie(
        type_counts,
        names="Type",
        values="Count",
        hole=0.45,
        title="Content Type Distribution",
        color_discrete_sequence=px.colors.qualitative.Set2,
        template="plotly_dark"
    )
    fig_type.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_type, use_container_width=True)

# -------------------------------------------------
# CHART 3 + 4
# -------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    genre_series = filtered_df["listed_in"].str.split(",").explode().str.strip()
    genre_counts = genre_series.value_counts().reset_index()
    genre_counts.columns = ["Genre", "Count"]

    fig_genre = px.bar(
        genre_counts.head(10),
        x="Genre",
        y="Count",
        title="Top 10 Genres",
        color="Count",
        color_continuous_scale="Reds",
        template="plotly_dark"
    )
    fig_genre.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_genre, use_container_width=True)

with c4:
    country_counts = filtered_df["country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]

    fig_country = px.bar(
        country_counts.head(10),
        x="Country",
        y="Count",
        title="Top 10 Countries by Content",
        color="Count",
        color_continuous_scale="Blues",
        template="plotly_dark"
    )
    fig_country.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_country, use_container_width=True)

# -------------------------------------------------
# CHART 5 + 6
# -------------------------------------------------
c5, c6 = st.columns(2)

with c5:
    rating_counts = filtered_df["rating"].value_counts().reset_index()
    rating_counts.columns = ["Rating", "Count"]

    fig_rating = px.bar(
        rating_counts,
        x="Rating",
        y="Count",
        title="Rating Analysis",
        color="Count",
        color_continuous_scale="Purples",
        template="plotly_dark"
    )
    fig_rating.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_rating, use_container_width=True)

with c6:
    length_counts = filtered_df["Content Length Category"].value_counts().reset_index()
    length_counts.columns = ["Category", "Count"]

    fig_length = px.bar(
        length_counts,
        x="Category",
        y="Count",
        title="Content Length Category Distribution",
        color="Count",
        color_continuous_scale="Tealgrn",
        template="plotly_dark"
    )
    fig_length.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_length, use_container_width=True)

# -------------------------------------------------
# CHART 7 + 8
# -------------------------------------------------
c7, c8 = st.columns(2)

with c7:
    year_added_counts = filtered_df["year_added"].value_counts().sort_index().reset_index()
    year_added_counts.columns = ["Year Added", "Count"]

    fig_year_added = px.area(
        year_added_counts,
        x="Year Added",
        y="Count",
        title="Content Added to Netflix Over Time",
        color_discrete_sequence=["#ef4444"],
        template="plotly_dark"
    )
    fig_year_added.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_year_added, use_container_width=True)

with c8:
    rating_type = filtered_df.groupby(["rating", "type"]).size().reset_index(name="Count")

    fig_rating_type = px.bar(
        rating_type,
        x="rating",
        y="Count",
        color="type",
        barmode="group",
        title="Ratings by Content Type",
        color_discrete_sequence=px.colors.qualitative.Safe,
        template="plotly_dark"
    )
    fig_rating_type.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
    st.plotly_chart(fig_rating_type, use_container_width=True)

# -------------------------------------------------
# CHART 9 + 10
# -------------------------------------------------
c9, c10 = st.columns(2)

with c9:
    top_directors = filtered_df[filtered_df["director"] != "Unknown"]["director"].value_counts().head(10).reset_index()
    top_directors.columns = ["Director", "Count"]

    fig_director = px.bar(
        top_directors,
        x="Director",
        y="Count",
        title="Top 10 Directors",
        color="Count",
        color_continuous_scale="Oranges",
        template="plotly_dark"
    )
    fig_director.update_layout(
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font=dict(color="white"),
        xaxis_tickangle=-35
    )
    st.plotly_chart(fig_director, use_container_width=True)

with c10:
    movie_duration_df = filtered_df[filtered_df["type"] == "Movie"].copy()
    movie_duration_df = movie_duration_df.dropna(subset=["duration_value"])

    fig_movie_duration = px.histogram(
        movie_duration_df,
        x="duration_value",
        nbins=30,
        title="Movie Duration Distribution",
        color_discrete_sequence=["#7c3aed"],
        template="plotly_dark"
    )
    fig_movie_duration.update_layout(
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font=dict(color="white"),
        xaxis_title="Duration (minutes)",
        yaxis_title="Number of Movies"
    )
    st.plotly_chart(fig_movie_duration, use_container_width=True)

# -------------------------------------------------
# TOP GENRE PER YEAR
# -------------------------------------------------
genre_year_df = filtered_df.copy()
genre_year_df = genre_year_df.assign(Genre=genre_year_df["listed_in"].str.split(",")).explode("Genre")
genre_year_df["Genre"] = genre_year_df["Genre"].str.strip()

genre_year_count = genre_year_df.groupby(["release_year", "Genre"]).size().reset_index(name="Count")
top_genre_per_year = genre_year_count.loc[genre_year_count.groupby("release_year")["Count"].idxmax()]

fig_top_genre = px.bar(
    top_genre_per_year,
    x="release_year",
    y="Count",
    color="Genre",
    title="Top Genre in Each Year",
    template="plotly_dark"
)
fig_top_genre.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
st.plotly_chart(fig_top_genre, use_container_width=True)

# -------------------------------------------------
# GLOBAL MAP
# -------------------------------------------------
map_data = filtered_df["country"].value_counts().reset_index()
map_data.columns = ["country", "count"]

fig_map = px.choropleth(
    map_data,
    locations="country",
    locationmode="country names",
    color="count",
    hover_name="country",
    title="Global Content Distribution by Country",
    color_continuous_scale="Reds",
    template="plotly_dark"
)
fig_map.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
st.plotly_chart(fig_map, use_container_width=True)

# -------------------------------------------------
# MONTHLY ADDITIONS
# -------------------------------------------------
month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

monthly_counts = filtered_df["month_added"].value_counts().reindex(month_order).reset_index()
monthly_counts.columns = ["Month", "Count"]
monthly_counts = monthly_counts.fillna(0)

fig_month = px.line(
    monthly_counts,
    x="Month",
    y="Count",
    markers=True,
    title="Monthly Content Additions",
    color_discrete_sequence=["#10b981"],
    template="plotly_dark"
)
fig_month.update_layout(plot_bgcolor="#111111", paper_bgcolor="#111111", font=dict(color="white"))
st.plotly_chart(fig_month, use_container_width=True)

# -------------------------------------------------
# DATA TABLE
# -------------------------------------------------
st.markdown('<p class="section-title">📄 Filtered Dataset Preview</p>', unsafe_allow_html=True)
with st.expander("Click to view filtered data"):
    st.dataframe(filtered_df, use_container_width=True)

# -------------------------------------------------
# KEY INSIGHTS
# -------------------------------------------------
st.markdown('<p class="section-title">💡 Key Insights</p>', unsafe_allow_html=True)

most_common_genre = genre_counts.iloc[0]["Genre"] if not genre_counts.empty else "N/A"
most_common_rating = rating_counts.iloc[0]["Rating"] if not rating_counts.empty else "N/A"
top_director_name = top_directors.iloc[0]["Director"] if not top_directors.empty else "N/A"

st.markdown(
    f"""
    <div class="insight-box"><b>Total Titles:</b> The filtered dataset contains <b>{total_titles}</b> titles available for analysis.</div>
    <div class="insight-box"><b>Top Country:</b> <b>{top_country}</b> contributes the highest amount of content in the selected filters.</div>
    <div class="insight-box"><b>Most Popular Genre:</b> The most common genre is <b>{most_common_genre}</b>.</div>
    <div class="insight-box"><b>Most Frequent Rating:</b> The dominant content rating is <b>{most_common_rating}</b>.</div>
    <div class="insight-box"><b>Content Mix:</b> The selection contains <b>{total_movies}</b> movies and <b>{total_tvshows}</b> TV shows.</div>
    <div class="insight-box"><b>Leading Director:</b> The most frequently appearing director is <b>{top_director_name}</b>.</div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.markdown('<p class="footer-text">Built with Streamlit | Netflix Content Strategy Analyzer Dashboard</p>', unsafe_allow_html=True)