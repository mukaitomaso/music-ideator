#!/usr/bin/env python3
"""
Music Theory MCP Server

Provides music theory generation tools including chord progressions and melodies.
"""

import asyncio
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from mcp import ServerSession, Request, Response, types
from mcp.server import Server
from mcp.server.stdio import stdio_server


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for tool inputs/outputs
class ProgressionInput(BaseModel):
    mood: str = Field(..., description="The mood or emotion (e.g., 'happy', 'sad', 'dreamy', 'energetic')")
    key: str = Field(..., description="The musical key (e.g., 'C', 'D', 'Am', 'F#m')")
    genre: str = Field(..., description="The genre (e.g., 'pop', 'jazz', 'lofi', 'classical')")


class MelodyInput(BaseModel):
    chords: List[str] = Field(..., description="List of chords to generate melody over")
    mood: str = Field(..., description="The mood or emotion")
    rhythm_style: str = Field(..., description="Rhythm style (e.g., 'smooth', 'staccato', 'syncopated')")


class AnalysisInput(BaseModel):
    chords: List[str] = Field(..., description="List of chords to analyze")


class MusicTheoryEngine:
    """Core music theory logic engine"""
    
    # Basic chord mappings by key
    MAJOR_SCALE_CHORDS = {
        'C': ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'Bdim'],
        'D': ['D', 'Em', 'F#m', 'G', 'A', 'Bm', 'C#dim'],
        'E': ['E', 'F#m', 'G#m', 'A', 'B', 'C#m', 'D#dim'],
        'F': ['F', 'Gm', 'Am', 'Bb', 'C', 'Dm', 'Edim'],
        'G': ['G', 'Am', 'Bm', 'C', 'D', 'Em', 'F#dim'],
        'A': ['A', 'Bm', 'C#m', 'D', 'E', 'F#m', 'G#dim'],
        'B': ['B', 'C#m', 'D#m', 'E', 'F#', 'G#m', 'A#dim'],
    }
    
    MINOR_SCALE_CHORDS = {
        'Am': ['Am', 'Bdim', 'C', 'Dm', 'Em', 'F', 'G'],
        'Bm': ['Bm', 'C#dim', 'D', 'Em', 'F#m', 'G', 'A'],
        'Cm': ['Cm', 'Ddim', 'Eb', 'Fm', 'Gm', 'Ab', 'Bb'],
        'Dm': ['Dm', 'Edim', 'F', 'Gm', 'Am', 'Bb', 'C'],
        'Em': ['Em', 'F#dim', 'G', 'Am', 'Bm', 'C', 'D'],
        'F#m': ['F#m', 'G#dim', 'A', 'Bm', 'C#m', 'D', 'E'],
        'Gm': ['Gm', 'Adim', 'Bb', 'Cm', 'Dm', 'Eb', 'F'],
    }
    
    # Common progression patterns
    PROGRESSION_PATTERNS = {
        'pop': {
            'happy': ['I', 'V', 'vi', 'IV'],
            'sad': ['vi', 'IV', 'I', 'V'],
            'dreamy': ['I', 'vi', 'IV', 'V'],
            'energetic': ['I', 'IV', 'V', 'I']
        },
        'jazz': {
            'smooth': ['ii', 'V', 'I', 'vi'],
            'dreamy': ['I', 'vi', 'ii', 'V'],
            'energetic': ['I', 'IV', 'V', 'I']
        },
        'lofi': {
            'dreamy': ['I', 'vi', 'IV', 'V'],
            'chill': ['vi', 'IV', 'I', 'V'],
            'smooth': ['I', 'V', 'vi', 'IV']
        }
    }
    
    # Note sequences for melodies
    SCALE_NOTES = {
        'C': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
        'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
        'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
        'F': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E'],
        'G': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
        'A': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
        'B': ['B', 'C#', 'D#', 'E', 'F#', 'G#', 'A#'],
        'Am': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
        'Bm': ['B', 'C#', 'D', 'E', 'F#', 'G', 'A'],
        'Cm': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb'],
        'Dm': ['D', 'E', 'F', 'G', 'A', 'Bb', 'C'],
        'Em': ['E', 'F#', 'G', 'A', 'B', 'C', 'D'],
        'F#m': ['F#', 'G#', 'A', 'B', 'C#', 'D', 'E'],
        'Gm': ['G', 'A', 'Bb', 'C', 'D', 'Eb', 'F'],
    }
    
    def get_chord_progression(self, mood: str, key: str, genre: str) -> List[str]:
        """Generate chord progression based on mood, key, and genre"""
        # Get the appropriate chord set
        if key in self.MAJOR_SCALE_CHORDS:
            chord_set = self.MAJOR_SCALE_CHORDS[key]
        elif key in self.MINOR_SCALE_CHORDS:
            chord_set = self.MINOR_SCALE_CHORDS[key]
        else:
            # Default to C major if key not found
            chord_set = self.MAJOR_SCALE_CHORDS['C']
        
        # Get pattern based on genre and mood
        pattern = self.PROGRESSION_PATTERNS.get(genre, {}).get(mood)
        if not pattern:
            # Default pattern
            pattern = ['I', 'vi', 'IV', 'V']
        
        # Convert roman numerals to actual chords
        roman_to_index = {
            'I': 0, 'ii': 1, 'iii': 2, 'IV': 3, 'V': 4, 'vi': 5, 'vii': 6
        }
        
        progression = []
        for roman in pattern:
            if roman in roman_to_index:
                progression.append(chord_set[roman_to_index[roman]])
            else:
                progression.append(chord_set[0])  # Default to I
        
        return progression
    
    def generate_melody(self, chords: List[str], mood: str, rhythm_style: str) -> List[str]:
        """Generate melody notes based on chord progression and mood"""
        # Determine key from first chord
        first_chord = chords[0] if chords else 'C'
        key = first_chord.replace('m', '').replace('dim', '')
        
        # Get scale notes
        scale_notes = self.SCALE_NOTES.get(key, self.SCALE_NOTES['C'])
        
        # Generate melody based on mood and rhythm style
        melody = []
        notes_per_chord = 4  # 4 notes per chord
        
        for chord in chords:
            # Get chord tones (simplified - just use root and third)
            root = chord.replace('m', '').replace('dim', '')
            chord_tones = [root]
            
            # Add some scale notes around the root
            if root in scale_notes:
                root_index = scale_notes.index(root)
                # Add notes around the root
                for i in range(notes_per_chord):
                    note_index = (root_index + i) % len(scale_notes)
                    melody.append(scale_notes[note_index])
            else:
                # Fallback to scale
                for i in range(notes_per_chord):
                    melody.append(scale_notes[i % len(scale_notes)])
        
        return melody
    
    def analyze_progression(self, chords: List[str]) -> str:
        """Analyze chord progression and provide theory explanation"""
        if not chords:
            return "No chords provided for analysis"
        
        # Basic analysis
        analysis = []
        analysis.append(f"Chord progression: {' - '.join(chords)}")
        
        # Determine likely key
        first_chord = chords[0]
        if 'm' in first_chord and 'dim' not in first_chord:
            key = first_chord
            analysis.append(f"Likely key: {key} (minor)")
        else:
            key = first_chord.replace('dim', '')
            analysis.append(f"Likely key: {key} (major)")
        
        # Check for common patterns
        if len(chords) >= 4:
            chord_str = ' '.join(chords)
            if any(pattern in chord_str for pattern in ['C F G', 'Am F C G', 'G Am F C']):
                analysis.append("Pattern: Contains popular pop progression elements")
            elif any(pattern in chord_str for pattern in ['ii V I', 'Dm G C']):
                analysis.append("Pattern: Contains jazz ii-V-I progression")
        
        # Mood assessment
        minor_count = sum(1 for chord in chords if 'm' in chord and 'dim' not in chord)
        if minor_count > len(chords) / 2:
            analysis.append("Mood: Tends toward melancholy or introspective")
        else:
            analysis.append("Mood: Tends toward bright or uplifting")
        
        return "\n".join(analysis)


