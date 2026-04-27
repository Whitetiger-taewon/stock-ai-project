import json
import re
import os
import random
import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# [설정] 페이지 기본 구성
st.set_page_config(page_title="Stock-AI AX: 실시간 AI 변곡점 리포트", layout="wide")

# --- 1. 데이터 및 유틸리티 함수 ---

def get_scanning_list():
    """target_stocks.txt 파일을 읽어 전체 분석 대상 종목을 가져옵니다."""
    default_scan = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차"}
    try:
        if os.path.exists("target_stocks.txt"):
            with open("target_stocks.txt", "r", encoding="utf-8") as f:
                new_scan = {}
                for line in f.readlines():
                    if ':' in line:
                        code, name = line.strip().split(':')
                        new_scan[code.strip()] = name.strip()
                return new_scan if new_scan else default_scan
    except:
        pass
    return default_scan

def get_past_targets():
    """지난주 추천 종목을 읽어오되, 파일이 없으면 전체 풀에서 랜덤 3개를 선정합니다."""
    # 1. 확정된 지난주 성과 파일 확인
    try:
        if os.path.exists("past_recommend_results.txt"):
            with open("past_recommend_results.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    target_dict = {}
                    for item in content.split(','):
                        code, name = item.split(':')
                        target_dict[code.strip()] = name.strip()
                    return target_dict
    except:
        pass

    # 2. 파일 부재 시, target_stocks.txt에서 랜덤 3개 추출
    full_list = get_scanning_list()
    if len(full_list) >= 3:
        # 딕셔너리를 리스트로 변환 후 랜덤 샘플링
        keys = random.sample(list(full_list.keys()), 3)
        return {k: full_list[k] for k in keys}
    
    return full_list

@st.cache_data(ttl=3600)
def fetch_real_data(codes):
    """주식 종목의 실시간 수익률 성과를 계산합니다."""
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

@st.cache_data(ttl=3600)
def fetch_realtime_recommendations():
    """실시간 시장 스캐닝을 통해 상위 3개 종목을 추출합니다."""
    scan_list = get_scanning_list()
    analysis_results = []
    kst_today = datetime.utcnow() + timedelta(hours=9)
    start_date = (kst_today - timedelta(days=10)).strftime('%Y-%m-%d')
    
    for code, name in scan_list.items():
        try:
            df = fdr.DataReader(code, start_date)
            if not df.empty and len(df) >= 2:
                curr_price = df.iloc[-1]['Close']
                prev_price = df.iloc[-2]['Close']
                change_rate = ((curr_price - prev_price) / prev_price) * 100
                analysis_results.append({
                    "종목명": name,
                    "현재가": f"{curr_price:,.0f}원",
                    "상태": "강한 수급" if change_rate > 0.5
