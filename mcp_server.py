import os
import sqlite3
from collections.abc import Sequence
from typing import Tuple

# Tools dependencies
import requests

# Default MCP server dependencies
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextResourceContents, Tool

app = Server("my-serveur")

# load environment variables from .env
from dotenv import load_dotenv

load_dotenv()


##
# Define some Resources
##


@app.list_resources()
async def list_resources():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(current_dir, "datasources/docs")
    file_path = os.path.join(docs_dir, "demo-document.md")
    file_uri = f"file://{file_path.replace(os.sep, '/')}"
    print("Resource file path:", file_uri)

    ressources = [Resource(uri=file_uri, name="Demo Document", mimeType="text/markdown")]
    print("List of ressources:", ressources)
    return ressources


from urllib.parse import unquote, urlparse


@app.read_resource()
async def read_resource(uri: str):
    parsed = urlparse(uri)

    if parsed.scheme == "file":
        # Décoder le chemin (gère les espaces et caractères spéciaux)
        file_path = unquote(parsed.path)

        if file_path.endswith("guide.md") and os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                return TextResourceContents(uri=uri, mimeType="text/markdown", text=content)
            except Exception as e:
                return TextResourceContents(uri=uri, mimeType="text/markdown", text=f"# Erreur de lecture\n{str(e)}")


##
# Add tools
##
@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="calculate",
            description="Effectue un calcul mathématique",
            inputSchema={
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        ),
        Tool(
            name="weather",
            description="Fournit les prévisions météorologiques pour une ville donnée",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        ),
        Tool(
            name="execute_sqlite",
            description="Exécute une requête SQL sur une base de données SQLite locale et retourne les résultats.",
            inputSchema={
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"],
            },
        ),
    ]


##
# Tool implementations
##
def execute_sqlite(self, sql: str):
    print("SQLiteDataSource executing query: {}", sql)
    from pathlib import Path

    db_path = "datasources/databases/demo-database.db"
    if not Path(db_path).exists():
        raise ValueError(f"Database path does not exist: {db_path}")

    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(sql)
        rows: Sequence[Tuple[object, ...]] = cursor.fetchall()
    return rows


def get_weather_from_api(city: str) -> str:
    API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    if not API_KEY:
        return "Erreur: La clé API OPENWEATHERMAP_API_KEY n'est pas définie."

    API = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=fr&appid={API_KEY}"
    print("Requesting weather for city:", city)

    try:
        response = requests.get(API, timeout=10, verify=False)
        print("API Response Status Code:", response.status_code)

        if response.status_code != 200:
            return f"Erreur API: {response.status_code} - {response.text}"

        data = response.json()
        return f"Le temps à {city} est {data['weather'][0]['description']} avec {data['main']['temp']}°C."
    except requests.exceptions.SSLError:
        return "Erreur SSL: Problème de certificat. Vérifiez votre configuration réseau."
    except requests.exceptions.RequestException as e:
        return f"Erreur de connexion: {str(e)}"


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "calculate":
        result = eval(arguments["expression"])
        return {"result": result}
    if name == "weather":
        city = arguments["city"]
        # Simuler une réponse météo
        # return {"forecast": f"Le temps à {city} est ensoleillé avec 25°C."}
        # Meteo via API
        return {"forecast": get_weather_from_api(city)}
    if name == "execute_sqlite":
        sql = arguments["sql"]
        rows = execute_sqlite(None, sql)
        return {"rows": [list(row) for row in rows]}


##
# Démarrage du serveur MCP
##
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
