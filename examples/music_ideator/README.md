# 🎵 Ableton Live Music Ideator Agent

A creative music ideation agent built with the mcp-agent framework that generates chord progressions and melodies using two specialized MCP servers.

## 🏗️ Architecture

This project demonstrates a **2-Server Music Ideator Agent** with the following components:

### MCP Servers
1. **Music Theory Server** (`music_theory_server.py`)
   - `suggest_progression(mood, key, genre)` → generates chord progressions
   - `generate_melody(chords, mood, rhythm_style)` → creates melody lines
   - `analyze_progression(chords)` → provides music theory analysis

2. **Daw Controller Server** provided by `ableton-mcp`: https://glama.ai/mcp/servers/@ahujasid/ableton-mcp

### Agent
- **music_ideator**: An OpenAI-powered agent with access to both servers
- Generates creative musical ideas and renders them for DAW production
- Supports interactive workflows and human-in-the-loop feedback

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository (if not already done)
cd examples/music_ideator

# Install dependencies
pip install -r requirements.txt

# Or use uv (recommended)
uv add -r requirements.txt
```

Next, refer to the ableton-mcp documentation to run the Ableton remote server in your Ableton DAW (Digital Audio Workstation): https://glama.ai/mcp/servers/@ahujasid/ableton-mcp

### 2. Configuration

```bash
# Copy the secrets template and add your OpenAI API key
cp mcp_agent.secrets.yaml.example mcp_agent.secrets.yaml

# Edit mcp_agent.secrets.yaml and add your OpenAI API key:
# openai:
#   api_key: "sk-your-openai-api-key-here"
```

### 3. Run the Demo

```bash
# Ensure the Ableton Remote Script is running locally in your DAW

# Basic demo (as requested in the prompt)
python main.py

# OR using uv
uv run main.py

# Interactive demo
python main.py interactive

# Advanced multi-composition demo
python main.py advanced
```

## 🎼 Expected Output

When you run `uv run main.py`, you should see:

```
🎵 Music Ideator Agent - Starting...
🚀 Starting Music Ideator Demo - BASIC mode
📡 MCP App initialized successfully
🎵 Setting up Music Ideator Agent
🔗 Agent connected to MCP servers
🔧 Listing Available Tools
📋 Available tools (7 total):
  🛠️  suggest_progression: Suggest a chord progression based on mood, key, and genre
  🛠️  generate_melody: Generate melody notes based on chord progression and mood
  🛠️  analyze_progression: Analyze a chord progression and provide theory explanation
  🛠️  render_to_daw: Render chords and melody to DAW via MIDI, OSC, or file export
  🛠️  get_current_key: Get the current key setting
  🛠️  set_current_key: Set the current key for the DAW
  🛠️  list_output_files: List generated output files
🤖 OpenAI LLM attached to agent
🎼 Starting Basic Music Ideation Workflow
📝 Sample prompt: Generate a dreamy chord progression and melody in D major with a lofi vibe and send it to the DAW.
✅ Composition complete!
📊 Result: [Generated chord progression and melody details]
🎉 Demo completed successfully!
🎵 Music Ideator Agent - Finished!
```

The agent will:
1. Generate a chord progression (e.g., `['D', 'Bm', 'G', 'A']`)
2. Create a complementary melody
3. Render the composition to a DAW-ready format
4. Save output files in the `output/` directory

## 📁 Project Structure

```
music_ideator/
├── main.py                           # Agent runner (main entry point)
├── music_theory_server.py            # MCP server for music theory
├── daw_driver_server.py              # MCP server for DAW integration
├── mcp_agent.config.yaml             # App configuration
├── mcp_agent.secrets.yaml.example    # Secrets template
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── output/                           # Generated music files (created on first run)
│   ├── composition_YYYYMMDD_HHMMSS.json
│   ├── composition_YYYYMMDD_HHMMSS.midi.json
│   └── composition_YYYYMMDD_HHMMSS.osc.json
└── logs/                            # Application logs (created on first run)
    └── music_ideator-YYYYMMDD_HHMMSS.jsonl
