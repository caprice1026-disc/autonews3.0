import os
import requests
import base64
import json

# WordPress APIのURL、ユーザー名、パスワードの取得
wordpress_url = os.getenv('WORDPRESS_URL')
username = os.getenv('WP_USER')
password = os.getenv('WP_PASS')
# 記事投稿用のURL
url = f'{wordpress_url}/wp-json/wp/v2/posts'

# ベーシック認証のためのヘッダーを作成
credentials = username + ':' + password
token = base64.b64encode(credentials.encode())
header = {'Authorization': 'Basic ' + token.decode('utf-8')}

# 記事のメタデータ
data = {
    "title": "test",
    "content": "テスト中です。",
    "excerpt": "テスト中です。",
    "author": "1"  ,
    "status": "publish" 
}

# 記事を投稿
response = requests.post(url, headers=header, json=data)
print(response.json())
