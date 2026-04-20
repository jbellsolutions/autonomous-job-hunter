import math
import re
import time
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By


SEARCH_URL = "https://www.upwork.com/nx/search/jobs/?q={q}&sort=recency"

CARD_SELECTORS = [
    "article[data-test='JobTile']",
    "article[data-test='job-tile']",
    "section[data-test='JobTile']",
    "div[data-test='job-tile']",
    "article.job-tile",
    "article",
]

TITLE_SELECTORS = [
    "a[data-test='job-tile-title-link']",
    "a[data-test='job-title-link']",
    "h2 a[href*='/jobs/']",
    "h3 a[href*='/jobs/']",
    "h2.job-tile-title a",
    "[data-test='JobTileHeader'] a",
]

_DATE_RE = re.compile(r"(\d+\s+\w+\s+ago|posted\b|yesterday|today|^new$)", re.I)
_BUDGET_RE = re.compile(r"\$[\d,]+|₱[\d,]+|PHP\s*\d", re.I)


def _is_login_page(driver) -> bool:
    url = (driver.current_url or "").lower()
    if "/login" in url or "/ab/account-security/login" in url:
        return True
    try:
        if driver.find_elements(By.CSS_SELECTOR, "input[name='login[username]']"):
            return True
    except Exception:
        pass
    return False


def _wait_for_login(driver, search_url: str):
    print("  ! Upwork requires login — log in manually in the Chrome window.")
    print("  ! Waiting 90 seconds for you to log in...")
    time.sleep(90)
    driver.get(search_url)
    time.sleep(4)


def _skip_low_rate(text: str) -> bool:
    t = text.lower()
    low_hourly = re.search(r"\$[0-4](\.\d+)?\s*(?:/|-|\s|hr|hour)", t)
    if low_hourly:
        return True
    return False


def _extract_title(card, selectors, fallback_text: str) -> str:
    for sel in selectors:
        try:
            for el in card.find_elements(By.CSS_SELECTOR, sel):
                t = (el.text or "").strip()
                if t and len(t) >= 8:
                    return t[:200]
        except Exception:
            continue
    # Line-filtering fallback: drop date/budget/short lines, take first clean line
    for line in fallback_text.split("\n"):
        s = line.strip()
        if len(s) < 8:
            continue
        if _DATE_RE.search(s) or _BUDGET_RE.search(s):
            continue
        return s[:200]
    return "Untitled Job"


def _collect_cards(driver):
    for _ in range(3):
        try:
            driver.execute_script("window.scrollBy(0, 800)")
        except Exception:
            break
        time.sleep(1.5)

    for selector in CARD_SELECTORS:
        try:
            found = driver.find_elements(By.CSS_SELECTOR, selector)
        except Exception:
            found = []
        if len(found) >= 2:
            return found
    return []


def scrape(driver, config: dict, max_jobs: int = 5) -> list[dict]:
    keywords = config.get("keywords") or ["AI automation"]
    per_kw_cap = max(2, math.ceil(max_jobs / len(keywords)) + 1)

    results: list[dict] = []
    seen_links = set()
    logged_in = False

    for kw in keywords:
        if len(results) >= max_jobs:
            break

        search_url = SEARCH_URL.format(q=quote_plus(kw))
        try:
            driver.get(search_url)
        except Exception as e:
            print(f"  ! Upwork navigation failed for '{kw}': {e}")
            continue

        time.sleep(4)

        if not logged_in and _is_login_page(driver):
            _wait_for_login(driver, search_url)
            logged_in = True
        elif not _is_login_page(driver):
            logged_in = True

        cards = _collect_cards(driver)
        print(f"  Upwork ['{kw}']: found {len(cards)} candidate cards")

        kept_this_kw = 0
        for card in cards:
            if len(results) >= max_jobs or kept_this_kw >= per_kw_cap:
                break
            try:
                text = (card.text or "").strip()
                if len(text) < 50:
                    continue
                if _skip_low_rate(text):
                    continue

                link = ""
                try:
                    link_el = card.find_element(By.CSS_SELECTOR, "a[href*='/jobs/']")
                    link = link_el.get_attribute("href") or ""
                except Exception:
                    try:
                        link_el = card.find_element(By.TAG_NAME, "a")
                        link = link_el.get_attribute("href") or ""
                    except Exception:
                        link = driver.current_url

                if not link or link in seen_links:
                    continue
                seen_links.add(link)

                title = _extract_title(card, TITLE_SELECTORS, text)

                lines = [l.strip() for l in text.split("\n") if l.strip()]
                description = "\n".join(lines[:15])

                budget = ""
                m = re.search(r"\$[\d,]+(?:\.\d+)?(?:\s*-\s*\$[\d,]+(?:\.\d+)?)?(?:\s*/\s*hr)?", text)
                if m:
                    budget = m.group(0)

                posted = ""
                p = re.search(r"(\d+\s+\w+\s+ago|Posted\s+[^\n]+|Yesterday|Today)", text, re.I)
                if p:
                    posted = p.group(0)

                results.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "budget": budget,
                    "posted_date": posted,
                })
                kept_this_kw += 1
            except Exception as e:
                print(f"  ! Upwork card skipped: {e}")
                continue

    return results
