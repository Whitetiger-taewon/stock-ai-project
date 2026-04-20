import smtplib
import os
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

# [설정] 본부장님의 계정 정보
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 465
SENDER_EMAIL = "dmstjq2534@naver.com"
# GitHub Secrets에 저장한 변수명을 가져옵니다.
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') 

def get_subscribers():
    """CSV에서 구독자 정보를 읽어옵니다."""
    sub_list = [{"name": "본부장님(관리자)", "email": "dmstjq2534@gmail.com"}]
    if os.path.exists("subscribers.csv"):
        try:
            # Streamlit에서 저장한 형식: 일시, 이름, 이메일
            df = pd.read_csv("subscribers.csv", names=['time', 'name', 'email'], header=None)
            for _, row in df.iterrows():
                if pd.notnull(row['email']) and "@" in str(row['email']):
                    sub_list.append({"name": str(row['name']), "email": str(row['email']).strip()})
        except Exception as e:
            print(f"⚠️ 명단 로딩 중 오류: {e}")
    return sub_list

def send_newsletter():
    subscribers = get_subscribers()
    print(f"🚀 총 {len(subscribers)}명에게 리포트 발송을 시작합니다.")

    # 추천 결과 텍스트 확보
    recommend_text = ""
    if os.path.exists("recommend_results.txt"):
        with open("recommend_results.txt", "r", encoding="utf-8") as f:
            recommend_text = f.read()

    # 생성된 차트 이미지들 확보
    charts = [f for f in os.listdir() if f.startswith('chart_') and f.endswith('.png')]

    for sub in subscribers:
        try:
            msg = MIMEMultipart('related')
            msg['Subject'] = f"📈 [Stock-AI AX] {sub['name']}님, 이번 주 AI 추천 종목입니다."
            msg['From'] = SENDER_EMAIL
            msg['To'] = sub['email']

            # HTML 레이아웃 (반응형)
            html_body = f"""
            <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #007bff;">🚀 Stock-AI AX 리포트</h2>
                    <p>안녕하세요 <b>{sub['name']}</b>님, 인공지능이 분석한 이번 주 변곡점 리포트입니다.</p>
                    <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        {recommend_text.replace('\n', '<br>')}
                    </div>
            """
            for i, _ in enumerate(charts):
                html_body += f"""
                <div style="margin-top: 25px; text-align: center;">
                    <img src="cid:chart_{i}" style="width: 100%; border-radius: 10px;">
                </div>"""

            html_body += """<p style="text-align: center; font-size: 11px; color: #999; margin-top: 30px;">
                본 메일은 구독 신청자에 한해 발송됩니다. © 2026 Stock-AI AX Lab.</p></div></body></html>"""

            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            for i, chart_file in enumerate(charts):
                with open(chart_file, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<chart_{i}>')
                    msg.attach(img)

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, sub['email'], msg.as_string())
            print(f"✅ 발송 성공: {sub['email']}")
        except Exception as e:
            print(f"❌ 발송 실패({sub['email']}): {e}")

if __name__ == "__main__":
    send_newsletter()
