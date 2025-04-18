"""
This module interacts with the Google AI API to enrich video game data.
It processes game titles to generate genres, descriptions, and player modes,
then saves the enhanced data to a CSV file.

Installation:
    pip install pandas google-generativeai python-dotenv

Usage:
    python -u main.py
"""

import os
import time
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv


# --- Step 1: Setup ---
print("--- Step 1: Setting up ---")

# Load environment variables from .env file
load_dotenv()

# Configure the genai library with the API key
api_key = os.getenv("GOOGLE_API_KEY")  # Standard name often used, or use your "API_KEY"
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables or .env file")

try:
    genai.configure(api_key=api_key)
    print("Successfully configured Google AI service.")

    # Using 1.5 flash as it's fast and capable for these kinds of tasks
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    print(f"Using model: {model.model_name}")


except Exception as e:
    print(f"Error configuring Google AI or initializing model: {e}")
    exit()  # Exit if setup fails

# --- Step 2: Load the CSV Data ---
print("\n--- Step 2: Loading CSV Data ---")
try:
    INPUT_FILE = "Game_Thumbnail.csv"
    df = pd.read_csv(INPUT_FILE)
    print(f"Successfully loaded {INPUT_FILE}.")
    print("DataFrame Head:")
    print(df.head())
except FileNotFoundError:
    print(
        f"Error: {INPUT_FILE} not found. Please ensure it's in the correct directory."
    )
    exit()
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()


# --- Step 3: Interact with Google AI API ---
print("\n--- Step 3: Enriching Data using Google AI API ---")

# Lists to store the generated data
GENRES = []
SHORT_DESCRIPTIONS = []
PLAYER_MODES = []

# Loop through each game title in the DataFrame
total_games = len(df)
for index, row in df.iterrows():
    game_title = row["game_title"]
    print(f"\nProcessing ({index + 1}/{total_games}): {game_title}")

    # --- A. Genre Classification ---
    prompt_genre = (
        f"What is the primary single-word genre for the video game '{game_title}'? "
        f"Examples: Fighting, Shooter, RPG, Simulation, Strategy, Action, Adventure, Puzzle, Sports, Racing. "
        f"Respond with only the single-word genre."
    )
    try:
        response_genre = model.generate_content(
            prompt_genre,
            # generation_config=generation_config # Optional config
        )
        GENRE = response_genre.text.strip()
        print(f"  Genre: {GENRE}")
        GENRES.append(GENRE)
    except Exception as e:
        print(f"  Error getting genre for {game_title}: {e}")
        # Check if the error is due to blocked content (safety settings)
        try:
            print(f"  Safety feedback: {response_genre.prompt_feedback}")
        except (
            Exception
        ):  # Handle case where response object might not exist or have feedback
            pass
        GENRES.append("Error")  # Placeholder for errors

    time.sleep(3)  # Small delay to avoid hitting rate limits

    # --- B. Short Description Generation ---
    prompt_description = (
        f"Imagine you are writing the content for a 'description' field in a game database for '{game_title}'. "
        f"Write only the text for that field, ensuring it's concise (strictly under 30 words) and starts directly with the description itself."
        f"Do NOT use the game title in the description. Focus on the gameplay."
    )
    try:
        response_description = model.generate_content(prompt_description)
        DESCRIPTION = response_description.text.strip()

        prefix_to_remove = "Description: "
        # Check if the description starts with the prefix (case-insensitive)
        if DESCRIPTION.lower().startswith(prefix_to_remove.lower()):
            # If it does, remove the prefix and any leading whitespace left over
            DESCRIPTION = DESCRIPTION[len(prefix_to_remove) :].strip()

        if DESCRIPTION.startswith(prefix_to_remove):
            # If it does, remove the prefix and any leading whitespace left over
            DESCRIPTION = DESCRIPTION[len(prefix_to_remove) :].strip()

        # Optional: Add a check/truncation if the model ignores the length limit
        if len(DESCRIPTION.split()) > 35:  # Allow a little leeway
            DESCRIPTION = " ".join(DESCRIPTION.split()[:30]) + "..."
            print(f"  Description (truncated): {DESCRIPTION}")
        else:
            print(f"  Description: {DESCRIPTION}")
        SHORT_DESCRIPTIONS.append(DESCRIPTION)
    except Exception as e:
        print(f"  Error getting description for {game_title}: {e}")
        try:
            print(f"  Safety feedback: {response_description.prompt_feedback}")
        except Exception:
            pass
        SHORT_DESCRIPTIONS.append("Error")

    time.sleep(3)  # Small delay

    # --- C. Player Mode Determination ---
    prompt_player_mode = (
        f"Does the video game '{game_title}' support single-player only, multiplayer only, or both? "
        f"Respond with *only one* of these exact words: 'Singleplayer', 'Multiplayer', or 'Both'."
    )
    try:
        response_player_mode = model.generate_content(prompt_player_mode)
        PLAYER_MODE = response_player_mode.text.strip()
        # Basic validation to ensure it's one of the expected outputs
        if PLAYER_MODE not in ["Singleplayer", "Multiplayer", "Both"]:
            print(
                f"  Warning: Unexpected player mode response '{PLAYER_MODE}'. Storing as received."
            )
            # You could add logic here to retry or default if needed
        print(f"  Player Mode: {PLAYER_MODE}")
        PLAYER_MODES.append(PLAYER_MODE)
    except Exception as e:
        print(f"  Error getting player mode for {game_title}: {e}")
        try:
            print(f"  Safety feedback: {response_player_mode.prompt_feedback}")
        except Exception:
            pass
        PLAYER_MODES.append("Error")

    time.sleep(6)  # Small delay before processing the next game


