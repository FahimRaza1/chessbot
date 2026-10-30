# ChessBot

A lightweight Python chess engine with terminal play and Lichess bot interfaces.

## Features

- Material and piece-square evaluation
- Alpha-beta search with quiescence and iterative deepening
- Move ordering and transposition-table caching
- Terminal game mode
- Lichess bot integration using the official streaming API

## Project structure

- `main.py` runs a playable terminal game against a basic engine
- `bot/` contains evaluation, search, move ordering, and transposition logic
- `tests/` contains a few sanity tests for evaluation and search behavior
- `lichess/` contains a UCI wrapper for deploying to lichess-bot

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Enter moves in UCI format, such as `e2e4`.

## Notes

The opening book file in `data/openings.bin` is optional and can be populated later with a Polyglot opening book.

## Run as a Lichess bot

Create a separate Lichess bot account and generate an API token with the `Play games with the bot` permission. Copy `.env.example` to `.env`, then set `LICHESS_TOKEN` in `.env`. Upgrade the account through Lichess before starting the bot. The bot account ID is discovered automatically after authentication.

Install the dependencies and start the bot from the project root:

```powershell
python -m pip install -r requirements.txt
python -m lichess.bot
```

The bot accepts incoming challenges, streams games, and submits moves from the local search engine. Set `CHESSBOT_DEPTH=3` in `.env` for stronger but slower moves.

Never commit `.env` or share its token. If a token has been exposed publicly, revoke it in Lichess and create a replacement.

## Testing

```powershell
python -m pytest
```

GitHub Actions runs this test suite for pushes and pull requests.

## Publishing to GitHub

After creating an empty repository on GitHub, run these commands from the project root:

```powershell
git init
git add .
git commit -m "Initial chess bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Check `git status` before committing and confirm `.env` is not listed.
