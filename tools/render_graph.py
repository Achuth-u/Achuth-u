"""
Futuristic Cyberpunk Contribution Graph Renderer.

Reads `assets/contributions.json` and renders an animated SVG contribution graph `graph.svg`
with rounded cells, blue cyber palette, summary metrics, and sequential column animations.

Output: graph.svg
"""

import json
import os
from datetime import datetime

# Configuration Constants
INPUT_JSON_PATH = os.path.join("assets", "contributions.json")
OUTPUT_SVG_PATH = "graph.svg"

# Palette Constants (Cyberpunk Blue Theme)
COLOR_BG = "#0d1117"
COLOR_CARD_BG = "#161b22"
COLOR_BORDER = "#30363d"
COLOR_TEXT_PRIMARY = "#c9d1d9"
COLOR_TEXT_SECONDARY = "#8b949e"
COLOR_BLUE_ACCENT = "#58A6FF"
COLOR_BLUE_GLOW = "#3BA8FF"

# Level Colors (0: None -> 4: Peak)
LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e3860",
    2: "#11589c",
    3: "#1f6feb",
    4: "#3ba8ff",
}


def load_contribution_data(filepath: str) -> dict:
    """
    Load contribution JSON payload, running scraper fallback if missing.

    Args:
        filepath (str): JSON file path.

    Returns:
        dict: Data payload with metrics and daily contributions list.
    """
    if not os.path.exists(filepath):
        print(f"[!] {filepath} not found. Triggering contribution pull...")
        from pull_contributions import main as pull_main
        pull_main()

    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def build_month_labels(daily_data: list[dict], cell_size: float, cell_gap: float) -> list[tuple[str, float]]:
    """
    Compute x-coordinates for month labels above the calendar grid.

    Args:
        daily_data (list[dict]): Daily contribution records.
        cell_size (float): Width of each day square.
        cell_gap (float): Spacing between day squares.

    Returns:
        list[tuple[str, float]]: List of (month_name, x_position) tuples.
    """
    month_labels = []
    last_month = None

    for idx, item in enumerate(daily_data):
        date_obj = datetime.strptime(item["date"], "%Y-%m-%d")
        month_str = date_obj.strftime("%b")
        week_idx = idx // 7

        if month_str != last_month:
            x_pos = week_idx * (cell_size + cell_gap)
            month_labels.append((month_str, x_pos))
            last_month = month_str

    return month_labels


