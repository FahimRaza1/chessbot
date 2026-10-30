"""Standalone Lichess bot client for ChessBot.

Run from the project root with: python -m lichess.bot
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Iterator

import chess
import requests
from dotenv import load_dotenv

from bot.search import search_best_move

LOGGER = logging.getLogger("chessbot.lichess")


class LichessBot:
    def __init__(self, token: str, api_url: str = "https://lichess.org", depth: int = 2) -> None:
        self.api_url = api_url.rstrip("/")
        self.depth = depth
        self.account_id: str | None = None
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/x-ndjson",
        })

    def _url(self, path: str) -> str:
        return f"{self.api_url}{path}"

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        response = self.session.request(method, self._url(path), timeout=(10, 30), **kwargs)
        response.raise_for_status()
        return response

    def stream_events(self) -> Iterator[dict[str, Any]]:
        """Yield account events, reconnecting after transient network failures."""
        while True:
            try:
                with self.session.get(
                    self._url("/api/stream/event"),
                    stream=True,
                    timeout=(10, None),
                ) as response:
                    response.raise_for_status()
                    for raw_line in response.iter_lines(decode_unicode=True):
                        if raw_line:
                            yield json.loads(raw_line)
            except (requests.RequestException, json.JSONDecodeError) as error:
                LOGGER.warning("Event stream interrupted: %s; reconnecting", error)
                time.sleep(5)

    def accept_challenge(self, challenge_id: str) -> None:
        try:
            self._request("POST", f"/api/challenge/{challenge_id}/accept")
            LOGGER.info("Accepted challenge %s", challenge_id)
        except requests.HTTPError as error:
            LOGGER.warning("Could not accept challenge %s: %s", challenge_id, error)

    def identify(self) -> None:
        account = self._request("GET", "/api/account").json()
        self.account_id = account["id"].lower()
        title = account.get("title") or "regular account"
        LOGGER.info("Authenticated as %s (%s)", account["username"], title)
        if title != "BOT":
            raise RuntimeError(
                "This Lichess account is not upgraded to a BOT account. "
                "Upgrade it at https://lichess.org/api/bot/account/upgrade."
            )

    def stream_game(self, game_id: str) -> Iterator[dict[str, Any]]:
        with self.session.get(
            self._url(f"/api/bot/game/stream/{game_id}"),
            stream=True,
            timeout=(10, None),
        ) as response:
            if not response.ok:
                detail = response.text[:300].replace("\n", " ")
                raise requests.HTTPError(
                    f"Lichess game stream rejected the bot ({response.status_code}): {detail}",
                    response=response,
                )
            for raw_line in response.iter_lines(decode_unicode=True):
                if raw_line:
                    yield json.loads(raw_line)

    def play_game(self, game_id: str) -> None:
        board = chess.Board()
        bot_color: chess.Color | None = None
        processed_move_count = 0

        try:
            for event in self.stream_game(game_id):
                event_type = event.get("type")
                if event_type == "gameFull":
                    bot_color = self._bot_color(event)
                    initial_moves = event.get("state", {}).get("moves", "").split()
                    self._reset_board(board, initial_moves)
                    processed_move_count = len(initial_moves)
                    if self._maybe_move(game_id, board, bot_color):
                        processed_move_count += 1
                elif event_type == "gameState" and bot_color is not None:
                    moves = event.get("moves", "").split()
                    if len(moves) <= processed_move_count:
                        continue
                    self._reset_board(board, moves)
                    processed_move_count = len(moves)
                    if event.get("status") != "started":
                        LOGGER.info("Game %s finished with status %s", game_id, event.get("status"))
                        return
                    if self._maybe_move(game_id, board, bot_color):
                        processed_move_count += 1
        except (requests.RequestException, json.JSONDecodeError, ValueError) as error:
            LOGGER.warning("Game %s ended with an integration error: %s", game_id, error)

    def _bot_color(self, game: dict[str, Any]) -> chess.Color:
        white_id = game.get("white", {}).get("id")
        black_id = game.get("black", {}).get("id")
        if self.account_id and white_id and white_id.lower() == self.account_id:
            return chess.WHITE
        if self.account_id and black_id and black_id.lower() == self.account_id:
            return chess.BLACK
        raise ValueError("Could not identify the bot color in game %s" % game.get("id", ""))

    @staticmethod
    def _reset_board(board: chess.Board, moves: list[str]) -> None:
        board.reset()
        for move in moves:
            board.push_uci(move)

    def _maybe_move(self, game_id: str, board: chess.Board, bot_color: chess.Color) -> bool:
        if board.is_game_over() or board.turn != bot_color:
            return False
        move = search_best_move(board, depth=self.depth)
        if move is None or move not in board.legal_moves:
            return False
        self._request("POST", f"/api/bot/game/{game_id}/move/{move.uci()}")
        board.push(move)
        LOGGER.info("Game %s: played %s", game_id, move.uci())
        return True

    def run(self) -> None:
        self.identify()
        for event in self.stream_events():
            event_type = event.get("type")
            if event_type == "challenge":
                challenge = event.get("challenge", {})
                if challenge.get("id"):
                    self.accept_challenge(challenge["id"])
            elif event_type == "gameStart":
                game_id = event.get("game", {}).get("id")
                if game_id:
                    LOGGER.info("Starting game %s", game_id)
                    self.play_game(game_id)


def main() -> None:
    load_dotenv()
    token = os.getenv("LICHESS_TOKEN")
    if not token or token == "your_lichess_token_here":
        raise SystemExit("Set LICHESS_TOKEN in .env before starting the bot")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    api_url = os.getenv("LICHESS_API_URL", "https://lichess.org")
    depth = int(os.getenv("CHESSBOT_DEPTH", "2"))
    LichessBot(token=token, api_url=api_url, depth=depth).run()


if __name__ == "__main__":
    main()
