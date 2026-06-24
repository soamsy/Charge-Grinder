import re
import sys

profile_file = sys.argv[1] if len(sys.argv) > 1 else "profile_results.txt"
filter_path = sys.argv[2] if len(sys.argv) > 2 else "source/shop"

with open(profile_file, "r") as f:
    content = f.read()

data = {}
pattern = r'Total time:\s*([\d.e+-]+)\s*s\s*\nFile:\s*(.+)\nFunction:\s*(\S+)'
for time_str, filepath, funcname in re.findall(pattern, content):
    if filter_path in filepath:
        filename = filepath.split(filter_path + "/")[-1]
        key = f"{filename}::{funcname}"
        data[key] = data.get(key, 0) + float(time_str)

sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
nonzero = [(k, v) for k, v in sorted_data if v >= 1e-6]
zero = [(k, v) for k, v in sorted_data if v < 1e-6]

max_time = nonzero[0][1] if nonzero else 1
BAR_WIDTH = 40
LABEL_WIDTH = 44

COLORS = {
    "shop.py":        "\033[91m",
    "browse_shop.py": "\033[93m",
    "refresh.py":     "\033[96m",
    "sell.py":        "\033[95m",
    "skill3.py":      "\033[92m",
    "fuse.py":        "\033[94m",
    "heal.py":        "\033[97m",
    "uptie.py":       "\033[33m",
}
RESET = "\033[0m"
BOLD = "\033[1m"

def fmt_time(t):
    if t >= 1:        return f"{t:6.2f}s "
    if t >= 1e-3:     return f"{t*1e3:5.1f}ms"
    if t >= 1e-6:     return f"{t*1e6:5.1f}µs"
    return "  <1µs"

title = f"{filter_path}/ — Function Profile Times"
width = LABEL_WIDTH + BAR_WIDTH + 14
print(f"\n{BOLD}{title:^{width}}{RESET}")
print("─" * width)

seen_files = dict.fromkeys(k.split("::")[0] for k, _ in nonzero)
legend = "  ".join(f"{COLORS.get(f, '')}{f}{RESET}" for f in seen_files)
print(f"  {legend}\n")

for label, t in nonzero:
    file, func = label.split("::", 1)
    color = COLORS.get(file, "")
    bar = "█" * int((t / max_time) * BAR_WIDTH)
    print(f"  {color}{label:<{LABEL_WIDTH}}{RESET} {color}{bar:<{BAR_WIDTH}}{RESET} {fmt_time(t)}")

print(f"\n  {BOLD}+ {len(zero)} functions with <1µs (not shown){RESET}")

print(f"\n  {BOLD}── Totals by file ──{RESET}")
by_file = {}
for k, v in sorted_data:
    f = k.split("::")[0]
    by_file[f] = by_file.get(f, 0) + v
for fname, total in sorted(by_file.items(), key=lambda x: x[1], reverse=True):
    color = COLORS.get(fname, "")
    bar = "█" * int((total / max_time) * BAR_WIDTH)
    print(f"  {color}{fname:<{LABEL_WIDTH}}{RESET} {color}{bar:<{BAR_WIDTH}}{RESET} {fmt_time(total)}")
print()
