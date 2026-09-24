#!/usr/bin/env python3
"""
.env 의 WORSHIP_PASSWORD 를 읽어 SHA-256 해시를 index.html 에 주입한다.

GitHub Pages 는 서버가 없어 .env 를 런타임에 읽을 수 없다.
그래서 배포 전에 이 스크립트를 한 번 돌려 해시를 파일에 박아 넣는다.
평문 비밀번호는 .env 에만 있고 git 에는 올라가지 않는다.

    python build.py
"""
import hashlib
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV = ROOT / ".env"
HTML = ROOT / "index.html"
KEY = "WORSHIP_PASSWORD"


def read_env(path):
    """아주 단순한 .env 파서. KEY=VALUE, # 주석, 양끝 따옴표 처리."""
    values = {}
    for raw in io.open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        values[k.strip()] = v
    return values


def main():
    if not ENV.exists():
        sys.exit(
            ".env 가 없습니다.\n"
            "  cp .env.example .env   로 만든 뒤 비밀번호를 적어주세요."
        )

    env = read_env(ENV)
    password = env.get(KEY, "")

    if not password:
        sys.exit(f".env 에 {KEY} 값이 비어 있습니다.")
    if password == "바꿔주세요":
        sys.exit(f".env 의 {KEY} 가 아직 샘플 값입니다. 실제 비밀번호로 바꿔주세요.")

    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()

    html = io.open(HTML, encoding="utf-8").read()
    pattern = r"(const PASS_HASH = ')[0-9a-f]{64}(';)"
    if not re.search(pattern, html):
        sys.exit("index.html 에서 PASS_HASH 줄을 찾지 못했습니다.")

    new_html, n = re.subn(pattern, r"\g<1>" + digest + r"\g<2>", html)
    if n != 1:
        sys.exit(f"PASS_HASH 줄이 {n}개 발견되어 중단했습니다.")

    if new_html == html:
        print(f"이미 최신입니다. (해시 {digest[:12]}...)")
        return

    io.open(HTML, "w", encoding="utf-8", newline="").write(new_html)
    print(f"index.html 에 해시를 주입했습니다. ({digest[:12]}...)")
    print("이제 git commit && git push 하면 배포됩니다.")


if __name__ == "__main__":
    main()
