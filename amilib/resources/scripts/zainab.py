#!/usr/bin/env python3
import os
import re
import subprocess
import time
import webbrowser
import warnings
from bs4 import BeautifulSoup
import networkx as nx
from pyvis.network import Network
import requests

# ==========================
# Step 0: Auto-install basics
# ==========================
def ensure_packages(packages):
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            print(f"📦 Installing {pkg} ...")
            subprocess.check_call(["pip", "install", pkg])

ensure_packages(["beautifulsoup4", "networkx", "pyvis", "requests"])


# ==========================
# Step 1: Input/Output files
# ==========================
input_file = "wg2.html"
output_file = "wg2_cleaned_sorted.html"
book_pdf = "encyclopaedia_book.pdf"
graph_html = "encyclopedia_kg_visual.html"
graphml_path = os.path.join("output", "data", "graph", "encyclopedia_kg.graphml")

# Only create the graph folder — skip PDF extraction folders
os.makedirs(os.path.dirname(graphml_path), exist_ok=True)


warnings.filterwarnings("ignore")

# ==========================
# Step 2: Clean HTML entries
# ==========================
print(f"🔎 Reading {input_file} ...")
with open(input_file, "r", encoding="utf-8") as f:
    html = f.read()

cleaned_html = re.sub(r'<sup[^>]*(cite_ref|reference)[^>]*>.*?</sup>', '', html, flags=re.I | re.S)
soup = BeautifulSoup(cleaned_html, "html.parser")

entries = []
seen = set()

for i, entry in enumerate(soup.find_all("div", attrs={"role": "ami_entry"})):
    term = entry.get("term", "").strip().lower() or f"entry_{i}"
    desc = entry.find("p", class_="wpage_first_para")
    description = desc.get_text(strip=True) if desc else ""
    img = entry.find("img")
    img_src = img["src"] if img and img.has_attr("src") else ""
    key = (description, img_src)
    if key not in seen:
        seen.add(key)
        entries.append((term, entry))

entries.sort(key=lambda x: x[0])

new_soup = BeautifulSoup("""
<html><head><meta charset='utf-8'><base href='https://en.wikipedia.org/wiki/'>
<title>Semantic Encyclopedia</title>
<style>
body { font-family: Georgia, serif; margin: 40px; line-height: 1.6; }
div[role] { border: 1px solid #ccc; margin: 10px; padding: 10px; border-radius: 8px; }
</style></head><body></body></html>
""", "html.parser")

wrapper = new_soup.new_tag("div", role="ami_dictionary", title=output_file)
new_soup.body.append(wrapper)

for _, entry in entries:
    wrapper.append(entry)

for img in wrapper.find_all("img"):
    src = img.get("src", "")
    if src.startswith("//"):
        img["src"] = "https:" + src

with open(output_file, "w", encoding="utf-8") as f:
    f.write(str(new_soup))

print(f"✅ Cleaned & saved: {output_file} ({len(entries)} entries)")

