"""Two bounded AI calls per article; publish only a fully verified language pair."""
from __future__ import annotations
import copy
import hashlib
from urllib.parse import urlparse
import ai_dev_digest as ai
from validate_dev_digest import SOURCE_HOSTS


def paired_schema(schema):
    return {"type": "OBJECT", "properties": {"en": copy.deepcopy(schema), "ko": copy.deepcopy(schema)}, "required": ["en", "ko"]}


CLAIM_SCHEMA = paired_schema(ai.CLAIM_SCHEMA)
for schema in CLAIM_SCHEMA["properties"].values():
    schema["properties"]["title"] = {"type": "STRING"}
    schema["required"].append("title")
english = CLAIM_SCHEMA["properties"]["en"]["properties"]["claims"]["items"]
english["properties"]["text_en"] = english["properties"].pop("text_ko")
english["required"] = ["text_en", "evidence"]
REVIEW_SCHEMA = paired_schema(ai.REVIEW_SCHEMA)


def summarize_item(item, client):
    original = ai.fetch_document(item.link, SOURCE_HOSTS[item.source_name])
    documents = [original]
    sensitive = bool(ai.SENSITIVE.search(item.title + " " + item.summary))
    if sensitive and urlparse(original.url).hostname not in ai.PRIMARY_HOSTS:
        seen = set()
        for link in original.links:
            if link in seen or not ai.safe_source_url(link, ai.PRIMARY_HOSTS) or len(urlparse(link).path.strip("/")) < 8:
                continue
            seen.add(link)
            try:
                documents.append(ai.fetch_document(link, ai.PRIMARY_HOSTS))
            except ai.ArticleUnavailable:
                continue
            if len(documents) >= 3:
                break
        if len(documents) == 1:
            raise ai.ArticleUnavailable("sensitive report lacks an accessible primary reference")
    data = {"title": item.title, "documents": [{"document_id": i, "url": d.url, "body": d.body} for i, d in enumerate(documents)]}
    generated = client.generate(
        "Summarize this article in English (en) and Korean (ko), including a faithfully translated title for each edition. Each edition needs 2–3 complete factual sentences, one claim per sentence. "
        "Use text_en for English (80–800 characters total) and text_ko for Korean (80–420 characters total). "
        "Each claim needs 1–3 exact source quotes, 20–240 characters each. Both editions must convey the same facts. "
        "Preserve numerical/version/date/preview/GA details and limitations. Attribute vendor benchmark claims. No advice. "
        "For security, release/version and deprecation news, support every claim with a primary-source quote. "
        "Document 0 is the article; other documents must concern the same event.", data, CLAIM_SCHEMA)
    summaries = {}
    claims = {}
    titles = {}
    for language in ("en", "ko"):
        edition = generated.get(language)
        if not isinstance(edition, dict):
            raise ai.ArticleUnavailable("AI omitted a language edition")
        title = edition.get("title")
        if not isinstance(title, str) or not 1 <= len(title) <= 240 or any(c in title for c in ("\n", "<", ">")):
            raise ai.ArticleUnavailable("invalid translated title")
        titles[language] = title
        claims[language] = edition.get("claims")
        summaries[language] = ai.verify_claims(claims[language], documents, sensitive, language)
    review = client.generate(
        "Independently check the translated titles and EVERY claim in BOTH language editions against the source documents and each other. "
        "Reject invented facts, numerical/version/date/status changes, lost conditions, unqualified benchmarks, unrelated references, "
        "contradictions and mistranslations. Return a verdict for each zero-based claim index in each edition. "
        "supported is true only if every claim is entailed and both editions agree. requires_official is true for security, release/version or deprecation claims.",
        {**data, "editions": generated}, REVIEW_SCHEMA)
    for language in ("en", "ko"):
        verdict = review.get(language)
        if not isinstance(verdict, dict) or verdict.get("supported") is not True or type(verdict.get("requires_official")) is not bool:
            raise ai.ArticleUnavailable("language pair did not pass independent review")
        verdicts = verdict.get("claims")
        if (not isinstance(verdicts, list) or len(verdicts) != len(claims[language])
                or any(not isinstance(v, dict) or type(v.get("index")) is not int or v["index"] != i or v.get("supported") is not True for i, v in enumerate(verdicts))):
            raise ai.ArticleUnavailable("independent review omitted or rejected a claim")
        ai.verify_claims(claims[language], documents, sensitive or verdict["requires_official"], language)
    return {
        "editions": {language: {"title": titles[language], "summary": summaries[language],
            "claims": [{"text": c[f"text_{language}"], "evidence": c["evidence"]} for c in claims[language]]} for language in ("en", "ko")},
        "model": client.model, "verification": "source_consistency_checked",
        "documents": [{"url": d.url, "sha256": hashlib.sha256(d.body.encode()).hexdigest()} for d in documents],
    }


def enrich_items(items):
    client = ai.Gemini()
    accepted = []
    for item in items:
        try:
            enriched = summarize_item(item, client)
        except ai.ArticleUnavailable as exc:
            print(f"[withheld] {item.source_name}: {exc}")
            continue
        accepted.append({"id": hashlib.sha256(item.link.encode()).hexdigest()[:16], "source": item.source_name,
            "url": item.link, "publishedAt": item.published_at.isoformat(), "tags": item.topic_tags, **enriched})
    return accepted
