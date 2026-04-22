import json
import re
import os
import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# [설정] 페이지 기본 구성
st.set_page_config(page_title="Stock-AI AX: AI 파동 분석 리포트", layout="wide")

# --- 1. 유틸리티 함수 ---

def get_past_targets():
    """지난주 추천 종목 리스트를 파일에서 읽어옵니다."""
    # 파일이 없을 때 보여줄 기본값 (초기 세팅용)
    default_targets = {"000660": "SK하이닉스", "005380": "현대차", "035420": "NAVER"}
    
    try:
        # 파일 형식 예: 000660:SK하이닉스,005380:현대차
        if os.path.exists("past_recommend_results.txt"):
            with open("past_recommend_results.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    target_dict = {}
                    for item in content.split(','):
                        code, name = item.split(':')
                        target_dict[code.strip()] = name.strip()
                    return target_dict
    except Exception:
        pass
    return default_targets

def save_to_google_sheet(name, email):
    """구독자 정보를 구글 시트에 저장합니다."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        raw_json = st.secrets["gcp_service_account_json"]
        clean_json = re.sub(r'[\x00-\x1F\x7F]', '', raw_json) 
        
        try:
            service_account_info = json.loads(clean_json)
        except Exception:
            service_account_info = json.loads(raw_json.strip())
        
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Stock-AI_Subscribers").sheet1
        
        kst_now = datetime.utcnow() + timedelta(hours=9)
        now_str = kst_now.strftime("%Y-%m-%d %H:%M:%S")
        
        sheet.append_row([now_str, name, email])
        return True
    except Exception as e:
        st.error(f"시트 연동 에러: {e}")
        return False

@st.cache_data(ttl=3600)
def fetch_real_data(codes):
    """주식 종목의 실시간 수익률을 가져옵니다."""
    results = []
    kst_today = datetime.utcnow() + timedelta(hours=9)
    end_date = kst_today.strftime('%Y-%m-%d')
    start_date = (kst_today - timedelta(days=14)).strftime('%Y-%m-%d')
    
    for code, name in codes.items():
        try:
            df = fdr.DataReader(code, start_date, end_date)
            if not df.empty and len(df) >= 5:
                prev_close = df.iloc[-5]['Close'] 
                curr_close = df.iloc[-1]['Close'] 
                change = ((curr_close - prev_close) / prev_close) * 100
                results.append({'name': name, 'curr': curr_close, 'change': change})
        except:
            continue
    return results

# --- 2. UI 구현부 ---

st.title("🚀 Stock-AI AX")
st.subheader("12년 IT 전문가의 인사이트와 AI의 결합, '진짜' 변곡점을 배달합니다.")
st.write("단순한 종목 추천이 아닙니다. 엘리어트 파동과 RSI 필터링을 거친 AX 솔루션입니다.")
st.divider()

# B. 실시간 성과 대역 (지난주 추천 종목 기반)
st.subheader("📊 지난주 AI 추천 종목 실시간 성과")
past_targets = get_past_targets()
real_perf = fetch_real_data(past_targets)

if real_perf:
    cols = st.columns(len(real_perf))
    for i, item in enumerate(real_perf):
        cols[i].metric(
            label=item['name'], 
            value=f"{item['curr']:,.0f}원", 
            delta=f"{item['change']:.2f}% (지난 리포트 대비)"
        )
else:
    st.info("성과 데이터를 불러오는 중입니다...")
st.divider()

# C. 이번 주 추천 미리보기 & 구독 섹션
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.subheader("🎯 이번 주 AI 분석 TOP 3 (실시간)")
    
    if os.path.exists("recommend_results.txt"):
        try:
            with open("recommend_results.txt", "r", encoding="utf-8") as f:
                rec_content = f.read()
            st.success("✅ 현재 AI 엔진이 분석한 최신 타점 정보입니다.")
            st.markdown(f"```text\n{rec_content}\n```")
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")
    else:
        st.info("🔍 차기 리포트 분석 및 데이터 생성 중입니다.")
        # 데이터 생성 전 보여줄 전문적인 테이블
        upcoming_data = [
            {"종목명": "두산에너빌리티", "상태": "데이터 수집", "예상타점": "계산 중"},
            {"종목명": "삼성SDI", "상태": "RSI 필터링", "예상타점": "계산 중"},
            {"종목명": "한화오션", "상태": "파동 분석", "예상타점": "계산 중"}
        ]
        st.table(pd.DataFrame(upcoming_data))
        
    st.caption("💡 매주 월요일 아침, 상세 차트 분석 리포트가 구독자에게 발송됩니다.")

with col_right:
    st.subheader("📩 리포트 무료 구독")
    with st.container(border=True):
        st.write("전문가급 HTML 분석 리포트를 받아보세요.")
        u_name = st.text_input("성함", placeholder="홍길동")
        u_email = st.text_input("이메일", placeholder="example@gmail.com")
        
        if st.button("지금 바로 구독 신청", use_container_width=True):
            if u_name and u_email:
                if save_to_google_sheet(u_name, u_email):
                    st.success(f"🎉 {u_name}님, 구독 완료! 월요일 아침에 뵙겠습니다.")
                    st.balloons()
            else:
                st.warning("정보를 모두 입력해주세요.")

# D. 푸터
kst_now = datetime.utcnow() + timedelta(hours=9)
st.sidebar.info(f"📍 KST: {kst_now.strftime('%Y-%m-%d %H:%M')} 기준 갱신")
st.sidebar.write("본 서비스는 **AX(AI Transformation)** 기술을 활용한 자산관리 보조 도구입니다.")
