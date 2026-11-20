"""A9 (lead 20 Nov, from proof sample B0365-P04): in a should-point EVERY verify sentence carries "(recommended)".
sentences(t): split at ". " followed by a capital letter, outside parentheses, not after an abbreviation.
mark(t): mechanical fix: insert " (recommended)" before the final "." of each unmarked sentence."""
import re
ABBR = re.compile(r"(\be\.g|\bi\.e|\bPh|\bEur|\betc|\bRef|\bNo|\bpara|\bArt|\bvs|\bFig|\bSec|\bapprox|\bincl|\b[A-Z])$", re.I)


def sentences(t):
    out, cur, depth, i = [], "", 0, 0
    while i < len(t):
        ch = t[i]; cur += ch
        if ch in "([": depth += 1
        elif ch in ")]": depth = max(0, depth - 1)
        elif ch == "." and depth == 0 and i + 2 < len(t) and t[i + 1] == " " and t[i + 2].isupper() and not ABBR.search(cur[:-1]):
            out.append(cur.strip()); cur = ""
        i += 1
    if cur.strip(): out.append(cur.strip())
    return out


def unmarked(t):
    return [s for s in sentences(t) if "(recommended)" not in s.lower()]


def mark(t):
    fixed = []
    for s in sentences(t):
        if "(recommended)" not in s.lower():
            s = s[:-1] + " (recommended)." if s.endswith(".") else s + " (recommended)"
        fixed.append(s)
    return " ".join(fixed)
