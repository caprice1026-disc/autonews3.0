import requests
import base64
import json
import os


# WordPressのURLとエンドポイント
url = 'https://your-wordpress-site.com/wp-json/wp/v2'

# ベーシック認証のためのユーザー名とパスワード
# 認証情報を環境変数から取得
username = os.environ['WP_USER']  
password = os.environ['WP_PASS']

# ベーシック認証のためのヘッダーを作成
credentials = username + ':' + password
token = base64.b64encode(credentials.encode())
header = {'Authorization': 'Basic ' + token.decode('utf-8')}

# 記事のメタデータ
data = {
  "title": "記事のタイトル",
  "content": "記事の内容...",
  "excerpt": "記事の抜粋...",
  "categories": ["category-slug1"],
  "tags": ["tag-slug1", "tag-slug2"],
  "author": "user_id"  
}

# 記事を投稿
response = requests.post(url + '/posts', headers=header, data=data)

# 投稿した記事のIDを取得
post_id = response.json()['id']

# コメントのメタデータ
comment_data = {
    'author_name': 'コメントの著者名',
    'content': 'コメントの内容',
    'post': post_id  # コメントを投稿する記事のID
}

# 記事にコメントを投稿
requests.post(url + '/comments', headers=header, data=comment_data)
