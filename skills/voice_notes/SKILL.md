---
name: voice_notes
description: >
  Transcribe audio files to text using OpenAI Whisper API. Use when the user
  has a voice memo, audio recording, or any audio file they want transcribed.
  Do NOT use for video files or live audio streams.
allowed-tools: Bash(uv run *)
---

Transcribe audio files to text using the OpenAI Whisper API.

## Usage

```bash
uv run --directory SKILL_DIR python scripts/transcribe.py FILE [OPTIONS]
```

Where `SKILL_DIR` is the directory containing this skill.

### Options

- `FILE` — Path to audio file (mp3, mp4, m4a, wav, webm, mpeg, mpga, oga, ogg)
- `--language` / `-l` — ISO-639-1 language code (e.g. `en`, `es`, `ja`). Auto-detected if omitted.
- `--output` / `-o` — Write transcript to this file instead of stdout
- `--model` / `-m` — Whisper model (default: `gpt-4o-mini-transcribe`)

## After Transcription

1. Read the transcript output
2. Ask the user what to do with it:
   - Save to hierarchical_memory as a daily note
   - Save to obsidian as a knowledge graph note
   - Summarize and extract action items
   - Just display the raw text

## Requirements

- `OPENAI_API_KEY` environment variable must be set (same key used by discussion_partners)
- Supported formats: mp3, mp4, m4a, wav, webm, mpeg, mpga, oga, ogg
- Max file size: 25MB per OpenAI API limit
