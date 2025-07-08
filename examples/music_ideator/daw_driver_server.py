#!/usr/bin/env python3
"""
DAW Driver MCP Server

Handles sending generated musical content to DAW systems via MIDI, OSC, or file export.
"""

import asyncio
import json
import logging
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from mcp import ServerSession, Request, Response, types
from mcp.server import Server
from mcp.server.stdio import stdio_server


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for tool inputs/outputs
class RenderInput(BaseModel):
    chords: List[str] = Field(..., description="List of chords to render")
    melody: List[str] = Field(..., description="List of melody notes to render")
    tempo: Optional[int] = Field(120, description="Tempo in BPM")
    output_format: Optional[str] = Field("midi", description="Output format (midi, osc, json)")


class DAWDriverEngine:
    """Core DAW driver logic engine"""
    
    def __init__(self):
        self.current_key = "C"  # Default key
        self.current_tempo = 120
        self.output_directory = "output"
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
    
    def note_to_midi(self, note: str) -> int:
        """Convert note name to MIDI note number"""
        # Basic note to MIDI mapping (middle octave)
        note_map = {
            'C': 60, 'C#': 61, 'Db': 61,
            'D': 62, 'D#': 63, 'Eb': 63,
            'E': 64,
            'F': 65, 'F#': 66, 'Gb': 66,
            'G': 67, 'G#': 68, 'Ab': 68,
            'A': 69, 'A#': 70, 'Bb': 70,
            'B': 71
        }
        
        # Handle octave notation (e.g., C4, A3)
        if note[-1].isdigit():
            octave = int(note[-1])
            note_name = note[:-1]
            base_midi = note_map.get(note_name, 60)
            return base_midi + (octave - 4) * 12
        else:
            return note_map.get(note, 60)
    
    def chord_to_midi_notes(self, chord: str) -> List[int]:
        """Convert chord name to MIDI note numbers"""
        # Basic chord mappings
        chord_intervals = {
            'major': [0, 4, 7],
            'minor': [0, 3, 7],
            'dim': [0, 3, 6],
            'aug': [0, 4, 8],
            '7': [0, 4, 7, 10],
            'maj7': [0, 4, 7, 11],
            'm7': [0, 3, 7, 10]
        }
        
        # Parse chord name
        root_note = chord[0]
        if len(chord) > 1 and chord[1] in ['#', 'b']:
            root_note = chord[:2]
            chord_type = chord[2:]
        else:
            chord_type = chord[1:]
        
        # Determine chord type
        if chord_type == '':
            intervals = chord_intervals['major']
        elif chord_type == 'm':
            intervals = chord_intervals['minor']
        elif chord_type == 'dim':
            intervals = chord_intervals['dim']
        elif chord_type == 'aug':
            intervals = chord_intervals['aug']
        elif chord_type == '7':
            intervals = chord_intervals['7']
        elif chord_type == 'maj7':
            intervals = chord_intervals['maj7']
        elif chord_type == 'm7':
            intervals = chord_intervals['m7']
        else:
            intervals = chord_intervals['major']  # Default
        
        # Get root MIDI note
        root_midi = self.note_to_midi(root_note)
        
        # Build chord
        chord_notes = [root_midi + interval for interval in intervals]
        return chord_notes
    
    def render_to_daw_mock(self, chords: List[str], melody: List[str], 
                          tempo: int = 120, output_format: str = "midi") -> str:
        """Mock implementation of rendering to DAW"""
        logger.info(f"🎵 Rendering to DAW (Mock Implementation)")
        logger.info(f"   Chords: {chords}")
        logger.info(f"   Melody: {melody}")
        logger.info(f"   Tempo: {tempo} BPM")
        logger.info(f"   Format: {output_format}")
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "midi":
            return self._render_to_midi(chords, melody, tempo, timestamp)
        elif output_format == "osc":
            return self._render_to_osc(chords, melody, tempo, timestamp)
        elif output_format == "json":
            return self._render_to_json(chords, melody, tempo, timestamp)
        else:
            return f"Unknown output format: {output_format}"
    
    def _render_to_midi(self, chords: List[str], melody: List[str], 
                       tempo: int, timestamp: str) -> str:
        """Mock MIDI rendering"""
        # In a real implementation, this would use mido or similar MIDI library
        midi_data = {
            "format": "midi",
            "tempo": tempo,
            "tracks": []
        }
        
        # Chord track
        chord_track = {
            "name": "Chords",
            "notes": []
        }
        
        time_position = 0
        for chord in chords:
            midi_notes = self.chord_to_midi_notes(chord)
            for note in midi_notes:
                chord_track["notes"].append({
                    "note": note,
                    "velocity": 80,
                    "start_time": time_position,
                    "duration": 1920  # Quarter note duration in ticks
                })
            time_position += 1920
        
        midi_data["tracks"].append(chord_track)
        
        # Melody track
        melody_track = {
            "name": "Melody",
            "notes": []
        }
        
        time_position = 0
        for note in melody:
            midi_note = self.note_to_midi(note)
            melody_track["notes"].append({
                "note": midi_note,
                "velocity": 90,
                "start_time": time_position,
                "duration": 480  # Sixteenth note duration in ticks
            })
            time_position += 480
        
        midi_data["tracks"].append(melody_track)
        
        # Save mock MIDI data
        filename = f"{self.output_directory}/composition_{timestamp}.midi.json"
        with open(filename, 'w') as f:
            json.dump(midi_data, f, indent=2)
        
        return f"✅ MIDI data rendered to: {filename}\n" \
               f"🎹 Chord track: {len(chords)} chords\n" \
               f"🎼 Melody track: {len(melody)} notes\n" \
               f"⏱️ Tempo: {tempo} BPM"
    
    def _render_to_osc(self, chords: List[str], melody: List[str], 
                      tempo: int, timestamp: str) -> str:
        """Mock OSC rendering"""
        # In a real implementation, this would use python-osc library
        osc_messages = []
        
        # Generate OSC messages for chords
        time_position = 0.0
        for chord in chords:
            midi_notes = self.chord_to_midi_notes(chord)
            for note in midi_notes:
                osc_messages.append({
                    "address": "/daw/chord/note_on",
                    "args": [note, 80, time_position],  # note, velocity, time
                    "timestamp": time_position
                })
                osc_messages.append({
                    "address": "/daw/chord/note_off",
                    "args": [note, time_position + 2.0],  # note, time
                    "timestamp": time_position + 2.0
                })
            time_position += 2.0
        
        # Generate OSC messages for melody
        time_position = 0.0
        for note in melody:
            midi_note = self.note_to_midi(note)
            osc_messages.append({
                "address": "/daw/melody/note_on",
                "args": [midi_note, 90, time_position],  # note, velocity, time
                "timestamp": time_position
            })
            osc_messages.append({
                "address": "/daw/melody/note_off",
                "args": [midi_note, time_position + 0.5],  # note, time
                "timestamp": time_position + 0.5
            })
            time_position += 0.5
        
        # Save mock OSC data
        filename = f"{self.output_directory}/composition_{timestamp}.osc.json"
        with open(filename, 'w') as f:
            json.dump(osc_messages, f, indent=2)
        
        return f"✅ OSC messages rendered to: {filename}\n" \
               f"📡 Total messages: {len(osc_messages)}\n" \
               f"⏱️ Tempo: {tempo} BPM"
    
    def _render_to_json(self, chords: List[str], melody: List[str], 
                       tempo: int, timestamp: str) -> str:
        """Render to JSON format"""
        composition_data = {
            "timestamp": timestamp,
            "tempo": tempo,
            "key": self.current_key,
            "chords": chords,
            "melody": melody,
            "chord_analysis": [
                {
                    "chord": chord,
                    "midi_notes": self.chord_to_midi_notes(chord)
                }
                for chord in chords
            ],
            "melody_analysis": [
                {
                    "note": note,
                    "midi_note": self.note_to_midi(note)
                }
                for note in melody
            ]
        }
        
        filename = f"{self.output_directory}/composition_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(composition_data, f, indent=2)
        
        return f"✅ Composition data saved to: {filename}\n" \
               f"🎵 Format: JSON\n" \
               f"📊 Chords: {len(chords)}, Melody notes: {len(melody)}"
    
    def get_current_key(self) -> str:
        """Get the current key setting"""
        return self.current_key
    
    def set_current_key(self, key: str):
        """Set the current key"""
        self.current_key = key
        logger.info(f"🎹 Current key set to: {key}")


