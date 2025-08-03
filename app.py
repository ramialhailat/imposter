import streamlit as st
import random
import time
import json
import os
from streamlit_autorefresh import st_autorefresh
from game_logic import Game, Player
from data import DOMAINS, get_items_for_domain

# Page config
st.set_page_config(
    page_title="Imposter / برّه السالفة",
    page_icon="🎲",
    layout="wide"
)

# Initialize session state
if 'game' not in st.session_state:
    st.session_state.game = None

# Create a directory for storing game states if it doesn't exist
os.makedirs('game_states', exist_ok=True)

def save_game_state(game):
    """Save game state to file"""
    if game:
        game_data = {
            'room_code': game.room_code,
            'phase': game.phase,
            'players': [{'name': p.name, 'is_host': p.is_host, 'score': p.score} for p in game.players],
            'min_players': game.min_players,
            'current_domain': game.current_domain,
            'current_item': game.current_item,
            'imposter': game.imposter.name if game.imposter else None,
            'discussion_end_time': game.discussion_end_time,
            'votes': game.votes,
            'most_voted_player': game.most_voted_player,
            'imposter_guess': game.imposter_guess if hasattr(game, 'imposter_guess') else None,
        }
        with open(f'game_states/{game.room_code}.json', 'w') as f:
            json.dump(game_data, f)

def load_game_state(room_code):
    """Load game state from file"""
    try:
        with open(f'game_states/{room_code}.json', 'r') as f:
            data = json.load(f)
            game = Game(data['room_code'])
            game.phase = data['phase']
            
            # Recreate players
            for p_data in data['players']:
                player = Player(p_data['name'], p_data['is_host'])
                player.score = p_data['score']
                game.add_player(player)
            
            game.min_players = data['min_players']
            game.current_domain = data['current_domain']
            game.current_item = data['current_item']
            
            # Set imposter and their guess
            if data['imposter']:
                game.imposter = next((p for p in game.players if p.name == data['imposter']), None)
            if 'imposter_guess' in data:
                game.imposter_guess = data['imposter_guess']
            
            game.discussion_end_time = data['discussion_end_time']
            game.votes = data['votes']
            game.most_voted_player = data['most_voted_player']
            
            return game
    except FileNotFoundError:
        return None

def sync_game_state():
    """Sync game state with the stored state"""
    if st.session_state.game and hasattr(st.session_state.game, 'room_code'):
        stored_game = load_game_state(st.session_state.game.room_code)
        if stored_game:
            # Check if there's any change in game state
            current_phase = st.session_state.game.phase
            
            # Always update the game state to ensure synchronization
            st.session_state.game = stored_game
            
            # Show update notification if something changed
            if current_phase != stored_game.phase:
                st.toast(f"Game phase changed to: {stored_game.phase} 🔄")

def create_room():
    """Create a new game room"""
    if not st.session_state.get('player_name'):
        st.error("Please enter your name first")
        return
    
    # Generate room code
    room_code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
    game = Game(room_code)
    game.add_player(Player(st.session_state.player_name, is_host=True))
    st.session_state.game = game
    save_game_state(game)
    st.query_params['room'] = room_code
    st.query_params['name'] = st.session_state.player_name

def join_room():
    """Join an existing game room"""
    if not st.session_state.get('player_name') or not st.session_state.get('room_code'):
        st.error("Please enter both your name and room code")
        return
    
    room_code = st.session_state.room_code.upper()
    game = load_game_state(room_code)
    
    if game is None:
        st.error("Room not found!")
        return
    
    player = Player(st.session_state.player_name)
    game.add_player(player)
    st.session_state.game = game
    save_game_state(game)
    st.query_params['room'] = room_code
    st.query_params['name'] = st.session_state.player_name

