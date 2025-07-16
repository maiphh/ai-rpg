import streamlit as st
from player import Player
from game import *

def initialize_session_state():
    """Initialize session state variables"""
    if 'player' not in st.session_state:
        st.session_state.player = None
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
    if 'game_log' not in st.session_state:
        st.session_state.game_log = []
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False

def add_to_log(message):
    """Add message to game log"""
    st.session_state.game_log.append(message)

def main():
    st.set_page_config(page_title="AI RPG Game", page_icon="⚔️", layout="wide")
    
    initialize_session_state()
    
    st.title("⚔️ AI RPG Adventure")
    
    # Sidebar for character info
    with st.sidebar:
        st.header("Character Info")
        
        if st.session_state.player:
            player = st.session_state.player
            st.write(f"**Name:** {player.name}")
            st.write(f"**Level:** {player.level}")
            st.write(f"**HP:** {player.hp}/{player.max_hp}")
            
            # Display stats (using actual Player attributes)
            st.subheader("Stats")
            st.write(f"**Attack:** {player.atk}")
            st.write(f"**Defense:** {player.df}")
            
            # Display inventory
            if hasattr(player, 'inventory') and player.inventory:
                st.subheader("Inventory")
                for item in player.inventory:
                    if isinstance(item, dict):
                        st.write(f"• **{item['name']}**: {item['description']}")
                    else:
                        st.write(f"• {item}")
            else:
                st.subheader("Inventory")
                st.write("*Empty*")
        else:
            st.write("No character created yet")
    
    # Main game area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Character creation
        if not st.session_state.game_started:
            st.header("Create Your Character")
            
            with st.form("character_creation"):
                player_name = st.text_input("Enter your character's name:", 
                                          placeholder="Enter character name...")
                submitted = st.form_submit_button("Start Adventure")
                
                if submitted and player_name:
                    st.session_state.player = Player(name=player_name)
                    st.session_state.game_started = True
                    add_to_log(f"Welcome, {player_name}! Your adventure begins...")
                    
                    # Start the game
                    try:
                        start_game(st.session_state.player)
                        add_to_log("Game initialized successfully!")
                    except Exception as e:
                        add_to_log(f"Error starting game: {e}")
                    
                    st.rerun()
                elif submitted and not player_name:
                    st.error("Please enter a character name!")
        
        # Game interface
        else:
            st.header(f"Adventure of {st.session_state.player.name}")
            
            # Player input section
            if not st.session_state.game_over:
                st.subheader("Your Action")
                
                # Text input for player actions
                with st.form("player_action_form"):
                    player_input = st.text_input(
                        "What do you want to do?", 
                        placeholder="Enter your action (e.g., '1', 'attack goblin', 'use health potion')...",
                        key="action_input"
                    )
                    col_submit, col_continue = st.columns([1, 1])
                    
                    with col_submit:
                        action_submitted = st.form_submit_button("Take Action", type="primary")
                    
                    with col_continue:
                        continue_submitted = st.form_submit_button("Continue Story")
                
                # Handle player input
                if action_submitted and player_input:
                    try:
                        add_to_log(f"🎯 You: {player_input}")
                        
                        # Send player input to the game
                        from game import chat
                        response = chat(st.session_state.player, player_input)
                        
                        # Add the AI response to log
                        add_to_log(f"🎮 {response}")
                        
                        # Check if player died
                        if st.session_state.player.hp <= 0:
                            st.session_state.game_over = True
                            add_to_log("💀 Game Over! Your character has fallen.")
                            
                    except Exception as e:
                        add_to_log(f"Error: {e}")
                    
                    st.rerun()
                
                elif continue_submitted:
                    try:
                        # Continue without specific input
                        from game import chat
                        response = chat(st.session_state.player, "Continue the adventure")
                        
                        # Add the AI response to log
                        add_to_log(f"🎮 {response}")
                        
                        # Check if player died
                        if st.session_state.player.hp <= 0:
                            st.session_state.game_over = True
                            add_to_log("💀 Game Over! Your character has fallen.")
                            
                    except Exception as e:
                        add_to_log(f"Error: {e}")
                    
                    st.rerun()
                
                elif action_submitted and not player_input:
                    st.warning("Please enter an action!")
            
            # Quick action buttons
            if not st.session_state.game_over:
                st.subheader("Quick Actions")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("View Stats"):
                        add_to_log(f"📊 Current Stats - HP: {st.session_state.player.hp}/{st.session_state.player.max_hp}, ATK: {st.session_state.player.atk}, DEF: {st.session_state.player.df}, Level: {st.session_state.player.level}")
                
                with col_b:
                    if st.button("Rest", help="Restore some HP"):
                        if hasattr(st.session_state.player, 'rest'):
                            st.session_state.player.rest()
                        else:
                            # Simple rest implementation
                            heal_amount = min(10, st.session_state.player.max_hp - st.session_state.player.hp)
                            st.session_state.player.hp += heal_amount
                        add_to_log(f"🛌 You rest and recover some health. HP: {st.session_state.player.hp}")
                        st.rerun()
                
                with col_c:
                    if st.button("Use Item"):
                        if st.session_state.player.inventory:
                            # Show inventory items as selectbox
                            st.session_state.show_inventory = True
                        else:
                            add_to_log("🎒 Your inventory is empty!")
                
                # Inventory usage
                if hasattr(st.session_state, 'show_inventory') and st.session_state.show_inventory:
                    st.subheader("Use Item from Inventory")
                    if st.session_state.player.inventory:
                        item_names = [item['name'] if isinstance(item, dict) else str(item) for item in st.session_state.player.inventory]
                        selected_item = st.selectbox("Select item to use:", item_names)
                        
                        col_use, col_cancel = st.columns(2)
                        with col_use:
                            if st.button("Use Selected Item"):
                                try:
                                    result = st.session_state.player.use_item(selected_item)
                                    add_to_log(f"🎒 {result}")
                                    st.session_state.show_inventory = False
                                    st.rerun()
                                except Exception as e:
                                    add_to_log(f"Error using item: {e}")
                        
                        with col_cancel:
                            if st.button("Cancel"):
                                st.session_state.show_inventory = False
                                st.rerun()
            
            # Game over screen
            if st.session_state.game_over:
                st.error("💀 Game Over!")
                if st.button("Start New Game"):
                    # Reset session state
                    st.session_state.player = None
                    st.session_state.game_started = False
                    st.session_state.game_log = []
                    st.session_state.game_over = False
                    st.rerun()
    
    with col2:
        st.header("Game Log")
        
        # Display game log
        log_container = st.container()
        with log_container:
            if st.session_state.game_log:
                for i, message in enumerate(reversed(st.session_state.game_log[-20:])):  # Show last 20 messages
                    st.text(message)
            else:
                st.text("Game log will appear here...")
        
        # Clear log button
        if st.button("Clear Log"):
            st.session_state.game_log = []
            st.rerun()

if __name__ == "__main__":
    main()