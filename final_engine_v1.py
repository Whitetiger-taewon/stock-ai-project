import FinanceDataReader as fdr
from scipy.signal import find_peaks
import pandas as pd
from datetime import datetime, timedelta
import time

def analyze_stock(stock_code, stock_name):
    try:
        # 1. 데이터 수집 (최근 1년)
        df = fdr.DataReader(stock_code, (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
        if len(df) < 100: return None

        # 2. 변곡점 추출
        peaks, _ = find_peaks(df['High'], distance=20)
        troughs, _ = find_peaks(-df['Low'], distance=20)
        pts = pd.concat([pd.Series(peaks), pd.Series(troughs)]).sort_values()
        wave_points = df.iloc[pts]

        if len(wave_points) < 5: return None
        
        # 최근 5개 변곡점의 종가 데이터
        p = wave_points.tail(5)['Close'].values
        p1, p2, p3, p4, p5 = p[0], p[1], p[2], p[3], p[4]

        # 3. 엘리어트 파동 간소화 규칙 검증
        rule1 = p2 > p1 * 0.95 # 저점 관리
        rule2 = (p4 - p3) > (p2 - p1) # 3파의 힘

        if rule1 and rule2:
            # 4. 피보나치 매수 타점 계산 (최근 고점과 저점 사이의 61.8% 되돌림)
            recent_high = max(p3, p5)
            recent_low = p4
            diff = recent_high - recent_low
            buy_target = recent_high - (diff * 0.618) # 61.8% 되돌림 지점
            
            return {
                '종목명': stock_name,
                '현재가': p5,
                '매수권장가': round(buy_target),
                '상태': '상승3파 감지'
            }
    except:
        return None
    return None

# --- 메인 실행부 ---
print("--- [Stock-AI KR] KOSPI 상위 종목 스캔 시작 ---")
kospi_list = fdr.StockListing('KOSPI').head(50) # 시간 관계상 상위 50개만 우선 테스트
recommend_list = []

for index, row in kospi_list.iterrows():
    print(f"분석 중: {row['Name']}...", end='\r')
    result = analyze_stock(row['Code'], row['Name'])
    if result:
        recommend_list.append(result)
    time.sleep(0.1) # 서버 과부하 방지

print("\n" + "="*50)
print(f"스캔 완료! 추천 후보 종목: {len(recommend_list)}개")
print("="*50)

# 파일 저장을 위한 준비
save_lines = []

for rec in recommend_list:
    line_info = f"[{rec['종목명']}] 현재가: {rec['현재가']:,}원 | ★매수타점: {rec['매수권장가']:,}원"
    print(line_info) # 화면 출력
    save_lines.append(line_info) # 저장용 리스트에 담기

# 텍스트 파일로 한 줄씩 저장
with open("recommend_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(save_lines))

print("\n✅ 추천 종목 리스트가 파일로 저장되었습니다.")