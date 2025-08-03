# Imposter / برّه السالفة

A multiplayer social deduction party game built with Streamlit.

## 🎲 Game Overview

"Imposter / برّه السالفة" is a quick social-deduction party game for 3–10 players (2 in Test Mode). In each round:

- One player is secretly the Imposter—they don't know the chosen item
- Everyone else sees that item and must ask questions to spot who's "out" of the loop
- Players then vote on who they think the Imposter is
- Correct voters earn 100 points
- The Imposter gets a 4-choice guess of the hidden item—correct guess = 100 points
- Scores are tallied, and you can play multiple rounds

## 🛠️ Setup & Requirements

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   streamlit run app.py
   ```

## 🎮 How to Play

### Creating a Room
1. Host clicks "Create Room / أنشئ غرفة" and enters their name
2. A 4-letter code appears
3. Share the URL with other players (it will include the room code)

### Joining a Room
1. Players can either:
   - Paste the shared URL
   - Go to the app and enter the room code + their name
2. Click "Join / انضم"

### Game Flow
1. **Starting**: Host can start when minimum players have joined (3 by default, 2 in Test Mode)
2. **Setup**: Host picks a domain (e.g., "Clothes / الملابس")
3. **Round Info**: All players except the Imposter see the chosen item
4. **Discussion**: Players ask questions and discuss (2-minute timer)
5. **Voting**: Everyone votes on who they think is the Imposter
6. **Reveal**: True Imposter is revealed, correct voters get points
7. **Imposter Guess**: Imposter gets 4 choices to guess the item
8. **Scores**: Points are tallied, and the next round can begin

## 🎯 Scoring
- Correctly voting for the Imposter: +100 points
- Imposter correctly guessing the item: +100 points

## 🔄 Features
- Real-time updates
- Multiple domains with bilingual items (Arabic/English)
- Test mode for 2 players
- Persistent scoring across rounds
- Host controls for game flow
