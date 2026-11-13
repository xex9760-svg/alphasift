#!/usr/bin/env python3
"""Run an AlphaSift A-share screen and push the picks to a Telegram bot.

Only the standard library is used for Telegram, so the only dependency is
AlphaSift itself (pip install -e . inside the cloned repo).

Environment variables:
  TELEGRAM_BOT_TOKEN   token from @BotFather
  TELEGRAM_CHAT_ID     your chat id (see README below)
  ALPHASIFT_STRATEGY   optional, default "dual_low"
  ALPHASIFT_MAX_OUTPUT optional, default "10"
  ALPHASIFT_USE_LLM    optional, "1" to enable LLM ranking (needs API key in .env)
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime

STRATEGY = os.environ.get("ALPHASIFT_STRATEGY", "dual_low")
MAX_OUTPUT = os.environ.get("ALPHASIFT_MAX_OUTPUT", "10")
USE_LLM = os.environ.get("ALPHASIFT_USE_LLM", "0") == "1"
TG_LIMIT = 4000  # Telegram hard limit is 4096 chars per message

DISCLAIMER = "仅为量化筛选结果，不构成投资建议。"


def run_screen() -> str:
    cmd = ["alphasift", "screen", STRATEGY, "--max-output", MAX_OUTPUT]
    if not USE_LLM:
        cmd.append("--no-llm")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        raise RuntimeError(f"alphasift failed ({proc.returncode}):\n{proc.stderr[-1500:]}")
    return proc.stdout


def try_parse_json(text: str):
    """Return parsed JSON if stdout contains a JSON object, else None."""
    start = text.find("{")
    if start == -1:
        return None
    try:
        return json.loads(text[start:])
    except json.JSONDecodeError:
        return None


def format_result(data: dict) -> str:
    picks = data.get("picks") or []
    lines = [
        f"📊 AlphaSift 选股 · {data.get('strategy', STRATEGY)}",
        f"{datetime.now():%Y-%m-%d %H:%M}",
        f"全市场 {data.get('snapshot_count', '?')} 只 → 过滤后 {data.get('after_filter_count', '?')} 只",
        "",
    ]
    for p in picks:
        score = p.get("final_score")
        score_txt = f"{score:.1f}" if isinstance(score, (int, float)) else "-"
        price = p.get("price")
        price_txt = f" ¥{price}" if price is not None else ""
        lines.append(f"{p.get('rank', '-')}. {p.get('code', '')} {p.get('name', '')}{price_txt}  得分 {score_txt}")
        if p.get("ranking_reason"):
            lines.append(f"   理由：{p['ranking_reason']}")
        if p.get("risk_summary"):
            lines.append(f"   风险：{p['risk_summary']}")
    if data.get("llm_market_view"):
        lines += ["", f"市场观点：{data['llm_market_view']}"]
    if data.get("degradation"):
        lines += ["", f"⚠️ 数据降级：{data['degradation']}"]
    lines += ["", DISCLAIMER]
    return "\n".join(lines)


def send_telegram(text: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    # split into chunks under the Telegram limit, on line boundaries
    chunks, cur = [], ""
    for line in text.splitlines(keepends=True):
        if len(cur) + len(line) > TG_LIMIT:
            chunks.append(cur)
            cur = ""
        cur += line
    if cur:
        chunks.append(cur)
    for chunk in chunks:
        body = urllib.parse.urlencode({"chat_id": chat_id, "text": chunk}).encode()
        with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=30) as r:
            if r.status != 200:
                raise RuntimeError(f"Telegram returned {r.status}")


def main() -> int:
    try:
        out = run_screen()
        data = try_parse_json(out)
        message = format_result(data) if data else f"📊 AlphaSift · {STRATEGY}\n\n{out.strip()}\n\n{DISCLAIMER}"
    except Exception as exc:  # report failures to Telegram too
        message = f"❌ AlphaSift 运行失败：{exc}"
        try:
            send_telegram(message)
        finally:
            print(message, file=sys.stderr)
        return 1
    send_telegram(message)
    print("sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
