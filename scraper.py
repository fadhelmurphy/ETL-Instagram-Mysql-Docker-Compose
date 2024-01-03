# File: scraper.py

from sqlalchemy import create_engine
import pandas as pd
import os
import instaloader
from scipy.stats import shapiro
# from dotenv import load_dotenv

# load_dotenv()

def scrape_instagram_comments(username, password, target_post_url):
    L = instaloader.Instaloader()

    # Login ke akun Instagram menggunakan environment variables
    L.login(username, password)

    # Mendapatkan metadata postingan dari URL
    post = instaloader.Post.from_shortcode(L.context, target_post_url)

    # Mendapatkan komentar dari postingan
    comments = post.get_comments()

    # Menyimpan komentar ke dalam list
    comment_list = []
    for comment in comments:
        comment_list.append({
            'username': comment.owner.username,
            'comment_text': comment.text,
            'comment_likes': comment.likes_count
            # Tambahkan kolom lain jika diperlukan
        })

    # Logout dari akun Instagram (jika login sebelumnya)
    L.context.close()

    return comment_list

def data_cleaning(comment_list):
    df = pd.DataFrame(comment_list)

    # Hitung proporsi duplikat
    duplicate_proportion = len(df[df.duplicated()]) / len(df)
    
    # Hapus baris dengan proporsi duplikat kurang dari 10%
    if duplicate_proportion < 0.1:
        df.drop_duplicates(inplace=True)
    
    # Hitung proporsi missing values untuk setiap kolom
    missing_values_proportion = df.isnull().sum() / len(df)
    
    # Hapus baris dengan proporsi missing values kurang dari 10%
    columns_to_drop = missing_values_proportion[missing_values_proportion < 0.1].index
    df.dropna(subset=columns_to_drop, inplace=True)
    
    # Isi missing values dengan nilai rata-rata atau median, tergantung pada distribusi data
    for column in df.columns:
        if df[column].isnull().sum() > 0:  # Periksa kolom dengan missing values
            is_normal = check_normality(df[column])
            if is_normal:
                mean_value = df[column].mean()
                df[column].fillna(mean_value, inplace=True)
            else:
                median_value = df[column].median()
                df[column].fillna(median_value, inplace=True)
    
    return df

def check_normality(column):
    stat_shapiro, p_shapiro = shapiro(column)
    if p_shapiro > 0.05:
        return True  # Data terdistribusi normal
    else:
        return False  # Data tidak terdistribusi normal

def load_data_to_mysql(data):
    # Konfigurasi koneksi ke MySQL menggunakan environment variables dari Docker Compose
    db_username = os.environ.get('MYSQL_USER')
    db_password = os.environ.get('MYSQL_PASSWORD')
    db_host = os.environ.get('MYSQL_HOST')
    db_name = os.environ.get('MYSQL_DB')

    # Buat engine SQLAlchemy
    engine = create_engine(f'mysql+mysqlconnector://{db_username}:{db_password}@{db_host}/{db_name}')

    # Muat DataFrame ke dalam tabel MySQL
    data.to_sql(name='instagram_comments', con=engine, if_exists='replace', index=False)

# Gunakan environment variables dari Docker untuk scraping komentar dari postingan Instagram
comment_list = scrape_instagram_comments(os.environ['INSTAGRAM_USERNAME'], os.environ['INSTAGRAM_PASSWORD'], os.environ['TARGET_POST_URL'])

# Lakukan data cleaning pada komentar
cleaned_data = data_cleaning(comment_list)
print(cleaned_data)

# Muat data ke dalam MySQL
load_data_to_mysql(cleaned_data)
