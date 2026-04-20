import math
import re
import time
from urllib.parse import quote_plus

from selenium.webdriver.common.by import By


SEARCH_URL = (
    "https://www.onlinejobs.ph/jobseekers/jobsearch?"
    "jobkeyword={q}&jobtype=0&joblocation_city=&jobpay=&jobpaycriteria=0"
)

CARD_SELECTORS = [
    "div.jobpost-cat-box",
    "div.latest-job-post",
    "div[class*='jobpost']",
    "article",
    "div.row.py-3",
]

TITLE_SELECTORS = [
    "h4 a[href*='/jobseekers/job/']",
    "h4",
    "a[href*='/jobseekers/job/'] h4",
    "a[href*='/jobseekers/job/']",
    "h3",
    ".jobpost-title",
]

_DATE_RE = re.compile(r"(\d+\s+\w+\s+ago|posted\b|yesterday|today|^new$)", re.I)
_BUDGET_RE = re.compile(r"\$[\d,]+|₱[\d,]+|PHP\s*\d", re.I)


def _is_login_page(driver) -> bool:
    url = (driver.current_url or "").lower()
    if "/login" in url or "/signin" in url:
        return True
    try:
        if driver.find_elements(By.CSS_SELECTOR, "input[type='password']"):
            # OJP search works without login — only treat as login if there's no job content
            if not driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobseekers/job/']"):
                return True
    except Exception:
        pass
    return False


def _wait_for_login(driver, search_url: str):
    print("  ! OnlineJobs.ph requires login — log in manually in the Chrome window.")
    print("  ! Waiting 90 seconds for you to log in...")
    time.sleep(90)
    driver.get(search_url)
    time.sleep(4)


def _extract_title(card, selectors, fallback_text: str) -> str:
    for sel in selectors:
        try:
            for el in card.find_elements(By.CSS_SELECTOR, sel):
                t = (el.text or "").strip()
                if t and len(t) >= 8:
                    return t[:200]
        except Exception:
            continue
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

    # Final fallback: job links
    try:
        return driver.find_elements(By.CSS_SELECTOR, "a[href*='/jobseekers/job/']")
    except Exception:
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

        q = quote_plus(kw)
        search_url = SEARCH_URL.format(q=q)

        try:
            driver.get(search_url)
        except Exception as e:
            print(f"  ! OnlineJobs.ph navigation failed for '{kw}': {e}")
            continue

        time.sleep(4)

        if not logged_in and _is_login_page(driver):
            _wait_for_login(driver, search_url)
            logged_in = True
        elif not _is_login_page(driver):
            logged_in = True

        cards = _collect_cards(driver)
        print(f"  OnlineJobs.ph ['{kw}']: found {len(cards)} candidate cards")

        kept_this_kw = 0
        for card in cards:
            if len(results) >= max_jobs or kept_this_kw >= per_kw_cap:
                break
            try:
                text = (card.text or "").strip()
                if len(text) < 50:
                    continue

                link = ""
                try:
                    if card.tag_name.lower() == "a":
                        link = card.get_attribute("href") or ""
                    else:
                        link_el = card.find_element(By.CSS_SELECTOR, "a[href*='/jobseekers/job/']")
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
                m = re.search(r"(?:TBD|\$[\d,]+(?:\.\d+)?|₱[\d,]+|PHP\s*[\d,]+)", text, re.I)
                if m:
                    budget = m.group(0)

                posted = ""
                p = re.search(r"(\d+\s+\w+\s+ago|Yesterday|Today|\w+\s+\d+,\s+\d{4})", text, re.I)
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
                print(f"  ! OnlineJobs.ph card skipped: {e}")
                continue

    return results
