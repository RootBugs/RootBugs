#!/usr/bin/env python3
"""
Generate a contribution grid snake that spells 'KARAN'
"""

import urllib.request
import json
import os

GITHUB_USER = "RootBugs"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# KARAN letter patterns (7 rows x 5 cols each)
LETTERS = {
    'K': [
        [1,0,0,1,0],
        [1,0,1,0,0],
        [1,1,0,0,0],
        [1,0,1,0,0],
        [1,0,0,1,0],
        [1,0,0,1,0],
        [1,0,0,1,0],
    ],
    'A': [
        [0,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
    ],
    'R': [
        [1,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,0],
        [1,0,1,0,0],
        [1,0,0,1,0],
        [1,0,0,0,1],
    ],
    'N': [
        [1,0,0,0,1],
        [1,1,0,0,1],
        [1,0,1,0,1],
        [1,0,1,0,1],
        [1,0,0,1,1],
        [1,0,0,1,1],
        [1,0,0,0,1],
    ],
}

def build_karan_grid():
    rows = 7
    cols = 52
    grid = [[0]*cols for _ in range(rows)]
    start_col = 11
    letters = ['K', 'A', 'R', 'A', 'N']
    col = start_col
    for letter in letters:
        pattern = LETTERS[letter]
        for r in range(7):
            for c in range(5):
                if pattern[r][c]:
                    grid[r][col + c] = 1
        col += 6
    return grid

def fetch_contribution_data():
    query = """
    query {
      user(login: "%s") {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """ % GITHUB_USER

    headers = {
        "Authorization": f"bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }

    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=data,
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            return weeks
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def generate_svg(karan_grid, contribution_weeks):
    CELL = 12
    GAP = 2
    ROWS = 7
    COLS = 52

    W = COLS * (CELL + GAP) + GAP
    H = ROWS * (CELL + GAP) + GAP

    colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

    # Build contribution grid
    contrib = [[0]*COLS for _ in range(ROWS)]
    if contribution_weeks:
        for wi, week in enumerate(contribution_weeks[:COLS]):
            for di, day in enumerate(week["contributionDays"][:ROWS]):
                cnt = day["contributionCount"]
                if cnt == 0: contrib[di][wi] = 0
                elif cnt < 3: contrib[di][wi] = 1
                elif cnt < 6: contrib[di][wi] = 2
                elif cnt < 10: contrib[di][wi] = 3
                else: contrib[di][wi] = 4

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    svg.append('<defs>')
    svg.append('<style>')
    svg.append(f'.g{{shape-rendering:geometricPrecision;width:{CELL}px;height:{CELL}px;rx:2px;ry:2px}}')
    svg.append('.s{fill:#ff6b35}')
    svg.append('.karan-cell{fill:#54a3ff}')
    svg.append('</style>')
    svg.append('</defs>')

    # Base grid
    for r in range(ROWS):
        for c in range(COLS):
            x = GAP + c * (CELL + GAP)
            y = GAP + r * (CELL + GAP)
            lvl = contrib[r][c]
            svg.append(f'<rect class="g" x="{x}" y="{y}" fill="{colors[lvl]}"/>')

    # KARAN letters overlay (blue cells)
    karan_cells = []
    for r in range(ROWS):
        for c in range(COLS):
            if karan_grid[r][c]:
                karan_cells.append((r, c))
                x = GAP + c * (CELL + GAP)
                y = GAP + r * (CELL + GAP)
                svg.append(f'<rect class="g karan-cell" x="{x}" y="{y}" opacity="0.85"/>')

    # Snake head that moves through all green cells then KARAN
    green_cells = []
    for r in range(ROWS):
        for c in range(COLS):
            if contrib[r][c] > 0:
                green_cells.append((c, r))  # x,y format

    # Path: zigzag through green cells, then through KARAN
    path = green_cells + [(c, r) for r, c in karan_cells]

    if path:
        # Create snake segments
        snake_size = 8
        total_dur = max(30, len(path) * 0.5)

        for i in range(min(snake_size, len(path))):
            cx, cy = path[i]
            x = GAP + cx * (CELL + GAP) + CELL/2
            y = GAP + cy * (CELL + GAP) + CELL/2
            r = CELL/2 + 2

            # Animate position along path
            values = []
            times = []
            for frame_idx in range(len(path)):
                idx = (frame_idx + i) % len(path)
                px, py = path[idx]
                fx = GAP + px * (CELL + GAP) + CELL/2
                fy = GAP + py * (CELL + GAP) + CELL/2
                values.append(f"{fx},{fy}")
                times.append(f"{frame_idx/len(path):.4f}")

            cx_val = ";".join(values)
            key_times = ";".join(times)

            cy_val = ";".join([v.split(",")[1] for v in values])
            svg.append(f'<circle r="{r}" fill="#ff6b35" opacity="0.9">')
            svg.append(f'<animate attributeName="cx" values="{cx_val}" keyTimes="{key_times}" dur="{total_dur}s" repeatCount="indefinite"/>')
            svg.append(f'<animate attributeName="cy" values="{cy_val}" keyTimes="{key_times}" dur="{total_dur}s" repeatCount="indefinite"/>')
            svg.append('</circle>')

        # Snake head (bigger, brighter)
        if path:
            hx, hy = path[0]
            fx = GAP + hx * (CELL + GAP) + CELL/2
            fy = GAP + hy * (CELL + GAP) + CELL/2

            head_values = []
            for frame_idx in range(len(path)):
                px, py = path[frame_idx]
                head_values.append(f"{GAP + px * (CELL + GAP) + CELL/2},{GAP + py * (CELL + GAP) + CELL/2}")

            head_x = ";".join([v.split(",")[0] for v in head_values])
            head_y = ";".join([v.split(",")[1] for v in head_values])
            key_times = ";".join([f"{i/len(path):.4f}" for i in range(len(path))])

            svg.append(f'<circle r="{CELL/2 + 3}" fill="#ff4500" stroke="#fff" stroke-width="1.5">')
            svg.append(f'<animate attributeName="cx" values="{head_x}" keyTimes="{key_times}" dur="{total_dur}s" repeatCount="indefinite"/>')
            svg.append(f'<animate attributeName="cy" values="{head_y}" keyTimes="{key_times}" dur="{total_dur}s" repeatCount="indefinite"/>')
            svg.append('</circle>')

    svg.append('</svg>')
    return "\n".join(svg)

def main():
    print("Fetching contribution data...")
    weeks = fetch_contribution_data()

    print("Building KARAN grid...")
    karan_grid = build_karan_grid()

    print("Generating SVG...")
    svg = generate_svg(karan_grid, weeks)

    os.makedirs("dist", exist_ok=True)
    with open("dist/karan-snake.svg", "w") as f:
        f.write(svg)

    print(f"Generated: dist/karan-snake.svg ({len(svg)} bytes)")

if __name__ == "__main__":
    main()
