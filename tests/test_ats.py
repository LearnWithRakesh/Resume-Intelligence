from src.ats import keyword_match

def test_keyword_match_basic():
    resume='Skills: Java Selenium Playwright CI/CD'
    jd='Need Playwright CI/CD API testing'
    r=keyword_match(resume,jd)
    assert 'playwright' in r.keyword_matches
