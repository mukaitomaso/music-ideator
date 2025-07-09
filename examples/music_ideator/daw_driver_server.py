#!/usr/bin/env python3
"""
Simple DAW Driver MCP Server - Hello World Implementation

This is a simplified version that just returns "Hello World" responses but keeps the same tool names.
"""

import asyncio
import logging
from typing import List, Dict, Any

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create the MCP server
server = Server("daw-driver")


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available DAW driver tools"""
    return [
        types.Tool(
            name="render_to_daw",
            description="Render chords and melody to DAW (Hello World mock)",
            inputSchema={
                "type": "object",
                "properties": {
                    "chords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of chords to render"
                    },
                    "melody": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of melody notes to render"
                    },
                    "tempo": {
                        "type": "integer",
                        "description": "Tempo in BPM",
                        "default": 120
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (midi, osc, json)",
                        "enum": ["midi", "osc", "json"],
                        "default": "midi"
                    }
                },
                "required": ["chords", "melody"]
            }
        ),
        types.Tool(
            name="get_current_key",
            description="Get the current key setting (Hello World mock)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="set_current_key",
            description="Set the current key for the DAW (Hello World mock)",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The musical key to set (e.g., 'C', 'Am', 'F#')"
                    }
                },
                "required": ["key"]
            }
        ),
        types.Tool(
            name="list_output_files",
            description="List generated output files (Hello World mock)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "render_to_daw":
            chords = arguments.get("chords", [])
            melody = arguments.get("melody", [])
            tempo = arguments.get("tempo", 120)
            output_format = arguments.get("output_format", "midi")
            
            return [types.TextContent(
                type="text",
                text=f"🎵 Hello World from DAW Driver! 🎵\n"
                     f"Received {len(chords)} chords: {chords}\n"
                     f"Received {len(melody)} melody notes: {melody}\n"
                     f"Tempo: {tempo} BPM\n"
                     f"Format: {output_format}\n"
                     f"✅ Successfully rendered to DAW (mock implementation)"
            )]
        
        elif name == "get_current_key":
            return [types.TextContent(
                type="text",
                text="🎵 Hello World! Current key: C major 🎵"
            )]
        
        elif name == "set_current_key":
            key = arguments.get("key", "C")
            return [types.TextContent(
                type="text",
                text=f"🎵 Hello World! Key set to: {key} 🎵"
            )]
        
        elif name == "list_output_files":
            return [types.TextContent(
                type="text",
                text="🎵 Hello World! No output files (mock implementation) 🎵"
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"🎵 Hello World! Unknown tool: {name} 🎵"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"🎵 Hello World! Error: {str(e)} 🎵"
        )]


async def main():
    """Main entry point for the DAW driver server"""
    logger.info("Starting Simple DAW Driver MCP Server (Hello World)")
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())