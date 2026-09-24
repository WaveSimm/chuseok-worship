#!/usr/bin/env python3
"""
비밀번호 바꾸기. .env 를 직접 열 필요 없다.

    python setpw.py

물어보는 대로 새 비밀번호를 넣으면
  1) .env 갱신
  2) index.html 에 해시 주입
  3) (원하면) GitHub 에 push 까지 한다.
"""
import io
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
ENV = ROOT / ".env"
KEY = "WORSHIP_PASSWORD"


def current_password():
    if not ENV.exists():
        return ""
    for raw in io.open(ENV, encoding="utf-8"):
        line = raw.strip()
        if line.startswith(KEY + "="):
            return line.split("=", 1)[1].strip()
    return ""


def ask(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n취소했습니다.")
        sys.exit(1)


def run(args):
    sys.stdout.flush()   # 자식 프로세스 출력과 순서가 뒤섞이지 않게
    return subprocess.run(args, cwd=str(ROOT)).returncode == 0


def main():
    print("=" * 46)
    print("  2026 추석 가정예배 — 비밀번호 바꾸기")
    print("=" * 46)

    now = current_password()
    print(f"\n지금 비밀번호: {now or '(없음)'}\n")

    new = ask("새 비밀번호: ")
    if not new:
        print("\n입력이 없어 그대로 둡니다.")
        return
    if new == now:
        print("\n지금과 같은 비밀번호입니다. 그대로 둡니다.")
        return

    again = ask("한 번 더 확인: ")
    if again != new:
        print("\n두 번 입력한 값이 다릅니다. 아무것도 바꾸지 않았습니다.")
        sys.exit(1)

    io.open(ENV, "w", encoding="utf-8", newline="").write(
        "# 실제 비밀번호 (git에 올라가지 않음)\n"
        f"{KEY}={new}\n"
    )
    print(f"\n.env 를 갱신했습니다.")

    if not run([sys.executable, "build.py"]):
        print("build.py 실행에 실패했습니다.")
        sys.exit(1)

    print()
    if ask("GitHub 에 바로 올릴까요? (y/n): ").lower() not in ("y", "yes", "ㅇ"):
        print("\n올리지 않았습니다. 나중에 올리려면:")
        print('  git commit -am "비밀번호 변경" && git push')
        return

    run(["git", "commit", "-am", "비밀번호 변경"])
    if run(["git", "push"]):
        print("\n올렸습니다. 1~2분 뒤 새 비밀번호가 적용됩니다.")
        print("  https://wavesimm.github.io/chuseok-worship/")
    else:
        print("\npush 에 실패했습니다. 인터넷 연결을 확인해 주세요.")


if __name__ == "__main__":
    main()
