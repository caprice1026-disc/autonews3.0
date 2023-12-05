import feedparser
import os
import logging
from google.cloud import storage
from flask import escape

def save_to_gcs(bucket_name, file_name, content):
    """ GCSバケットにファイルを保存する関数 """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        blob.upload_from_string(content)
        return True
    except Exception as e:
        logging.error(f"GCSへの保存中にエラーが発生しました: {e}")
        return False

def rss_to_gcs(request):
    """ RSSフィードをチェックし、最新のエントリをGCSに保存するCloud Function """
    try:
        request_json = request.get_json(silent=True)
        request_args = request.args

        if request_json and 'url' in request_json:
            rss_url = request_json['url']
        elif request_args and 'url' in request_args:
            rss_url = request_args['url']
        else:
            return 'RSSフィードのURLが指定されていません。'

        feed = feedparser.parse(rss_url)
        latest_entry = feed.entries[0] if feed.entries else None

        if latest_entry:
            content = f"タイトル: {latest_entry.title}\nリンク: {latest_entry.link}"
            bucket_name = 'あなたのバケット名'
            file_name = 'rss_latest_entry.txt'

            if save_to_gcs(bucket_name, file_name, content):
                return f"GCSに保存しました: {file_name}"
            else:
                return "GCSへの保存に失敗しました。"
        else:
            return '新しいエントリはありません。'
    except Exception as e:
        logging.error(f"RSSフィードの処理中にエラーが発生しました: {e}")
        return "処理中にエラーが発生しました。"