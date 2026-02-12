from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import html
import datetime
import os

def scrape_tier(tier_name, url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # 추세 기록용이므로 창 안 뜨게 설정
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"🌐 [{tier_name}] 데이터 수집 시작...")
        driver.get(url)
        time.sleep(12) 

        element = driver.find_element(By.TAG_NAME, "blz-data-table")
        raw_data = element.get_attribute("allrows")
        
        if raw_data:
            heroes_list = json.loads(html.unescape(raw_data))
            return [{
                "id": item['id'].lower(),
                "name": item['cells']['name'],
                "role": item['hero']['role'],
                "winRate": item['cells']['winrate'],
                "pickRate": item['cells']['pickrate']
            } for item in heroes_list]
        return []
    except Exception as e:
        print(f"  ❌ {tier_name} 에러: {e}")
        return []
    finally:
        driver.quit()

def save_to_history(new_data):
    file_path = 'history.json'
    today = datetime.datetime.now().strftime("%m/%d") # 그래프에 표시하기 좋게 월/일 포맷
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try: history = json.load(f)
            except: history = []
    else: history = []

    # 오늘 데이터 기록
    entry = {"date": today, "data": new_data}
    history = [item for item in history if item['date'] != today] # 중복 방지
    history.append(entry)
    history = history[-30:] # 최근 30일치만 저장

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    print(f"📊 {today} 데이터가 history.json에 기록되었습니다.")

def main():
    base_url = "https://overwatch.blizzard.com/ko-kr/rates/?input=PC&map=all-maps&region=Asia&role=All&rq=2&tier="
    tier_list = ["All", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster", "Champion"]
    
    final_result = {}
    for t in tier_list:
        data = scrape_tier(t, base_url + t)
        final_result[t.lower()] = data
        time.sleep(2)

    # 1. 현재 데이터 저장
    with open('heroes.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=4)
    
    # 2. 추세 데이터 저장
    save_to_history(final_result)
    print("\n🎉 모든 업데이트 완료!")

if __name__ == "__main__":
    main()