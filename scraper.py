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
    options.add_argument("--headless") # 창 안 뜨게 설정
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"🌐 [{tier_name}] 데이터 수집 시도: {url}")
        driver.get(url)
        
        # 블리자드 서버에서 데이터를 완전히 불러올 때까지 충분히 대기 (15초로 상향)
        time.sleep(15) 

        # 데이터가 담긴 커스텀 태그 찾기
        element = driver.find_element(By.TAG_NAME, "blz-data-table")
        raw_data = element.get_attribute("allrows")
        
        if raw_data:
            # HTML 엔티티 제거 및 JSON 변환
            heroes_list = json.loads(html.unescape(raw_data))
            
            # 수집된 데이터가 실제 해당 티어인지 검증을 위해 로그 출력 (선택 사항)
            print(f"   ✅ {tier_name} 수집 성공! (영웅 수: {len(heroes_list)})")
            
            return [{
                "id": item['id'].lower(),
                "name": item['cells']['name'],
                "role": item['hero']['role'].upper(), # roleMap 일치를 위해 대문자 유지
                "winRate": float(item['cells']['winrate']),
                "pickRate": float(item['cells']['pickrate'])
            } for item in heroes_list]
        
        print(f"   ⚠️ {tier_name} 데이터 속성을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"   ❌ {tier_name} 에러 발생: {e}")
        return []
    finally:
        driver.quit()

def save_to_history(new_data):
    file_path = 'history.json'
    today = datetime.datetime.now().strftime("%m/%d")
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                history = json.load(f)
            except:
                history = []
    else:
        history = []

    # 오늘 데이터 기록 (티어별 구조 유지)
    entry = {"date": today, "data": new_data}
    history = [item for item in history if item['date'] != today]
    history.append(entry)
    history = history[-30:] # 최근 30일 데이터만 유지

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    print(f"📊 {today} 추세 데이터 기록 완료.")

def main():
    # URL 파라미터는 반드시 '소문자'여야 블리자드 서버가 인식합니다.
    base_url = "https://overwatch.blizzard.com/ko-kr/rates/?input=PC&map=all-maps&region=Asia&role=All&rq=2&tier="
    
    # 챔피언 티어는 데이터에 따라 'champion' 또는 'champ'일 수 있으나 공식은 'champion'입니다.
    tier_list = ["all", "bronze", "silver", "gold", "platinum", "diamond", "master", "grandmaster", "champion"]
    
    final_result = {}
    
    for t in tier_list:
        # 각 티어별로 개별적인 URL 요청을 보냄
        data = scrape_tier(t, base_url + t)
        
        # 만약 특정 티어 수집에 실패했다면 'all' 데이터를 복사하지 않고 빈 배열로 두어 오류 확인 가능하게 함
        final_result[t] = data
        
        # 연속 요청으로 인한 차단 방지를 위해 티어 간 대기 시간 추가
        time.sleep(5)

    # 1. 현재 데이터 저장 (heroes.json)
    with open('heroes.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=4)
    
    # 2. 히스토리 데이터 저장 (history.json)
    save_to_history(final_result)
    
    print("\n🎉 모든 티어 데이터 수집 및 업데이트 완료!")

if __name__ == "__main__":
    main()
