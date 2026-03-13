"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
from pathlib import Path
import streamlit as st
import constants as ct


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown("こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。")
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """
    商品情報の表示

    Args:
        result: LLMからの回答
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    product = build_product_dict(result)
    image_path = Path(__file__).resolve().parent / "images" / "products" / product["file_name"]

    st.markdown("以下の商品をご提案いたします。")

    # 「商品名」と「価格」
    st.success(f"""
            商品名：{product['name']}（商品ID: {product['id']}）\n
            価格：{product['price']}
    """)

    # 「商品カテゴリ」と「メーカー」と「ユーザー評価」
    st.code(f"""
        商品カテゴリ：{product['category']}\n
        メーカー：{product['maker']}\n
        評価：{product['score']}({product['review_number']}件)
    """, language=None, wrap_lines=True)

    # 商品画像
    if image_path.exists():
        st.image(str(image_path), width=400)
    else:
        logger.warning(f"商品画像が見つかりません: {image_path}")

    # 商品説明
    st.code(product['description'], language=None, wrap_lines=True)

    # おすすめ対象ユーザー
    st.markdown("**こんな方におすすめ！**")
    st.info(product["recommended_people"])

    # 商品ページのリンク
    st.link_button("商品ページを開く", type="primary", use_container_width=True, url="https://google.com")


def build_product_dict(result):
    """
    Retrieverの戻り値から商品情報の辞書を作成

    Args:
        result: Retrieverの戻り値

    Returns:
        商品情報の辞書
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    if not result:
        raise ValueError("商品候補が取得できませんでした。")

    document = result[0] if isinstance(result, list) else result
    page_content = getattr(document, "page_content", None)

    if not page_content:
        raise ValueError("商品データの本文が取得できませんでした。")

    product = {}
    for line in page_content.splitlines():
        if ": " not in line:
            continue

        key, value = line.split(": ", 1)
        product[key] = value

    required_keys = {
        "id",
        "name",
        "category",
        "price",
        "maker",
        "recommended_people",
        "review_number",
        "score",
        "file_name",
        "description",
    }
    missing_keys = required_keys - product.keys()

    if missing_keys:
        logger.error(f"商品データの解析に失敗しました。不足項目: {sorted(missing_keys)}")
        raise ValueError("商品データの形式が想定と異なります。")

    return product