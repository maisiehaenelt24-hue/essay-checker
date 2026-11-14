import streamlit as st
from collections import Counter
import re

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(layout="wide")
st.title("Academic Writing Improver")
st.caption(
    "A rule-based checker (no AI). Treat each flag as a prompt to look again, not as a definite error. "
    "The app does not save your text."
)

text = st.text_area("Paste your essay:", height=350)

# -----------------------------
# STOPWORDS
# -----------------------------
stopwords = {
    "the","a","an","and","or","but","if","in","on","at","to","for","of",
    "is","are","was","were","be","been","being","it","this","that",
    "these","those","as","by","with","from","all","we","they","you","which",
    "how","what","who","whom","whose","when","where","why","both","each",
    "any","some","such","no","not","only","own","same","so","than","too"
}

# -----------------------------
# WORD BANK (informal or vague wording -> academic alternatives)
# Whole words and phrases only, matched in lower case.
# -----------------------------
word_bank = {
    # intensifiers and vague quantities
    "very": ["extremely", "highly", "significantly"],
    "really": ["particularly", "notably"],
    "quite": ["fairly", "relatively", "reasonably"],
    "a lot of": ["many", "numerous", "a considerable number of"],
    "lots of": ["many", "numerous", "a considerable amount of"],
    "a lot": ["considerably", "frequently", "extensively"],
    "a bit": ["slightly", "somewhat"],
    "kind of": ["somewhat", "rather"],
    "sort of": ["somewhat", "rather"],
    "huge": ["substantial", "considerable", "significant"],
    "tiny": ["minimal", "negligible", "marginal"],
    "big": ["substantial", "considerable", "extensive"],
    "small": ["minimal", "limited", "marginal"],
    "good": ["effective", "beneficial", "valuable"],
    "bad": ["ineffective", "detrimental", "problematic"],
    "important": ["crucial", "significant", "fundamental"],
    "things": ["factors", "elements", "aspects"],
    "thing": ["factor", "element", "aspect"],
    "stuff": ["materials", "components"],

    # filler and conversational words
    "basically": ["fundamentally", "essentially"],
    "actually": ["in fact", "(often best removed)"],
    "obviously": ["clearly", "evidently"],
    "maybe": ["perhaps", "possibly"],
    "mostly": ["largely", "predominantly"],
    "nowadays": ["currently", "in contemporary society"],
    "these days": ["currently", "in recent years"],
    "in today's society": ["in contemporary society"],

    # absolutes that are hard to defend in academic writing
    "always": ["frequently", "consistently", "typically"],
    "never": ["rarely", "seldom"],
    "everyone": ["most people", "the majority"],
    "everybody": ["most people", "the majority"],
    "proves": ["demonstrates", "indicates", "supports"],
    "prove": ["demonstrate", "indicate", "support"],
    "proved": ["demonstrated", "indicated", "supported"],

    # reporting verbs
    "shows": ["demonstrates", "illustrates", "indicates"],
    "show": ["demonstrate", "illustrate", "indicate"],
    "showed": ["demonstrated", "illustrated", "indicated"],
    "says": ["argues", "states", "asserts"],
    "said": ["argued", "stated", "asserted"],
    "finds": ["reveals", "indicates", "suggests"],
    "found": ["revealed", "identified", "established"],
    "thinks": ["argues", "suggests", "contends"],
    "uses": ["employs", "applies", "draws on"],
    "use": ["employ", "apply", "draw on"],

    # phrasal verbs -> single formal verbs
    "talks about": ["discusses", "examines", "addresses"],
    "looks at": ["examines", "investigates", "considers"],
    "look into": ["investigate", "examine"],
    "deals with": ["addresses", "tackles"],
    "points out": ["highlights", "notes", "observes"],
    "find out": ["determine", "establish", "ascertain"],
    "come up with": ["devise", "propose", "develop"],
    "carry out": ["conduct", "perform", "undertake"],
    "make up": ["constitute", "comprise"],
    "bring about": ["cause", "produce"],
    "goes up": ["increases", "rises"],
    "go up": ["increase", "rise"],
    "goes down": ["decreases", "declines"],
    "go down": ["decrease", "decline"],
    "get better": ["improve", "develop"],
    "get worse": ["deteriorate", "decline"],
    "make sure": ["ensure", "verify"],
    "need to": ["must", "is required to"],
    "try to": ["attempt to", "seek to"],
    "want to": ["aim to", "seek to"],
    "get": ["obtain", "acquire", "receive"],
    "gets": ["obtains", "acquires", "receives"],
    "got": ["obtained", "acquired", "received"],

    # wordy phrases
    "in order to": ["to"],
    "due to the fact that": ["because", "since"],
    "a number of": ["several", "various"],
    "at this point in time": ["currently", "at present"],
    "in terms of": ["regarding", "with respect to"],

    # signposting
    "this shows that": ["this demonstrates that", "this suggests that", "this indicates that"],
    "this means that": ["this implies that", "this suggests that"],
    "this is important": ["this is significant", "this is crucial"],
    "in conclusion": ["to conclude", "overall", "in summary"]
}

