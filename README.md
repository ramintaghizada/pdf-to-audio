# 🎧 pdf-to-audio

Turn any PDF into a natural-sounding MP3 and listen instead of reading.

`pdf-to-audio` extracts the text from a PDF, cleans it up, and converts it to speech with neural voices from [edge-tts](https://github.com/rany2/edge-tts). It works on long documents because it splits the text into chunks and converts several at once, with timeouts and automatic retries.

## Features

- **Natural neural voices** instead of robotic system speech
- **Many languages**, including English, Azerbaijani, Russian and Turkish
- **Fast on long PDFs**: parallel conversion with the original order preserved
- **Reliable**: per-chunk timeout and automatic retries, so one stalled request doesn't freeze everything
- **Sentence-aware chunking**: sentences are never cut in the middle
- **Text cleanup**: rejoins hyphenated words and fixes broken lines
- **Desktop notification** when the audio is ready (Linux)
- **Autoplay** when conversion finishes
- Saves a regular **MP3** you can copy to your phone

## Requirements

- Python 3.9+
- Internet connection (edge-tts uses Microsoft's online voices)
- Linux extras (optional): `ffmpeg` for playback and `libnotify-bin` for notifications

## Installation

```bash
git clone https://github.com/ramintaghizada/pdf-to-audio.git
cd pdf-to-audio

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install pypdf edge-tts
```

On Ubuntu/Debian, for playback and notifications:

```bash
sudo apt install ffmpeg libnotify-bin
```

## Usage

```bash
python3 reader.py book.pdf
```

The audio is saved as `output.mp3` in the current folder, a notification appears, and playback starts automatically.

To leave the virtual environment when you're done:

```bash
deactivate
```

## Configuration

Edit the settings at the top of `reader.py`:

| Setting | Default | Description |
|---|---|---|
| `VOICE` | `en-US-AriaNeural` | Voice to use. Match it to the PDF's language |
| `CHUNK_SIZE` | `3000` | Characters per request |
| `TIMEOUT` | `90` | Seconds to wait for one chunk before retrying |
| `RETRIES` | `3` | Attempts per chunk before giving up |
| `CONCURRENCY` | `5` | Chunks converted at the same time |
| `rate` | `+0%` | Speech speed, for example `"-10%"` or `"+20%"` |

### Choosing a voice

List every available voice:

```bash
edge-tts --list-voices
```

Examples: `en-US-AriaNeural`, `az-AZ-BabekNeural`, `az-AZ-BanuNeural`.

### Tuning speed

- Raise `CONCURRENCY` (try 4, 6, 8) until you see "failed" messages, then step back.
- Skip front matter or references by limiting the pages, for example `reader.pages[5:120]`.
- A faster `rate` makes the audio shorter and slightly quicker to generate.

## How it works

1. Extract text from every page with `pypdf`
2. Clean the text (hyphenation, line breaks)
3. Split it into sentence-aware chunks
4. Convert chunks in parallel with `edge-tts`, retrying on timeouts
5. Join the audio in the original order and save the MP3

## Limitations

- **Scanned PDFs** (pages stored as images) have no text layer. They need OCR first, for example with `pytesseract` and `pdf2image`.
- Headers, footers and page numbers may be read aloud unless you filter them out.
- Conversion needs an internet connection.
- `edge-tts` is an unofficial client for Microsoft's online service, so behavior may change.

## Troubleshooting

| Problem | Fix |
|---|---|
| `externally-managed-environment` error | Use a virtual environment as shown above |
| Conversion hangs or is slow | Update with `pip install -U edge-tts`, lower `CONCURRENCY`, lower `TIMEOUT` |
| `ffplay: command not found` | `sudo apt install ffmpeg` |
| `notify-send: command not found` | `sudo apt install libnotify-bin` |
| Wrong accent or garbled speech | Use a voice that matches the PDF's language |

## Roadmap

- [ ] Play each chunk as soon as it is ready
- [ ] OCR support for scanned PDFs
- [ ] Skip headers, footers and page numbers automatically
- [ ] One MP3 per chapter
- [ ] Remember the last position
- [ ] Offline mode with Piper
- [ ] Simple GUI

## Contributing

Issues and pull requests are welcome. If you have an idea or found a bug, please open an issue.

## License

Released under the MIT License. Add a `LICENSE` file to your repository to make it official.

## Acknowledgements

- [edge-tts](https://github.com/rany2/edge-tts) for the speech synthesis
- [pypdf](https://github.com/py-pdf/pypdf) for PDF text extraction

---

If this project helped you, consider giving it a ⭐