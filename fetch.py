import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from draw import draw_clock, draw_sky

USER = "Hyeonju-u"

# 출입증: GitHub 서버에선 있고, 내 맥에선 없음
token = os.environ.get("GITHUB_TOKEN")
headers = {"Authorization": f"Bearer {token}"} if token else {}

def get_all(url):
    """페이지를 넘겨 가며 결과를 전부 모아서 리스트로 돌려준다."""
    results = []
    page = 1
    while True:
        res = requests.get(url, headers=headers,
                           params={"per_page": 100, "page": page}).json()
        if type(res) != list:                        # 리스트가 아니면 = 뭔가 문제
            print("⚠️", url, res.get("message"))      # 무슨 문제인지 출력
            break
        if len(res) == 0:                             # 더 이상 없으면
            break
        results = results + res                       
        if len(res) < 100:                            # 100개 안 찼으면 마지막 페이지
            break
        page = page + 1
    return results

# ① 내 저장소 목록 가져오기
repos = get_all(f"https://api.github.com/users/{USER}/repos")

hours = [0] * 24

for r in repos:
    # ② 저장소마다 내 커밋 가져오기
    url = f"https://api.github.com/repos/{r['full_name']}/commits?author={USER}"
    data = get_all(url)

    # ③ 한국 시간으로 바꿔서 세기
    for c in data:
        tm = c["commit"]["author"]["date"]
        kst = datetime.fromisoformat(tm).astimezone(ZoneInfo("Asia/Seoul"))
        hours[kst.hour] = hours[kst.hour] + 1

print(hours)
print(sum(hours), "commits")
if sum(hours) == 0:
    print("❌ 커밋이 0개라서 SVG를 덮어쓰지 않고 종료")
    raise SystemExit(1)

# ④ SVG로 저장
with open("commit-clock.svg", "w", encoding="utf-8") as f:
    f.write(draw_clock(hours))

with open("commit-sky.svg", "w", encoding="utf-8") as f:
    f.write(draw_sky(hours))