# -----------------------------
# DISCOURSE MARKERS
# -----------------------------
discourse_markers = [
    "therefore", "however", "moreover", "furthermore",
    "in addition", "thus", "consequently", "overall"
]

# -----------------------------
# GRAMMAR AND PUNCTUATION RULES
# -----------------------------
ABBREVIATIONS = ["e.g.", "i.e.", "et al.", "etc.", "cf.", "vs.", "fig."]

CONTRACTION_PATTERN = re.compile(
    r"\b[A-Za-z]+n't\b|\b(?:I|you|we|they|he|she|it|that|there|here|what|who|let)'(?:s|m|re|ve|ll|d)\b",
    re.IGNORECASE,
)

CONTRACTION_FIXES = {
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "can't": "cannot", "won't": "will not", "isn't": "is not",
    "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "couldn't": "could not", "wouldn't": "would not", "shouldn't": "should not",
    "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
    "it's": "it is / it has", "that's": "that is", "there's": "there is",
    "they're": "they are", "we're": "we are", "you're": "you are",
    "i'm": "I am", "i've": "I have", "we've": "we have", "they've": "they have",
}

INFORMAL_FORMS = {
    "alot": "a lot (or, better, many / considerably)",
    "could of": "could have",
    "would of": "would have",
    "should of": "should have",
    "must of": "must have",
    "irregardless": "regardless",
    "alright": "all right",
    "gonna": "going to",
    "wanna": "want to",
    "kinda": "somewhat",
    "sorta": "somewhat",
}

WEAK_STARTS = {"and", "but", "so", "plus"}

MISSING_COMMA_PATTERN = re.compile(
    r"(however|moreover|furthermore|consequently|additionally|nevertheless|"
    r"nonetheless|similarly|likewise|in addition|for example|for instance|"
    r"in contrast|in conclusion|in summary|on the other hand|as a result)\s+(?=\w)",
    re.IGNORECASE,
)

# -----------------------------
# FUNCTIONS
# -----------------------------

def normalise(text):
    # pasted Word text often has curly quotes and apostrophes
    return (
        text.replace("’", "'").replace("‘", "'")
        .replace("“", '"').replace("”", '"')
    )


def clean_word(word):
    # lower-case and strip surrounding punctuation, including quotes and brackets
    return word.lower().strip(".,!?;:\"'()[]“”‘’")


def protect_abbreviations(text):
    # hide the full stops in abbreviations like "e.g." so they don't end a sentence
    protected = text
    for abbr in ABBREVIATIONS:
        protected = re.sub(
            r"\b" + re.escape(abbr),
            lambda m: m.group(0).replace(".", "<dot>"),
            protected,
            flags=re.IGNORECASE,
        )
    return protected


def get_sentences(text):
    protected = protect_abbreviations(text)
    # a sentence ends at . ! or ? followed by whitespace or the end of the text,
    # so decimals like 3.5 stay intact
    raw = re.split(r'[.!?]+(?:\s+|$)', protected)
    return [s.replace("<dot>", ".").strip() for s in raw if s.strip()]


def get_long_sentences(sentences):
    return [s for s in sentences if len(s.split()) > 25]


def readability_level(words, sentences):
    if not sentences:
        return "Unknown"
    avg_len = len(words) / len(sentences)
    if avg_len < 12:
        return "Easy"
    elif avg_len < 20:
        return "Moderate"
    else:
        return "Complex"


def smart_repetition_analysis(words, text):

    # clean first, then remove stopwords, so "that," is filtered like "that"
    cleaned = [c for c in (clean_word(w) for w in words) if c and c not in stopwords]
    counts = Counter(cleaned)
    total_words = len(cleaned)

    paragraphs = [p for p in text.split("\n") if p.strip()]
    para_presence = Counter()

    for p in paragraphs:
        unique_words = set([clean_word(w) for w in p.split()])
        for w in unique_words:
            para_presence[w] += 1

    strong, soft, key_terms = [], [], []

    # -------------------------
    # DETECT KEY TERMS (CONTENT WORDS)
    # -------------------------
    for word, count in counts.items():
        spread = para_presence[word]

        if (
            spread >= 2 and
            count >= 3 and
            word not in discourse_markers  # don't treat discourse as key terms
        ):
            key_terms.append(word)

    # -------------------------
    # REPETITION ANALYSIS
    # -------------------------
    for word, count in counts.items():

        freq_ratio = count / total_words if total_words > 0 else 0

        # ALWAYS CHECK DISCOURSE MARKERS
        if word in discourse_markers:
            if count > 3:
                strong.append(word)
            elif count > 2:
                soft.append(word)
            continue

        # KEY TERMS (LESS STRICT)
        if word in key_terms:
            if count > 12 or freq_ratio > 0.08:
                strong.append(word)
            continue

        # NORMAL WORDS
        if count > 8 or freq_ratio > 0.04:
            strong.append(word)
        elif count > 4:
            soft.append(word)

    return strong, soft, key_terms


