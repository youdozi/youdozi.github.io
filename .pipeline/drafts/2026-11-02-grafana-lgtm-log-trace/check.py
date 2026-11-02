import base64
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

trace_id = sys.argv[1]
if not re.fullmatch(r"[0-9a-f]{32}", trace_id):
    raise SystemExit("usage: python check.py <32-character trace_id>")
base = "http://127.0.0.1:13000/api/datasources/proxy/uid/"


def get(path, params=None):
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.load(response)


query = '{service_name="checkout-demo"} | trace_id = "' + trace_id + '"'
last_error = None
for attempt in range(30):
    try:
        result = get("loki/loki/api/v1/query_range", {
            "query": query, "since": "1h", "limit": 100})
        entries = [(stream["stream"], value)
                   for stream in result["data"]["result"]
                   for value in stream["values"]]
        assert sorted(value[1] for _, value in entries) == [
            "checkout_started", "inventory_unavailable"]
        data = get("tempo/api/traces/" + trace_id)
        spans = [span for batch in data["batches"]
                 for scope in batch["scopeSpans"] for span in scope["spans"]]
        by_name = {span["name"]: span for span in spans}
        assert len(spans) == 2
        assert set(by_name) == {"checkout", "inventory.lookup"}
        parent, child = by_name["checkout"], by_name["inventory.lookup"]
        assert child["parentSpanId"] == parent["spanId"]
        for span in spans:
            assert base64.b64decode(span["traceId"]).hex() == trace_id
            assert span["status"]["code"] == "STATUS_CODE_ERROR"
        for labels, value in entries:
            expected = parent if value[1] == "checkout_started" else child
            assert labels["trace_id"] == trace_id
            assert labels["span_id"] == base64.b64decode(expected["spanId"]).hex()
        series = get("loki/loki/api/v1/series", {
            "match[]": '{service_name="checkout-demo"}', "since": "1h"})
        assert series["data"]
        assert all("trace_id" not in labels and "span_id" not in labels
                   for labels in series["data"])
        absent = get("loki/loki/api/v1/query_range", {
            "query": '{service_name="checkout-demo"} | trace_id = "' + "0" * 32 + '"',
            "since": "1h", "limit": 10})
        assert absent["data"]["result"] == []
        print(json.dumps({"trace_id": trace_id, "logs": len(entries),
                          "spans": len(spans), "parent_child_match": True,
                          "log_span_match": True, "trace_id_not_indexed": True,
                          "nonmatching_trace_returns_no_logs": True}))
        break
    except (AssertionError, KeyError, urllib.error.URLError, TimeoutError) as error:
        last_error = repr(error)
        if attempt == 29:
            raise SystemExit("verification failed: " + last_error)
        time.sleep(2)
