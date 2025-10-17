def test_llm_summarize():
    from .processor import llm_summarize
    s = llm_summarize('happy', {'happy': 99.1})
    assert 'happy' in s