def get_word_suggestions(text):
    suggestions = {}
    lower_text = normalise(text).lower()

    for phrase, replacements in word_bank.items():
        # match whole words/phrases only, so "use" doesn't match inside "because"
        if re.search(r"\b" + re.escape(phrase) + r"\b", lower_text):
            suggestions[phrase] = replacements

    return suggestions


def context(source, start, end, pad=25):
    # a short snippet of the text around a flagged spot
    a = max(0, start - pad)
    b = min(len(source), end + pad)
    snippet = source[a:b].replace("\n", " ").replace("<dot>", ".").strip()
    return ("..." if a > 0 else "") + snippet + ("..." if b < len(source) else "")


def find_issues(text):
    # returns a list of (category, excerpt, advice)
    issues = []
    t = normalise(text)
    protected = protect_abbreviations(t)

    def add(category, start, end, advice):
        issues.append((category, context(protected, start, end), advice))

    # repeated words ("the the"), allowing the two real English cases
    for m in re.finditer(r"\b([A-Za-z']+)[ \t]+\1\b", protected, flags=re.IGNORECASE):
        if m.group(1).lower() in ("that", "had"):
            continue
        add("Repeated word", m.start(), m.end(), f'"{m.group(1)}" appears twice in a row')

    # spacing around punctuation
    for m in re.finditer(r"(?<=[A-Za-z0-9\)])\s+[,;:.!?](?=\s|$)", protected):
        add("Punctuation spacing", m.start(), m.end(), "Remove the space before the punctuation mark")
    for m in re.finditer(r"(?<=[a-z])[,;:](?=[A-Za-z])", protected):
        add("Punctuation spacing", m.start(), m.end(), "Add a space after the punctuation mark")
    for m in re.finditer(r"(?<=[a-z])[.!?](?=[A-Z])", protected):
        add("Punctuation spacing", m.start(), m.end(), "Add a space after the full stop")

    double_spaces = len(re.findall(r"(?<=\S)  +(?=\S)", t))
    if double_spaces:
        issues.append(("Punctuation spacing", f"{double_spaces} double space(s)", "Use a single space between words"))

    # lower-case "i" as a pronoun (ignoring list markers like "(i)")
    for m in re.finditer(r"(?<![\w'(])i(?![\w)])(?!<dot>)", protected):
        add("Capital letters", m.start(), m.end(), 'Write the pronoun "I" with a capital letter')

    # contractions are too informal for most academic writing
    for m in CONTRACTION_PATTERN.finditer(t):
        fix = CONTRACTION_FIXES.get(m.group(0).lower(), "write it out in full")
        issues.append(("Contraction", context(t, m.start(), m.end()), f'Too informal: use "{fix}"'))

    # common informal or incorrect forms
    for phrase, fix in INFORMAL_FORMS.items():
        for m in re.finditer(r"\b" + re.escape(phrase) + r"\b", t, flags=re.IGNORECASE):
            issues.append(("Informal or incorrect wording", context(t, m.start(), m.end()), f'Try "{fix}"'))

    # sentence-level checks
    for s in get_sentences(t):
        first_word = s.split()[0]
        first_char = s[0]

        if (
            first_char.isalpha() and first_char.islower()
            and not (len(s) > 1 and s[1].isupper())
            and not s.lower().startswith(("e.g.", "i.e.", "et al.", "etc."))
        ):
            issues.append(("Capital letters", s[:60], "Sentence starts with a lower-case letter"))

        if first_word.lower() in WEAK_STARTS:
            issues.append(("Sentence style", s[:60], f'Starting with "{first_word}" is informal: try "However," or "Additionally,"'))

        if MISSING_COMMA_PATTERN.match(s):
            issues.append(("Possible missing comma", s[:60], "Add a comma after the opening phrase"))

    # unbalanced brackets and quotation marks
    if t.count("(") != t.count(")"):
        issues.append(("Brackets and quotes", "Round brackets", "The number of ( and ) does not match"))
    if t.count("[") != t.count("]"):
        issues.append(("Brackets and quotes", "Square brackets", "The number of [ and ] does not match"))
    if t.count('"') % 2 == 1:
        issues.append(("Brackets and quotes", "Quotation marks", "There is an odd number of double quotation marks"))

    # paragraphs that end without punctuation (short lines are treated as headings)
    for line in t.split("\n"):
        stripped = line.strip()
        if len(stripped.split()) > 8 and stripped[-1] not in ".!?:;\")'":
            issues.append(("Final punctuation", "..." + stripped[-40:], "This paragraph may be missing a full stop"))

    return issues


