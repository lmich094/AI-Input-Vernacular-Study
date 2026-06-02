from abbreviations import apply_abbreviations

def test_substitutes_you():
    assert apply_abbreviations("Can you help me?") == "Can u help me?"

def test_substitutes_are():
    assert apply_abbreviations("What are you doing?") == "Wut r u doing?"

def test_whole_word_only():
    # "your" should not match inside "yourself"
    result = apply_abbreviations("yourself")
    assert result == "yourself"

def test_does_not_alter_short_words():
    # "a", "I", "is" — already short, no substitution defined
    assert apply_abbreviations("a") == "a"

def test_case_insensitive():
    result = apply_abbreviations("You are here")
    assert result == "U r here"

def test_no_substitution_for_unknown_words():
    result = apply_abbreviations("photosynthesis")
    assert result == "photosynthesis"

def test_multiple_substitutions_in_sentence():
    result = apply_abbreviations("What are you doing because of that?")
    assert result == "Wut r u doing bc of dat?"
