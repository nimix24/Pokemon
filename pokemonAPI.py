from flask import Flask, jsonify, request
import requests
import json
import random
import os

app = Flask(__name__)


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


# Initialize PokemonManager
pokemon_manager = PokemonManager()


@app.route('/add_pokemon', methods=['GET'])
def add_pokemon():
    # Fetch a random Pokémon name
    pokemon_name = pokemon_manager.fetch_random_pokemon()

    # Check if Pokémon is already in the collection
    pokemon_data = pokemon_manager.get_pokemon(pokemon_name)
    if not pokemon_data:
        # Fetch Pokémon details and add to the collection
        pokemon_data = pokemon_manager.fetch_pokemon_details(pokemon_name)
        pokemon_manager.add_pokemon(pokemon_data)
        result = {
            "message": f"Added {pokemon_name} to your collection",
            "pokemon_data": pokemon_data
        }
    else:
        result = {
            "message": f"{pokemon_name} already exists in your collection",
            "pokemon_data": pokemon_data
        }

    return jsonify(result)


if __name__ == '__main__':
    # Run the app on host='0.0.0.0' to make it externally accessible
    app.run(host='0.0.0.0', port=80)
