import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ===== 取得する期間 =====
start_date = datetime(2025, 9, 18)
end_date   = datetime(2025, 9, 22)

base_url = "https://www.timeanddate.com/weather/malaysia/kota-kinabalu/historic"
all_records = []

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

    for row in table.find_all("tr"):
        # 時刻は th または最初の td
        time_cell = row.find("th") or row.find("td")
        if not time_cell:
            continue
        time_str = time_cell.get_text(strip=True)

        # 温度は 2列目
        temp_cells = row.find_all("td")
        if len(temp_cells) < 1:
            continue
        temp_str = temp_cells[0].get_text(strip=True)

        temp_value = None
        if "°" in temp_str:
            temp_value = temp_str.split("°")[0]

        if not time_str or ":" not in time_str:
            continue

        all_records.append({
            "date": current_date.strftime("%Y/%-m/%-d"),
            "time": time_str,
            "temperature_C": temp_value
        })

    current_date += timedelta(days=1)

# ===== CSV 出力 =====
df = pd.DataFrame(all_records)
df.to_csv("kota_kinabalu_temp_2025-09-18_to_22.csv", index=False, encoding="utf-8-sig")
print("✅ 完了: kota_kinabalu_temp_2025-09-18_to_22.csv を保存しました。")

