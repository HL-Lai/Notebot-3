# Notebot v3

**Notebot v3** is a web-based application that helps users generate notes using a *Large Language Model (LLM)* via the Microsoft Azure API. This project is built with Python and Flask, providing a simple and intuitive interface for users to create, manage, and export their notes.

## Features

*   Generate notes using GPT-based LLM.
*   User-friendly web interface powered by Flask.
*   Ability to edit and manage API keys securely.
*   Support for exporting and saving generated notes.
*   Easy setup using Conda environment YAML file.

## Project Structure

*   `chatbot.py` - Chatbot functions for the project
*   `notebot3.py` - Main Flask app backend for chatbot/note generation functionality.
*   `utils.py` - Utility functions used across the project.
*   `templates/` - HTML templates for the web interface.
*   `static/styles/` - CSS styles for the web interface.
*   `notebot_fl.yml` - Conda environment file for easy setup.
*   `.gitignore` - Git ignore file.

Installation
------------

1.  Clone this repository:
2.  Create and activate the Conda environment:
    *   `conda env create -f notebot_fl.yml`
    *   `conda activate notebot_fl`
3.  Set up your API key and endpoint in `.env`, e.g.

```
OPENAI_API_ENDPOINT = {your_endpoint}
OPENAI_API_KEY = {your_key}
```

4.  Run the code:
    *   run chatbot only:
        `python chatbot.py`
    *   run notebot:
        `python notebot3.py`
5.  Open your browser and go to the mentioned address.

## Usage

*   Enter your API key via settings (not required if `.env` has been set).
*   Enter the prompt and adjust temperature via settings.
*   Input your note topic or instructions and let Notebot generate notes for you.  Images are also allowed.
*   Save your notes as needed.

## Dependencies

All Python dependencies are listed in `notebot_fl.yml`.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for new features or bug fixes.

## License

This project is licensed under the MIT License.