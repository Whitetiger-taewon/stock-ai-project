import smtplib
import os
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

# [설정]
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 465
SENDER_EMAIL = "dmstjq2534@naver.com"
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') 

def get_subscribers():
    sub_list = [{"name": "본부장님(관리자)", "email": "dmstjq2534@gmail.com"}]
    if os.path.exists("subscribers.csv"):
        try:
            df = pd.read_csv("subscribers.csv", names=['time', 'name', 'email'], header=None)
            for _, row in df.iterrows():
                if pd.notnull(row['email']) and "@" in str(row['email']):
                    sub_list.append({"name": str(row['name']), "email": str(row['email']).strip()})
        except:
            pass
    return sub_list

def send_newsletter():
    subscribers = get_subscribers()
    
    recommend_text = ""
    if os.path.exists("recommend_results.txt"):
        with open("recommend_results.txt", "r", encoding="utf-8") as f:
            # 에러 방지: f-string 밖에서 미리 <br>로 변환해둡니다.
            recommend_text = f.read().replace('\n', '<br>')

    charts = [f for f in os.listdir() if f.startswith('chart_') and f.endswith('.png')]

    for sub in subscribers:
        try:
            msg = MIMEMultipart('related')
            msg['Subject'] = f"📈 [Stock-AI AX] {sub['name']}님을 위한 AI 변곡점 리포트"
            msg['From'] = SENDER_EMAIL
            msg['To'] = sub['email']

            # 에러가 났던 f-string 부분을 안전하게 구성
            html_content = f"""
            <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #007bff;">🚀 Stock-AI AX 리포트</h2>
                    <p>안녕하세요 <b>{sub['name']}</b>님, AI가 분석한 이번 주 종목입니다.</p>
                    <div style="background: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        {recommend_text}
                    </div>
            """
            
            for i, _ in enumerate(charts):
                html_content += f"""
                <div style="margin-top: 25px; text-align: center;">
                    <p style="color: #666; font-size: 13px;">[AI 분석 차트 이미지]</p>
                    <img src="cid:chart_{i}" style="width: 100%; border-radius: 10px; border: 1px solid #ddd;">
                </div>"""

            html_content += """
                    <p style="text-align: center; font-size: 11px; color: #999; margin-top: 30px;">
                        본 리포트는 투자 참고용이며 결과에 대한 책임은 본인에게 있습니다.<br>
                        © 2026 Stock-AI AX Lab.
                    </p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 이미지 첨부 로직
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
    if SENDER_PASSWORD:
        send_newsletter()
    else:
        print("❌ SENDER_PASSWORD가 설정되지 않았습니다.")
