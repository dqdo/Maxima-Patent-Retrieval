import json

from patent_claim import build_claim_tree

# Path to your JSON data_Lens
JSON_PATH = "patent_status_data/patent_family_set_status.json"
# Output HTML file
OUTPUT_HTML = "patents.html"

# 1) Load your patent data_Lens
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

# 3) Build HTML head and CSS (including tooltip styles with dynamic left-side positioning)
html_head = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Patent Family Status Overview</title>
  <style>
    body {
      font-family: sans-serif;
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
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

    /* Tooltip container */
    .tooltip {
      position: relative;
      display: inline-block;
      cursor: help;
    }
    /* Tooltip text positioned directly to the left with a small margin */
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
      top: 50%;
      right: 100%;          /* align right edge to parent */
      margin-right: 8px;    /* small gap */
      transform: translateY(-50%);
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
  <ul class=\"timeline\">"""

# 4) Generate each entry with tooltip hover and collapsible abstract
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
        claim_txt = claim_txt + "\n" +  root.print_tree()


    # expiration text
    parts = []
    if ant and "not found" not in ant.lower():
        parts.append(f"Anticipated Expiration Date: {ant}")
    if adj and "not found" not in adj.lower():
        parts.append(f"Adjusted Expiration Date: {adj}")
    exp_text = " | ".join(parts) or "Expiration date not found"

    # label and hover text
    label = f"{idx}: Patent Number: {num} | Status: {raw} | Title: {title} | {exp_text}"
    hover_text = (
        f"Index: {idx}\n"
        f"Patent: {num}\n"
        f"Status: {raw}\n"
        f"Title: {title}\n"
        f"{exp_text}"
    )

    abstract = p.get("abstract", "Abstract not found").strip()

    html_body.append(f"""
    <li class=\"entry\"> 
      <span class=\"marker {cls}\"></span>
      <div>
        <span class=\"tooltip\">{label}
          <span class=\"tooltiptext\">{hover_text}</span>
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
    </li>"""
    )

# 5) Close out HTML
html_tail = """
  </ul>
</body>
</html>"""

# 6) Write to file
with open(OUTPUT_HTML, 'w', encoding='utf-8') as out:
    out.write(html_head)
    out.write("\n".join(html_body))
    out.write(html_tail)

print(f"✅ Generated '{OUTPUT_HTML}' with left‐side hover tooltips and collapsible abstracts.")