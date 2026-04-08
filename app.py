import streamlit as st
import json, os, base64

st.set_page_config(layout="wide")

# =========================
# 🔐 허용된 사용자
# =========================
ALLOWED_USERS = [
    "dlehdgus3","rlarufdl","rladuswl2","shehrbs",
    "qkralwjd1","rlagmlwls2","didtjfl","dlaudrhks","dlawlsgh"
]

# =========================
# 상태
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
if "page" not in st.session_state:
    st.session_state.page="login"
if "selected_customer" not in st.session_state:
    st.session_state.selected_customer=None

# =========================
# 데이터
# =========================
def load_data(uid):
    path=f"data/{uid}.json"
    if os.path.exists(path):
        return json.load(open(path,"r",encoding="utf-8"))
    return []

def save_data(uid,data):
    os.makedirs("data",exist_ok=True)
    json.dump(data,open(f"data/{uid}.json","w",encoding="utf-8"),
              ensure_ascii=False,indent=2)

# =========================
# 로그인
# =========================
def login():
    st.title("🔐 보험 분석 시스템")

    uid=st.text_input("아이디")
    pw=st.text_input("비밀번호",type="password")

    if st.button("로그인"):
        if uid in ALLOWED_USERS and uid == pw:
            st.session_state.logged_in=True
            st.session_state.user_id=uid
            st.session_state.page="list"
            st.rerun()
        else:
            st.error("허용되지 않은 계정이거나 비밀번호가 일치하지 않습니다")

# =========================
# 고객 목록
# =========================
def list_page():
    st.title(f"📂 고객 목록 ({st.session_state.user_id})")

    data=load_data(st.session_state.user_id)

    if st.button("➕ 신규 고객 등록"):
        st.session_state.selected_customer=None
        st.session_state.page="editor"
        st.rerun()

    st.divider()

    if not data:
        st.info("저장된 고객이 없습니다.")
        return

    for i,c in enumerate(data):
        col1,col2=st.columns([4,1])
        with col1:
            st.write(f"👤 {c['name']} ({c.get('birth','')}) / {c['premium']:,}원")
        with col2:
            if st.button("열기",key=f"open{i}"):
                st.session_state.selected_customer=i
                st.session_state.page="editor"
                st.rerun()

# =========================
# 평가
# =========================
def check(u,s):
    if u == 0:
        return "✖"
    elif u >= s:
        return "●"
    elif u > 0:
        return "▲"

def img64(f):
    return base64.b64encode(f.getvalue()).decode() if f else None