print("\n--- Finished processing all games ---")

# --- Step 4: Add New Data to DataFrame ---
print("\n--- Step 4: Adding New Data to DataFrame ---")

# First, check if the number of results matches the number of rows in the DataFrame
if (
    len(GENRES) == len(df)
    and len(SHORT_DESCRIPTIONS) == len(df)
    and len(PLAYER_MODES) == len(df)
):
    # Add the lists as new columns to the DataFrame
    df["genre"] = GENRES
    df["short_description"] = SHORT_DESCRIPTIONS
    df["player_mode"] = PLAYER_MODES

    print(
        "Successfully added new columns: 'genre', 'short_description', 'player_mode'."
    )
    print("Updated DataFrame Head:")
    print(df.head())
else:
    # This handles potential issues if the loop was interrupted or an error caused list length mismatch
    print(
        "Error: Mismatch between the number of results and the number of rows in the DataFrame."
    )
    print(f"  DataFrame rows: {len(df)}")
    print(f"  Genres found: {len(GENRES)}")
    print(f"  Descriptions found: {len(SHORT_DESCRIPTIONS)}")
    print(f"  Player modes found: {len(PLAYER_MODES)}")
    print("Cannot reliably add columns. Please check processing logs for errors.")

# --- Step 5: Save the Enhanced Data ---
print("\n--- Step 5: Saving Enhanced Data ---")

# Define the output file name
OUTPUT_FILE = "enhanced_game_data.csv"

# Save the DataFrame (only if columns were added successfully)
if (
    "genre" in df.columns
    and "short_description" in df.columns
    and "player_mode" in df.columns
):
    try:
        # Save to CSV, without writing the Pandas index column
        df.to_csv(
            OUTPUT_FILE, index=False, encoding="utf-8"
        )  # Added encoding='utf-8' for broader compatibility
        print(f"Enhanced data successfully saved to '{OUTPUT_FILE}'")
    except Exception as e:
        print(f"Error saving DataFrame to CSV: {e}")
else:
    print("Skipping save because new columns were not added due to previous errors.")

print("\n--- Script finished ---")
