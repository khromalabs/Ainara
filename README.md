# Ainara AI Assistant Framework

![Ainara logo](./assets/ainara_logo.png)
**Ainara** _/aɪˈnɑːrə/ (n.) [Basque origin]: 1. A feminine given name meaning "swallow" (the bird) or "beloved one". [..] Associated with spring, and the beginning of life._
<br><br>

Ainara is a (work-in-progress) modular AI assistant framework that combines local LLM capabilities with extensible skills and recipes. It consists of multiple components that work together to provide a flexible and powerful AI interaction system.

## Demonstration video

This video demonstrates the first foundation stone what I'm working on, which is the ability to interact with the real world in real-time. For this purpose, I'm developing what I call Ainara's Orakle server - a REST API that provides 'skills' (concrete actions) and 'recipes' (chained actions of skills potentially combined with LLM processing).

Another component of the system is 'kommander', a CLI application designed to chat with the LLM, process Orakle commands in real-time, and make the LLM aware of the feedback from those commands.

As a proof of concept, I've developed several skills in Orakle that allow the AI assistant to search for real-time news. I've also created a more complex recipe that can download a web page, extract any articles within it, and process the content according to the desired profile - whether that's a layman's summary, easy-to-read language, or even content adapted for a young child, which works remarkably well.

UPDATE January 27, 2025: This is the 4th video in my series featuring Ainara. It shows a full natural language conversation with the assistant, where I discuss Bitcoin and look up real-time news and market info. I also explore how the AI assistant can find connections between these sources.

[![Watch the video](https://img.youtube.com/vi/WSfvNAtOSQw/0.jpg)](https://www.youtube.com/watch?v=WSfvNAtOSQw)

## $AINARA Token

The Ainara Project has now it's own Solana cryptocurrency token, CA: HhQhdSZNp6DvrxkPZLWMgHMGo9cxt9ZRrcAHc88spump

While the project will always remain open-source and aims to be a universal AI assistant tool, the officially developed 'skills' and 'recipes' (allowing AI to interact with the external world through Ainara's Orakle server) will primarily focus on cryptocurrency integrations. The project's official token will serve as the payment method for all related services.

## Components

### Kommander
A CLI chat interface that connects to local/commercial LLM servers and the Orakle API server. Features:
- Interactive chat with AI models
- Support for multiple LLM providers
- Command execution through Orakle API
- Chat history backup
- Light/dark theme support
- Pipe mode for non-interactive use

### Orakle
A REST API server that provides:
- Extensible skills system
- Recipe workflow execution
- Web content processing
- News search capabilities
- Text processing with LLMs

### Polaris
Desktop integrated app (TODO)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ainara.git
cd ainara
```

2. Install dependencies:
```bash
pip install -r requirements.txt
# Download required NLTK data
python setup_nltk.py
```

## Usage

### Starting Kommander CLI

Basic usage:
```bash
./kommander/kommander
```

Options:
- `-l, --light`: Use colors for light themes
- `-m, --model MODEL`: Specify LLM model
- `-s, --strip`: Strip everything except code blocks in non-interactive mode
- `-h, --help`: Show help message

You can also pipe input for non-interactive use:
```bash
echo "What is 2+2?" | ./kommander/kommander
```

### Environment Variables

- `AI_API_MODEL`: Override default LLM model

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt
- Local LLM server (compatible with OpenAI API format)
- Orakle API server running locally or on network

## License

[GNU GPL 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)

## Contributing

Everyone's invited to join this project - developers, designers, sponsors, testers, and more! My ultimate goal would be to create an open, community-driven AI companion/assistant that achieves for the emerging open source AI tools what Linux did for Unix: a widely adopted, powerful, and endlessly customizable assistant that empowers users and developers alike.
