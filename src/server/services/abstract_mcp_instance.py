import asyncio

from fastmcp import FastMCP

list_of_instances = []


class AbstractMCPInstance:
    def __init__(self, main_mcp: FastMCP):
        self.mcp: FastMCP = main_mcp
        list_of_instances.append(self)

    def start_mcp_server(self, transport: str = "stdio"):
        self.mcp.run(transport=transport)

    def start_all(self, transport: str = "stdio"):
        if not list_of_instances:
            raise ValueError("No MCP instances to start.")

        if len(list_of_instances) == 1:
            list_of_instances[0].start_mcp_server(transport=transport)
            return

        main_mcp = list_of_instances[0].mcp
        for instance in list_of_instances[1:]:
            sub_mcp = instance.mcp
            main_mcp.mount(sub_mcp, prefix=f"/{sub_mcp.name.replace(' ', '_').lower()}")
        main_mcp.run(transport=transport)
