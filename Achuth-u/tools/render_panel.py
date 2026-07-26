"""
System Info Terminal Panel SVG Generator.

Generates a futuristic cyberpunk terminal panel `sysinfo.svg` displaying
user stats, roles, focus areas, links, and status with typing & cursor animations.

Output: sysinfo.svg
"""

import os
import xml.sax.saxutils as xml_escape

OUTPUT_SVG_PATH = "sysinfo.svg"

# Profile Metadata Configuration
USER_METADATA = [
    ("USER", "Achuth U"),
    ("ROLE", "Software Developer"),
    ("FOCUS", "Python • React • FastAPI • AI"),
    ("LEARNING", "Agentic AI"),
    ("PROJECTS", "BudgetBuddy • Blockchain Voting • 3D Portfolio"),
    ("STATUS", "Open to Work"),
    ("GITHUB", "github.com/Achuth-u"),
    ("PORTFOLIO", "3dportfolioachuth.vercel.app"),
    ("LINKEDIN", "linkedin.com/in/achuth-u"),
]

# Color Palette Constants
COLOR_BG = "#0d1117"
COLOR_HEADER_BG = "#161b22"
COLOR_BORDER = "#1f6feb"
COLOR_PRIMARY_BLUE = "#3BA8FF"
COLOR_ACCENT_BLUE = "#58A6FF"
COLOR_TEXT = "#c9d1d9"
COLOR_TEXT_DIM = "#8b949e"
COLOR_GREEN = "#3fb950"


