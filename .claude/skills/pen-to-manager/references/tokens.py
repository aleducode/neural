"""Inventory the tokens of a .pen file by counting them, not by eyeballing.

    python3 .claude/skills/pen-to-manager/references/tokens.py FZjwU KgwzQ YdrZV

With no frame ids it walks the whole document. The real token is the one that
repeats, not the one that caught your eye.
"""

import collections
import io
import json
import sys

PEN = "docs/design/manager.pen"


def main(frame_ids):
    data = json.load(io.open(PEN, encoding="utf-8"))
    index = {c["id"]: c for c in data["children"]}
    roots = [index[i] for i in frame_ids] if frame_ids else data["children"]

    counters = {k: collections.Counter() for k in (
        "fill", "stroke", "cornerRadius", "fontSize", "fontWeight",
        "fontFamily", "gap", "padding", "strokeWidth", "lineHeight",
    )}

    def record(node):
        for key, counter in counters.items():
            if key not in node:
                continue
            value = node[key]
            # A fill can be a hex string, a gradient/image dict, or a list of layers.
            if key in ("fill", "stroke"):
                if isinstance(value, str):
                    counter[value] += 1
                elif isinstance(value, dict) and value.get("color"):
                    counter[value["color"]] += 1
                continue
            counter[value if isinstance(value, (str, int, float)) else json.dumps(value)] += 1
        for child in node.get("children") or []:
            record(child)

    for root in roots:
        record(root)

    for key, counter in counters.items():
        if not counter:
            continue
        print(f"\n== {key} ==")
        for value, count in counter.most_common(24):
            print(f"  {count:>5}  {value}")


if __name__ == "__main__":
    main(sys.argv[1:])
