import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from draw import draw_clock, draw_sky

USER = "Hyeonju-u"

# 출입증: GitHub 서버에선 있고, 내 맥에선 없음
token = os.environ.get("GITHUB_TOKEN")
headers = {"Authorization": f"Bearer {token}"} if token else {}

# ① 내 저장소 목록 가져오기
repos = requests.get(f"https://api.github.com/users/{USER}/repos", headers=headers).json()

hours = [0] * 24

for r in repos:
    # ② 저장소마다 내 커밋 가져오기
    url = f"https://api.github.com/repos/{r['full_name']}/commits?author={USER}"
    data = requests.get(url, headers=headers).json()

    if type(data) != list:      # 빈 저장소 건너뛰기
        continue

    # ③ 한국 시간으로 바꿔서 세기
    for c in data:
        tm = c["commit"]["author"]["date"]
        kst = datetime.fromisoformat(tm).astimezone(ZoneInfo("Asia/Seoul"))
        hours[kst.hour] = hours[kst.hour] + 1

print(hours)
print(sum(hours), "commits")

# ④ SVG로 저장
with open("commit-clock.svg", "w", encoding="utf-8") as f:
    f.write(draw_clock(hours))

with open("commit-sky.svg", "w", encoding="utf-8") as f:
    f.write(draw_sky(hours))