# Game Data Enrichment using Google AI

This Python script uses the Google Generative AI API (Gemini) to enrich video game data provided in a CSV file. It takes a list of game titles and generates corresponding genres, short descriptions, and player modes (Singleplayer, Multiplayer, or Both).

## Features

- Loads game titles from a `Game_Thumbnail.csv` file.
- Uses the `gemini-1.5-flash-latest` model via the Google Generative AI API to:
  - Determine the primary genre.
  - Generate a concise description (under 30 words).
  - Identify the player mode.
- Adds the generated data as new columns (`genre`, `short_description`, `player_mode`) to the DataFrame.
- Saves the enriched data to a new CSV file named `enhanced_game_data.csv`.
- Includes delays between API calls to respect rate limits.

## Prerequisites

- Python 3.x
- A Google API Key with access to the Generative Language API (Gemini).

## Installation

1. **Clone the repository or download the files.**

2. **Navigate to the project directory:**

   ```bash
   cd path/to/Task-2
   ```

3. **(Optional but recommended) Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install the required Python libraries:**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Create a `.env` file** in the root of the project directory.
2. **Add your Google API Key** to the `.env` file:

   ```bash
   GOOGLE_API_KEY=YOUR_API_KEY_HERE
   ```

   Replace `YOUR_API_KEY_HERE` with your actual Google API key.

## Running the Script

1. **Ensure the input file `Game_Thumbnail.csv` is present** in the project directory. It should contain at least a column named `game_title`.

2. **Run the Python script:**

   ```bash
   python main.py
   ```

3. The script will print progress updates to the console.
4. Upon completion, a new file named `enhanced_game_data.csv` will be created in the same directory, containing the original data along with the newly generated columns.

## Input File Format

The input `Game_Thumbnail.csv` file must contain a column named `game_title`.

Example `Game_Thumbnail.csv`:

```csv
Game_ID,game_title,thumbnail_url
1,Elden Ring,url1
2,Stardew Valley,url2
3,Grand Theft Auto V,url3
```

## Output File Format

The output `enhanced_game_data.csv` will contain the original columns plus the new `genre`, `short_description`, and `player_mode` columns.

Example `enhanced_game_data.csv`:

```csv
Game_ID,game_title,thumbnail_url,genre,short_description,player_mode
1,Elden Ring,url1,Action RPG,Explore a vast, dark fantasy world filled with challenging foes and intricate lore. Master combat and magic.,Both
2,Stardew Valley,url2,Simulation,Inherit a farm plot. Cultivate crops, raise animals, build relationships, and explore caves.,Both
3,Grand Theft Auto V,url3,Action-Adventure,"Switch between three criminals pulling off heists in a sprawling satirical city. Engage in driving, shooting, and various activities.",Both
```
