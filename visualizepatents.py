import json
import plotly.graph_objects as go

# Load JSON data
with open("data/US8377085_extended_family_status.json", "r", encoding="utf-8") as file:
    patents = json.load(file)

# Classify status
def classify_status(status):
    status = status.lower()
    if "not found" in status:
        return "Not Found"
    elif "active" in status:
        return "Active"
    elif any(word in status for word in ["expired", "withdrawn", "ceased", "abandoned"]):
        return "Expired"
    else:
        return "Misc"

# Color mapping
status_colors = {
    "Active": "red",
    "Expired": "green",
    "Misc": "yellow",
    "Not Found": "gray"
}

# Prepare data
y_vals = []
colors = []
hover_texts = []
display_texts = []

for i, patent in enumerate(reversed(patents)):  # reversed for top-down layout
    index = patent.get("index", i)
    patent_num = patent.get("patent_number", "N/A")
    raw_status = patent.get("status", "not found")
    status = classify_status(raw_status)
    color = status_colors.get(status, "gray")

    y_vals.append(i)
    colors.append(color)

    # Expiration details
    ant_exp = patent.get("anticipated_expiration_date", "")
    adj_exp = patent.get("adjusted_expiration_date", "")

    exp_parts = []
    if "not found" not in ant_exp.lower():
        exp_parts.append(f"Anticipated Expiration Date: {ant_exp}")
    if "not found" not in adj_exp.lower():
        exp_parts.append(f"Adjusted Expiration Date: {adj_exp}")
    expiration_text = " | ".join(exp_parts) if exp_parts else "Expiration date not found"

    # Label for the point
    label = f"{index}: {patent_num} | {status} | {expiration_text}" if status != "Not Found" else f"{index}: {patent_num} | not found"
    display_texts.append(label)

    # Hover text
    hover = (
        f"<b>Index:</b> {index}<br>"
        f"<b>Patent:</b> {patent_num}<br>"
        f"<b>Status:</b> {raw_status}<br>"
    )
    if status != "Not Found":
        hover += f"<b>{expiration_text}</b>"
    else:
        hover += "<b>Patent details not found</b>"

    hover_texts.append(hover)

# Create figure
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=[0] * len(y_vals),
    y=y_vals,
    mode='markers+text',
    marker=dict(color=colors, size=18),
    text=display_texts,
    textposition="middle right",
    hovertext=hover_texts,
    hoverinfo="text"
))

# Layout settings
fig.update_layout(
    title="Patent Family Status Overview (Hover to View Details)",
    xaxis=dict(visible=False),
    yaxis=dict(
        tickvals=y_vals,
        ticktext=[''] * len(y_vals),
        showgrid=False
    ),
    height=max(500, len(patents) * 60),
    showlegend=False,
    margin=dict(l=130, r=130, t=80, b=50),
    dragmode=False
)

# Export to HTML with selectable text below chart
html_output = fig.to_html(
    include_plotlyjs='cdn',
    config={
        'displayModeBar': False,
        'staticPlot': False
    },
    full_html=False
)

# Add text labels for selection
selectable_text_block = "<div style='margin:30px;font-family:monospace;'>"
selectable_text_block += "<h3>Patent Status List (Selectable)</h3><pre style='white-space:pre-wrap;'>"
selectable_text_block += "\n".join(display_texts)
selectable_text_block += "</pre></div>"

# Combine HTML
final_html = f"""
<html>
<head><meta charset="utf-8"><title>Patent Status Visualization</title></head>
<body>
{html_output}
{selectable_text_block}
</body>
</html>
"""

# Save the combined HTML
with open("patent_status_scrollable_with_text.html", "w", encoding="utf-8") as f:
    f.write(final_html)
