from dataclasses import dataclass
import random
import time
from typing import List, Dict, Optional

@dataclass
class Player:
    name: str
    is_host: bool = False
    score: int = 0
    vote: Optional[str] = None

class Game:
    def __init__(self, room_code: str):
        self.room_code = room_code
        self.players: List[Player] = []
        self.phase = "lobby"
        self.min_players = 3
        self.current_domain = None
        self.current_item = None
        self.imposter = None
        self.discussion_duration = 120  # seconds
        self.discussion_end_time = None
        self.votes: Dict[str, str] = {}  # voter_name -> voted_for_name
        self.most_voted_player = None
        self.imposter_guess = None

    def add_player(self, player: Player) -> None:
        if not any(p.name == player.name for p in self.players):
            self.players.append(player)

    def is_player_host(self, player_name: str) -> bool:
        return any(p.name == player_name and p.is_host for p in self.players)

    def start_round(self) -> None:
        if len(self.players) >= self.min_players:
            self.phase = "round_setup"

    def set_domain(self, domain: str) -> None:
        self.current_domain = domain

    def select_item(self) -> None:
        from data import get_items_for_domain
        items = get_items_for_domain(self.current_domain)
        self.current_item = random.choice(items)
        self.imposter = random.choice(self.players)

    def is_player_imposter(self, player_name: str) -> bool:
        return self.imposter and self.imposter.name == player_name

    def start_discussion(self) -> None:
        self.phase = "discussion"
        self.discussion_end_time = time.time() + self.discussion_duration

    def start_voting(self) -> None:
        self.phase = "voting"
        self.votes.clear()

    def submit_vote(self, voter_name: str, voted_for: str) -> None:
        self.votes[voter_name] = voted_for

    def has_player_voted(self, player_name: str) -> bool:
        return player_name in self.votes

    def all_votes_submitted(self) -> bool:
        return len(self.votes) == len(self.players)

    def reveal_imposter(self) -> None:
        self.phase = "reveal"
        # Set most_voted_player to None since we're not using group voting
        self.most_voted_player = None

    def did_player_vote_correctly(self, player_name: str) -> bool:
        return (player_name in self.votes and 
                self.votes[player_name] == self.imposter.name)

    def start_imposter_guess(self) -> None:
        self.phase = "imposter_guess"

    def get_guess_options(self) -> List[str]:
        from data import get_items_for_domain
        items = get_items_for_domain(self.current_domain)
        options = random.sample([i for i in items if i != self.current_item], 3)
        options.append(self.current_item)
        random.shuffle(options)
        return options

    def submit_imposter_guess(self, guess: str) -> None:
        self.imposter_guess = guess
        # Award points
        if guess == self.current_item:
            self.imposter.score += 100
        # Award points to correct voters
        for player in self.players:
            if self.did_player_vote_correctly(player.name):
                player.score += 100
        self.show_scores()

    def show_scores(self) -> None:
        self.phase = "scores"

    def get_scores(self) -> Dict[str, int]:
        return {player.name: player.score for player in self.players}

    def reset_round(self) -> None:
        self.phase = "round_setup"
        self.current_item = None
        self.imposter = None
        self.votes.clear()
        self.most_voted_player = None
        self.imposter_guess = None

    def reset_game(self) -> None:
        self.phase = "lobby"
        self.current_domain = None
        self.current_item = None
        self.imposter = None
        self.votes.clear()
        self.most_voted_player = None
        self.imposter_guess = None
