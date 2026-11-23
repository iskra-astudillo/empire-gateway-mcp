# Empire Gateway MCP

Read the model IDs available to your Empire Gateway API key.

Use the Gateway API key you use for the model endpoint. The account page lives under Lumen. The model list comes directly from the Gateway engine. Looking up a model here does not run it.

[Product account or API docs](https://lumen.eliteaiempire.com/pricing#api)

From the GitHub repository, run the first command below and enter your product key at the hidden prompt. The second command lists the tools. The last command revokes the read key and removes the local file.

```sh
python3 client.py --key-file ./empire-gateway.key connect
python3 client.py --key-file ./empire-gateway.key list
python3 client.py --key-file ./empire-gateway.key revoke
```

Choose Streamable HTTP in your MCP client. Paste the endpoint below. In its private header settings, enter Authorization with the value Bearer followed by a space and the read key from your file.

https://auth.eliteaiempire.com/mcp/empire-gateway

To issue a read key directly, POST to https://auth.eliteaiempire.com/mcp-access/empire-gateway with your product key in the Authorization bearer header. Use the access_key from the response. To revoke it, send DELETE to the same address with the read key.

## Tools

- `list_models` — List model IDs returned for your Gateway account.

## Try it

Which model IDs can I use with my Gateway key?

## Access

The read key works for 24 hours. Each product key can make 60 MCP requests a minute. If you get HTTP 429, wait for the number of seconds in Retry-After. Revoke a connection as soon as you finish with it.

[Connection guide](https://auth.eliteaiempire.com/mcp-docs/empire-gateway) · [Server manifest](https://auth.eliteaiempire.com/mcp-docs/empire-gateway/server.json)
