import smtplib
import os
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

# 1. [환경 설정]
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 465
SENDER_EMAIL = "dmstjq2534@naver.com"
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') # 보안을 위해 환경변수 권장
RECEIVER_DEFAULT = "dmstjq2534@gmail.com" # 기본 수신인

def get_subscribers():
    """subscribers.csv 파일을 읽어 구독자 리스트 반환"""
    sub_list = [{"name": "본부장님", "email": RECEIVER_DEFAULT}] # 관리자 포함
    
    if os.path.exists("subscribers.csv"):
        try:
            # CSV 읽기 (app_v2.py 저장 형식: 일시, 성함, 이메일)
            df = pd.read_csv("subscribers.csv", names=['date', 'name', 'email'], header=None)
            for _, row in df.iterrows():
                # 데이터 유효성 확인 후 추가
                if pd.notnull(row['email']) and "@" in str(row['email']):
                    sub_list.append({"name": str(row['name']), "email": str(row['email']).strip()})
        except Exception as e:
            print(f"⚠️ 구독자 명단 로딩 중 오류: {e}")
    return sub_list

def send_newsletter():
    subscribers = get_subscribers()
    print(f"🚀 총 {len(subscribers)}명의 구독자에게 발송을 시작합니다.")

    # 분석 결과 텍스트 파일 읽기
    recommend_text = ""
    if os.path.exists("recommend_results.txt"):
        with open("recommend_results.txt", "r", encoding="utf-8") as f:
            recommend_text = f.read()

    # 차트 이미지 파일 리스트 확보
    charts = [f for f in os.listdir() if f.startswith('chart_') and f.endswith('.png')]

    for sub in subscribers:
        try:
            msg = MIMEMultipart('related')
            msg['Subject'] = f"🚀 [Stock-AI] {sub['name']}님을 위한 이번 주 AI 분석 리포트"
            msg['From'] = SENDER_EMAIL
            msg['To'] = sub['email']

            # HTML 레이아웃 구성
            html_body = f"""
            <html>
            <body style="font-family: 'Apple SD Gothic Neo', sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #007bff;">📈 Stock-AI AX 리포트</h2>
                    <p>안녕하세요, <b>{sub['name']}</b>님! AI가 분석한 이번 주 시장의 맥점입니다.</p>
                    <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid #007bff; margin: 20px 0;">
                        {recommend_text.replace('\n', '<br>')}
                    </div>
            """

            # 차트 이미지 삽입 로직
            for i, chart_file in enumerate(charts):
                html_body += f"""
                <div style="text-align: center; margin-top: 30px;">
                    <p style="font-weight: bold; color: #555;">[분석 차트 #{i+1}]</p>
                    <img src="cid:image{i}" style="width: 100%; max-width: 500px; border-radius: 8px;">
                </div>
                """

            html_body += """
                    <p style="font-size: 12px; color: #999; margin-top: 40px; text-align: center;">
                        본 메일은 구독 신청하신 분들께 발송되는 자동 리포트입니다.<br>
                        © 2026 Stock-AI AX Lab. All rights reserved.
                    </p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # 이미지 파일 첨부 (CID 매핑)
            for i, chart_file in enumerate(charts):
                with open(chart_file, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<image{i}>')
                    msg.attach(img)

            # 실제 발송
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, sub['email'], msg.as_string())
            
            print(f"✅ 발송 완료: {sub['name']} ({sub['email']})")

        except Exception as e:
            print(f"❌ 발송 실패 ({sub['email']}): {e}")

if __name__ == "__main__":
    if not SENDER_PASSWORD:
        print("❌ 오류: SENDER_PASSWORD 환경변수가 설정되지 않았습니다.")
    else:
        send_newsletter()