def generate_graph_svg(data: dict, output_path: str) -> None:
    """
    Build and write animated graph.svg.

    Args:
        data (dict): Contribution payload dict.
        output_path (str): SVG output file path.
    """
    metrics = data.get("metrics", {"total_contributions": 0, "current_streak": 0, "longest_streak": 0})
    daily_list = data.get("contributions", [])

    svg_width = 820
    svg_height = 230

    cell_size = 10.5
    cell_gap = 3.5
    grid_start_x = 35.0
    grid_start_y = 105.0

    # 1. Render Metric Summary Cards
    cards_html = f"""
    <!-- Metric Cards Header -->
    <g transform="translate(20, 15)">
      <!-- Card 1: Total Contributions -->
      <rect x="0" y="0" width="245" height="52" rx="8" ry="8" fill="{COLOR_CARD_BG}" stroke="{COLOR_BORDER}" stroke-width="1"/>
      <text x="16" y="22" font-family="'Courier New', monospace" font-size="11" fill="{COLOR_TEXT_SECONDARY}">TOTAL CONTRIBUTIONS</text>
      <text x="16" y="42" font-family="'Courier New', monospace" font-size="18" font-weight="700" fill="{COLOR_BLUE_GLOW}">{metrics.get('total_contributions', 0):,}</text>

      <!-- Card 2: Current Streak -->
      <rect x="260" y="0" width="245" height="52" rx="8" ry="8" fill="{COLOR_CARD_BG}" stroke="{COLOR_BORDER}" stroke-width="1"/>
      <text x="276" y="22" font-family="'Courier New', monospace" font-size="11" fill="{COLOR_TEXT_SECONDARY}">CURRENT STREAK</text>
      <text x="276" y="42" font-family="'Courier New', monospace" font-size="18" font-weight="700" fill="#3fb950">{metrics.get('current_streak', 0)} DAYS</text>

      <!-- Card 3: Longest Streak -->
      <rect x="520" y="0" width="255" height="52" rx="8" ry="8" fill="{COLOR_CARD_BG}" stroke="{COLOR_BORDER}" stroke-width="1"/>
      <text x="536" y="22" font-family="'Courier New', monospace" font-size="11" fill="{COLOR_TEXT_SECONDARY}">LONGEST STREAK</text>
      <text x="536" y="42" font-family="'Courier New', monospace" font-size="18" font-weight="700" fill="{COLOR_BLUE_ACCENT}">{metrics.get('longest_streak', 0)} DAYS</text>
    </g>
    """

    # 2. Month Labels
    month_labels = build_month_labels(daily_list, cell_size, cell_gap)
    month_svg_elements = []
    for m_name, m_x in month_labels:
        pos_x = grid_start_x + m_x
        month_svg_elements.append(
            f'<text x="{pos_x:.1f}" y="{grid_start_y - 8}" font-family="monospace" font-size="10" fill="{COLOR_TEXT_SECONDARY}">{m_name}</text>'
        )
    month_labels_code = "\n    ".join(month_svg_elements)

    # 3. Grid Columns (Weekly groups)
    weeks: dict[int, list[dict]] = {}
    for idx, day_info in enumerate(daily_list):
        week_num = idx // 7
        weeks.setdefault(week_num, []).append(day_info)

    grid_columns_code = []

    for week_idx, days in weeks.items():
        col_x = grid_start_x + week_idx * (cell_size + cell_gap)
        rects = []
        for day_idx, day_info in enumerate(days):
            col_y = grid_start_y + day_idx * (cell_size + cell_gap)
            lvl = day_info.get("level", 0)
            color = LEVEL_COLORS.get(lvl, LEVEL_COLORS[0])
            count = day_info.get("count", 0)
            date = day_info.get("date", "")

            rect_code = (
                f'<rect x="{col_x:.1f}" y="{col_y:.1f}" width="{cell_size}" height="{cell_size}" '
                f'rx="2.5" ry="2.5" fill="{color}" stroke="#1b222c" stroke-width="0.5">'
                f'<title>{count} contributions on {date}</title></rect>'
            )
            rects.append(rect_code)

        delay_sec = min(1.8, week_idx * 0.03)
        col_group = (
            f'<g class="grid-col" style="animation-delay: {delay_sec:.2f}s;">\n'
            + "  " + "\n  ".join(rects) + "\n</g>"
        )
        grid_columns_code.append(col_group)

    grid_code = "\n".join(grid_columns_code)

    # 4. Legend Section
    legend_x = svg_width - 170
    legend_y = svg_height - 20
    legend_boxes = []
    for lvl in range(5):
        box_x = legend_x + 35 + lvl * (cell_size + 3)
        legend_boxes.append(
            f'<rect x="{box_x:.1f}" y="{legend_y - 9}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{LEVEL_COLORS[lvl]}" />'
        )
    legend_code = (
        f'<g transform="translate(0, 0)">\n'
        f'  <text x="{legend_x}" y="{legend_y}" font-family="monospace" font-size="10" fill="{COLOR_TEXT_SECONDARY}">Less</text>\n'
        f'  {" ".join(legend_boxes)}\n'
        f'  <text x="{legend_x + 115}" y="{legend_y}" font-family="monospace" font-size="10" fill="{COLOR_TEXT_SECONDARY}">More</text>\n'
        f'</g>'
    )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="{svg_width}" height="{svg_height}">
  <defs>
    <style>
      @keyframes popIn {{
        0% {{ opacity: 0; transform: scale(0.6); }}
        100% {{ opacity: 1; transform: scale(1); }}
      }}

      .bg-rect {{
        fill: {COLOR_BG};
        stroke: {COLOR_BORDER};
        stroke-width: 1.5px;
        rx: 12px;
        ry: 12px;
      }}

      .grid-col {{
        animation: popIn 0.4s ease-out forwards;
        opacity: 0;
        transform-origin: center;
      }}
    </style>
  </defs>

  <!-- Outer Card Frame -->
  <rect class="bg-rect" x="2" y="2" width="{svg_width - 4}" height="{svg_height - 4}" />

  {cards_html}

  <!-- Calendar Grid Month Labels -->
  {month_labels_code}

  <!-- Contribution Grid Columns -->
  {grid_code}

  <!-- Graph Legend -->
  {legend_code}
</svg>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[OK] Futuristic contribution graph SVG rendered to: {output_path}")


def main() -> None:
    """Main render entry point."""
    print("[+] Rendering graph.svg from contribution payload...")
    payload = load_contribution_data(INPUT_JSON_PATH)
    generate_graph_svg(payload, OUTPUT_SVG_PATH)


if __name__ == "__main__":
    main()
