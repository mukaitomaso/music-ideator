#!/usr/bin/env python3
"""
Music Theory MCP Server

Provides music theory generation tools including chord progressions and melodies.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from mcp import ServerSession, Request, Response, types
from mcp_agent.agents.agent import Agent
from mcp.server import Server, MCPToolServer, ToolDefinition, MCPApp
from mcp.server.stdio import stdio_server
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for tool inputs/outputs
class ProgressionInput(BaseModel):
    mood: str = Field(..., description="The mood or emotion (e.g., 'happy', 'sad', 'dreamy', 'energetic')")
    key: str = Field(..., description="The musical key (e.g., 'C', 'D', 'Am', 'F#m')")
    genre: str = Field(..., description="The genre (e.g., 'pop', 'jazz', 'lofi', 'classical')")

class ProgressionOutput(BaseModel):
    chords: List[str]

class MelodyInput(BaseModel):
    chords: List[str] = Field(..., description="List of chords to generate melody over")
    mood: str = Field(..., description="The mood or emotion")
    rhythm_style: str = Field(..., description="Rhythm style (e.g., 'smooth', 'staccato', 'syncopated')")

class MelodyOutput(BaseModel):
    melody: List[str]


class MusicEngine():

    def __init__(self):
        self.llm: Optional[OpenAIAugmentedLLM] = None
        self.agent: Optional[Agent] = None
        self.app: Optional[MCPApp] = None
        self.initialize_llm()

    async def initialize_llm(self):
          """Initialize the LLM for music generation"""
          try:
              # Create MCP app with configuration
              self.app = MCPApp(name="music_theory_agent")

              async with self.app.run() as agent_app:
                  context = agent_app.context

                  # Create agent with music theory expertise
                  self.agent = Agent(
                      name="music_theorist",
                      instruction="""You are an expert music theorist and composer.
                      You have deep knowledge of:
                      - Music theory, harmony, and chord progressions
                      - Different musical genres and their characteristics
                      - Emotional expression through music
                      - Melody composition and voice leading
                      - Music analysis and interpretation

                      Always provide creative, musically sound suggestions that align with
                      the requested mood, key, and genre. Be specific and practical.""",
                      server_names=[]  # No additional MCP servers needed
                  )

                  async with self.agent:
                      # Attach LLM to agent
                      self.llm = await self.agent.attach_llm(OpenAIAugmentedLLM)
                      logger.info("Music Theory Server: LLM initialized successfully")

          except Exception as e:
              logger.error(f"Failed to initialize LLM: {e}")
              self.llm = None

    
    
    async def get_chord_progression(self, mood: str, key: str, genre: str) -> List[str]:
        """Generate chord progression based on mood, key, and genre"""
        
        prompt = f"""
              Generate a chord progression for the following specifications:
              - Mood: {mood}
              - Key: {key}
              - Genre: {genre}

              Please provide:
              1. A chord progression (4-6 chords) that fits the mood and genre
              2. Brief explanation of why this progression works

              Return the response in this format:
              CHORDS: [chord1, chord2, chord3, chord4]
              EXPLANATION: [brief explanation]

              Example:
              CHORDS: ['C', 'Am', 'F', 'G']
              EXPLANATION: This I-vi-IV-V progression in C major creates a happy, uplifting feel perfect for pop music.
              """
        pattern = await self.llm.generate_str(prompt )
        
        # Parse the response to extract chords
        chords = self._parse_chord_response(response)
        if chords:
            logger.info(f"LLM generated progression: {chords}")
            return chords
        else:
            logger.warning("Failed to parse LLM response, using fallback")
            return [] # no fallback for prototype
    
    
    async def generate_melody(self, chords: List[str], mood: str, rhythm_style: str) -> List[str]:
        prompt = f"""
              Generate a melody for the following chord progression:
              - Chords: {chords}
              - Mood: {mood}
              - Rhythm style: {rhythm_style}

              Please provide:
              1. A sequence of melody notes that work well over these chords
              2. Consider the mood and rhythm style in your note choices
              3. Provide about 2-4 notes per chord

              Return the response in this format:
              MELODY: [note1, note2, note3, note4, ...]
              EXPLANATION: [brief explanation of melodic choices]

              Example:
              MELODY: ['C', 'E', 'G', 'A', 'C', 'E', 'F', 'A', 'G', 'E', 'C', 'D']
              EXPLANATION: This melody emphasizes chord tones and creates a smooth, flowing line.
              """
        pattern = await self.llm.generate_str(prompt)
        
        melody = self._parse_melody_response(response)
        if melody:
            logger.info(f"LLM generated melody: {melody}")
            return melody
        else:
            logger.warning("Failed to parse LLM melody response, using fallback")
            return [] # no fallback for prototype
    
    def _parse_chord_response(self, response: str) -> List[str]:
          """Parse LLM response to extract chord progression"""
          try:
              # Look for CHORDS: line
              lines = response.split('\n')
              for line in lines:
                  if line.strip().startswith('CHORDS:'):
                      # Extract the chord list
                      chord_part = line.split('CHORDS:')[1].strip()
                      # Remove brackets and split by comma
                      chord_part = chord_part.strip('[]')
                      chords = [chord.strip().strip("'\"") for chord in chord_part.split(',')]
                      return [chord for chord in chords if chord]  # Filter empty strings
          except Exception as e:
              logger.error(f"Error parsing chord response: {e}")
          return []

    def _parse_melody_response(self, response: str) -> List[str]:
        """Parse LLM response to extract melody notes"""
        try:
            # Look for MELODY: line
            lines = response.split('\n')
            for line in lines:
                if line.strip().startswith('MELODY:'):
                    # Extract the melody list
                    melody_part = line.split('MELODY:')[1].strip()
                    # Remove brackets and split by comma
                    melody_part = melody_part.strip('[]')
                    notes = [note.strip().strip("'\"") for note in melody_part.split(',')]
                    return [note for note in notes if note]  # Filter empty strings
        except Exception as e:
            logger.error(f"Error parsing melody response: {e}")
        return []
    
# Initialize the music theory engine
music_engine = MusicEngine()

# Create the MCP server
server = MCPToolServer("music-theory")

server.add_tool(
    ToolDefinition(
        name="suggest_progression",
        description="Suggest a chord progression based on mood, key, and genre.",
        input_model=ProgressionInput,
        output_model=ProgressionOutput,
        func=music_engine.get_chord_progression
    )
)

server.add_tool(
    ToolDefinition(
        name="generate_melody",
        description="Generate a melody to fit a chord progression and mood.",
        input_model=MelodyInput,
        output_model=MelodyOutput,
        func=music_engine.generate_melody
    )
)

async def main():
    """Main entry point for the music theory server"""
    logger.info("Starting Music Theory MCP Server")
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())