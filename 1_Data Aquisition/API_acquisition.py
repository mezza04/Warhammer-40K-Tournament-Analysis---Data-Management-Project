"""
Step 1 del pipeline: acquisizione dei dati e caricamento in un file json.
"""
import requests
import json
import time
from typing import Dict, Optional, List

API_BASE_URL = "https://listengine-v3-be.onrender.com"
REQUEST_TIMEOUT = 10
DELAY_BETWEEN_REQUESTS = 0.5


def normalize_army_name(army_name: str) -> str:
    """Normalizza il nome dell'esercito: iniziali maiuscole per ogni parola"""
    return army_name.title()


def clean_list_data(list_data: Optional[Dict]) -> Optional[Dict]:
    """Rimuove informazioni ridondanti da listData"""
    if not list_data:
        return None
    
    cleaned = {
        'list': list_data.get('list'),
        'path': list_data.get('path', []),
        'roundsNumber': list_data.get('roundsNumber')
    }
    
    # Normalizza army names nel path
    for match in cleaned.get('path', []):
        if 'army' in match:
            match['army'] = normalize_army_name(match['army'])
    
    return cleaned


def fetch_event_data(event_id: str) -> Dict:
    """Scarica i dati dell'evento dall'API"""
    api_url = f"{API_BASE_URL}/events/{event_id}"
    print(f"Fetching event data from: {api_url}")
    
    response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    
    return response.json()


def fetch_player_list(player_id: str) -> Optional[Dict]:
    """Scarica la lista e i match di un giocatore specifico"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/lists/{player_id}", 
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero lista per player {player_id}: {e}")
        return None


def enrich_player_data(player: Dict) -> Dict:
    """Arricchisce i dati del giocatore con la lista e normalizza l'esercito"""
    print(f"Scaricando lista di {player['playerName']}...", end=" ")
    
    player_list_data = fetch_player_list(player['playerId'])
    
    # Aggiorna il player esistente invece di ricostruirlo
    player['army'] = normalize_army_name(player['army'])
    player['listData'] = clean_list_data(player_list_data) if player_list_data else None
    
    print("✓" if player_list_data else "✗")
    
    return player


def scraping_warhammer(event_id: str) -> Dict:
    """Fa scraping dall'API di Warhammer e restituisce i dati dei giocatori"""
    data = fetch_event_data(event_id)
    
    print(f"Evento: {data['eventName']}\nGiocatori: {data['playersNumber']}\n"
          f"Città: {data['city']}, {data['state']}, {data['country']}")
    
    return data


def scraping_complete_with_lists(event_id: str, max_players: Optional[int] = None) -> Dict:
    """Scarica tutti i dati dell'evento incluse le liste dei giocatori"""
    event_data = scraping_warhammer(event_id)
    players = event_data['players'][:max_players] if max_players else event_data['players']
    
    print(f"\n=== Scaricamento liste per {len(players)} giocatori ===\n")
    
    players_with_lists = []
    for i, player in enumerate(players, 1):
        print(f"[{i}/{len(players)}] ", end="")
        enriched_player = enrich_player_data(player)
        players_with_lists.append(enriched_player)
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    return {
        'eventInfo': {
            'eventName': event_data['eventName'],
            'eventDate': event_data['eventdate'],
            'location': f"{event_data['city']}, {event_data['state']}, {event_data['country']}",
            'totalPlayers': event_data['playersNumber']
        },
        'players': players_with_lists
    }


def save_to_json(data: Dict, filename: str = 'warhammer_complete_data.json') -> None:
    """Salva i dati in un file JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Dati salvati in {filename}")


def extract_lists_summary(data: Dict) -> List[Dict]:
    """Estrae un sommario delle liste di tutti i giocatori"""
    return [{
        'rank': p['rank'],
        'playerName': p['playerName'],
        'army': p['army'],
        'detachment': p['detachment'],
        'score': p['score'],
        'hasListData': p.get('listData') is not None
    } for p in data['players']]


def print_summary(lists_summary: List[Dict]) -> None:
    """Stampa il sommario dei risultati"""
    with_lists = sum(1 for p in lists_summary if p['hasListData'])
    
    print("\n" + "=" * 60)
    print("SOMMARIO")
    print("=" * 60)
    print(f"Giocatori processati: {len(lists_summary)}")
    print(f"Liste scaricate con successo: {with_lists}")
    print(f"Liste non disponibili: {len(lists_summary) - with_lists}")
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETATO!")
    print("=" * 60)


# FUNZIONE DI ATTIVAZIONE
if __name__ == "__main__":
    event_id = '163e56b3c0ede8300a6ccb5a'
    
    print("=" * 60)
    print("WARHAMMER LIST SCRAPER")
    print("=" * 60)
    
    # Esegui lo scraping
    data = scraping_complete_with_lists(event_id)
    save_to_json(data, 'warhammer_complete_data.json')
    
    # Stampa sommario
    lists_summary = extract_lists_summary(data)
    print_summary(lists_summary)