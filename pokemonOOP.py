import tkinter as tk
import requests
import json
import random
import os


# This class is responsible for managing Pokémon data
class PokemonManager:
    def __init__(self):
        self.pokemon_json_path = 'pokemon_collection.json'
        self.pokemon_collection = self.load_pokemon_collection()

    def load_pokemon_collection(self):
        # Load the Pokémon collection from a JSON file if it exists
        if os.path.exists(self.pokemon_json_path):
            with open(self.pokemon_json_path, 'r') as f:
                return json.load(f)
        return {}

    def save_pokemon_collection(self):
        # Save the Pokémon collection to a JSON file
        with open(self.pokemon_json_path, 'w') as f:
            json.dump(self.pokemon_collection, f, indent=4)

    def fetch_random_pokemon(self):
        # Fetch a random Pokémon name from the API
        url = "https://pokeapi.co/api/v2/pokemon?limit=1000"
        response = requests.get(url)
        data = response.json()
        all_pokemon = data['results']
        return random.choice(all_pokemon)['name']

    def fetch_pokemon_details(self, name):
        # Fetch Pokémon details from the API by name
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        response = requests.get(url)
        data = response.json()
        pokemon_data = {
            'name': data['name'],
            'height': data['height'],
            'weight': data['weight'],
            'base_experience': data['base_experience']
        }
        return pokemon_data

    def add_pokemon(self, pokemon_data):
        # Add Pokémon to the local collection and save it
        if pokemon_data['name'] not in self.pokemon_collection:
            self.pokemon_collection[pokemon_data['name']] = pokemon_data
            self.save_pokemon_collection()

    def get_pokemon(self, name):
        # Get Pokémon from local collection if it exists
        return self.pokemon_collection.get(name, None)


# This class handles the GUI
class PokemonApp:
    def __init__(self, root, pokemon_manager):
        self.manager = pokemon_manager
        self.root = root
        self.root.title("Pokemon Drawer")    # Set the window title

        # Question label
        #self.root.geometry("270x200")
        #self.root.resizable(True, True)
        self.question_label = tk.Label(root, text="Would you like to draw a Pokémon?", font=('Helvetica', 12))
        self.question_label.pack(pady=20)

        # Yes and No buttons
        self.yes_button = tk.Button(root, text="Yes", command=self.draw_pokemon)
        self.yes_button.pack(side=tk.LEFT, padx=20)

        self.no_button = tk.Button(root, text="No", command=self.exit_app)
        self.no_button.pack(side=tk.RIGHT, padx=20)

        # Label for displaying results
        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=20)

    def draw_pokemon(self):
        # Get a random Pokémon and show the result
        pokemon_name = self.manager.fetch_random_pokemon()

        # Check if the Pokémon is already in the collection
        pokemon_data = self.manager.get_pokemon(pokemon_name)
        if pokemon_data:
            result_text = f"{pokemon_name} already exists in your collection:\n" + \
                          json.dumps(pokemon_data, indent=4)
        else:
            # Fetch new Pokémon details from API
            pokemon_data = self.manager.fetch_pokemon_details(pokemon_name)
            self.manager.add_pokemon(pokemon_data)
            result_text = f"Added {pokemon_name} to your collection:\n" + \
                          json.dumps(pokemon_data, indent=4)

        # Update the result label with the Pokémon details
        self.result_label.config(text=result_text)

    def exit_app(self):
        # Exit the application
        self.root.quit()


# Main function to run the app
if __name__ == "__main__":
    # Create root window
    root = tk.Tk()

    # Create an instance of PokemonManager to handle Pokémon logic
    pokemon_manager = PokemonManager()

    # Create the application using the PokemonApp class
    app = PokemonApp(root, pokemon_manager)

    # Start the Tkinter event loop
    root.mainloop()
