#!/usr/bin/env python3
"""Build script: converts posts/*.md → blog/*.html and generates blog/index.html."""

import os
import re
from datetime import datetime
from pathlib import Path

import markdown

POSTS_DIR = Path("posts")
BLOG_DIR = Path("blog")

def parse_frontmatter(text):
    """Parse YAML frontmatter from markdown text (simple regex, no pyyaml)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, text[m.end():]

def post_template(title, date_str, hero_image, content_html):
    hero_tag = f'<img width="720" height="360" src="{hero_image}" alt="" />' if hero_image else ""
    date_tag = f"<time>{date_str}</time>" if date_str else ""
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{title}</title>
    <meta name="title" content="{title}" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="{title}" />
    <meta property="og:image" content="/placeholder-social.jpg" />
    <link rel="stylesheet" href="/style.css" />
    <script src="/mathjax.config.js"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
      const theme = (() => {{
        if (typeof localStorage !== 'undefined' && localStorage.getItem('theme')) return localStorage.getItem('theme');
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
        return 'light';
      }})();
      if (theme === 'dark') document.documentElement.classList.add('dark');
      window.localStorage.setItem('theme', theme);
    </script>
  </head>
  <body>
    <header>
      <h2></h2>
      <nav>
        <button id="themeToggle">
          <svg width="30px" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path class="sun" fill-rule="evenodd" d="M12 17.5a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11zm0 1.5a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm12-7a.8.8 0 0 1-.8.8h-2.4a.8.8 0 0 1 0-1.6h2.4a.8.8 0 0 1 .8.8zM4 12a.8.8 0 0 1-.8.8H.8a.8.8 0 0 1 0-1.6h2.5a.8.8 0 0 1 .8.8zm16.5-8.5a.8.8 0 0 1 0 1l-1.8 1.8a.8.8 0 0 1-1-1l1.7-1.8a.8.8 0 0 1 1 0zM6.3 17.7a.8.8 0 0 1 0 1l-1.7 1.8a.8.8 0 1 1-1-1l1.7-1.8a.8.8 0 0 1 1 0zM12 0a.8.8 0 0 1 .8.8v2.5a.8.8 0 0 1-1.6 0V.8A.8.8 0 0 1 12 0zm0 20a.8.8 0 0 1 .8.8v2.4a.8.8 0 0 1-1.6 0v-2.4a.8.8 0 0 1 .8-.8zM3.5 3.5a.8.8 0 0 1 1 0l1.8 1.8a.8.8 0 1 1-1 1L3.5 4.6a.8.8 0 0 1 0-1zm14.2 14.2a.8.8 0 0 1 1 0l1.8 1.7a.8.8 0 0 1-1 1l-1.8-1.7a.8.8 0 0 1 0-1z"/>
            <path class="moon" fill-rule="evenodd" d="M16.5 6A10.5 10.5 0 0 1 4.7 16.4 8.5 8.5 0 1 0 16.4 4.7l.1 1.3zm-1.7-2a9 9 0 0 1 .2 2 9 9 0 0 1-11 8.8 9.4 9.4 0 0 1-.8-.3c-.4 0-.8.3-.7.7a10 10 0 0 0 .3.8 10 10 0 0 0 9.2 6 10 10 0 0 0 4-19.2 9.7 9.7 0 0 0-.9-.3c-.3-.1-.7.3-.6.7a9 9 0 0 1 .3.8z"/>
          </svg>
        </button>
        <a href="/">Home</a>
        <a href="/about.html">About</a>
        <a href="/blog/">Blog</a>
        <a href="/cv.pdf">CV</a>
        <a href="/publications.html">Publications</a>
      </nav>
    </header>
    <main>
      <article>
        {hero_tag}
        <h1 class="title">{title}</h1>
        {date_tag}
        <hr />
        {content_html}
      </article>
    </main>
    <footer>
      <a href="https://www.github.com/atakaragoz">GitHub</a>
      <a href="https://bsky.app/profile/atabk.bsky.social">Bluesky</a>
      <a href="https://www.linkedin.com/in/ata-b-karagoz">LinkedIn</a>
    </footer>
    <script>
      document.querySelectorAll('nav a').forEach(a => {{
        const path = window.location.pathname;
        const href = a.getAttribute('href');
        if (href === path || href === path.replace(/\\/$/, '') || (href === '/' && (path === '/' || path === '/index.html'))) a.classList.add('active');
      }});
      document.getElementById('themeToggle').addEventListener('click', () => {{
        document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
      }});
    </script>
  </body>
</html>"""

