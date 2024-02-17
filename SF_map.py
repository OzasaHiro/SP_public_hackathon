import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

from getpass import getpass
from collections import Counter

from astrapy.db import AstraDB
import openai
import os
from typing import List, Dict, Optional

import datetime
import pytz

ASTRA_DB_API_ENDPOINT = os.environ['ASTRA_DB_API_ENDPOINT']
ASTRA_DB_APPLICATION_TOKEN = os.environ['ASTRA_DB_APPLICATION_TOKEN']
OPENAI_API_KEY= os.environ['OPENAI_API_KEY']

astra_db = AstraDB(
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
)

coll_name = "sf_mobile_food_db"
collection = astra_db.create_collection(coll_name, dimension=1536)

def find_food_and_shop_by_quote(query_quote: str, n: int, tags: Optional[List[str]] = None) -> Dict[str, List[Dict[str, str]]]:

    try:
        query_vector = client.embeddings.create(
            input=[query_quote],
            model=embedding_model_name,
        ).data[0].embedding
    except Exception as e:
        print(f"Error in embedding the query: {e}")
        return {"results": []}

    filter_clause = {}
    if tags:
        filter_clause["tags"] = {tag: True for tag in tags}

    try:
        results = collection.vector_find(
            query_vector,
            limit=n,
            filter=filter_clause,
            fields=["food", "shop", "latitude", "longitude", "day_of_week", "start_time", "end_time"],
        )
    except Exception as e:
        print(f"Error in vector search: {e}")
        return {"results": []}

    formatted_results = [
        {
         "food": str(result["food"]), 
         "shop": str(result["shop"]), 
         "latitude": str(result["latitude"]),
         "longitude": str(result["longitude"]),
         "day_of_week": str(result["day_of_week"]),
         "start_time": str(result["start_time"]),
         "end_time": str(result["end_time"])
        }
        for result in results
    ]

    return {"results": formatted_results}


client = openai.OpenAI(api_key=OPENAI_API_KEY)
embedding_model_name = "text-embedding-3-small"

# サンフランシスコの中心の緯度と経度
latitude = 37.7749
longitude = -122.4194

user_input = st.text_input("What would you like to eat or drink?", "Cheese burger")

# サンフランシスコのタイムゾーンを設定
sf_timezone = pytz.timezone('America/Los_Angeles')
# サンフランシスコの現在時刻を取得
current_time = datetime.datetime.now(sf_timezone).strftime('%H:%M')


# 地図を生成
sf_map = folium.Map(location=[latitude, longitude], zoom_start=12)

# 検索クエリと結果数
query_quote = user_input
n = 10  # 取得したい結果の数

# 検索結果の取得
search_results = find_food_and_shop_by_quote(query_quote, n)
stores = search_results["results"]

    
# 各店舗の位置にマーカーを追加
for store in stores:
    latitude = float(store["latitude"])
    longitude = float(store["longitude"])
    popup_text = f"<b>{store['shop']}</b>: <br>Time: {store['start_time']} - {store['end_time']}<br><br>{store['food']}"
    folium.Marker([latitude, longitude], popup=popup_text).add_to(sf_map)

# Streamlitで地図を表示
folium_static(sf_map)
