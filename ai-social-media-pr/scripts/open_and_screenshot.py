#!/usr/bin/env python3
"""
打开达人主页 URL，检查是否已登录；未登录则提示用户登录后按回车再截图。
登录完成后对当前页面截图并保存。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 确保可导入项目根模块
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="打开 URL，检查登录，截图保存")
    parser.add_argument("url", type=str, help="达人主页 URL，如 https://www.douyin.com/user/xxx")
    parser.add_argument("-o", "--output", type=str, default="screenshot.png", help="截图保存路径")
    parser.add_argument("--headless", action="store_true", help="无头模式（不检查登录，直接截图）")
    parser.add_argument("--timeout", type=float, default=30, help="页面加载等待秒数")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("请安装: pip install playwright && playwright install chromium")
        sys.exit(1)

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        try:
            page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"打开页面失败: {e}")
            browser.close()
            sys.exit(1)

        if not args.headless:
            # 简单登录检查：页面上是否出现“登录”按钮（未登录时常见）
            try:
                login_btn = page.locator("text=登录").first
                if login_btn.is_visible(timeout=2000):
                    print("检测到未登录（存在「登录」按钮）。请在浏览器中完成登录，完成后在此按回车继续...")
                    input()
            except Exception:
                pass
            print("正在截图...")
        else:
            print("无头模式：直接截图（不进行登录检查）。")

        page.screenshot(path=str(output_path), full_page=True)
        browser.close()

    print(f"截图已保存: {output_path}")


if __name__ == "__main__":
    main()
