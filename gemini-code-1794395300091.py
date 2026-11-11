import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 1. إعداد الاتصال بـ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# ملف الاعتماد الذي ستنزله من Google Developer Console
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# فتح الجدول باسمه
sheet = client.open("أسعار السوق المصري").sheet1

# 2. سحب البيانات من موقع بوابة الأسعار المصرية
url = "http://www.agriprice.gov.eg/local-prices"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# قيم افتراضية للاختبار في حال تغير تصميم الموقع
sugar_price = None
oil_price = None

# البحث عن أسعار السكر والزيت داخل عناصر الصفحة
# يمكنك تعديل النص أو الخلية حسب السلعة المراد قراءتها
rows = soup.find_all('tr')
for row in rows:
    text = row.text
    if 'السكر' in text and not sugar_price:
        # استخراج أول رقم يظهر في الخلية
        words = text.split()
        for w in words:
            if w.replace('.', '', 1).isdigit():
                sugar_price = float(w)
                break
    elif 'زيت' in text and not oil_price:
        words = text.split()
        for w in words:
            if w.replace('.', '', 1).isdigit():
                oil_price = float(w)
                break

# تاريخ اليوم
today_date = datetime.now().strftime("%Y-%m-%d")

# 3. إضافة الصف الجديد في Google Sheets (التاريخ، سعر السكر، سعر الزيت)
if sugar_price or oil_price:
    sheet.append_row([today_date, sugar_price or 0, oil_price or 0])
    print(f"تمت إضافة الأسعار بنجاح: {today_date} - سكر: {sugar_price}ج - زيت: {oil_price}ج")
else:
    print("لم يتم العثور على الأسعار تلقائياً، يرجى التثبت من عناصر الصفحة.")