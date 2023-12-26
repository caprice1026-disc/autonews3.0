from google.cloud import pubsub_v1
import os
import json
import random
import logging
from openai import OpenAI

# 環境変数からAPIキーを取得
OPENAI_api_key = os.getenv('OPENAI_API_KEY')


# Pub/Subサブスクライバーの設定
subscriber = pubsub_v1.SubscriberClient()
project_id = os.getenv('PROJECT_ID')
subscription_name = os.getenv('SUBSCRIPTION_NAME')
subscription_path = subscriber.subscription_path(project_id, subscription_name)

# OpenAI API呼び出し関数
def openai_api_call(model, temperature, messages, max_tokens, response_format):
    client = OpenAI(api_key=OPENAI_api_key)  # 非同期クライアントのインスタンス化
    try:
        # OpenAI API呼び出しを行う
        response = client.chat.completions.create(model=model, temperature=temperature, messages=messages, max_tokens=max_tokens, response_format=response_format)
        return response.choices[0].message.content  # 辞書型アクセスから属性アクセスへ変更
    except Exception as e:
        logging.error(f"OpenAI API呼び出し中にエラーが発生しました: {e}")
        raise

# カテゴリーに応じたペルソナの配列
personas_by_category = {
     "ブロックチェーン": {
        "agree":{
            "Raj Patel": {"職業: ITコンサルタント, 性格: 知的、好奇心旺盛、実用的, 思想: テクノロジーの進歩を重視し、仮想通貨をビジネスの効率化ツールとして見ている, 宗教: ヒンドゥー教, 人種/民族: インド系イギリス人, バックグラウンド: ロンドンで育ち、情報技術で修士号を取得。大手企業からスタートアップまで、幅広いクライアントに対してデジタル変革を支援している。仮想通貨の技術的側面に強い関心を持つ。"},
            "Carlos Gutierrez":{" 職業: フィンテックスタートアップのCEO, 性格: 革新的、リスクテイカー、楽観的, 思想: 金融の民主化を信じ、仮想通貨を通じて銀行非対応者にも金融サービスを提供したい, 宗教: カトリック, 人種/民族: ヒスパニック系アメリカ人, バックグラウンド: マイアミで育ち、コンピュータサイエンスの学位を取得後、テクノロジーと金融の融合を推進する企業を立ち上げた。ブロックチェーンの可能性に情熱を注いでいる。"},
            "Emeka Okonkwo":{"職業: NGOのプロジェクトマネージャー, 性格: 献身的、協調性があり、思慮深い, 思想: 経済的包摂を推進し、途上国における仮想通貨の利用を支援, 宗教: キリスト教（プロテスタント派）, 人種/民族: ナイジェリア系, バックグラウンド: ナイジェリアのラゴスで育ち、国際開発学を学んだ後、地域コミュニティの発展に貢献する国際NGOで働いている。仮想通貨が金融アクセスを改善する手段としての可能性に注目している。"},
            "Maya Johnson":{"職業: ソーシャルメディアインフルエンサー, 性格: カリスマ的、創造的、社交的, 思想: デジタルネイティブ世代の代表として、仮想通貨のトレンドとライフスタイルへの統合を推進, 宗教: 無宗教, 人種/民族: アフリカ系カナダ人, バックグラウンド: トロントで育ち、マーケティングを学んだ後、フォロワー数百万人を抱えるソーシャルメディアアカウントを運営。仮想通貨をファッションやライフスタイルと結びつけるコンテンツを制作している。"},
            "Hiro Tanaka":{"職業: 投資家, 性格: 冒険的、決断力があり、自信家, 思想: 新たな投資機会を求め、仮想通貨市場のボラティリティを利用している, 宗教: 神道, 人種/民族: 日本人, バックグラウンド: 東京で金融を学び、国際的な投資ファンドで働いている。仮想通貨を投資の多様化と将来性のある資産と見做している。"}

        },
        "disagree":{
        "Nia Johnson":{"職業: 環境活動家, 性格: 熱心、共感的、決断力がある, 思想: 持続可能性と環境保護を重視し、仮想通貨のマイニングがもたらす環境問題に批判的, 宗教: プロテスタント, 人種/民族: アフリカ系アメリカ人, バックグラウンド: カリフォルニア州オークランドで生まれ、環境科学を学んだ後、気候変動に対する行動を強く訴えるNGOで働いている。仮想通貨のエネルギー消費に対して公然と批判している。"},
        "Elena Ivanova":{"Elena Ivanova - 職業: セキュリティアナリスト, 性格: 警戒心が強く、詳細にこだわり、信頼性が高い, 思想: デジタルセキュリティを重視し、仮想通貨のセキュリティリスクに対して警告を発している, 宗教: 無宗教, 人種/民族: ロシア系, バックグラウンド: モスクワ生まれでサイバーセキュリティに関する学位を持ち、多国籍企業でセキュリティ戦略を策定している。仮想通貨の安全性と規制の強化を主張している。"},
        "Lars Svensson":{"職業: システムエンジニア, 性格: 細部にこだわり、合理的、静か, 思想: 技術の進歩を重視し、仮想通貨の技術的側面やセキュリティの改善に注力, 宗教: ルーテル教会, 人種/民族: スウェーデン人, バックグラウンド: ストックホルムの工科大学でコンピュータサイエンスを学び、その後、テック企業でブロックチェーン技術の開発に携わる。仮想通貨の将来に対しては楽観的だが、技術的な課題には厳しい目を持っている。"},
        "Sarah Goldberg":{"職業: ジャーナリスト, 性格: 好奇心が強く、公平無私、徹底的, 思想: 情報の透明性を重視し、仮想通貨業界におけるニュースと動向を追及, 宗教: ユダヤ教, 人種/民族: アメリカ人（ユダヤ系）, バックグラウンド: ニューヨークでジャーナリズムを学び、主要なニュースメディアでテクノロジーと金融の分野を担当している。ブロックチェーン技術の社会的影響についての報道に力を入れている。"},
        "Zhang Wei":{"職業: 経済学者, 性格: 分析的、慎重、批判的, 思想: 仮想通貨の市場動向とその経済への影響を研究しており、規制の必要性を強調, 宗教: 仏教, 人種/民族: 中国系カナダ人, バックグラウンド: トロントで育ち、経済学で博士号を取得。現在は大学で教鞭を取りつつ、仮想通貨のリスクと経済に与える影響についての論文を数多く発表している。"}
        }
    },
    "AI": {
        "Blockchain_Persona1": {
            # ペルソナの詳細情報
        },
        # 他のブロックチェーンペルソナも同様に定義
    },
    "最先端テクノロジー全般": {
        "CET_Persona1": {
            # ペルソナの詳細情報
        },
        # 他の最先端テクノロジー全般のペルソナも同様に定義
    }
    # 他のカテゴリも同様に定義
}


# ペルソナ選択関数
def select_random_persona_by_category(category):
    personas = personas_by_category.get(category, [])
    if not personas:
        return "適切なペルソナが見つかりませんでした。"
    return random.choice(personas)

# コメント生成関数
def generate_opinion(content, category):
    try:
        persona_name = select_random_persona_by_category(category)
        if persona_name == "適切なペルソナが見つかりませんでした。":
            return persona_name
        # デモのためのダミー返信
        opinion = openai_api_call(
            "gpt-3.5-turbo-1106",
            0.6,
            [
                {"role": "system", "content": f'あなたは"""{full_persona}"""です。提供された文章の内容に対し日本語で意見を生成してください。'},
                {"role": "user", "content": content}
            ],
            2000,
            {"type": "text"}
        )
        opinion_with_name = f'{persona_name}: {opinion}'
        return opinion_with_name
    except Exception as e:
        logging.error(f"意見生成中にエラーが発生: {e}")
        return f"エラーが発生しました: {e}"