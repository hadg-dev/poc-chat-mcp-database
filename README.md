# MCP Databases Agent (Server + CLI Client)

This repository contains a minimal Model Context Protocol (MCP) server and an interactive CLI client. The server exposes tools (calculator, weather lookup, SQLite query) and a markdown resource. The client connects over stdio and uses Anthropic to decide when to call tools.

This project serves as a demo and starting point for building MCP-based applications.

This educational example was developed to illustrate MCP concepts and tool/resource integration. First steps to build upon for more complex use cases.

## Highlights

- **MCP server** with:
  - Tools: `calculate`, `weather`, `execute_sqlite`
  - Resource: `datasources/docs/demo-document.md`
- **CLI client** that:
  - Connects via stdio to a server script
  - Uses Anthropic tool-calling to answer user prompts

## Project structure

- `mcp_server.py` — MCP server implementation
- `mcp_client_cli.py` — interactive CLI client
- `datasources/docs/demo-document.md` — sample resource
- `datasources/databases/demo-database.db` — sample SQLite DB (expected path)
- `docs/` — HTML/MD guides

## Prerequisites

- Python 3.10+ recommended
- An Anthropic API key for the client
- (Optional) OpenWeatherMap API key for weather tool

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file at the repo root:

```ini
# Required for the CLI client
ANTHROPIC_API_KEY=your_key_here

# Optional for the weather tool
OPENWEATHERMAP_API_KEY=your_key_here
```

## Run the MCP server

The server runs over stdio and is intended to be launched by the client.

```bash
python mcp_server.py
```

## Run the CLI client

The CLI takes the path to the server script (Python or Node) and opens an interactive prompt.

```bash
python mcp_client_cli.py mcp_server.py
```

Type your query and let the client call tools as needed. Use `quit` to exit.

## Available tools

- `calculate`: evaluates a math expression (string)
- `weather`: fetches weather from OpenWeatherMap for a city
- `execute_sqlite`: runs a SQL query against `datasources/databases/demo-database.db`

## Resources

The server exposes the resource:

- `file://.../datasources/docs/demo-document.md`

## Notes and best practices

- **Security**: `calculate` uses `eval` for demonstration. Do not expose this to untrusted input in production.
- **Certificates**: the weather tool currently sets `verify=False` in the HTTP request. This is not recommended in production.
- **SQLite path**: ensure `datasources/databases/demo-database.db` exists before calling `execute_sqlite`.

## Troubleshooting

- If the client fails to authenticate, confirm `ANTHROPIC_API_KEY` is set.
- If weather requests fail, verify `OPENWEATHERMAP_API_KEY` and network access.
- If resource reads fail, check that `datasources/docs/demo-document.md` exists.

## License

MIT License. See `LICENSE` file for details.
