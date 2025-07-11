#!/usr/bin/env python3
"""
Music Ideator Agent

Main entry point for the music ideation agent that uses two MCP servers:
- music-theory: Generates chord progressions and melodies
- daw-driver: Renders content to DAW systems

Example usage:
    python main.py
"""

import asyncio
import logging
import sys
from typing import Optional

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.human_input.handler import console_input_callback


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MusicIdeatorDemo:
    """Main demo class for the music ideator agent"""
    
    def __init__(self):
        self.app = MCPApp(name="music_ideator")
        self.agent: Optional[Agent] = None
        self.llm: Optional[OpenAIAugmentedLLM] = None
    
    async def setup_agent(self) -> Agent:
        """Set up the music ideator agent with both MCP servers"""
        logger.info("🎵 Setting up Music Ideator Agent")
        
        # Create the agent with access to both MCP servers
        agent = Agent(
            name="music_ideator",
            instruction="""You are a creative music ideation agent with access to advanced music theory and DAW integration capabilities.

Your role:
1. Generate chord progressions based on mood, key, and genre preferences
2. Create complementary melodies that work with the generated chords
3. Analyze musical compositions to provide theory insights
4. Manipulate DAW applications to transcribe generated chord progressions and melodies

When generating music:
- Consider the emotional context and desired mood
- Apply appropriate music theory principles for the specified genre
- Create melodic lines that complement the harmonic structure
- Write final products to the connected DAW application

Always explain your musical choices and provide theory context when requested.
You can also accept feedback and iterate on compositions to refine them.

When a tool call fails, don't proceed and just terminate early, letting the user know.

Be creative, educational, and focus on producing high-quality musical ideas!""",
            server_names=["music-theory"], # server_names=["music-theory", "daw-driver"],
            human_input_callback=console_input_callback  # Enable human interaction
        )
        
        return agent
    
    async def demo_basic_workflow(self):
        """Run the basic music ideation workflow"""
        logger.info("🎼 Starting Basic Music Ideation Workflow")
        
        # Sample prompt as requested
        sample_prompt = ("Generate a dreamy chord progression and melody in D major "
                        "with a lofi vibe and send it to the DAW.")
        
        logger.info(f"📝 Sample prompt: {sample_prompt}")
        
        try:
            # Generate and render the composition
            result = await self.llm.generate_str(sample_prompt)
            logger.info(f"✅ Composition complete!")
            logger.info(f"📊 Result: {result}")
            
        except Exception as e:
            logger.error(f"❌ Error in basic workflow: {str(e)}")
            raise
    
    async def demo_interactive_workflow(self):
        """Run an interactive music ideation session"""
        logger.info("🎹 Starting Interactive Music Ideation Session")
        
        # Interactive prompts
        interactive_prompts = [
            "Create a jazz chord progression in Bb major with a smooth, sophisticated mood",
            "Now generate a melody over those chords with a syncopated rhythm style",
            "Analyze the musical theory behind this progression",
            "Render this composition to the DAW as a MIDI file"
        ]
        
        for i, prompt in enumerate(interactive_prompts, 1):
            logger.info(f"\n🎯 Step {i}: {prompt}")
            
            try:
                result = await self.llm.generate_str(prompt)
                logger.info(f"✅ Step {i} complete: {result}")
                
                # Small delay for readability
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ Error in step {i}: {str(e)}")
                continue
    
    async def demo_advanced_workflow(self):
        """Run an advanced workflow with multiple compositions"""
        logger.info("🎼 Starting Advanced Multi-Composition Workflow")
        
        # Advanced workflow with multiple styles
        compositions = [
            {
                "name": "Lofi Hip-Hop",
                "prompt": "Create a chill lofi hip-hop progression in Am with a dreamy, nostalgic feel"
            },
            {
                "name": "Pop Ballad",
                "prompt": "Generate an emotional pop ballad progression in F major with a melancholic mood"
            },
            {
                "name": "Jazz Standard",
                "prompt": "Create a sophisticated jazz progression in Bb major with smooth, professional feel"
            }
        ]
        
        for comp in compositions:
            logger.info(f"\n🎵 Creating {comp['name']}...")
            
            try:
                # Generate the composition
                result = await self.llm.generate_str(
                    f"{comp['prompt']}, then generate a complementary melody and render to DAW"
                )
                
                logger.info(f"✅ {comp['name']} complete!")
                logger.info(f"📊 Details: {result}")
                
            except Exception as e:
                logger.error(f"❌ Error creating {comp['name']}: {str(e)}")
                continue
    
    async def list_available_tools(self):
        """List all available tools from both MCP servers"""
        logger.info("🔧 Listing Available Tools")
        
        try:
            tools = await self.agent.list_tools()
            logger.info(f"📋 Available tools ({len(tools.tools)} total):")
            
            for tool in tools.tools:
                logger.info(f"  🛠️  {tool.name}: {tool.description}")
            
        except Exception as e:
            logger.error(f"❌ Error listing tools: {str(e)}")
    
    async def run_demo(self, demo_type: str = "basic"):
        """Run the music ideator demo"""
        logger.info(f"🚀 Starting Music Ideator Demo - {demo_type.upper()} mode")
        
        try:
            # Initialize the MCP app
            async with self.app.run() as mcp_app:
                logger.info("📡 MCP App initialized successfully")
                
                # Set up the agent
                self.agent = await self.setup_agent()
                
                # Connect to MCP servers
                async with self.agent:
                    logger.info("🔗 Agent connected to MCP servers")
                    
                    # List available tools
                    await self.list_available_tools()
                    
                    # Attach the LLM
                    self.llm = await self.agent.attach_llm(OpenAIAugmentedLLM)
                    logger.info("🤖 OpenAI LLM attached to agent")
                    
                    # Run the selected demo
                    if demo_type == "basic":
                        await self.demo_basic_workflow()
                    elif demo_type == "interactive":
                        await self.demo_interactive_workflow()
                    elif demo_type == "advanced":
                        await self.demo_advanced_workflow()
                    else:
                        logger.error(f"❌ Unknown demo type: {demo_type}")
                        return
                    
                    logger.info("🎉 Demo completed successfully!")
        
        except Exception as e:
            logger.error(f"❌ Demo failed: {str(e)}")
            raise


async def main():
    """Main entry point"""
    logger.info("🎵 Music Ideator Agent - Starting...")
    
    # Check command line arguments for demo type
    demo_type = "basic"
    if len(sys.argv) > 1:
        demo_type = sys.argv[1].lower()
        if demo_type not in ["basic", "interactive", "advanced"]:
            logger.error(f"❌ Invalid demo type: {demo_type}")
            logger.info("   Valid options: basic, interactive, advanced")
            sys.exit(1)
    
    # Create and run the demo
    demo = MusicIdeatorDemo()
    
    try:
        await demo.run_demo(demo_type)
        logger.info("🎵 Music Ideator Agent - Finished!")
    
    except KeyboardInterrupt:
        logger.info("⏹️  Demo interrupted by user")
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the main demo
    asyncio.run(main())