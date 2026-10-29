"""
Step 2 del pipeline: parsing + validazione + separazione liste.
"""
import re
import json
from typing import Dict
from validator import validate_and_separate


def parse_warhammer_list(html_text: str) -> Dict:
    """
    Parsa l'HTML della lista Warhammer e organizza per categorie.
    (PARSING LOGIC IMMUTATA - non toccare)
    """
    if not html_text or not isinstance(html_text, str):
        return {
            'characters': [],
            'battleline': [],
            'dedicated_transports': [],
            'other_datasheets': []
        }
    
    # Rimuovi i tag HTML preservando la struttura con spazi
    clean_text = re.sub(r'<br\s*/?>', '\n', html_text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    lines = clean_text.split('\n')
    
    result = {
        'characters': [],
        'battleline': [],
        'dedicated_transports': [],
        'other_datasheets': []
    }
    
    current_section = None
    current_unit = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Salta righe vuote
        if not stripped:
            i += 1
            continue
        
        line_upper = stripped.upper()
        
        # Identifica le sezioni
        if line_upper == 'CHARACTERS':
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'characters'
            current_unit = None
            i += 1
            continue
        elif line_upper == 'BATTLELINE':
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'battleline'
            current_unit = None
            i += 1
            continue
        elif line_upper == 'DEDICATED TRANSPORTS':
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'dedicated_transports'
            current_unit = None
            i += 1
            continue
        elif line_upper.startswith('OTHER DATASHEET'):
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'other_datasheets'
            current_unit = None
            i += 1
            continue
        
        # Identifica una nuova unità
        points_match = re.search(r'\((\d+)\s*points?\)\s*$', stripped, re.IGNORECASE)
        if points_match and not stripped.startswith('•') and not stripped.startswith('◦') and current_section:
            if current_unit:
                result[current_section].append(current_unit)
            
            unit_name = re.sub(r'\s*\(\d+\s*points?\)\s*$', '', stripped, flags=re.IGNORECASE).strip()
            points = int(points_match.group(1))
            
            current_unit = {
                'name': unit_name,
                'points': points,
                'enhancements': [],
                'is_warlord': False
            }
            
            i += 1
            continue
        
        # Processa Warlord ed Enhancements
        if current_unit and current_section and (stripped.startswith('•') or stripped.startswith('◦')):
            if stripped.startswith('•'):
                content = stripped[1:].strip()
            else:
                content = stripped[1:].strip()
            
            # Warlord
            if content.lower() == 'warlord':
                current_unit['is_warlord'] = True
                i += 1
                continue
            
            # Enhancement
            if 'Enhancement:' in content or 'Enhancements:' in content:
                enhancement = content.split('Enhancement')[1].strip()
                if enhancement.startswith('s:'):
                    enhancement = enhancement[2:].strip()
                elif enhancement.startswith(':'):
                    enhancement = enhancement[1:].strip()
                current_unit['enhancements'].append(enhancement)
                i += 1
                continue
            
            i += 1
            continue
        
        i += 1
    
    # Aggiungi l'ultima unità
    if current_unit and current_section:
        result[current_section].append(current_unit)
    
    return result


def parse_json_file(
    input_filename: str,
    output_filename: str = 'warhammer_extended_lists.json',
    auto_validate: bool = True
):
    """
    Parsa le liste HTML dal file JSON e opzionalmente valida/separa.
    
    Args:
        input_filename: File JSON di input
        output_filename: File JSON di output con liste parsate
        auto_validate: Se True, valida automaticamente e separa le liste
    """
    print("=" * 70)
    print(" " * 15 + "WARHAMMER JSON LIST PARSER")
    print("=" * 70)
    
    # Leggi il file JSON
    print(f"\nLettura file: {input_filename}")
    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERRORE: File '{input_filename}' non trovato!")
        return
    except json.JSONDecodeError:
        print(f"ERRORE: File '{input_filename}' non è un JSON valido!")
        return
    
    print(f"✓ File caricato correttamente")
    print(f"  Evento: {data['eventInfo']['eventName']}")
    print(f"  Giocatori totali: {len(data['players'])}")
    
    # Processa tutte le liste
    print(f"\n=== Parsing liste ===\n")
    
    extended_lists = []
    parsed_count = 0
    skipped_count = 0
    
    for i, player in enumerate(data['players'], 1):
        player_name = player['playerName']
        print(f"[{i}/{len(data['players'])}] Parsing lista di {player_name}...", end=" ")
        
        # Verifica se ha listData
        if not player.get('listData') or not player['listData']:
            print("✗ (lista non disponibile)")
            skipped_count += 1
            continue
        
        list_data = player['listData']
        
        # Verifica se ha la lista HTML
        if not list_data.get('list'):
            print("✗ (HTML lista mancante)")
            skipped_count += 1
            continue
        
        # Parsa la lista HTML
        html_list = list_data['list']
        categorized_list = parse_warhammer_list(html_list)
        
        print("✓")
        parsed_count += 1
        
        # Crea documento esteso per questo giocatore
        extended_list = {
            'playerId': player['playerId'],
            'playerName': player['playerName'],
            'firstName': player['firstName'],
            'lastName': player['lastName'],
            'rank': player['rank'],
            'army': player['army'],
            'detachment': player['detachment'],
            'score': player['score'],
            'list': categorized_list,
            'path': list_data.get('path', []),
            'tags': list_data.get('tags', [])
        }
        
        extended_lists.append(extended_list)
    
    # Crea documento finale
    result = {
        'eventInfo': data['eventInfo'],
        'extendedLists': extended_lists,
        'statistics': {
            'totalPlayers': len(data['players']),
            'listsParsed': parsed_count,
            'listsSkipped': skipped_count
        }
    }
    
    # Salva il file
    print(f"\nSalvataggio file: {output_filename}")
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ File salvato correttamente")
    
    # Mostra statistiche base
    print("\n" + "=" * 70)
    print(" " * 25 + "STATISTICHE")
    print("=" * 70)
    print(f"\nGiocatori totali: {len(data['players'])}")
    print(f"Liste parsate con successo: {parsed_count}")
    print(f"Liste saltate (non disponibili): {skipped_count}")
    
    if extended_lists:
        total_units = 0
        total_points = 0
        
        for ext_list in extended_lists:
            cat_list = ext_list['list']
            for category in cat_list.values():
                total_units += len(category)
                for unit in category:
                    total_points += unit.get('points', 0)
        
        avg_units = total_units / len(extended_lists)
        avg_points = total_points / len(extended_lists)
        
        print(f"\nMedia unità per lista: {avg_units:.1f}")
        print(f"Media punti per lista: {avg_points:.0f}")
    
    print("\n" + "=" * 70)
    print(" " * 25 + "COMPLETATO!")
    print("=" * 70)
    print(f"\n✓ File di output: {output_filename}")
    
    # Auto-validazione se richiesta
    if auto_validate:
        print("\n" + "=" * 70)
        print("AVVIO AUTO-VALIDAZIONE")
        print("=" * 70)
        
        valid_count, invalid_count = validate_and_separate(
            extended_lists_file=output_filename,
            complete_data_file=input_filename,
            output_valid_file='warhammer_valid_lists.json',
            output_invalid_file='warhammer_invalid_for_reparse.json'
        )
        
        print(f"\n✓ {valid_count} liste valide → warhammer_valid_lists.json")
        print(f"✓ {invalid_count} liste invalide → warhammer_invalid_for_reparse.json")


# FUNZIONE DI ATTIVAZIONE
if __name__ == "__main__":
    input_file = 'warhammer_complete_data.json'
    output_file = 'warhammer_extended_lists.json'
    
    # Parse con auto-validazione
    parse_json_file(input_file, output_file, auto_validate=True)