def main():
    st.title("Imposter / برّه السالفة 🎲")
    
    # Get query parameters and sync state
    if 'room' in st.query_params and 'name' in st.query_params:
        st.session_state.room_code = st.query_params['room']
        st.session_state.player_name = st.query_params['name']
        
        # Try to load existing game
        if st.session_state.game is None:
            stored_game = load_game_state(st.session_state.room_code)
            if stored_game:
                st.session_state.game = stored_game
    
    # Keep auto-refresh for all phases
    count = st_autorefresh(interval=2000, key="game_refresh")
    sync_game_state()
    
    if st.session_state.game is None:
        # Login screen with instructions
        st.write("### How to Play:")
        st.write("1. One player creates a room and becomes the host")
        st.write("2. Other players join using the room code")
        st.write("3. The host starts the game when enough players have joined")
        st.divider()

        # Create tabs with Join Room as default
        join_tab, create_tab = st.tabs(["🎮 Join Existing Room / الانضمام إلى غرفة", "🎲 Create New Room / إنشاء غرفة جديدة"])
        
        with join_tab:
            st.write("Choose this to join someone else's game / اختر هذا للانضمام إلى لعبة شخص آخر")
            room_code = st.text_input("Room Code / رمز الغرفة:", key="join_room_code", placeholder="Enter 4-letter code / أدخل رمز من 4 أحرف", max_chars=4)
            player_name = st.text_input("Your Name / اسمك:", key="join_name", placeholder="Enter your name / أدخل اسمك")
            if st.button("👥 Join Room / انضم للغرفة", use_container_width=True):
                st.session_state.player_name = player_name
                st.session_state.room_code = room_code
                join_room()
        
        with create_tab:
            st.write("Choose this if you want to host a game / اختر هذا إذا كنت تريد أن تكون المضيف")
            player_name = st.text_input("Your Name / اسمك:", key="create_name", placeholder="Enter your name / أدخل اسمك")
            if st.button("� Create Room & Become Host / إنشاء غرفة وكن المضيف", use_container_width=True):
                st.session_state.player_name = player_name
                create_room()
    
    else:
        game = st.session_state.game
        
        # Create two columns - main game area and scoreboard
        main_col, score_col = st.columns([7, 3])
        
        with score_col:
            # Scoreboard in right column
            st.subheader("🏆 Scoreboard / النتائج")
            
            # Room info at the top of scoreboard
            st.write(f"Room Code / رمز الغرفة: {game.room_code}")
            st.write(f"Players / اللاعبين: {len(game.players)}")
            if game.current_domain:
                st.write(f"Domain / المجال: {game.current_domain}")
            st.divider()
            
            # Sort players by score in descending order
            sorted_players = sorted(game.players, key=lambda x: x.score, reverse=True)
            
            # Show your score prominently
            for player in sorted_players:
                if player.name == st.session_state.player_name:
                    st.markdown(f"**You / أنت:** {player.score} نقطة")
                else:
                    st.write(f"{player.name}: {player.score} نقطة")
        
        with main_col:
            # Game phases
            if game.phase == "lobby":
                st.subheader("Lobby / الغرفة")
                st.divider()
                st.write("Players in the room / اللاعبون في الغرفة:")
                for player in game.players:
                    st.write(f"- {player.name} {'(Host / المضيف)' if player.is_host else ''}")
                
                # Show lobby status
                st.write(f"Number of players / عدد اللاعبين: {len(game.players)} (Minimum needed / الحد الأدنى المطلوب: {game.min_players})")
                
                # Host controls
                if game.is_player_host(st.session_state.player_name):
                    st.write("👑 You are the host / أنت المضيف")
                    test_mode = st.checkbox("Enable Test Mode (2 players minimum) / تفعيل وضع الاختبار (لاعبين كحد أدنى)")
                    if test_mode:
                        game.min_players = 2
                        save_game_state(game)
                    
                    if len(game.players) >= game.min_players:
                        if st.button("▶️ Start Round / ابدأ الجولة"):
                            game.start_round()
                            save_game_state(game)
                            st.rerun()
                    else:
                        st.warning(f"Need {game.min_players - len(game.players)} more players to start / نحتاج {game.min_players - len(game.players)} لاعب إضافي للبدء")
                else:
                    st.info("Waiting for the host to start the game... / بانتظار المضيف لبدء اللعبة...")
        if game.phase == "lobby":
            st.subheader("Lobby")
            st.write("Players in the room:")
            for player in game.players:
                st.write(f"- {player.name} {'(Host)' if player.is_host else ''}")
            
            # Show lobby status
            st.write(f"Number of players: {len(game.players)} (Minimum needed: {game.min_players})")
            
            # Host controls
            if game.is_player_host(st.session_state.player_name):
                st.write("👑 You are the host")
                test_mode = st.checkbox("Enable Test Mode (2 players minimum)")
                if test_mode:
                    game.min_players = 2
                    save_game_state(game)
                
                if len(game.players) >= game.min_players:
                    if st.button("▶️ Start Round"):
                        game.start_round()
                        save_game_state(game)
                        st.rerun()
                else:
                    st.warning(f"Need {game.min_players - len(game.players)} more players to start")
            else:
                st.info("Waiting for the host to start the game...")
        
        elif game.phase == "round_setup":
            st.subheader("👑 Host: Select Domain")
            
            if game.is_player_host(st.session_state.player_name):
                st.write("Choose a category for this round:")
                domain = st.selectbox("Available domains:", DOMAINS, index=0)
                if st.button("✅ Start Round with Selected Domain"):
                    game.set_domain(domain)
                    game.select_item()
                    game.start_discussion()
                    save_game_state(game)
                    st.rerun()
            else:
                st.info("💭 Waiting for the host to select a domain...")
        
        elif game.phase == "discussion":
            st.subheader("Discussion Phase")
            
            # Display role and item
            player_role = "Imposter!" if game.is_player_imposter(st.session_state.player_name) else f"Regular Player (Item: {game.current_item})"
            st.info(f"You are the {player_role}")
            
            # Chat/Discussion area
            st.write("Use this time to ask questions and discuss!")
            
            # Timer
            time_left = max(0, game.discussion_end_time - time.time())
            st.progress(time_left / game.discussion_duration)
            st.write(f"Time remaining: {int(time_left)} seconds")
            
            if game.is_player_host(st.session_state.player_name):
                if st.button("End Discussion & Open Voting"):
                    game.start_voting()
                    save_game_state(game)
                    st.rerun()
        
        elif game.phase == "voting":
            st.subheader("Voting Phase")
            
            if not game.has_player_voted(st.session_state.player_name):
                st.write("Who do you think is the Imposter? Choose carefully!")
                st.warning("Remember: You'll get 100 points if you guess correctly!")
                
                for player in game.players:
                    if player.name != st.session_state.player_name:
                        if st.button(f"Vote for {player.name}"):
                            game.submit_vote(st.session_state.player_name, player.name)
                            save_game_state(game)
                            st.rerun()
            else:
                your_vote = game.votes.get(st.session_state.player_name)
                st.info(f"You voted for: {your_vote}")
                st.write("Waiting for other players to vote...")
            
            total_votes = len(game.votes)
            total_players = len(game.players)
            st.progress(total_votes / total_players)
            st.write(f"Votes: {total_votes}/{total_players}")
            
            if game.all_votes_submitted():
                game.reveal_imposter()
                save_game_state(game)
                st.rerun()
        
        elif game.phase == "reveal":
            st.subheader("Results")
            st.write(f"The Imposter was: {game.imposter.name}")
            
            # Show individual results
            st.write("\nVoting Results:")
            correct_voters = []
            for player in game.players:
                if game.did_player_vote_correctly(player.name):
                    correct_voters.append(player.name)
                    if player.name == st.session_state.player_name:
                        st.success(f"🎉 Excellent! You identified the Imposter correctly! +100 points")
                    else:
                        st.success(f"✅ {player.name} identified the Imposter correctly (+100 points)")
                else:
                    if player.name == st.session_state.player_name:
                        if player.name in game.votes:
                            voted_for = game.votes[player.name]
                            st.error(f"❌ You guessed {voted_for}, but it was incorrect")
                        else:
                            st.warning("⚠️ You didn't vote")
            
            if game.is_player_host(st.session_state.player_name):
                if st.button("Proceed to Imposter Guess"):
                    game.start_imposter_guess()
                    save_game_state(game)
                    st.rerun()
        
        elif game.phase == "imposter_guess":
            st.subheader("Imposter's Guess")
            
            if game.is_player_imposter(st.session_state.player_name):
                st.write("Choose the item you think everyone else was discussing:")
                
                # Store options and their order in session state to keep them stable
                if 'imposter_options' not in st.session_state:
                    st.session_state.imposter_options = game.get_guess_options()
                    # Create a fixed order for the options
                    st.session_state.options_order = list(range(len(st.session_state.imposter_options)))
                
                options = st.session_state.imposter_options
                
                # Create a container for the grid
                grid = st.container()
                
                # Calculate number of columns (3 items per row)
                num_cols = 3
                num_options = len(options)
                num_rows = (num_options + num_cols - 1) // num_cols
                
                # Create the grid using the fixed order
                for row in range(num_rows):
                    cols = st.columns(num_cols)
                    for col in range(num_cols):
                        idx = row * num_cols + col
                        if idx < num_options:
                            option = options[st.session_state.options_order[idx]]
                            with cols[col]:
                                image_path = f"item_images/{option.lower().replace(' ', '_')}.png"
                                if os.path.exists(image_path):
                                    st.image(image_path, caption=option, width=200)
                                
                                if st.button(f"{option}", key=f"guess_{option}", use_container_width=True):
                                    game.submit_imposter_guess(option)
                                    game.imposter_guess = option  # Explicitly set the guess
                                    if option == game.current_item:
                                        st.success("🎯 You got it! +100 points")
                                    else:
                                        st.error(f"❌ Wrong! The correct item was: {game.current_item}")
                                    # Clear the options from session state when done
                                    if 'imposter_options' in st.session_state:
                                        del st.session_state.imposter_options
                                    if 'options_order' in st.session_state:
                                        del st.session_state.options_order
                                    game.show_scores()
                                    save_game_state(game)
                                    st.rerun()
            else:
                st.write("Waiting for the Imposter to make their guess...")
                st.info(f"The item was: {game.current_item}")
                image_path = f"item_images/{game.current_item.lower().replace(' ', '_')}.png"
                if os.path.exists(image_path):
                    st.image(image_path, caption=game.current_item, width=200)
        
        elif game.phase == "scores":
            st.subheader("Round Complete!")
            
            if game.imposter_guess == game.current_item:
                st.success(f"🎯 The Imposter ({game.imposter.name}) won!")
                st.write(f"Correctly guessed: {game.current_item}")
            else:
                st.error(f"The Imposter ({game.imposter.name}) lost!")
                st.write(f"The item was: {game.current_item}")
            
            if game.is_player_host(st.session_state.player_name):
                st.write("Host Controls:")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Next Round (Same Domain)", key="same_domain"):
                        current_domain = game.current_domain
                        game.reset_round()
                        game.current_domain = current_domain
                        game.select_item()
                        game.start_discussion()
                        save_game_state(game)
                        st.rerun()
                
                with col2:
                    if st.button("Next Round (New Domain)", key="new_domain"):
                        game.reset_round()
                        save_game_state(game)
                        st.rerun()
                
                if st.button("End Game", key="end_game"):
                    game.reset_game()
                    save_game_state(game)
                    st.rerun()

if __name__ == "__main__":
    main()