# Initialize the music theory engine
music_engine = MusicTheoryEngine()

# Create the MCP server
server = Server("music-theory")


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available music theory tools"""
    return [
        types.Tool(
            name="suggest_progression",
            description="Suggest a chord progression based on mood, key, and genre",
            inputSchema={
                "type": "object",
                "properties": {
                    "mood": {"type": "string", "description": "The mood or emotion"},
                    "key": {"type": "string", "description": "The musical key"},
                    "genre": {"type": "string", "description": "The genre"}
                },
                "required": ["mood", "key", "genre"]
            }
        ),
        types.Tool(
            name="generate_melody",
            description="Generate melody notes based on chord progression and mood",
            inputSchema={
                "type": "object",
                "properties": {
                    "chords": {"type": "array", "items": {"type": "string"}, "description": "List of chords"},
                    "mood": {"type": "string", "description": "The mood or emotion"},
                    "rhythm_style": {"type": "string", "description": "Rhythm style"}
                },
                "required": ["chords", "mood", "rhythm_style"]
            }
        ),
        types.Tool(
            name="analyze_progression",
            description="Analyze a chord progression and provide theory explanation",
            inputSchema={
                "type": "object",
                "properties": {
                    "chords": {"type": "array", "items": {"type": "string"}, "description": "List of chords to analyze"}
                },
                "required": ["chords"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "suggest_progression":
            # Validate input
            input_data = ProgressionInput(**arguments)
            chords = music_engine.get_chord_progression(
                input_data.mood, input_data.key, input_data.genre
            )
            
            result = {
                "chords": chords,
                "key": input_data.key,
                "mood": input_data.mood,
                "genre": input_data.genre
            }
            
            return [types.TextContent(
                type="text",
                text=f"Generated chord progression: {chords}\n"
                     f"Key: {input_data.key}, Mood: {input_data.mood}, Genre: {input_data.genre}"
            )]
        
        elif name == "generate_melody":
            # Validate input
            input_data = MelodyInput(**arguments)
            melody_notes = music_engine.generate_melody(
                input_data.chords, input_data.mood, input_data.rhythm_style
            )
            
            return [types.TextContent(
                type="text",
                text=f"Generated melody: {melody_notes}\n"
                     f"Based on chords: {input_data.chords}\n"
                     f"Mood: {input_data.mood}, Style: {input_data.rhythm_style}"
            )]
        
        elif name == "analyze_progression":
            # Validate input
            input_data = AnalysisInput(**arguments)
            analysis = music_engine.analyze_progression(input_data.chords)
            
            return [types.TextContent(
                type="text",
                text=f"Music Theory Analysis:\n{analysis}"
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
    """Main entry point for the music theory server"""
    logger.info("Starting Music Theory MCP Server")
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())