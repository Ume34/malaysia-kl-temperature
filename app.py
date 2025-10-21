import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ===== 取得する期間をリストで指定 =====
periods = [
    (datetime(2025, 9, 3), datetime(2025, 9, 11)),
    (datetime(2025, 9, 25), datetime(2025, 10, 4))
]

base_url = "https://www.timeanddate.com/weather/malaysia/kuala-lumpur/historic"
all_records = []

for start_date, end_date in periods:
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        day = current_date.day

        print(f"📅 {year}-{month:02d}-{day:02d} のデータを取得中...")

        params = {
            "month": month,
            "year": year,
            "hd": f"{year}{month:02d}{day:02d}"
        }

        try:
            res = requests.get(base_url, params=params, timeout=30)
            res.raise_for_status()
        except Exception as e:
            print(f"❌ 取得失敗: {e}")
            current_date += timedelta(days=1)
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", {"id": "wt-his"})

        if not table:
            print(f"⚠️ {year}-{month:02d}-{day:02d} のデータが見つかりません。")
            current_date += timedelta(days=1)
            continue

        # 行ごとに抽出
        for row in table.find_all("tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) < 2:
                continue
            time_str = cols[0]
            temp_str = cols[1]

            temp_value = None
            if "°" in temp_str:
                temp_value = temp_str.split("°")[0]

            all_records.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "time": time_str,
                "temperature_C": temp_value
            })

        current_date += timedelta(days=1)

# ===== CSV出力 =====
df = pd.DataFrame(all_records)
df.to_csv("kuala_lumpur_temp_2025-09-03_to_10-04.csv", index=False, encoding="utf-8-sig")
print("✅ 完了: kuala_lumpur_temp_2025-09-03_to_10-04.csv を保存しました。")