def listing_template(posts_html):
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>Blog</title>
    <meta name="title" content="Blog" />
    <meta name="description" content="Ata Karagoz blog" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="Blog" />
    <meta property="og:description" content="Ata Karagoz blog" />
    <meta property="og:image" content="/placeholder-social.jpg" />
    <link rel="stylesheet" href="/style.css" />
    <script>
      const theme = (() => {{
        if (typeof localStorage !== 'undefined' && localStorage.getItem('theme')) return localStorage.getItem('theme');
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
        return 'light';
      }})();
      if (theme === 'dark') document.documentElement.classList.add('dark');
      window.localStorage.setItem('theme', theme);
    </script>
  </head>
  <body>
    <header>
      <h2></h2>
      <nav>
        <button id="themeToggle">
          <svg width="30px" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path class="sun" fill-rule="evenodd" d="M12 17.5a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11zm0 1.5a7 7 0 1 0 0-14 7 7 0 0 0 0 14zm12-7a.8.8 0 0 1-.8.8h-2.4a.8.8 0 0 1 0-1.6h2.4a.8.8 0 0 1 .8.8zM4 12a.8.8 0 0 1-.8.8H.8a.8.8 0 0 1 0-1.6h2.5a.8.8 0 0 1 .8.8zm16.5-8.5a.8.8 0 0 1 0 1l-1.8 1.8a.8.8 0 0 1-1-1l1.7-1.8a.8.8 0 0 1 1 0zM6.3 17.7a.8.8 0 0 1 0 1l-1.7 1.8a.8.8 0 1 1-1-1l1.7-1.8a.8.8 0 0 1 1 0zM12 0a.8.8 0 0 1 .8.8v2.5a.8.8 0 0 1-1.6 0V.8A.8.8 0 0 1 12 0zm0 20a.8.8 0 0 1 .8.8v2.4a.8.8 0 0 1-1.6 0v-2.4a.8.8 0 0 1 .8-.8zM3.5 3.5a.8.8 0 0 1 1 0l1.8 1.8a.8.8 0 1 1-1 1L3.5 4.6a.8.8 0 0 1 0-1zm14.2 14.2a.8.8 0 0 1 1 0l1.8 1.7a.8.8 0 0 1-1 1l-1.8-1.7a.8.8 0 0 1 0-1z"/>
            <path class="moon" fill-rule="evenodd" d="M16.5 6A10.5 10.5 0 0 1 4.7 16.4 8.5 8.5 0 1 0 16.4 4.7l.1 1.3zm-1.7-2a9 9 0 0 1 .2 2 9 9 0 0 1-11 8.8 9.4 9.4 0 0 1-.8-.3c-.4 0-.8.3-.7.7a10 10 0 0 0 .3.8 10 10 0 0 0 9.2 6 10 10 0 0 0 4-19.2 9.7 9.7 0 0 0-.9-.3c-.3-.1-.7.3-.6.7a9 9 0 0 1 .3.8z"/>
          </svg>
        </button>
        <a href="/">Home</a>
        <a href="/about.html">About</a>
        <a href="/blog/">Blog</a>
        <a href="/cv.pdf">CV</a>
        <a href="/publications.html">Publications</a>
      </nav>
    </header>
    <main>
      <section>
        <ul class="blog-list">
          {posts_html}
        </ul>
      </section>
    </main>
    <footer>
      <a href="https://www.github.com/atakaragoz">GitHub</a>
      <a href="https://bsky.app/profile/atabk.bsky.social">Bluesky</a>
      <a href="https://www.linkedin.com/in/ata-b-karagoz">LinkedIn</a>
    </footer>
    <script>
      document.querySelectorAll('nav a').forEach(a => {{
        const path = window.location.pathname;
        const href = a.getAttribute('href');
        if (href === path || href === path.replace(/\\/$/, '') || (href === '/' && (path === '/' || path === '/index.html'))) a.classList.add('active');
      }});
      document.getElementById('themeToggle').addEventListener('click', () => {{
        document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
      }});
    </script>
  </body>
</html>"""

def build():
    BLOG_DIR.mkdir(exist_ok=True)
    md = markdown.Markdown()
    posts = []

    for md_file in sorted(POSTS_DIR.glob("*.md")):
        text = md_file.read_text()
        meta, body = parse_frontmatter(text)
        title = meta.get("title", md_file.stem)
        pub_date = meta.get("pubDate", "")
        hero = meta.get("heroImage", "")
        slug = md_file.stem

        md.reset()
        content_html = md.convert(body)

        # Parse date for sorting
        try:
            dt = datetime.strptime(pub_date, "%b %d %Y")
        except ValueError:
            try:
                dt = datetime.strptime(pub_date, "%B %d %Y")
            except ValueError:
                dt = datetime(2000, 1, 1)

        # Format date for display
        date_display = dt.strftime("%b %d, %Y") if pub_date else ""

        html = post_template(title, date_display, hero, content_html)
        out_path = BLOG_DIR / f"{slug}.html"
        out_path.write_text(html)
        print(f"  {md_file} -> {out_path}")

        posts.append((dt, title, slug))

    # Sort newest first
    posts.sort(key=lambda x: x[0], reverse=True)

    # Generate listing
    items = []
    for dt, title, slug in posts:
        date_str = dt.strftime("%b %d, %Y")
        items.append(
            f'<li><time datetime="{dt.isoformat()}">{date_str}</time>'
            f'<a href="/blog/{slug}.html">{title}</a></li>'
        )
    listing_html = listing_template("\n          ".join(items))
    listing_path = BLOG_DIR / "index.html"
    listing_path.write_text(listing_html)
    print(f"  -> {listing_path} ({len(posts)} posts)")

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    print("Building blog...")
    build()
    print("Done!")
