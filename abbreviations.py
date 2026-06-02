import re

ABBREVIATIONS = {
    "you're": "ur",
    "you": "u",
    "your": "ur",
    "are": "r",
    "what": "wut",
    "the": "d",
    "because": "bc",
    "before": "b4",
    "to": "2",
    "too": "2",
    "for": "4",
    "and": "n",
    "with": "w/",
    "without": "w/o",
    "please": "plz",
    "thanks": "thx",
    "through": "thru",
    "though": "tho",
    "about": "abt",
    "between": "btwn",
    "probably": "prob",
    "definitely": "defn",
    "really": "rly",
    "very": "v",
    "that": "dat",
    "this": "dis",
    "there": "dere",
    "their": "dere",
    "know": "kno",
    "good": "gud",
    "want": "wnt",
    "right": "rite",
    "why": "y",
    "would": "wud",
    "could": "cud",
    "should": "shud",
    "have": "hav",
    "from": "frm",
    "just": "jst",
    "more": "mor",
    "some": "sum",
    "them": "dem",
    "then": "den",
    "than": "dan",
    "when": "wen",
    "where": "wher",
    "how": "hw",
    "which": "wch",
    "been": "bn",
    "people": "ppl",
    "something": "smth",
    "everything": "evryth",
    "nothing": "nthn",
    "maybe": "mayb",
    "actually": "actly",
    "seriously": "srsly",
    "tomorrow": "2moro",
    "tonight": "2nite",
    "great": "gr8",
    "later": "l8r",
    "night": "nite",
    "light": "lite",
    "okay": "ok",
    "see": "c",
    "be": "b",
}

def apply_abbreviations(text: str) -> str:
    result = text
    # Sort longest first so multi-word / longer matches take priority
    for word, abbrev in sorted(ABBREVIATIONS.items(), key=lambda x: -len(x[0])):
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        def _replace(match, _abbrev=abbrev):
            if match.group(0)[0].isupper():
                return _abbrev[0].upper() + _abbrev[1:]
            return _abbrev
        result = pattern.sub(_replace, result)
    return result
