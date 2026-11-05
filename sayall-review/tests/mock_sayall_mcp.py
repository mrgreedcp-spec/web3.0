#!/usr/bin/env python3
"""模拟 SayAll MCP Helper（stdio），供测试用。从 MOCK_RECORDS 指向的 JSON 读记录，分页大小 2。"""
import json, os, sys
recs = json.load(open(os.environ["MOCK_RECORDS"], encoding="utf-8"))
if os.environ.get("SAYALL_MCP_ACCESS_TOKEN") != "test-token":
    bad_auth = True
else:
    bad_auth = False
for line in sys.stdin:
    msg = json.loads(line)
    if "id" not in msg:
        continue
    m, rid = msg["method"], msg["id"]
    if m == "initialize":
        res = {"protocolVersion": msg["params"]["protocolVersion"], "capabilities": {"tools": {}},
               "serverInfo": {"name": "mock-sayall", "version": "0"}}
    elif m == "tools/call":
        a = msg["params"]["arguments"]
        if bad_auth:
            res = {"isError": True, "content": [{"type": "text", "text": "invalid credentials"}]}
        else:
            sel = [r for r in recs if a["startedAtOrAfter"] <= r["startedAt"] and r["endedAt"] < a["endedAtBefore"]]
            start = int(a.get("cursor") or 0)
            page = sel[start:start + 2]
            more = start + 2 < len(sel)
            body = {"records": page, "nextCursor": str(start + 2) if more else None, "hasMore": more, "skippedFileCount": 0}
            res = {"content": [{"type": "text", "text": json.dumps(body)}]}
    else:
        print(json.dumps({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "no"}}), flush=True)
        continue
    print("debug noise line", flush=True) if m == "initialize" else None
    print(json.dumps({"jsonrpc": "2.0", "id": rid, "result": res}), flush=True)
