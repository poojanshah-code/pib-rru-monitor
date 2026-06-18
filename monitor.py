import feedparser
import smtplib
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

KEYWORDS = ["RRU", "Rashtriya Raksha University"]

PIB_FEEDS = [
    "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
    "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=0",
    "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=17",
    "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=22",
]

SENDER = os.environ["EMAIL_SENDER"]
PASSWORD = os.environ["EMAIL_PASSWORD"]
RECIPIENT = os.environ["EMAIL_RECIPIENT"]

def matches(text):
    t = text.upper()
    for kw in KEYWORDS:
        if kw.upper() in t:
            return kw
    return None

def send_email(items):
    rows = ""
    for item in items:
        rows += f"""
        <tr>
          <td style="padding:12px 8px;border-bottom:1px solid #e5e7eb;">
            <a href="{item['link']}" style="color:#1d4ed8;font-weight:600;text-decoration:none;">{item['title']}</a><br>
            <span style="font-size:12px;color:#6b7280;">Keyword: <b>{item['keyword']}</b> &nbsp;|&nbsp; {item['published']}</span>
            {"<p style='margin:6px 0 0;font-size:13px;color:#374151;'>" + item['summary'][:250] + "…</p>" if item['summary'] else ""}
          </td>
        </tr>"""

    html = f"""
<html><body style="font-family:Arial,sans-serif;background:#f3f4f6;padding:24px;">
  <div style="max-width:620px;margin:auto;background:#fff;border-radius:8px;overflow:hidden;">
    <div style="background:#1e3a5f;padding:20px 24px;">
      <h2 style="margin:0;color:#fff;">🇮🇳 PIB India — RRU Alert</h2>
      <p style="margin:4px 0 0;color:#93c5fd;font-size:13px;">{len(items)} new release(s) · {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
    </div>
    <div style="padding:16px 24px;">
      <table width="100%">{rows}</table>
    </div>
    <div style="background:#f9fafb;padding:14px 24px;border-top:1px solid #e5e7eb;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">Source: pib.gov.in · Keywords: RRU, Rashtriya Raksha University</p>
    </div>
  </div>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔔 PIB Alert: {len(items)} RRU Press Release(s) — {datetime.now().strftime('%d %b %Y')}"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.starttls()
        s.login(SENDER, PASSWORD)
        s.sendmail(SENDER, RECIPIENT, msg.as_string())
    print(f"✅ Email sent with {len(items)} match(es)")

def run():
    matches_found = []
    seen_links = set()

    for url in PIB_FEEDS:
        print(f"Checking: {url}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                link = entry.get("link", entry.get("id", ""))
                if link in seen_links:
                    continue
                seen_links.add(link)
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                kw = matches(f"{title} {summary}")
                if kw:
                    print(f"🎯 Match [{kw}]: {title}")
                    matches_found.append({
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "keyword": kw,
                        "published": entry.get("published", "N/A"),
                    })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    if matches_found:
        send_email(matches_found)
    else:
        print("No RRU matches found.")

if __name__ == "__main__":
    run()
