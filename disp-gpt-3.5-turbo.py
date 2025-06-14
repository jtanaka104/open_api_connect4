import streamlit as st

st.title("app-gpt-3.5-turbo.py の内容")

try:
    with open('app-gpt-3.5-turbo.py', encoding='utf-8') as f:
        code = f.read()
except FileNotFoundError:
    code = 'app-gpt-3.5-turbo.py が見つかりません。'

st.code(code, language='python')