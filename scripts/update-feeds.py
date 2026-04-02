import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import os

# Configuración
BLOG_RSS = "https://yamilayma.github.io/blog/rss.xml"
POSTS_RSS = "https://yamilayma.github.io/posts/rss.xml"
README_PATH = "README.md"

def fetch_rss(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def format_date(date_str):
    # Formato esperado: Thu, 19 Mar 2026 00:00:00 GMT
    try:
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%d/%m/%Y")
    except:
        return date_str

def get_blog_posts(xml_content):
    if not xml_content: return ""
    root = ET.fromstring(xml_content)
    items = root.findall(".//item")[:4]
    
    lines = []
    for item in items:
        title = item.find("title").text
        link = item.find("link").text
        pub_date = item.find("pubDate").text
        formatted_date = format_date(pub_date)
        # Usamos doble salto de línea y un guion separador
        lines.append(f"- [{title}]({link}) - 🗓️ <i>{formatted_date}</i>")
    
    return "\n\n" + "\n\n".join(lines)

def get_visual_posts(xml_content):
    if not xml_content: return ""
    root = ET.fromstring(xml_content)
    # Namespaces
    ns = {'media': 'http://search.yahoo.com/mrss/'}
    
    items = root.findall(".//item")[:4]
    
    table_content = '<table>\n  <tr>\n'
    for i, item in enumerate(items):
        title = item.find("title").text
        link = item.find("link").text
        media_content = item.find("media:content", ns)
        media_desc = item.find("media:description", ns)
        
        img_url = media_content.get("url") if media_content is not None else ""
        alt_text = media_desc.text if media_desc is not None else title
        
        # Grid 2x2 - Actualizado a 310px de ancho
        table_content += f'    <td align="center" width="50%">\n'
        table_content += f'      <a href="{link}">\n'
        table_content += f'        <img src="{img_url}" alt="{alt_text}" width="310" style="border-radius:10px;" />\n'
        table_content += f'        <br />\n'
        table_content += f'        <sub>{title}</sub>\n'
        table_content += f'      </a>\n'
        table_content += f'    </td>\n'
        
        # New row every 2 items
        if (i + 1) % 2 == 0 and (i + 1) != len(items):
            table_content += '  </tr>\n  <tr>\n'
            
    table_content += '  </tr>\n</table>'
    return table_content

def update_readme(posts_content, blog_content):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update Posts
    posts_pattern = r"(<!-- POST-LIST:START -->).*?(<!-- POST-LIST:END -->)"
    content = re.sub(posts_pattern, f"\\1\n{posts_content}\n\\2", content, flags=re.DOTALL)
    
    # Update Blog
    blog_pattern = r"(<!-- BLOG-LIST:START -->).*?(<!-- BLOG-LIST:END -->)"
    content = re.sub(blog_pattern, f"\\1\n{blog_content}\n\\2", content, flags=re.DOTALL)
    
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    print("Updating RSS feeds...")
    blog_xml = fetch_rss(BLOG_RSS)
    posts_xml = fetch_rss(POSTS_RSS)
    
    blog_md = get_blog_posts(blog_xml)
    posts_html = get_visual_posts(posts_xml)
    
    update_readme(posts_html, blog_md)
    print("README.md updated successfully.")
