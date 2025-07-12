#!/usr/bin/env python3
"""
Music Theory MCP Server

Provides music theory generation workflows using the canonical MCPApp pattern.
"""

import asyncio
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from mcp_agent.app import MCPApp
from mcp_agent.server.app_server import create_mcp_server_for_app
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.executor.workflow import Workflow, WorkflowResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for workflow inputs/outputs
class ChordProgressionInput(BaseModel):
    mood: str = Field(..., description="The mood or emotion (e.g., 'happy', 'sad', 'dreamy', 'energetic')")
    key: str = Field(..., description="The musical key (e.g., 'C', 'D', 'Am', 'F#m')")
    genre: str = Field(..., description="The genre (e.g., 'pop', 'jazz', 'lofi', 'classical')")

class ChordProgressionOutput(BaseModel):
    chords: List[str] = Field(..., description="List of chord names")

class MelodyInput(BaseModel):
    chords: List[str] = Field(..., description="List of chords to generate melody over")
    mood: str = Field(..., description="The mood or emotion")
    rhythm_style: str = Field(..., description="Rhythm style (e.g., 'smooth', 'staccato', 'syncopated')")

class MelodyOutput(BaseModel):
    melody: List[str] = Field(..., description="List of melody notes")

# Create MCPApp
app = MCPApp(
    name="music-theory",
    description="Music theory generation agent with chord progressions and melodies"
)

@app.workflow
class ChordProgressionWorkflow(Workflow[ChordProgressionInput]):
    """Generate chord progressions based on mood, key, and genre"""
    
    @app.workflow_run
    async def run(self, input: ChordProgressionInput) -> WorkflowResult[ChordProgressionOutput]:
        # Create agent with music theory expertise
        agent = Agent(
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

        async with agent:
            # Attach LLM to agent
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            
            prompt = f"""
            Generate a chord progression for the following specifications:
            - Mood: {input["mood"]}
            - Key: {input["key"]}
            - Genre: {input["genre"]}

            Please provide:
            1. A chord progression (4-6 chords) that fits the mood and genre

            Return the response in this format:
            CHORDS: [chord1, chord2, chord3, chord4]

            Example:
            CHORDS: ['C', 'Am', 'F', 'G']
            """
            
            response = await llm.generate_str(message=prompt)
            
            # Parse the response
            chords = self._parse_chord_response(response)
            
            return WorkflowResult(
                value=ChordProgressionOutput(chords=chords)
            )
    
    def _parse_chord_response(self, response: str) -> List[str]:
        """Parse LLM response to extract chord progression and explanation"""
        chords = []
        
        try:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('CHORDS:'):
                    # Extract the chord list
                    chord_part = line.split('CHORDS:')[1].strip()
                    # Remove brackets and split by comma
                    chord_part = chord_part.strip('[]')
                    chords = [chord.strip().strip("'\"") for chord in chord_part.split(',')]
                    chords = [chord for chord in chords if chord]  # Filter empty strings
        except Exception as e:
            logger.error(f"Error parsing chord response: {e}")
            # Fallback
            chords = ['C', 'Am', 'F', 'G']
        
        return chords

@app.workflow
class MelodyWorkflow(Workflow[MelodyInput]):
    """Generate melodies to fit chord progressions"""
    
    @app.workflow_run
    async def run(self, input: MelodyInput) -> WorkflowResult[MelodyOutput]:
        # Create agent with music theory expertise
        agent = Agent(
            name="melody_composer",
            instruction="""You are an expert melody composer with deep knowledge of:
            - Melodic composition and voice leading
            - Chord-melody relationships
            - Rhythmic patterns and phrasing
            - Different musical styles and genres
            
            Create beautiful, singable melodies that complement the given chord progressions
            and match the specified mood and rhythm style.""",
            server_names=[]
        )

        async with agent:
            # Attach LLM to agent
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            
            prompt = f"""
            Generate a melody for the following chord progression:
            - Chords: {input["chords"]}
            - Mood: {input["mood"]}
            - Rhythm style: {input["rhythm_style"]}

            Please provide:
            1. A sequence of melody notes that work well over these chords
            2. Consider the mood and rhythm style in your note choices
            3. Provide about 2-4 notes per chord

            Return the response in this format:
            MELODY: [note1, note2, note3, note4, ...]

            Example:
            MELODY: ['C', 'E', 'G', 'A', 'C', 'E', 'F', 'A', 'G', 'E', 'C', 'D']
            """
            
            response = await llm.generate_str(message=prompt)
            
            # Parse the response
            melody = self._parse_melody_response(response)
            
            return WorkflowResult(
                value=MelodyOutput(melody=melody)
            )
    
    def _parse_melody_response(self, response: str) -> tuple[List[str], str]:
        """Parse LLM response to extract melody and explanation"""
        melody = []
        
        try:
            lines = response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('MELODY:'):
                    # Extract the melody list
                    melody_part = line.split('MELODY:')[1].strip()
                    # Remove brackets and split by comma
                    melody_part = melody_part.strip('[]')
                    melody = [note.strip().strip("'\"") for note in melody_part.split(',')]
                    melody = [note for note in melody if note]  # Filter empty strings
        except Exception as e:
            logger.error(f"Error parsing melody response: {e}")
            # Fallback
            melody = ['C', 'E', 'G', 'C']
        
        return melody

async def main():
    """Main entry point for the music theory server"""
    logger.info("Starting Music Theory MCP Server")
    
    # Run the server using the canonical pattern
    async with app.run() as agent_app:
        mcp_server = create_mcp_server_for_app(agent_app)
        await mcp_server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())