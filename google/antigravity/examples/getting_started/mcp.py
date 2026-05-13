# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""MCP Integration example for Google Antigravity SDK.

This example demonstrates how to connect an agent to external MCP servers
using stdio, SSE, and Streamable HTTP transports.
"""

import asyncio
import os

from google.antigravity import agent
from google.antigravity import types
from google.antigravity.connections import local


async def mcp_stdio(mcp_server_path: str):
  """Showcases the Stdio transport."""
  print("\n--- Showcasing Stdio Transport ---")
  config = local.LocalAgentConfig(
      mcp_servers=[
          types.McpStdioServer(
              command="python3",
              args=[mcp_server_path, "--transport=stdio"],
          )
      ]
  )

  async with agent.Agent(config) as my_agent:
    prompt = "Use the pirate_multiply tool to multiply 5 and 7."
    print(f"User: {prompt}")
    response = await my_agent.chat(prompt)
    print(f"Agent: {await response.text()}")


async def mcp_sse(mcp_server_path: str):
  """Showcases the SSE transport."""
  print("\n--- Showcasing SSE Transport ---")
  port = 8001
  # Start MCP server in background
  process = await asyncio.create_subprocess_exec(
      "python3",
      mcp_server_path,
      f"--port={port}",
      "--transport=sse",
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.STDOUT,
  )
  
  # Wait for server to start
  assert process.stdout is not None
  while True:
    line = await process.stdout.readline()
    if not line:
      break
    line_str = line.decode("utf-8")
    print(f"[SSE Server] {line_str.strip()}")
    if "Uvicorn running on" in line_str:
      break

  config = local.LocalAgentConfig(
      mcp_servers=[
          types.McpSseServer(url=f"http://localhost:{port}/sse")
      ]
  )

  try:
    async with agent.Agent(config) as my_agent:
      prompt = "Use the pirate_multiply tool to multiply 5 and 7."
      print(f"User: {prompt}")
      response = await my_agent.chat(prompt)
      print(f"Agent: {await response.text()}")
  finally:
    process.terminate()
    await process.wait()


async def mcp_http(mcp_server_path: str):
  """Showcases the Streamable HTTP transport."""
  print("\n--- Showcasing Streamable HTTP Transport ---")
  port = 8002
  # Start MCP server in background
  process = await asyncio.create_subprocess_exec(
      "python3",
      mcp_server_path,
      f"--port={port}",
      "--transport=streamable-http",
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.STDOUT,
  )
  
  # Wait for server to start
  assert process.stdout is not None
  while True:
    line = await process.stdout.readline()
    if not line:
      break
    line_str = line.decode("utf-8")
    print(f"[HTTP Server] {line_str.strip()}")
    if "Uvicorn running on" in line_str:
      break

  config = local.LocalAgentConfig(
      mcp_servers=[
          types.McpStreamableHttpServer(url=f"http://localhost:{port}/mcp")
      ]
  )

  try:
    async with agent.Agent(config) as my_agent:
      prompt = "Use the pirate_multiply tool to multiply 5 and 7."
      print(f"User: {prompt}")
      response = await my_agent.chat(prompt)
      print(f"Agent: {await response.text()}")
  finally:
    process.terminate()
    await process.wait()


async def main() -> None:
  # Setup path to the MCP server resource
  script_dir = os.path.dirname(os.path.abspath(__file__))
  resources_dir = os.path.join(script_dir, "..", "resources")
  mcp_server_path = os.path.join(resources_dir, "mcp_server.py")

  # Verify script exists
  if not os.path.exists(mcp_server_path):
    print(f"Error: MCP server script not found at {mcp_server_path}")
    return

  await mcp_stdio(mcp_server_path)
  await mcp_sse(mcp_server_path)
  await mcp_http(mcp_server_path)


if __name__ == "__main__":
  asyncio.run(main())
