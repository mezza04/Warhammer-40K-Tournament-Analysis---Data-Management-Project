"""
Warhammer Tournament Database Loader
Carica dati di tornei Warhammer 40K da JSON e crea un database SQLite normalizzato
"""

import sqlite3
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import re


class WarhammerDBLoader:
    """Per gestire il caricamento dei dati nel database"""
    
    def __init__(self, db_name='warhammer_tournaments.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Apre la connessione al database"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('PRAGMA foreign_keys = ON')
        
    def close(self):
        """Chiude la connessione al database"""
        if self.conn:
            self.conn.close()
            
    def create_schema(self):
        """Crea lo schema del database con tutte le constraints"""
        # Drop tabelle esistenti
        self.cursor.execute('DROP TABLE IF EXISTS matches')
        self.cursor.execute('DROP TABLE IF EXISTS army_list_units')
        self.cursor.execute('DROP TABLE IF EXISTS army_lists')
        self.cursor.execute('DROP TABLE IF EXISTS players')
        self.cursor.execute('DROP TABLE IF EXISTS tournaments')
        self.cursor.execute('DROP TABLE IF EXISTS prices')
        
        # Tournaments
        self.cursor.execute('''
        CREATE TABLE tournaments (
            ID_TOURNAMENT INTEGER PRIMARY KEY,
            NAME TEXT NOT NULL,
            LOCATION TEXT,
            EVENT_DATE DATE,
            TOTAL_PLAYERS INTEGER,
            YEAR INTEGER
        )
        ''')

        # Prices (reference table)
        self.cursor.execute('''
        CREATE TABLE prices (clean_name TEXT NOT NULL, 
            points_unit INTEGER NOT NULL,
            PRICE_unit REAL,
            army TEXT,
            PRIMARY KEY (clean_name, army)
        )
        ''')
        
        # Players
        self.cursor.execute('''
        CREATE TABLE players (
            ID_PLAYER TEXT PRIMARY KEY,
            ID_TOURNAMENT INTEGER NOT NULL,
            RANK INTEGER,
            NAME TEXT,
            SURNAME TEXT,
            FULL_NAME TEXT,
            ARMY TEXT,
            DETACHMENT TEXT,
            WINS INTEGER,
            LOSSES INTEGER,
            TIES INTEGER,
            SCORE TEXT,
            FOREIGN KEY (ID_TOURNAMENT) REFERENCES tournaments(ID_TOURNAMENT)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
        ''')
        
        # Army Lists
        self.cursor.execute('''
        CREATE TABLE army_lists (
            ID_TOURNAMENT INTEGER NOT NULL,
            ID_PLAYER TEXT NOT NULL,
            UNITS TEXT,
            WARLORD TEXT,
            FOREIGN KEY (ID_TOURNAMENT) REFERENCES tournaments(ID_TOURNAMENT)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (ID_PLAYER) REFERENCES players(ID_PLAYER)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
        ''')
        
        # Army List Units (dettaglio unità)
        self.cursor.execute('''
        CREATE TABLE army_list_units (
            ID_PLAYER TEXT NOT NULL,
            clean_name TEXT,
            points INTEGER,
            quantity INTEGER,
            single_price REAL,
            total_price REAL,
            FOREIGN KEY (ID_PLAYER) REFERENCES players(ID_PLAYER)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
        ''')
        
        # Matches
        self.cursor.execute('''
        CREATE TABLE matches (
            ID_MATCH INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_TOURNAMENT INTEGER NOT NULL,
            ID_PLAYER1 TEXT NOT NULL,
            NAME_PLAYER1 TEXT,
            ID_PLAYER2 TEXT NOT NULL,
            NAME_PLAYER2 TEXT,
            SCORE_PLAYER1 INTEGER,
            SCORE_PLAYER2 INTEGER,
            FOREIGN KEY (ID_TOURNAMENT) REFERENCES tournaments(ID_TOURNAMENT)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (ID_PLAYER1) REFERENCES players(ID_PLAYER)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (ID_PLAYER2) REFERENCES players(ID_PLAYER)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
        ''')
        
        print("Schema database creato")
        
    def create_indexes(self):
        """Crea indici per ottimizzare le query"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_players_tournament ON players(ID_TOURNAMENT)',
            'CREATE INDEX IF NOT EXISTS idx_players_army ON players(ARMY)',
            'CREATE INDEX IF NOT EXISTS idx_army_lists_player ON army_lists(ID_PLAYER)',
            'CREATE INDEX IF NOT EXISTS idx_army_lists_tournament ON army_lists(ID_TOURNAMENT)',
            'CREATE INDEX IF NOT EXISTS idx_army_units_player ON army_list_units(ID_PLAYER)',
            'CREATE INDEX IF NOT EXISTS idx_army_units_name ON army_list_units(clean_name)',
            'CREATE INDEX IF NOT EXISTS idx_matches_tournament ON matches(ID_TOURNAMENT)',
            'CREATE INDEX IF NOT EXISTS idx_matches_player1 ON matches(ID_PLAYER1)',
            'CREATE INDEX IF NOT EXISTS idx_matches_player2 ON matches(ID_PLAYER2)'
        ]
        
        for idx in indexes:
            self.cursor.execute(idx)
        
        print("Indici creati")


def load_tournament_data(json_path):
    """Carica i dati del torneo dal JSON"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    event_info = data['eventInfo']
    extended_lists = data['extendedLists']
    
    # Tournament DataFrame
    event_date = datetime.strptime(event_info['eventDate'], "%B %d, %Y")
    df_tournament = pd.DataFrame([{
        'ID_TOURNAMENT': 1,
        'NAME': event_info['eventName'],
        'LOCATION': event_info['location'],
        'EVENT_DATE': event_date,
        'TOTAL_PLAYERS': event_info['totalPlayers'],
        'YEAR': event_date.year
    }])
    
    return df_tournament, extended_lists


def create_players_df(extended_lists):
    """Crea DataFrame dei giocatori"""
    players_data = []
    
    for player in extended_lists:
        score = player['score']
        wins, losses, ties = map(int, score.split('-'))
        
        players_data.append({
            'ID_PLAYER': player['playerId'],
            'ID_TOURNAMENT': 1,
            'RANK': player['rank'],
            'NAME': player['firstName'].title(),
            'SURNAME': player['lastName'].title(),
            'FULL_NAME': re.sub(r'\s+', ' ', player['playerName'].strip()).title(),
            'ARMY': player['army'].lower(),
            'DETACHMENT': player['detachment'].lower(),
            'WINS': wins,
            'LOSSES': losses,
            'TIES': ties,
            'SCORE': score
        })
    players_data = pd.DataFrame(players_data)
    return players_data


def create_matches_df(extended_lists, players_data):
    """Crea DataFrame dei match"""
    match_data = []
    
    for player in extended_lists:
        player_name = player['playerName']
        player_id = player['playerId']
        path = player.get('path', [])
        
        for match in path:
            opponent_id = match['opponentListuuid']
            opponent_name = match['player']
            status = match['status']
            player_score = int(match['playerScore'])
            opponent_score = int(match['rivalScore'])
            
            match_data.append({
                'ID_TOURNAMENT': 1,
                'ID_PLAYER1': player_id,
                'NAME_PLAYER1': re.sub(r'\s+', ' ', player_name.strip()).title(),
                'ID_PLAYER2': opponent_id,
                'NAME_PLAYER2': re.sub(r'\s+', ' ', opponent_name.strip()).title(),
                'SCORE_PLAYER1': player_score,
                'SCORE_PLAYER2': opponent_score,
                'STATUS': status
            })
    
    df_match_tot = pd.DataFrame(match_data)
    
    
    # Filtra solo vittorie per evitare duplicati
    df_victory = df_match_tot[df_match_tot['STATUS'] == 'victory'].copy()
    
    # Pareggi: due righe speculari → ne teniamo una sola
    df_tie = df_match_tot[df_match_tot['STATUS'] == 'draw'].copy()
    
    # Regola deterministica: tieni solo ID_PLAYER1 < ID_PLAYER2
    df_tie = df_tie[df_tie['ID_PLAYER1'] < df_tie['ID_PLAYER2']]
    
    # Unione finale
    df_match = pd.concat([df_victory, df_tie], ignore_index=True)


    df_match = df_match.drop(columns=['STATUS'])
    
    return df_match


def create_army_lists_df(extended_lists):
    """Crea DataFrame delle liste esercito"""
    army_list_data = []
    
    for player in extended_lists:
        player_id = player['playerId']
        army_list = player.get('list', {})
        
        units_dict = {}
        warlord = None
        
        for category, units in army_list.items():
            if isinstance(units, list):
                for unit in units:
                    unit_name = unit['name'].lower().strip() + "_" + str(unit['points'])
                    
                    if unit.get('is_warlord', False):
                        warlord = unit_name
                    
                    units_dict[unit_name] = units_dict.get(unit_name, 0) + 1
        
        army_list_data.append({
            'ID_TOURNAMENT': 1,
            'ID_PLAYER': player_id,
            'UNITS': units_dict,
            'WARLORD': warlord
        })
    
    return pd.DataFrame(army_list_data)


def normalize_text(text_series):
    """Normalizza una serie di testo (lowercase, trim, spazi singoli)"""
    return (text_series
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
            .str.lower())


def load_prices(csv_path):
    """Carica la tabella dei prezzi"""
    df_prices_raw = pd.read_csv(
        csv_path, 
        sep=";", 
        encoding='cp1252',
        names=["army",'clean_name', 'points_unit', 'PRICE_unit'],
        header=0,
        usecols=[0, 1, 2, 3]
    )

    df_prices_raw['points_unit'] = pd.to_numeric(df_prices_raw['points_unit'], errors='coerce')
    df_prices_raw['PRICE_unit'] = pd.to_numeric(df_prices_raw['PRICE_unit'], errors='coerce')

    df_prices_army = df_prices_raw.copy()
    

    # Normalizzazione nome
    df_prices_army['clean_name'] = normalize_text(df_prices_army['clean_name']) #questo ha la colonna army
    df_prices_army= df_prices_army.drop_duplicates()

    # Versione CLEAN per merge
    df_prices = (
        df_prices_army[['clean_name', 'points_unit', 'PRICE_unit']]
        .copy().drop_duplicates()
    )
    
    return df_prices, df_prices_raw, df_prices_army # df_prices_raw per data quality assessment


def explode_army_lists(df_army_lists):
    """Esplode le liste esercito in unità separate"""
    rows = []
    
    for _, row in df_army_lists.iterrows():
        for unit_key, quantity in row['UNITS'].items():
            rows.append({
                'ID_PLAYER': row['ID_PLAYER'],
                'WARLORD': row['WARLORD'],
                'unit_name': unit_key,
                'quantity': quantity
            })
    
    df_expanded = pd.DataFrame(rows)
    
    # Separa nome e punti
    df_expanded[['clean_name', 'points']] = df_expanded['unit_name'].str.rsplit('_', n=1, expand=True)
    df_expanded['points'] = pd.to_numeric(df_expanded['points'], errors='coerce')
    df_expanded['clean_name'] = normalize_text(df_expanded['clean_name'])
    
    return df_expanded


def calculate_prices(df_expanded, df_prices):
    """Calcola i prezzi delle unita basandosi sui punti"""
    # Merge con prezzi
    df_merged = df_expanded.merge(
        df_prices[['clean_name', 'PRICE_unit', 'points_unit']],
        on='clean_name',
        how='left'
    )
    
    # Calcola ratio e prezzi
    df_merged['ratio'] = df_merged['points'] / df_merged['points_unit']
    df_merged['remainder'] = df_merged['points'] % df_merged['points_unit']
    
    # Arrotonda in base allo scarto (< 40 = floor, >= 40 = ceil)
    df_merged['ratio_rounded'] = df_merged.apply(
        lambda row: np.floor(row['ratio']) if row['remainder'] < 40 else np.ceil(row['ratio']),
        axis=1
    )
    
    df_merged['single_price'] = df_merged['PRICE_unit'] * df_merged['ratio_rounded']
    df_merged['total_price'] = df_merged['single_price'] * df_merged['quantity']
    
    return df_merged[['ID_PLAYER', 'clean_name', 'points', 'quantity', 'single_price', 'total_price']]


def main(json_path, prices_path, db_name='warhammer_tournaments.db'):
    """Funzione principale per caricare tutti i dati"""
    
    print(f"Inizio caricamento dati da {json_path}")
    
    # Carica dati
    df_tournament, extended_lists = load_tournament_data(json_path)
    print(f"Torneo: {df_tournament['NAME'].iloc[0]}")
    print(f"Giocatori: {len(extended_lists)}")
    
    df_players = create_players_df(extended_lists)
    df_matches = create_matches_df(extended_lists, df_players)
    df_army_lists = create_army_lists_df(extended_lists)
    
    # Processa prezzi
    print(f"Calcolo prezzi da {prices_path}")
    df_prices, df_prices_raw, df_prices_army = load_prices(prices_path)
    df_expanded = explode_army_lists(df_army_lists)
    df_army_list_units = calculate_prices(df_expanded, df_prices)

    
    missing_prices = df_army_list_units['total_price'].isna().sum()
    if missing_prices > 0:
        print(f"X {missing_prices} unità senza prezzo")
        print(df_army_list_units[df_army_list_units['total_price'].isna()])
    else:
        print("Tutti i prezzi calcolati correttamente")

    
    # Crea database
    print(f"Creazione database {db_name}")
    loader = WarhammerDBLoader(db_name)
    loader.connect()
    loader.create_schema()
    
    # Carica dati
    df_tournament.to_sql('tournaments', loader.conn, if_exists='append', index=False)
    print(f"Tournaments: {len(df_tournament)} righe")

    df_prices_army.to_sql('prices', loader.conn, if_exists='append', index=False)
    print(f"Prices: {len(df_prices_army)} righe")

    
    df_players.to_sql('players', loader.conn, if_exists='append', index=False)
    print(f"Players: {len(df_players)} righe")
    
    df_army_lists_copy = df_army_lists.copy()
    df_army_lists_copy['UNITS'] = df_army_lists_copy['UNITS'].astype(str)
    df_army_lists_copy[['ID_TOURNAMENT', 'ID_PLAYER', 'UNITS', 'WARLORD']].to_sql(
        'army_lists', loader.conn, if_exists='append', index=False
    )
    print(f"Army Lists: {len(df_army_lists)} righe")
    
    df_army_list_units.to_sql('army_list_units', loader.conn, if_exists='append', index=False)
    print(f"Army List Units: {len(df_army_list_units)} righe")
    
    df_matches[['ID_TOURNAMENT', 'ID_PLAYER1', 'NAME_PLAYER1', 'ID_PLAYER2', 
                'NAME_PLAYER2', 'SCORE_PLAYER1', 'SCORE_PLAYER2']].to_sql(
        'matches', loader.conn, if_exists='append', index=False
    )
    print(f"Matches: {len(df_matches)} righe")
    
    loader.create_indexes()
    loader.conn.commit()
    loader.close()
    
    print(f"Database '{db_name}' creato con successo!")


if __name__ == "__main__":
    # Configurazione
    JSON_FILE = "warhammer_final_cleaned.json"
    PRICES_FILE = "Warhammer_prezzi.csv"
    DB_NAME = "warhammer_tournaments.db"
    
    # Esegui caricamento
    main(JSON_FILE, PRICES_FILE, DB_NAME)