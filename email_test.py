import smtplib
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime, timedelta # timedelta 추가

# [설정]
SMTP_SERVER = "smtp.naver.com"
SMTP_PORT = 465
SENDER_EMAIL = "dmstjq2534@naver.com"
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') 

def get_subscribers():
    # 1. 기본 관리자 리스트 (항상 본부장님께는 가도록 설정)
    sub_list = [{"name": "본부장님(관리자)", "email": "dmstjq2534@gmail.com"}]
    
    try:
        # 2. GitHub Secrets에 저장한 JSON 키 로드
        gcp_json = os.environ.get('GCP_SERVICE_ACCOUNT_JSON')
        if not gcp_json:
            print("⚠️ GCP_SERVICE_ACCOUNT_JSON 설정이 없습니다. 기본 리스트로 진행합니다.")
            return sub_list
            
        gcp_info = json.loads(gcp_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(gcp_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # 3. 구글 시트 열기
        sheet = client.open("Stock-AI_Subscribers").sheet1
        
        # 4. 시트 데이터 로드
        records = sheet.get_all_records()
        for row in records:
            # 시트의 헤더명(name, email)과 반드시 일치해야 합니다.
            name = str(row.get('name', '구독자')).strip()
            email = str(row.get('email', '')).strip()
            if "@" in email:
                # 중복 발송 방지를 위해 관리자 이메일과 겹치지 않을 때만 추가
                if email != "dmstjq2534@gmail.com":
                    sub_list.append({"name": name, "email": email})
        
        print(f"✅ 구글 시트에서 {len(sub_list)-1}명의 구독자를 성공적으로 불러왔습니다.")
        
    except Exception as e:
        print(f"❌ 구글 시트 로딩 중 에러 발생: {e}")
        
    return sub_list

def send_newsletter():
    # 한국 시간 설정
    kst_now = datetime.utcnow() + timedelta(hours=9)
    current_date = kst_now.strftime("%Y-%m-%d")
    
    subscribers = get_subscribers()
    
    recommend_text = ""
    if os.path.exists("recommend_results.txt"):
        with open("recommend_results.txt", "r", encoding="utf-8") as f:
            recommend_text = f.read().replace('\n', '<br>')

    charts = [f for f in os.listdir() if f.startswith('chart_') and f.endswith('.png')]

    for sub in subscribers:
        try:
            msg = MIMEMultipart('related')
            # 제목에 한국 날짜 적용
            msg['Subject'] = f"[Stock-AI AX] {current_date} 리포트: {sub['name']}님 변곡점 분석결과"
            msg['From'] = SENDER_EMAIL
            msg['To'] = sub['email']

            html_content = f"""
            <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #007bff;">🚀 Stock-AI AX 리포트 ({current_date})</h2>
                    <p>안녕하세요 <b>{sub['name']}</b>님, AI가 분석한 이번 주 변곡점 정보입니다.</p>
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
                        본 리포트는 IT 전문가의 AX 기술을 활용한 투자 참고용 데이터입니다.<br>
                        결과에 대한 책임은 투자자 본인에게 있습니다.<br>
                        © 2026 Stock-AI AX Lab.
                    </p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

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
