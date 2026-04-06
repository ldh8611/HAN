import streamlit as st
import base64

st.set_page_config(layout="wide")

st.title("📊 보험 보장 분석 리포트")

# 고객 정보
col1, col2 = st.columns(2)
with col1:
    customer_name = st.text_input("고객명", "홍길동")
with col2:
    monthly_premium = st.number_input("월 보험료(원)", 0, value=200000)

# 설계사 의견
opinion = st.text_area("설계사 의견", "고객님께 필요한 보장 중심으로 보완을 권장드립니다.")

# 명함 업로드
uploaded_file = st.file_uploader("명함 이미지 업로드", type=["png", "jpg", "jpeg"])

# 기준금액
default_std = {
    "일반사망":10000,"질병사망":10000,"상해사망":10000,
    "상해후유장해":10000,"질병후유장해":3000,

    "일반암진단비":5000,"유사암진단비":1000,
    "뇌혈관진단비":2000,"뇌경색진단비":3000,"뇌출혈진단비":5000,
    "허혈성심장질환진단비":2000,"급성심근경색진단비":5000,

    "암주요치료비":2000,"뇌심 주요치료비":1000,
    "질병수술비":50,"질병종수술비":1000,
    "뇌혈관질환 수술비":1000,"심장질환 수술비":1000,
    "상해수술비":100,"상해종수술비":1000,

    "질병실비":5000,"상해실비":5000,

    "질병간병인일당":1,"상해간병인일당":1,
    "질병간호간병통합서비스 일당":7,"상해간호간병통합서비스 일당":7,

    "골절진단비":50,"자동차사고부상치료비":30,
    "교통사고처리지원금":20000,"벌금":3000,
    "변호사선임비":3000,"일상생활배상책임":10000
}

categories = {
    "사망/장해": ["일반사망","질병사망","상해사망","상해후유장해","질병후유장해"],
    "진단": [
        "일반암진단비","유사암진단비",
        "뇌혈관진단비","뇌경색진단비","뇌출혈진단비",
        "허혈성심장질환진단비","급성심근경색진단비"
    ],
    "치료/수술": [
        "암주요치료비","뇌심 주요치료비",
        "질병수술비","질병종수술비",
        "뇌혈관질환 수술비","심장질환 수술비",
        "상해수술비","상해종수술비"
    ],
    "실손/기타": [
        "질병실비","상해실비",
        "질병간병인일당","상해간병인일당",
        "질병간호간병통합서비스 일당","상해간호간병통합서비스 일당",
        "골절진단비","자동차사고부상치료비",
        "교통사고처리지원금","벌금","변호사선임비","일상생활배상책임"
    ]
}

std_values = {}
user_values = {}

# 입력
st.header("📥 기준금액 입력 (단위: 만원)")
for cat, items in categories.items():
    st.subheader(cat)
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i % 3]:
            std_values[item] = st.number_input(
                item, 0, step=10,
                value=default_std.get(item, 0),
                key=f"std_{item}"
            )

st.header("📥 내 보장 입력 (단위: 만원)")
for cat, items in categories.items():
    st.subheader(cat)
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i % 3]:
            user_values[item] = st.number_input(item, 0, step=10, key=f"user_{item}")

def check(user, std):
    if user == 0:
        return "✖"
    elif user >= std:
        return "●"
    else:
        return "▲"

def image_to_base64(uploaded_file):
    if uploaded_file:
        return base64.b64encode(uploaded_file.read()).decode()
    return None

def generate_html(results_by_cat, name, premium, opinion, image_base64):

    formatted_opinion = opinion.replace("\n", "<br>")

    all_items = sum(results_by_cat.values(), [])
    good = sum(1 for r in all_items if r["적정도"]=="●")
    mid = sum(1 for r in all_items if r["적정도"]=="▲")
    bad = sum(1 for r in all_items if r["적정도"]=="✖")

    html = f"""
    <html><head><meta charset="utf-8">
    <style>
    body {{ font-family:'Malgun Gothic'; position:relative; }}
    .title {{ font-size:24px; font-weight:bold; }}

    .summary {{ font-size:22px; font-weight:bold; margin-top:5px; }}
    .blue {{ color:#007bff; }}
    .orange {{ color:#f0ad4e; }}
    .red {{ color:#d9534f; }}

    .header {{ background:#bfe3e6; padding:6px; font-weight:bold; }}

    table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
    th, td {{ border:1px solid #ccc; font-size:11px; text-align:center; padding:4px; }}
    .left {{ background:#f0f0f0; font-weight:bold; }}

    .opinion {{ border:1px solid #ccc; padding:10px; margin-top:20px; line-height:1.6; }}

    .card-img {{ position:absolute; bottom:20px; right:20px; width:200px; }}
    </style>
    </head><body>

    <div class="title">한장으로 보는 보장현황</div>
    <div>{name} / 월보험료 {premium:,}원 (단위: 만원)</div>

    <div class="summary">
        <span class="blue">● {good}</span>
        <span class="orange">▲ {mid}</span>
        <span class="red">✖ {bad}</span>
    </div>
    """

    for cat, items in results_by_cat.items():

        html += f"<div class='header'>{cat}</div><table>"

        html += "<tr><th></th>" + "".join([f"<th>{r['항목']}</th>" for r in items]) + "</tr>"
        html += "<tr><td class='left'>보장</td>" + "".join([f"<td>{r['내 금액']:,}</td>" for r in items]) + "</tr>"
        html += "<tr><td class='left'>기준금액</td>" + "".join([f"<td>{r['기준 금액']:,}</td>" for r in items]) + "</tr>"
        html += "<tr><td class='left'>적정도</td>" + "".join([
            f"<td style='color:{'#007bff' if r['적정도']=='●' else '#f0ad4e' if r['적정도']=='▲' else '#d9534f'}; font-size:16px; font-weight:bold'>{r['적정도']}</td>"
            for r in items]) + "</tr>"

        html += "</table><br>"

        if cat == "실손/기타":
            html += "<div style='font-size:10px;'>※ 기준금액은 현재 나이에 필요한 권장 보장금액입니다 (단위: 만원)</div>"

    html += f"""
    <div class="opinion">
    <b>설계사 의견</b><br><br>
    {formatted_opinion}
    </div>
    """

    if image_base64:
        html += f"<img class='card-img' src='data:image/png;base64,{image_base64}'/>"

    html += "</body></html>"
    return html

# 실행
if st.button("📊 분석하기"):

    results_by_cat = {}

    for cat, items in categories.items():
        results_by_cat[cat] = []
        for item in items:
            results_by_cat[cat].append({
                "항목":item,
                "내 금액":user_values[item],
                "기준 금액":std_values[item],
                "적정도":check(user_values[item], std_values[item])
            })

    img_base64 = image_to_base64(uploaded_file)
    html = generate_html(results_by_cat, customer_name, monthly_premium, opinion, img_base64)

    # ✅ HTML 다운로드 (배포용 핵심)
    st.download_button(
        "📄 리포트 다운로드",
        html,
        file_name="보험보장리포트.html"
    )

    st.success("다운로드 후 'Ctrl + P → PDF 저장' 하시면 됩니다 👍")
