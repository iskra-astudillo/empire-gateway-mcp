"""Connect a local MCP client to the hosted service using Python 3."""
import argparse
import getpass
import json
import os
import sys
from pathlib import Path
from urllib import error, request

SLUG = "empire-gateway"
BASE = "https://auth.eliteaiempire.com"
VERSION = "2025-11-25"


class Direct(request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def send(path, key, body=None, method="POST"):
    headers = {"Authorization":"Bearer "+key, "Content-Type":"application/json",
               "Accept":"application/json, text/event-stream", "MCP-Protocol-Version":VERSION}
    req = request.Request(BASE+path, data=json.dumps(body).encode() if body is not None else b"",
                          headers=headers, method=method)
    try:
        with request.build_opener(Direct).open(req, timeout=20) as response:
            raw = response.read(1048577)
    except error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}. Check the key, the product permissions and the request.") from None
    if len(raw)>1048576:
        raise SystemExit("Response too large.")
    return json.loads(raw) if raw else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key-file", type=Path, help="private local file for the MCP read key")
    parsers = parser.add_subparsers(dest="action",required=True)
    for name in ("connect","list","revoke"):
        parsers.add_parser(name)
    call = parsers.add_parser("call")
    call.add_argument("tool")
    call.add_argument("arguments",type=json.loads)
    args = parser.parse_args()
    path, access = "/mcp/"+SLUG, "/mcp-access/"+SLUG
    if args.action == "connect":
        if not args.key_file:
            parser.error("connect requires --key-file")
        native = os.environ.get("PRODUCT_API_KEY") or getpass.getpass("Product API key: ")
        # Reserve the file before issuing the credential so existing keys cannot be overwritten.
        with os.fdopen(os.open(args.key_file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),"w") as f:
            try:
                reply = send(access,native)
                if reply.get("server_url") != BASE+path:
                    raise ValueError("Unexpected server")
                f.write(reply["access_key"]+"\n")
            except BaseException:
                args.key_file.unlink(missing_ok=True)
                raise
        print("Read key saved to the private file. It expires in 24 hours.")
        return
    key = args.key_file.read_text().strip() if args.key_file else os.environ.get("MCP_READ_KEY") or getpass.getpass("MCP read key: ")
    if args.action == "revoke":
        send(access,key,method="DELETE")
        if args.key_file:
            args.key_file.unlink()
        return
    def rpc(mid, method, params):
        reply = send(path,key,{"jsonrpc":"2.0","id":mid,"method":method,"params":params})
        if reply.get("id") != mid or "result" not in reply:
            raise SystemExit("The server could not complete the request.")
        return reply["result"]
    init = rpc(1,"initialize",{"protocolVersion":VERSION,"capabilities":{},"clientInfo":{"name":SLUG+"-client","version":"1"}})
    if init.get("protocolVersion") != VERSION:
        raise SystemExit("Incompatible protocol version.")
    send(path,key,{"jsonrpc":"2.0","method":"notifications/initialized"})
    result = rpc(2,"tools/list",{}) if args.action=="list" else rpc(2,"tools/call",{"name":args.tool,"arguments":args.arguments})
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if result.get("isError"):
        sys.exit(1)


if __name__ == "__main__":
    main()
