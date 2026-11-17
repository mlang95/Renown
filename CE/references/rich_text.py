"""rich_text.py — wrap and draw effect text with bold lead-in labels on a reportlab canvas.

Effect text may open a clause with a label ("Each Empire Phase:", "Ranger:"); renown_data.leadin_split finds them.
The print scripts draw plain text line by line, so these helpers keep that shape:
    lines = rich_wrap(c, text, font, bold_font, size, width)   # -> [[(word, font), ...], ...]
    draw_rich(c, x, y, line, size)                             # draws one line at (x, y)
len(lines) is the line count, as len(wrap(...)) was.
"""
import renown_data as rd


def rich_words(text, font, bold_font):
    """[(word, font)] for text, with lead-in label words in bold_font."""
    out = []
    for chunk, is_label in rd.leadin_split(text):
        f = bold_font if is_label else font
        out += [(w, f) for w in chunk.split()]
    return out


def rich_wrap(c, text, font, bold_font, size, maxw):
    lines, cur, cur_w = [], [], 0.0
    sp = {}
    for w, f in rich_words(text, font, bold_font):
        ww = c.stringWidth(w, f, size)
        gap = sp.setdefault(f, c.stringWidth(" ", f, size)) if cur else 0.0
        if cur and cur_w + gap + ww > maxw:
            lines.append(cur); cur, cur_w = [(w, f)], ww
        else:
            cur.append((w, f)); cur_w += gap + ww
    if cur:
        lines.append(cur)
    return lines


def line_text(line):
    return " ".join(w for w, _ in line)


def draw_rich(c, x, y, line, size, right=False):
    """Draw one wrapped line; the canvas fill colour is left as the caller set it."""
    if right:
        x -= sum(c.stringWidth(w, f, size) for w, f in line) + sum(c.stringWidth(" ", f, size) for _, f in line[1:])
    for i, (w, f) in enumerate(line):
        if i:
            x += c.stringWidth(" ", f, size)
        c.setFont(f, size)
        c.drawString(x, y, w)
        x += c.stringWidth(w, f, size)