# Initialize the DAW driver engine
daw_engine = DAWDriverEngine()

# Create the MCP server
server = Server("daw-driver")


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available DAW driver tools"""
    return [
        types.Tool(
            name="render_to_daw",
            description="Render chords and melody to DAW via MIDI, OSC, or file export",
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
            description="Get the current key setting",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="set_current_key",
            description="Set the current key for the DAW",
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
            description="List generated output files",
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
            # Validate input
            input_data = RenderInput(**arguments)
            
            result = daw_engine.render_to_daw_mock(
                input_data.chords,
                input_data.melody,
                input_data.tempo,
                input_data.output_format
            )
            
            return [types.TextContent(
                type="text",
                text=result
            )]
        
        elif name == "get_current_key":
            current_key = daw_engine.get_current_key()
            return [types.TextContent(
                type="text",
                text=f"Current key: {current_key}"
            )]
        
        elif name == "set_current_key":
            key = arguments.get("key", "C")
            daw_engine.set_current_key(key)
            return [types.TextContent(
                type="text",
                text=f"✅ Key set to: {key}"
            )]
        
        elif name == "list_output_files":
            # List files in output directory
            output_files = []
            if os.path.exists(daw_engine.output_directory):
                for file in os.listdir(daw_engine.output_directory):
                    if file.endswith(('.json', '.midi.json', '.osc.json')):
                        output_files.append(file)
            
            if output_files:
                return [types.TextContent(
                    type="text",
                    text=f"📁 Output files:\n" + "\n".join(f"  • {file}" for file in output_files)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="📁 No output files found"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point for the DAW driver server"""
    logger.info("Starting DAW Driver MCP Server")
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())