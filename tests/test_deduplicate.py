"""Covers app.search.aggregator's dedup/ranking logic, which replaced the
old (removed) app.research.deduplicate / app.research.base scaffold."""
from app.search.aggregator import SearchAggregator


def test_normalize_url_treats_www_and_trailing_slash_as_equal():
    agg = SearchAggregator()
    a = agg.normalize_url("https://www.example.com/page/")
    b = agg.normalize_url("https://example.com/page")
    assert a == b


def test_rank_and_deduplicate_removes_duplicate_urls():
    agg = SearchAggregator()
    results = [
        {"title": "A", "url": "https://example.com/page"},
        {"title": "A dup", "url": "https://www.example.com/page/"},
        {"title": "B", "url": "https://other.com/x"},
    ]
    deduped = agg.rank_and_deduplicate(results)
    assert len(deduped) == 2


def test_rank_and_deduplicate_ranks_high_authority_domains_first():
    agg = SearchAggregator()
    results = [
        {"title": "Random", "url": "https://randomsite.net/a"},
        {"title": "Wiki", "url": "https://wikipedia.org/b"},
    ]
    deduped = agg.rank_and_deduplicate(results)
    assert deduped[0]["url"] == "https://wikipedia.org/b"