# =========================
# HTML
# =========================
def make_html(results,name,birth,premium,opinion,img):

    op=opinion.replace("\n","<br>")
    all_items=sum(results.values(),[])
    g=sum(1 for r in all_items if r["적정도"]=="●")
    m=sum(1 for r in all_items if r["적정도"]=="▲")
    b=sum(1 for r in all_items if r["적정도"]=="✖")

    html=f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    body {{font-family:'Malgun Gothic';width:210mm;margin:auto;padding:20px;background:#f4f6f9}}
    .card {{background:white;padding:15px;margin-bottom:10px;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,0.05)}}
    .header {{display:flex;justify-content:space-between}}
    .title {{font-size:24px;font-weight:bold}}
    .summary span {{margin-right:10px;font-size:20px;font-weight:bold}}
    .blue {{color:#007bff}} .orange {{color:#f0ad4e}} .red {{color:#d9534f}}

    table {{width:100%;border-collapse:collapse;table-layout:fixed;margin-top:10px}}
    th, td {{border:1px solid #ddd;font-size:11px;padding:4px;text-align:center}}
    th {{background:#eef2f7}}
    .left {{background:#f7f7f7;font-weight:bold}}
    img {{width:150px;border-radius:8px}}

    .notice {{
        margin-top:20px;
        font-size:11px;
        color:#666;
        background:#fff3cd;
        padding:10px;
        border-radius:8px;
        line-height:1.6;
    }}
    </style>
    </head>

    <body>

    <div class="card header">
        <div>
            <div class="title">보험 보장 분석 리포트</div>
            <div>{name} ({birth}) / 월보험료 {premium:,}원</div>
            <div class="summary">
                <span class="blue">● {g}</span>
                <span class="orange">▲ {m}</span>
                <span class="red">✖ {b}</span>
            </div>
        </div>
        <div>{("<img src='data:image/png;base64,"+img+"'/>") if img else ""}</div>
    </div>
    """

    for cat,items in results.items():
        col_count=len(items)+1
        width=100/col_count

        html+=f"<div class='card'><b>{cat}</b><table>"
        html+="<colgroup>"+"".join([f"<col style='width:{width}%'>" for _ in range(col_count)])+"</colgroup>"

        html+="<tr><th></th>"+"".join(f"<th>{r['항목']}</th>" for r in items)+"</tr>"
        html+="<tr><td class='left'>보장</td>"+"".join(f"<td>{r['내 금액']}</td>" for r in items)+"</tr>"
        html+="<tr><td class='left'>기준</td>"+"".join(f"<td>{r['기준 금액']}</td>" for r in items)+"</tr>"
        html+="<tr><td class='left'>평가</td>"+"".join(
            f"<td style='color:{'#007bff' if r['적정도']=='●' else '#f0ad4e' if r['적정도']=='▲' else '#d9534f'};font-weight:bold'>{r['적정도']}</td>"
            for r in items)+"</tr>"

        html+="</table></div>"

    html+=f"<div class='card'><b>설계사 의견</b><br><br>{op}</div>"

    # ✅ ⭐ 면책 문구 추가
    html+=f"""
    <div class="notice">
    ※ 본 자료는 보험상품 가입을 권유하거나 자문을 제공하기 위한 것이 아닙니다.<br>
    ※ 일반적인 기준에 따른 참고용 분석 자료이며, 계약 체결 여부는 고객님의 판단과 책임 하에 결정됩니다.<br>
    ※ 실제 보장 내용은 보험약관 및 계약 내용에 따라 달라질 수 있습니다.
    </div>
    """

    html+="</body></html>"
    return html

# =========================
# 메인
# =========================
def editor():

    st.title("📊 보험 보장 분석 리포트")

    uid=st.session_state.user_id
    data=load_data(uid)
    idx=st.session_state.selected_customer

    if idx is not None:
        c=data[idx]
        d_user=c["data"]
        d_std=c["std"]
        name=c["name"]
        birth=c.get("birth","")
        premium=c["premium"]
        opinion=c.get("opinion","")
    else:
        d_user={}
        d_std={}
        name=""
        birth=""
        premium=0
        opinion=""

    col1,col2,col3=st.columns(3)
    with col1:
        name=st.text_input("고객명",name)
    with col2:
        birth=st.text_input("생년월일",birth)
    with col3:
        premium=st.number_input("월 보험료",value=premium)

    opinion=st.text_area("설계사 의견",opinion)
    file=st.file_uploader("명함",type=["png","jpg"])

    categories = {
        "사망/장해": ["일반사망","질병사망","상해사망","상해후유장해","질병후유장해"],
        "진단": ["일반암진단비","유사암진단비","뇌혈관진단비","뇌경색진단비","뇌출혈진단비","허혈성심장질환진단비","급성심근경색진단비"],
        "치료/수술": ["암주요치료비","뇌심 주요치료비","질병수술비","질병종수술비","뇌혈관질환 수술비","심장질환 수술비","상해수술비","상해종수술비"],
        "실손/기타": ["질병실비","상해실비","질병간병인일당","상해간병인일당","질병간호간병통합서비스 일당","상해간호간병통합서비스 일당","골절진단비","자동차사고부상치료비","교통사고처리지원금","벌금","변호사선임비","일상생활배상책임"]
    }

    std_values={}
    user_values={}

    st.header("📥 기준금액")
    for cat,items in categories.items():
        st.subheader(cat)
        cols=st.columns(3)
        for i,item in enumerate(items):
            with cols[i%3]:
                std_values[item]=st.number_input(item,key=f"std_{item}_{idx}",value=d_std.get(item,0))

    st.header("📥 내 보장")
    for cat,items in categories.items():
        st.subheader(cat)
        cols=st.columns(3)
        for i,item in enumerate(items):
            with cols[i%3]:
                user_values[item]=st.number_input(item,key=f"user_{item}_{idx}",value=d_user.get(item,0))

    colA, colB, colC = st.columns(3)

    with colA:
        if st.button("💾 저장"):
            new={"name":name,"birth":birth,"premium":premium,
                 "data":user_values,"std":std_values,"opinion":opinion}
            if idx is None:
                data.append(new)
            else:
                data[idx]=new
            save_data(uid,data)
            st.success("저장 완료")

    with colB:
        if st.button("📊 분석하기"):
            results={}
            for cat,items in categories.items():
                results[cat]=[]
                for item in items:
                    results[cat].append({
                        "항목":item,
                        "내 금액":user_values[item],
                        "기준 금액":std_values[item],
                        "적정도":check(user_values[item],std_values[item])
                    })

            html=make_html(results,name,birth,premium,opinion,img64(file))
            st.download_button("📄 리포트 다운로드",html,"report.html")

    with colC:
        if st.button("📂 목록"):
            st.session_state.page="list"
            st.rerun()

# 실행
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.page=="list":
        list_page()
    else:
        editor()
