# JARVIS Python Assistant

A hybrid AI automation assistant for Windows with local vision, WhatsApp automation, memory storage, and smart browser routing.

## Features

- **WhatsApp automation** using `pywhatkit`
- **Local vision** with `ollama` and `moondream` for screen and camera analysis
- **Screenshot diagnosis** using `pyautogui`
- **Camera object detection** using `OpenCV` (`cv2`)
- **Memory persistence** in `memory.json`
- **Smart browser routing** for music and research searches
- **Safe auto-restart loop** and `Esc` key speech stop using `keyboard`

## Installation

Install the required dependencies:

```bash
pip install ollama pywhatkit pyautogui opencv-python keyboard
```

If additional packages are missing, install them as needed:

```bash
pip install pyttsx3 SpeechRecognition pycaw comtypes screen_brightness_control requests pillow
```

## Usage

Run the assistant:

```bash
python jarvis_final.py
```

## Example commands

- `Send WhatsApp to Alice saying Hello, how are you?`
- `Remember that my favorite color is blue.`
- `What do you remember about color?`
- `Diagnose the screen` or `Diagnose the problem shown on screen`
- `JARVIS, look at this`
- `Open music` or `play song name`
- `Search research articles about AI`
- `Open Chrome for study`

## Notes

- Add your WhatsApp contacts to the `CONTACTS` dictionary in `jarvis_final.py`.
- Ensure Ollama is installed and the `moondream` model is available for local vision.
- On Windows, `Esc` stops speaking immediately.

## Startup checklist

- [ ] Install required Python packages:
  - `pip install ollama pywhatkit pyautogui opencv-python keyboard`
  - `pip install pyttsx3 SpeechRecognition pycaw comtypes screen_brightness_control requests pillow`
- [ ] Confirm `ollama` is installed and running locally.
- [ ] Confirm `moondream` model is available in Ollama.
- [ ] Add your WhatsApp contacts to the `CONTACTS` dictionary.
- [ ] Log into WhatsApp Web on your default browser.
- [ ] Run `python jarvis_final.py` and verify startup output.

## Files

- `jarvis_final.py` — main assistant script
- `memory.json` — persistent memory store (created automatically)
