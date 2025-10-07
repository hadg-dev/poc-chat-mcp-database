import asyncio

from fastmcp import FastMCP

list_of_instances = []


class AbstractMCPInstance:
    def __init__(self, main_mcp: FastMCP):
        self.mcp: FastMCP = main_mcp
        list_of_instances.append(self)

    def start_mcp_server(self):
        self.mcp.run(transport="stdio")
        # self.mcp.run(transport="http", host="0.0.0.0", port=8080)


    def start_all(self):
        if not list_of_instances:
            raise ValueError("No MCP instances to start.")

        if len(list_of_instances) == 1:
            list_of_instances[0].start_mcp_server()
            return

        main_mcp = list_of_instances[0].mcp
        for instance in list_of_instances[1:]:
            sub_mcp = instance.mcp
            main_mcp.mount(sub_mcp, prefix=f"/{sub_mcp.name.replace(' ', '_').lower()}")
        main_mcp.run(transport="stdio")
        # main_mcp.run(transport="http", host="0.0.0.0", port=8080)
