"""
このファイルは、Webアプリのメイン処理が記述されたファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
from dotenv import load_dotenv
import logging
import traceback
import streamlit as st
import utils
from initialize import initialize
import components as cn
import constants as ct


############################################################
# 設定関連
############################################################
st.set_page_config(
    page_title=ct.APP_NAME
)

load_dotenv()

logger = logging.getLogger(ct.LOGGER_NAME)


def show_exception_details(e: Exception) -> None:
    # st.exception が表示されない環境でも traceback 文字列を表示して原因追跡できるようにする
    with st.expander("エラー詳細を表示", expanded=True):
        st.exception(e)
        st.code(traceback.format_exc(), language="text")


############################################################
# 初期化処理
############################################################
try:
    initialize()
except Exception as e:
    logger.error(ct.INITIALIZE_ERROR_MESSAGE, exc_info=True)
    st.error(utils.build_error_message(ct.INITIALIZE_ERROR_MESSAGE))
    show_exception_details(e)
    st.stop()

# アプリ起動時のログ出力
if not "initialized" in st.session_state:
    st.session_state.initialized = True
    logger.info(ct.APP_BOOT_MESSAGE)


############################################################
# 初期表示
############################################################
# タイトル表示
cn.display_app_title()

# AIメッセージの初期表示
cn.display_initial_ai_message()


############################################################
# 会話ログの表示
############################################################
try:
    cn.display_conversation_log()
except Exception as e:
    logger.error(ct.CONVERSATION_LOG_ERROR_MESSAGE, exc_info=True)
    st.error(utils.build_error_message(ct.CONVERSATION_LOG_ERROR_MESSAGE))
    show_exception_details(e)
    st.stop()


############################################################
# チャット入力の受け付け
############################################################
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)


############################################################
# チャット送信時の処理
############################################################
if chat_message:
    # ==========================================
    # 1. ユーザーメッセージの表示
    # ==========================================
    logger.info({"message": chat_message})

    with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
        st.markdown(chat_message)

    # ==========================================
    # 2. LLMからの回答取得
    # ==========================================
    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            result = st.session_state.retriever.invoke(chat_message)
        except Exception as e:
            logger.error(ct.RECOMMEND_ERROR_MESSAGE, exc_info=True)
            st.error(utils.build_error_message(ct.RECOMMEND_ERROR_MESSAGE))
            show_exception_details(e)
            st.stop()
    
    # ==========================================
    # 3. LLMからの回答表示
    # ==========================================
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        try:
            cn.display_product(result)
            
            logger.info({"message": result})
        except Exception as e:
            logger.error(ct.LLM_RESPONSE_DISP_ERROR_MESSAGE, exc_info=True)
            st.error(utils.build_error_message(ct.LLM_RESPONSE_DISP_ERROR_MESSAGE))
            show_exception_details(e)
            st.stop()

    # ==========================================
    # 4. 会話ログへの追加
    # ==========================================
    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": result})