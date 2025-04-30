import json
from patent_claim import build_claim_tree

# Path to your JSON data
JSON_PATH = "patent_status_data/patent_family_set_status.json"
# Output HTML file
OUTPUT_HTML = "patents.html"

# 1) Load your patent data
with open(JSON_PATH, encoding="utf-8") as f:
    patents = json.load(f)

# 2) Map raw status to CSS class
def classify_status(raw_status: str) -> str:
    s = raw_status.lower()
    if "not found" in s:
        return "not-found"
    if "active" in s:
        return "active"
    if any(w in s for w in ["expired", "withdrawn", "ceased", "abandoned"]):
        return "expired"
    return "misc"

# 3) Build HTML head and CSS (including search bar and tooltip styles)
html_head = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Patent Family Status Overview</title>
  <style>
    body {
      font-family: sans-serif;
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
    }
    #searchInput {
      margin: 20px 0;
      padding: 8px;
      width: 100%;
      max-width: 400px;
      font-size: 1em;
    }
    .timeline {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    .entry {
      display: flex;
      align-items: flex-start;
      margin-bottom: 0.5em;
    }
    .marker {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      flex-shrink: 0;
      margin-top: 4px;
      margin-right: 8px;
    }
    .marker.active    { background: #e74c3c; }
    .marker.expired   { background: #27ae60; }
    .marker.misc      { background: #f1c40f; }
    .marker.not-found { background: #7f8c8d; }

    .tooltip {
      position: relative;
      display: inline-block;
      cursor: help;
    }
    .tooltip .tooltiptext {
      visibility: hidden;
      width: 240px;
      background-color: rgba(0,0,0,0.8);
      color: #fff;
      text-align: left;
      border-radius: 4px;
      padding: 8px;
      position: absolute;
      z-index: 1;
      bottom: 100%; /* above the label */
      left: 50%;
      transform: translateX(-50%) translateY(-8px); /* center it horizontally, and nudge up */
      opacity: 0;
      transition: opacity 0.2s;
      white-space: pre-wrap;
      font-family: monospace;
      font-size: 0.9em;
    }
    .tooltip:hover .tooltiptext {
      visibility: visible;
      opacity: 1;
    }
    details {
      margin-left: 20px;
      margin-top: 4px;
    }
    summary {
      cursor: pointer;
      font-weight: bold;
    }
    details p {
      margin: 0.5em 0 0 0;
      white-space: pre-wrap;
      font-family: monospace;
    }
  </style>
</head>
<body>
  <h1>Patent Family Status Overview</h1>
  <input type="text" id="searchInput" placeholder="Search by Patent Number..." />
  <ul class="timeline">"""

# 4) Generate each entry
html_body = []
for p in patents:
    idx = p.get("index", "?")
    num = p.get("patent_number", "N/A")
    raw = p.get("status", "Not Found")
    cls = classify_status(raw)
    title = p.get("title", "<No title>").strip()
    ant = p.get("anticipated_expiration_date", "").strip()
    adj = p.get("adjusted_expiration_date", "").strip()
    claims = build_claim_tree(p.get("claims", "<No claims>"))
    claim_txt = ""
    for root in claims:
        claim_txt += "\n" + root.print_tree()
    link = p.get("link", "<No link>")

    parts = []
    if ant and "not found" not in ant.lower():
        parts.append(f"Anticipated Expiration Date: {ant}")
    if adj and "not found" not in adj.lower():
        parts.append(f"Adjusted Expiration Date: {adj}")
    exp_text = " | ".join(parts) or "Expiration date not found"

    link_html = f'<a href="{link}" target="_blank" rel="noopener noreferrer">{num}</a>' if link and link.startswith("http") else num
    label = f"{idx}: Patent Number: {link_html} | Status: {raw} | Title: {title} | {exp_text}"

    hover_text = (
        f"Index: {idx}\n"
        f"Patent: {num}\n"
        f"Status: {raw}\n"
        f"Title: {title}\n"
        f"{exp_text}"
    )

    abstract = p.get("abstract", "Abstract not found").strip()

    html_body.append(f"""
    <li class="entry"> 
      <span class="marker {cls}"></span>
      <div>
        <span class="tooltip">{label}
          <span class="tooltiptext">{hover_text}</span>
        </span>
        <details>
          <summary>Abstract</summary>
          <p>{abstract}</p>
        </details>
        <details>
          <summary>Claims</summary>
          <p>{claim_txt}</p>
        </details>
      </div>
    </li>""")

# 5) Closing HTML and JS
html_tail = """
  </ul>
  <script>
    document.getElementById("searchInput").addEventListener("input", function () {
      const filter = this.value.toLowerCase();
      const entries = document.querySelectorAll(".entry");
      entries.forEach(entry => {
        const text = entry.textContent.toLowerCase();
        entry.style.display = text.includes(filter) ? "flex" : "none";
      });
    });
  </script>
</body>
</html>"""

# 6) Write output
with open(OUTPUT_HTML, 'w', encoding='utf-8') as out:
    out.write(html_head)
    out.write("\n".join(html_body))
    out.write(html_tail)
