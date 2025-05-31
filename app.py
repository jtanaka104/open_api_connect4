import streamlit as st
from openai import OpenAI

API_KEY = st.secrets.OpenAIAPI.openai_api_key

def init_board_str():
    return "１２３４５６７\n□□□□□□□\n□□□□□□□\n□□□□□□□\n□□□□□□□\n□□□□□□□\n□□□□□□□"

def board_to_html(board_str):
    html = board_str.replace("\n", "<br/>")
    return html

def ask_ai(board_str, last_move=None, player="ai"):
    if player == "human":
        prompt = f"""
あなたはConnect4のAIです。人間（●）の代理として、指定された列に●を落とした新しい盤面を作成してください。

【ルール】
- 盤面は7列×6行です。上から順に表示してください。
- コインは必ず一番下から積み上がります。
- 今回は人間（●）が「{last_move+1}列目」にコインを落とします。

【出力フォーマット】
- 盤面のみを7列×6行で、上から下へ、1行ずつ「１２３４５６７」から始めて表示してください。
- 盤面以外の説明やコメントは不要です。

現在の盤面:
{board_str}

あなたの番です。新しい盤面を出力してください。
"""
    else:
        prompt = f"""
あなたはConnect4のAIです。AI（×）として、最善の手を選び、盤面を更新してください。

【ルール】
- 盤面は7列×6行です。上から順に表示してください。
- コインは必ず一番下から積み上がります。
- 今回はあなた（×）の番です。

【出力フォーマット】
- 盤面のみを7列×6行で、上から下へ、1行ずつ「１２３４５６７」から始めて表示してください。
- 盤面以外の説明やコメントは不要です。

現在の盤面:
{board_str}

あなたの番です。新しい盤面を出力してください。
"""
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="o1",
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    import re
    content = response.choices[0].message.content
    match = re.search(r"１２３４５６７\n([□×●\n]{42,})", content)
    if match:
        board_str = "１２３４５６７\n" + match.group(1).strip()
        return board_str
    else:
        return None

# セッション初期化
if "board_str" not in st.session_state:
    st.session_state["board_str"] = init_board_str()
    st.session_state["turn"] = "human"
    st.session_state["message"] = ""
    st.session_state["gameover"] = False
    st.session_state["last_move"] = None

st.title("Connect4（盤面生成版）")
st.write(board_to_html(st.session_state["board_str"]), unsafe_allow_html=True)

if not st.session_state["gameover"]:
    if st.session_state["turn"] == "human":
        st.session_state["message"] = ""  # ← ここを追加
        with st.form(key="user_form", clear_on_submit=True):
            col = st.text_input("あなたの番です。1-7の数字を入力してください。", key="user_input")
            submitted = st.form_submit_button("決定")
        if submitted and col and col in "1234567":
            col_idx = int(col) - 1
            # AIに新しい盤面を作らせる
            new_board = ask_ai(st.session_state["board_str"], last_move=col_idx, player="human")
            if new_board:
                st.session_state["board_str"] = new_board
                st.session_state["turn"] = "ai"
                st.session_state["last_move"] = col_idx
            else:
                st.session_state["message"] = "AIが不正な盤面を返しました。"
            st.rerun()
    elif st.session_state["turn"] == "ai":
        st.text_input("", key="user_input", value="", disabled=True, label_visibility="collapsed")
        st.session_state["message"] = "AIの番です。考え中..."
        st.write(st.session_state["message"])
        # AIに新しい盤面を作らせる
        new_board = ask_ai(st.session_state["board_str"], last_move=st.session_state["last_move"], player="ai")
        if new_board:
            st.session_state["board_str"] = new_board
            st.session_state["turn"] = "human"
        else:
            st.session_state["message"] = "AIが不正な盤面を返しました。"
        st.rerun()

if st.session_state["message"]:
    st.write(st.session_state["message"])

if st.button("リセット"):
    st.session_state["board_str"] = init_board_str()
    st.session_state["turn"] = "human"
    st.session_state["message"] = ""
    st.session_state["gameover"] = False
    st.session_state["last_move"] = None
    st.rerun()

