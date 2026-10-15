"""Build a minimal stats panel from public GitHub repositories and visible activity.

Only public endpoints feed the published snapshot. A token raises API limits but
is sent only to api.github.com, never to the public contribution-calendar page.
Python standard library only; no external image/card service is required.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import os
import re
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USERNAME = 'prblydv'
INK, GREY, BLUE, LIGHT = '#1d1d1f', '#6e6e73', '#0071e3', '#f5f5f7'
FONT = "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"


def api_token():
    token = os.environ.get('GITHUB_TOKEN', '')
    if token:
        return token
    try:
        result = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else ''
    except FileNotFoundError:
        return ''


def read_url(url, token=''):
    headers = {'User-Agent': 'prblydv-public-profile-stats'}
    if url.startswith('https://api.github.com/'):
        headers['Accept'] = 'application/vnd.github+json'
        if token:
            headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read().decode('utf-8')


class PublicCalendar(HTMLParser):
    """Join public calendar dates with their accessible contribution-count labels."""
    def __init__(self):
        super().__init__()
        self.days = {}
        self.counts = {}
        self.tooltip = None
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and attrs.get('data-date') and attrs.get('id'):
            self.days[attrs['id']] = attrs['data-date']
        if tag == 'tool-tip' and attrs.get('for'):
            self.tooltip, self.parts = attrs['for'], []

    def handle_data(self, text):
        if self.tooltip:
            self.parts.append(text)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tooltip:
            text = ''.join(self.parts).strip()
            match = re.match(r'([\d,]+) contributions?\b', text)
            if match:
                self.counts[self.tooltip] = int(match.group(1).replace(',', ''))
            elif text.startswith('No contributions'):
                self.counts[self.tooltip] = 0
            self.tooltip, self.parts = None, []

    def records(self, start, end):
        rows = []
        for identity, day in self.days.items():
            if start <= day <= end:
                if identity not in self.counts:
                    raise ValueError('Public contribution count missing for ' + day)
                rows.append({'date': day, 'count': self.counts[identity]})
        rows.sort(key=lambda row: row['date'])
        expected = (date.fromisoformat(end) - date.fromisoformat(start)).days + 1
        if len(rows) != expected:
            raise ValueError(f'Expected {expected} calendar days; found {len(rows)}')
        return rows


def snapshot(now, token):
    repos, page = [], 1
    while True:
        batch = json.loads(read_url(
            f'https://api.github.com/users/{USERNAME}/repos?type=owner&per_page=100&page={page}', token))
        repos.extend(repo for repo in batch if not repo.get('private', False))
        if len(batch) < 100:
            break
        page += 1
    original = [repo for repo in repos if not repo['fork']]
    # GitHub's language endpoint measures source bytes, not developer proficiency.
    def languages(repo):
        return json.loads(read_url(repo['languages_url'], token))
    totals = Counter()
    with ThreadPoolExecutor(max_workers=6) as executor:
        for values in executor.map(languages, original):
            totals.update(values)
    totals.pop('Jupyter Notebook', None)
    source_bytes = sum(totals.values())
    if source_bytes <= 0:
        raise ValueError('No source-language data returned')
    start, end = f'{now.year}-01-01', now.date().isoformat()
    parser = PublicCalendar()
    parser.feed(read_url(f'https://github.com/users/{USERNAME}/contributions?from={start}&to={end}'))
    days = parser.records(start, end)
    months = Counter()
    for row in days:
        months[row['date'][:7]] += row['count']
    return {
        'username': USERNAME,
        'updated_date_utc': end,
        'period_start': start,
        'period_end': end,
        'public_repositories': len(repos),
        'stars_on_original_public_repositories': sum(repo['stargazers_count'] for repo in original),
        'visible_contributions': sum(row['count'] for row in days),
        'active_days': sum(row['count'] > 0 for row in days),
        'monthly_visible_contributions': [{'month': month, 'count': count} for month, count in sorted(months.items())],
        'languages': [{'name': name, 'bytes': size, 'percent': 100 * size / source_bytes}
                      for name, size in totals.most_common()],
        'scope': 'Activity counts are from the publicly visible GitHub calendar; they are not commit counts. '
                 'Language shares use bytes in original public repositories, excluding Jupyter notebooks. '
                 'Stars exclude forks. Repository count includes public forks. The current month is partial.',
    }


def label(x, y, value, size=13, fill=GREY, weight=400, anchor='start'):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>')


def render(data):
    year = data['period_start'][:4]
    end = date.fromisoformat(data['period_end']).strftime('%d %b %Y')
    s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="title desc">',
         '<title id="title">Public GitHub activity</title>',
         '<desc id="desc">' + escape(f"{data['public_repositories']} public repositories, {data['stars_on_original_public_repositories']} stars, "
             f"{data['visible_contributions']} visible contributions and {data['active_days']} active days in {year} through {end}. "
             'Monthly activity and source-language shares are shown below.') + '</desc>',
         '<rect x=".5" y=".5" width="999" height="389" rx="16" fill="#ffffff" stroke="#e5e5e7"/>']
    metrics = [(32, data['public_repositories'], 'Public repositories'),
               (276, data['stars_on_original_public_repositories'], 'Stars · original repositories'),
               (520, data['visible_contributions'], f'Visible contributions · {year}'),
               (764, data['active_days'], f'Active days · {year}')]
    for x, value, text in metrics:
        s += [label(x, 59, f'{value:,}', 32, INK, 600), label(x, 85, text, 12)]
    s += ['<path d="M32 111H968" stroke="#e5e5e7"/>',
          label(32, 145, 'Monthly contributions', 15, INK, 500),
          label(554, 145, 'Source languages', 15, INK, 500)]
    months = data['monthly_visible_contributions']
    peak = max(1, max(row['count'] for row in months))
    step = 468 / len(months)
    for i, row in enumerate(months):
        x = 32 + i * step + 5
        height = 113 * row['count'] / peak
        width = min(25, step - 10)
        s.append(f'<rect x="{x:.2f}" y="{291-height:.2f}" width="{width:.2f}" height="{height:.2f}" rx="3" fill="{BLUE}"/>')
        month = datetime.strptime(row['month'], '%Y-%m').strftime('%b')
        s += [label(x + width / 2, 312, month, 10, anchor='middle'),
              label(x + width / 2, 280-height, row['count'], 10, anchor='middle')]
    s.append('<path d="M32 292H500" stroke="#e5e5e7"/>')
    # A fixed 0–100% bar scale avoids overstating small language shares.
    for i, row in enumerate(data['languages'][:5]):
        y = 174 + i * 30
        s += [label(554, y, row['name'], 12, INK), label(966, y, f"{row['percent']:.1f}%", 12, anchor='end'),
              f'<rect x="714" y="{y-9}" width="187" height="7" rx="3.5" fill="{LIGHT}"/>',
              f'<rect x="714" y="{y-9}" width="{187*row["percent"]/100:.2f}" height="7" rx="3.5" fill="{BLUE}"/>']
    s += [label(32, 348, f'1 Jan – {end} · current month is partial', 11),
          label(554, 348, 'By source bytes · notebooks and forks excluded', 11),
          label(32, 373, f'Public GitHub data · updated {end}', 10), '</svg>']
    return '\n'.join(s) + '\n'


def main():
    data = snapshot(datetime.now(timezone.utc), api_token())
    svg = render(data)
    destination = ROOT / 'assets'
    destination.mkdir(exist_ok=True)
    (destination / 'github-stats.json').write_text(json.dumps(data, indent=2) + '\n')
    (destination / 'github-stats.svg').write_text(svg)
    print(json.dumps({key: data[key] for key in ['updated_date_utc', 'public_repositories',
          'stars_on_original_public_repositories', 'visible_contributions', 'active_days']}, indent=2))


if __name__ == '__main__':
    main()