def safe(text):
    # stop Streamlit treating $ as maths
    return text.replace("$", "\\$")


# -----------------------------
# ANALYSIS
# -----------------------------
if st.button("Analyse"):

    if not text.strip():
        st.warning("Please paste some text first.")
        st.stop()

    words = text.split()
    sentences = get_sentences(text)
    long_sentences = get_long_sentences(sentences)

    word_count = len(words)
    readability = readability_level(words, sentences)

    strong_rep, soft_rep, key_terms = smart_repetition_analysis(words, text)
    suggestions = get_word_suggestions(text)
    issues = find_issues(text)

    # -----------------------------
    # OVERVIEW
    # -----------------------------
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Word Count", word_count)
    col2.metric("Readability", readability)
    col3.metric("Long Sentences", len(long_sentences))
    col4.metric("Grammar and Punctuation Flags", len(issues))

    # -----------------------------
    # GRAMMAR AND PUNCTUATION
    # -----------------------------
    st.subheader("Grammar and Punctuation")

    if issues:
        by_category = {}
        for category, excerpt, advice in issues:
            by_category.setdefault(category, []).append((excerpt, advice))

        for category, items in by_category.items():
            st.markdown(f"**{category}** ({len(items)})")
            for excerpt, advice in items[:5]:
                st.write(f"- {safe(excerpt)} → {safe(advice)}")
            if len(items) > 5:
                with st.expander(f"Show all {len(items)} flags for: {category}"):
                    for excerpt, advice in items:
                        st.write(f"- {safe(excerpt)} → {safe(advice)}")
        st.caption("These checks use simple rules and cannot judge meaning, so they will miss some errors and occasionally flag correct text.")
    else:
        st.write("No grammar or punctuation flags")

    # -----------------------------
    # SENTENCE STRUCTURE
    # -----------------------------
    st.subheader("Sentence Structure")

    if long_sentences:
        st.write(f"{len(long_sentences)} sentences exceed 25 words")

        st.markdown("**Preview:**")
        for s in long_sentences[:5]:
            wc = len(s.split())
            st.write(f"- ({wc} words) {safe(s)}")

        with st.expander("Show all long sentences"):
            for s in long_sentences:
                wc = len(s.split())
                st.write(f"- ({wc} words) {safe(s)}")
    else:
        st.write("All sentences are within recommended length")

    # -----------------------------
    # KEY TERMS
    # -----------------------------
    st.subheader("Detected Key Terms")

    if key_terms:
        st.write(", ".join(list(key_terms)[:12]))
        st.caption("These are treated as subject-specific terms.")
    else:
        st.write("No clear key terms detected")

    # -----------------------------
    # REPETITION
    # -----------------------------
    st.subheader("Repetition and Vocabulary")

    if strong_rep:
        for word in strong_rep:
            st.write(f"{word} is overused")

    if soft_rep:
        for word in soft_rep:
            st.write(f"{word} could be varied")

    if not strong_rep and not soft_rep:
        st.write("No problematic repetition detected")

    # -----------------------------
    # WORD IMPROVEMENTS
    # -----------------------------
    st.subheader("Word and Phrase Improvements")

    if suggestions:
        for word, repl in suggestions.items():
            st.write(f"{safe(word)} → {', '.join(repl)}")
    else:
        st.write("No improvements suggested")

    # -----------------------------
    # FEEDBACK
    # -----------------------------
    st.subheader("Feedback")

    feedback = []

    if readability == "Complex":
        feedback.append("Some sentences are quite long and may reduce clarity.")

    if strong_rep:
        feedback.append("Certain words are used frequently and could be replaced with more precise alternatives.")

    if soft_rep:
        feedback.append("Some repetition is present; minor variation may improve flow.")

    if issues:
        feedback.append(f"{len(issues)} grammar or punctuation points are worth checking (see above).")

    if suggestions:
        feedback.append("Some informal or vague wording could be made more academic.")

    if not feedback:
        feedback.append("The writing is clear, structured, and uses appropriate vocabulary.")

    for f in feedback:
        st.write(f"- {f}")
