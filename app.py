import streamlit as st
import pandas as pd
import re
import io
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
from datetime import datetime

st.title("表記チェックアプリ")

# =========================
# ルール読み込み
# =========================

st.sidebar.header("① ルール設定")

hyoki_file = st.sidebar.file_uploader("表記便覧Excel（正表記・NG表記）", type=["xlsx"])

rules = None
if hyoki_file:
    rules = pd.read_excel(hyoki_file)
    st.sidebar.success(f"ルール読込: {len(rules)}件")

# =========================
# 文書アップロード
# =========================

st.header("② 文書アップロード")

uploaded = st.file_uploader("PDF または 画像", type=["pdf","png","jpg","jpeg"])

# =========================
# OCR
# =========================

def ocr_pdf(file_bytes):
    images = convert_from_bytes(file_bytes)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang="jpn")
    return text

def ocr_image(file_bytes):
    img = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(img, lang="jpn")

# =========================
# 曜日チェック
# =========================

def weekday_check(text):
    results = []
    pattern = r"(\d{4}/\d{1,2}/\d{1,2})（([月火水木金土日])）"

    for m in re.finditer(pattern, text):
        date_str = m.group(1)
        w = m.group(2)

        try:
            d = datetime.strptime(date_str, "%Y/%m/%d")
            real = "月火水木金土日"[d.weekday()]
            if real != w:
                results.append(f"{date_str}（{w}）→ 正:{real}")
        except:
            pass

    return results

# =========================
# 表記チェック
# =========================

def hyoki_check(text, rules_df):
    results = []
    if rules_df is None:
        return results

    for _, row in rules_df.iterrows():
        ng = str(row[1])
        ok = str(row[0])

        if ng in text:
            results.append(f"{ng} → {ok}")

    return results

# =========================
# 番号チェック
# =========================

def number_check(text):
    nums = re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩]", text)
    order = "①②③④⑤⑥⑦⑧⑨⑩"
    results = []

    last = -1
    for n in nums:
        idx = order.index(n)
        if idx != last + 1:
            results.append("番号順の乱れ")
            break
        last = idx

    return results

# =========================
# 実行
# =========================

if st.button("③ チェック実行"):

    if uploaded and rules is not None:

        bytes_data = uploaded.read()

        if uploaded.type == "application/pdf":
            text = ocr_pdf(bytes_data)
        else:
            text = ocr_image(bytes_data)

        st.subheader("抽出テキスト")
        st.text_area("", text, height=200)

        st.subheader("④ チェック結果")

        res = []
        res += hyoki_check(text, rules)
        res += weekday_check(text)
        res += number_check(text)

        if res:
            for r in res:
                st.warning(r)
        else:
            st.success("問題なし")