```

## 🎯 Features Demonstrated

### Core MCP-Agent Capabilities
- ✅ **2-Server Integration**: Music theory + DAW driver servers
- ✅ **OpenAI LLM Integration**: GPT-4o for intelligent music generation
- ✅ **Tool Orchestration**: Seamless coordination between multiple tools
- ✅ **Structured Output**: Pydantic models for type-safe tool inputs/outputs
- ✅ **Human-in-the-Loop**: Interactive feedback and iteration support

### Music Generation Features
- ✅ **Chord Progressions**: Genre and mood-aware harmony generation
- ✅ **Melody Creation**: Complementary melodic lines over chord changes
- ✅ **Music Theory Analysis**: Educational insights about generated music
- ✅ **Multiple Output Formats**: MIDI, OSC, and JSON export options
- ✅ **DAW Integration**: Mock implementation ready for real DAW connection

### Workflow Patterns
- ✅ **Basic Workflow**: Single prompt → complete composition
- ✅ **Interactive Workflow**: Step-by-step composition building
- ✅ **Advanced Workflow**: Multiple compositions in different styles

## 🎨 Example Interactions

### Basic Generation
```
"Generate a dreamy chord progression and melody in D major with a lofi vibe and send it to the DAW."
```

### Interactive Session
```
1. "Create a jazz chord progression in Bb major with a smooth, sophisticated mood"
2. "Now generate a melody over those chords with a syncopated rhythm style"
3. "Analyze the musical theory behind this progression"
4. "Render this composition to the DAW as a MIDI file"
```

### Creative Variations
```
"Create three different moods in Am: one dreamy lofi, one energetic pop, one melancholic ballad"
```

## 🔧 Customization

### Adding New Musical Styles
Edit `music_theory_server.py` to add new genre patterns:

```python
PROGRESSION_PATTERNS = {
    'your_genre': {
        'your_mood': ['I', 'vi', 'IV', 'V'],
        # Add more patterns...
    }
}
```

### Real DAW Integration
Replace mock implementations in `daw_driver_server.py` with actual libraries:

```python
# Example: Real MIDI output
import mido
import rtmidi

def render_to_real_daw(self, chords, melody):
    outport = mido.open_output()
    # Send real MIDI messages...
```

### Additional LLM Providers
Configure alternative providers in `mcp_agent.config.yaml`:

```yaml
anthropic:
  default_model: claude-3-5-sonnet-20241022
  api_key: "your-claude-api-key"
```

## 🧪 Testing

```bash
# Test individual MCP servers
python music_theory_server.py
python daw_driver_server.py

# Test the complete integration
python main.py

# Run with different demo modes
python main.py interactive
python main.py advanced
```

## 🎼 Musical Theory Implementation

The music theory server implements:
- **Western Music Theory**: Major/minor scales and chord progressions
- **Genre-Specific Patterns**: Pop, jazz, lofi, classical progressions
- **Mood-Based Selection**: Happy, sad, dreamy, energetic variations
- **Melody Generation**: Scale-based melodic lines that complement harmony
- **Theory Analysis**: Roman numeral analysis and pattern recognition

## 🚀 Future Enhancements

- **Real-time MIDI**: Live DAW integration via MIDI controllers
- **Audio Analysis**: Integration with librosa for audio processing
- **Machine Learning**: AI-powered chord progression and melody models
- **Multi-track Arrangements**: Bass lines, drums, and full arrangements
- **Style Transfer**: Converting between musical genres
- **Collaborative Features**: Multi-agent composition workflows

## 📋 Requirements

- Python 3.10+
- OpenAI API key
- mcp-agent framework
- Optional: Real DAW software (Ableton Live, Logic Pro, Reaper, etc.)

## 🤝 Contributing

This is a demonstration project showing mcp-agent capabilities. Feel free to:
- Add new musical styles and genres
- Implement real DAW integrations
- Enhance the music theory engine
- Add audio processing capabilities
- Create new workflow patterns

## 📄 License

Part of the mcp-agent examples. See the main project license for details.