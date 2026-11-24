# Spelled out instead of using \s: JavaScript's and Python's definitions of
# whitespace differ (BOM, U+0085, U+001C-U+001F), and both packages must agree.
# This is Unicode White_Space plus the BOM, which often rides along in pasted text.
WHITESPACE = "\t\n\v\f\r \u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"

# Invisible direction marks that come along when text is copied out of Arabic.
BIDI_MARKS = "\u061c\u200e\u200f\u202a-\u202e\u2066-\u2069"