# ==========================
# Step 3: Vivliostyle Preview
# ==========================
print("🌐 Checking Vivliostyle CLI...")
try:
    subprocess.run(["npx", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
except Exception:
    print("📦 Installing Vivliostyle CLI...")
    subprocess.run(["npm", "install", "-g", "@vivliostyle/cli"], stderr=subprocess.DEVNULL)

print("🚀 Launching Vivliostyle in Chromium (book mode)...")
try:
    proc = subprocess.Popen(
        ["npx", "@vivliostyle/cli", "preview", "--browser", "chromium", output_file],
        stderr=subprocess.DEVNULL
    )
    print("✅ Vivliostyle running — close browser when done...")
    proc.wait()
except Exception as e:
    print(f"⚠️ Vivliostyle preview failed: {e}")

# ==========================
# Step 4: PDF Generation
# ==========================
resp = input("\n🖨️ Generate PDF now (headless Chromium)? [Y/n]: ").strip().lower()
if resp in ["", "y", "yes"]:
    print(f"📘 Generating PDF: {book_pdf}")
    try:
        subprocess.run(
            ["npx", "@vivliostyle/cli", "build", output_file, "--output", book_pdf],
            check=True, stderr=subprocess.DEVNULL
        )
        print(f"✅ Saved PDF: {book_pdf}")
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")
else:
    print("⏭️ Skipped PDF generation.")
    if not os.path.exists(book_pdf):
        print(f"ℹ️ Note: {book_pdf} does not exist.")

# ==========================
# Step 4.5: Extract snippets
# ==========================
def extract_html_snippets(html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    html_snippets = {}
    for entry in soup.find_all("div", attrs={"role": "ami_entry"}):
        term = entry.get("term", "").strip()
        if not term:
            continue
        desc = entry.get_text(" ", strip=True)
        desc = re.sub(r"\s+", " ", desc)
        desc = desc[:500] + "..." if len(desc) > 500 else desc
        img_tag = entry.find("img")
        img_src = img_tag["src"] if img_tag and img_tag.has_attr("src") else None
        if img_src and img_src.startswith("//"):
            img_src = "https:" + img_src
        html_snippets[term] = {"text": desc, "image": img_src}
    return html_snippets

print("📖 Extracting snippets from cleaned HTML...")
html_snippets = extract_html_snippets(output_file)
print(f"✅ Extracted {len(html_snippets)} snippets from HTML.")

# ==========================
# Step 5: Build Knowledge Graph
# ==========================
print("🧠 Building knowledge graph...")
with open(output_file, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

entries2 = soup.find_all("div", {"role": "ami_entry"})
if not entries2:
    entries2 = soup.find_all("div", {"term": True})

nodes = {}
href_pattern = re.compile(r"/wiki/([^\"#]+)")

for div in entries2:
    term = (div.get("term") or "").strip()
    if not term:
        continue
    desc_tag = div.find("p") or div.find("div", {"class": "wpage_first_para"})
    desc = desc_tag.get_text(" ", strip=True) if desc_tag else ""
    img_tag = div.find("img")
    img = ""
    if img_tag:
        img = img_tag.get("src") or ""
        if img.startswith("//"):
            img = "https:" + img
    links = []
    for a in div.find_all("a", href=True):
        m = href_pattern.search(a["href"])
        if m:
            links.append(re.sub("_", " ", m.group(1)).strip())
    nodes[term] = {"desc": desc, "img": img, "links": links}

G = nx.Graph()
for term, data in nodes.items():
    G.add_node(term, description=data["desc"], image=data["img"])
for src, data in nodes.items():
    for tgt in data["links"]:
        for k in nodes.keys():
            if k.lower() == tgt.lower():
                G.add_edge(src, k)
                break

isolated = list(nx.isolates(G))
G.remove_nodes_from(isolated)
print(f"🧩 Filtered: {len(G.nodes)} connected nodes, {len(G.edges)} edges")

nx.write_graphml(G, graphml_path)
print(f"✅ Saved graphml: {graphml_path}")

# ==========================
# Step 6: Visualization (Tooltips)
# ==========================
net = Network(height="100vh", width="100%", bgcolor="#000000", font_color="#FFFFFF")

def make_tooltip(term, node_data):
    snippet_info = html_snippets.get(term, {"text": "", "image": None})
    raw_html = snippet_info.get("text", "")
    image = snippet_info.get("image", None)

    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    if not text:
        text = node_data.get("description", "")
    tidy = re.sub(r"\s+", " ", text).strip()
    if len(tidy) > 1200:
        tidy = tidy[:1200].rsplit(".", 1)[0] + "..."

    if image:
        tooltip_html = f"""
        <div style='max-width:420px;color:#fff;font-family:system-ui,Helvetica,Arial;'>
            <img src='{image}' style='max-width:120px;float:right;margin-left:10px;border-radius:4px'>
            <h3 style='margin:0 0 6px;color:#66b2ff;font-size:16px'>{term}</h3>
            <div style='font-size:12px;color:#ddd;line-height:1.4;'>{tidy}</div>
        </div>"""
    else:
        tooltip_html = f"""
        <div style='max-width:420px;color:#fff;font-family:system-ui,Helvetica,Arial;'>
            <h3 style='margin:0 0 6px;color:#66b2ff;font-size:16px'>{term}</h3>
            <div style='font-size:12px;color:#ddd;line-height:1.4;'>{tidy}</div>
        </div>"""
    return tooltip_html

for node, data in G.nodes(data=True):
    deg = len(G[node])
    color = "#00ff99" if deg > 25 else "#66b2ff" if deg > 10 else "#ff9933" if deg > 4 else "#ff5555"
    hover_html = make_tooltip(node, data)
    net.add_node(node, title=hover_html, color=color, size=10 + deg * 0.6)

for src, tgt in G.edges():
    net.add_edge(src, tgt, color="rgba(0,255,255,0.2)", width=0.8)

html_path = os.path.abspath(graph_html)
net.write_html(html_path)

# ==========================
# Step 7: Add Search + Legend
# ==========================
with open(html_path, "r+", encoding="utf-8") as f:
    html_data = f.read()

search_and_legend = """
<!-- 🔍 Search and Legend -->
<style>
#searchBox {
  position: fixed; top: 20px; left: 20px; z-index: 9999;
  background: rgba(0,0,0,0.6); padding: 10px 15px;
  border-radius: 8px; border: 1px solid #66b2ff;
}
#searchInput {
  width: 160px; padding: 5px; border: none; outline: none;
  background: #222; color: #fff; border-radius: 4px;
}
#searchButton {
  padding: 5px 8px; background: #66b2ff; color: #000;
  border: none; border-radius: 4px; cursor: pointer;
}
#legendBox {
  position: fixed; top: 20px; right: 20px; background: rgba(0,0,0,0.6);
  border: 1px solid #66b2ff; border-radius: 8px; padding: 10px 14px;
  z-index: 9999; color: #fff; font-family: system-ui, Helvetica, Arial;
  font-size: 13px; max-width: 200px; line-height: 1.6;
}
.legend-item { display: flex; align-items: center; margin-bottom: 5px; }
.legend-dot { width: 14px; height: 14px; border-radius: 50%; margin-right: 8px; }
.legend-blue { background: #66b2ff; }
.legend-orange { background: #ff9933; }
.legend-red { background: #ff5555; }
.legend-green { background: #00ff99; }
</style>

<div id="searchBox">
  <input id="searchInput" type="text" placeholder="Search node...">
  <button id="searchButton">Go</button>
</div>

<div id="legendBox">
  <div style="font-weight:bold;margin-bottom:5px;">🗺️ Node Colors</div>
  <div class="legend-item"><span class="legend-dot legend-green"></span>Highly Connected Nodes</div>
  <div class="legend-item"><span class="legend-dot legend-blue"></span>Main Topics</div>
  <div class="legend-item"><span class="legend-dot legend-orange"></span>Subfields / Categories</div>
  <div class="legend-item"><span class="legend-dot legend-red"></span>Related Concepts</div>
</div>

<script>
document.getElementById('searchButton').onclick = function() {
  var query = document.getElementById('searchInput').value.trim().toLowerCase();
  if (!query) return;
  var nodes = network.body.data.nodes.get();
  var found = nodes.find(n => n.label.toLowerCase() === query);
  if (found) {
    network.focus(found.id, {scale: 1.5, animation: true});
    network.selectNodes([found.id]);
  }
  document.getElementById('searchInput').value = '';
};
document.getElementById('searchInput').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') document.getElementById('searchButton').click();
});
</script>
"""

html_data = html_data.replace("</body>", search_and_legend + "\n</body>")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_data)

print(f"✅ Graph ready: {html_path}")
print(f"\n🔗 Opening: {html_path}")
try:
    subprocess.run(["open", html_path], check=False)
except Exception:
    webbrowser.open(f"file://{html_path}")