def generate_panel_svg(metadata: list[tuple[str, str]], output_path: str) -> None:
    """
    Build and render sysinfo.svg containing animated terminal panel.

    Args:
        metadata (list[tuple[str, str]]): Field key-value pairs to display.
        output_path (str): Output SVG file destination.
    """
    panel_width = 490
    panel_height = 360

    # Build lines of terminal content
    line_elements = []

    # Prompt header line
    line_elements.append(
        f'    <g class="term-line line-0">\n'
        f'      <text x="20" y="55" class="prompt-user">achuth@cyber-terminal</text>'
        f'<text x="182" y="55" class="prompt-colon">:</text>'
        f'<text x="190" y="55" class="prompt-path">~</text>'
        f'<text x="200" y="55" class="prompt-char">$ </text>'
        f'<text x="215" y="55" class="cmd-text">sysinfo --fetch</text>\n'
        f'    </g>'
    )

    start_y = 88
    line_spacing = 26

    for idx, (label, val) in enumerate(metadata, start=1):
        y_pos = start_y + (idx - 1) * line_spacing
        escaped_val = xml_escape.escape(val)

        # Apply specific accent styling for status or links
        val_class = "val-text"
        if label == "STATUS":
            val_class = "val-status"
        elif label in ("GITHUB", "PORTFOLIO", "LINKEDIN"):
            val_class = "val-link"

        line_markup = (
            f'    <g class="term-line line-{idx}">\n'
            f'      <text x="20" y="{y_pos}" class="label-text">{label.ljust(10)}:</text>\n'
            f'      <text x="125" y="{y_pos}" class="{val_class}">{escaped_val}</text>\n'
            f'    </g>'
        )
        line_elements.append(line_markup)

    # Add cursor line at the end
    cursor_y = start_y + len(metadata) * line_spacing + 5
    line_elements.append(
        f'    <g class="term-line line-{len(metadata)+1}">\n'
        f'      <text x="20" y="{cursor_y}" class="prompt-user">achuth@cyber-terminal</text>'
        f'<text x="182" y="{cursor_y}" class="prompt-colon">:</text>'
        f'<text x="190" y="{cursor_y}" class="prompt-path">~</text>'
        f'<text x="200" y="{cursor_y}" class="prompt-char">$ </text>\n'
        f'      <rect x="215" y="{cursor_y - 12}" width="8" height="14" class="blinking-cursor" />\n'
        f'    </g>'
    )

    lines_body = "\n".join(line_elements)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {panel_width} {panel_height}" width="{panel_width}" height="{panel_height}">
  <defs>
    <style>
      @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}

      @keyframes blinkCursor {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
      }}

      .window-bg {{
        fill: {COLOR_BG};
        stroke: {COLOR_BORDER};
        stroke-width: 1.5px;
        rx: 10px;
        ry: 10px;
      }}

      .header-bg {{
        fill: {COLOR_HEADER_BG};
        rx: 10px;
        ry: 10px;
      }}

      .window-title {{
        font-family: 'Courier New', Consolas, monospace;
        font-size: 12px;
        font-weight: 600;
        fill: {COLOR_TEXT_DIM};
      }}

      .prompt-user {{ font-family: 'Courier New', monospace; font-size: 13px; font-weight: 700; fill: {COLOR_PRIMARY_BLUE}; }}
      .prompt-colon {{ font-family: 'Courier New', monospace; font-size: 13px; fill: {COLOR_TEXT}; }}
      .prompt-path {{ font-family: 'Courier New', monospace; font-size: 13px; font-weight: 700; fill: {COLOR_ACCENT_BLUE}; }}
      .prompt-char {{ font-family: 'Courier New', monospace; font-size: 13px; fill: {COLOR_TEXT}; }}
      .cmd-text {{ font-family: 'Courier New', monospace; font-size: 13px; font-weight: 700; fill: #ffffff; }}

      .label-text {{
        font-family: 'Courier New', Consolas, monospace;
        font-size: 12px;
        font-weight: 700;
        fill: {COLOR_ACCENT_BLUE};
        letter-spacing: 0.5px;
      }}

      .val-text {{
        font-family: 'Courier New', Consolas, monospace;
        font-size: 12px;
        fill: {COLOR_TEXT};
      }}

      .val-status {{
        font-family: 'Courier New', Consolas, monospace;
        font-size: 12px;
        font-weight: 700;
        fill: {COLOR_GREEN};
      }}

      .val-link {{
        font-family: 'Courier New', Consolas, monospace;
        font-size: 12px;
        fill: {COLOR_PRIMARY_BLUE};
        text-decoration: underline;
      }}

      .blinking-cursor {{
        fill: {COLOR_PRIMARY_BLUE};
        animation: blinkCursor 1s infinite steps(2, start);
      }}

      .term-line {{
        animation: fadeIn 0.4s ease-out forwards;
        opacity: 0;
      }}

      .line-0 {{ animation-delay: 0.1s; }}
      .line-1 {{ animation-delay: 0.25s; }}
      .line-2 {{ animation-delay: 0.4s; }}
      .line-3 {{ animation-delay: 0.55s; }}
      .line-4 {{ animation-delay: 0.7s; }}
      .line-5 {{ animation-delay: 0.85s; }}
      .line-6 {{ animation-delay: 1.0s; }}
      .line-7 {{ animation-delay: 1.15s; }}
      .line-8 {{ animation-delay: 1.3s; }}
      .line-9 {{ animation-delay: 1.45s; }}
      .line-10 {{ animation-delay: 1.6s; }}
    </style>

    <filter id="panel-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Container Window Box -->
  <rect class="window-bg" x="2" y="2" width="{panel_width - 4}" height="{panel_height - 4}" filter="url(#panel-shadow)" />

  <!-- Terminal Header Bar -->
  <path class="header-bg" d="M 2,12 A 10,10 0 0 1 12,2 L {panel_width - 12},2 A 10,10 0 0 1 {panel_width - 2},12 L {panel_width - 2},32 L 2,32 Z" />
  
  <!-- Window Control Buttons (Red, Yellow, Green) -->
  <circle cx="18" cy="17" r="5" fill="#ff5f56" />
  <circle cx="34" cy="17" r="5" fill="#ffbd2e" />
  <circle cx="50" cy="17" r="5" fill="#27c93f" />

  <!-- Window Header Title -->
  <text x="{panel_width // 2}" y="21" text-anchor="middle" class="window-title">achuth@cyber-terminal:~</text>

  <!-- Divider Line -->
  <line x1="2" y1="32" x2="{panel_width - 2}" y2="32" stroke="{COLOR_BORDER}" stroke-width="1" />

  <!-- Terminal Content Lines -->
{lines_body}
</svg>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[OK] System info terminal panel rendered to: {output_path}")


def main() -> None:
    """Main rendering entry point."""
    print("[+] Rendering sysinfo.svg terminal panel...")
    generate_panel_svg(USER_METADATA, OUTPUT_SVG_PATH)


if __name__ == "__main__":
    main()
