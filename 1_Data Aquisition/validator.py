"""
Modulo per la validazione delle liste.
Utilizzato in tutti gli step del pipeline per mantenere coerenza.
"""
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

# === CONFIGURAZIONE REGOLE DI VALIDAZIONE ===
@dataclass
class ValidationRules:
    """Regole di validazione configurabili"""
    min_points: int = 1940
    max_points: int = 2000
    required_warlords: int = 1
    max_enhancements: int = 3
    min_units: int = 4


# === VALIDAZIONE CORE ===
def validate_parsed_list(
    parsed_list: Dict,
    rules: ValidationRules = ValidationRules()
) -> Tuple[bool, List[str], Dict]:
    """
    Valida una lista parsata secondo le regole standard.
    
    Args:
        parsed_list: Dizionario con categorie (characters, battleline, etc.)
        rules: Regole di validazione (opzionale)
        
    Returns:
        Tuple (is_valid, errors, stats)
        - is_valid: True se la lista è valida
        - errors: Lista di errori descrittivi
        - stats: Statistiche della lista (punti, unità, warlords, etc.)
    """
    errors = []
    stats = {
        'total_points': 0,
        'total_units': 0,
        'total_warlords': 0,
        'total_enhancements': 0,
        'units_by_category': {}
    }
    
    # Conta unità, punti, warlord ed enhancements
    for category, units in parsed_list.items():
        stats['units_by_category'][category] = len(units)
        stats['total_units'] += len(units)
        
        for unit in units:
            stats['total_points'] += unit.get('points', 0)
            if unit.get('is_warlord', False):
                stats['total_warlords'] += 1
            stats['total_enhancements'] += len(unit.get('enhancements', []))
    
    # Validazione punti
    if stats['total_points'] < rules.min_points:
        errors.append(f"Punti insufficienti: {stats['total_points']} (minimo {rules.min_points})")
    elif stats['total_points'] > rules.max_points:
        errors.append(f"Troppi punti: {stats['total_points']} (massimo {rules.max_points})")
    
    # Validazione warlord
    if stats['total_warlords'] == 0:
        errors.append("Nessun warlord trovato (richiesto 1)")
    elif stats['total_warlords'] > rules.required_warlords:
        errors.append(f"Troppi warlord: {stats['total_warlords']} (massimo {rules.required_warlords})")
    
    # Validazione enhancements
    if stats['total_enhancements'] > rules.max_enhancements:
        errors.append(f"Troppi enhancements: {stats['total_enhancements']} (massimo {rules.max_enhancements})")
    
    # Validazione unità
    if stats['total_units'] < rules.min_units:
        errors.append(f"Unità insufficienti: {stats['total_units']} (minimo {rules.min_units})")
    
    return len(errors) == 0, errors, stats


# === VALIDAZIONE E SEPARAZIONE ===
def validate_and_separate(
    extended_lists_file: str,
    complete_data_file: str,
    output_valid_file: str = 'warhammer_valid_lists.json',
    output_invalid_file: str = 'warhammer_invalid_lists.json',
    rules: ValidationRules = ValidationRules()
) -> Tuple[int, int]:
    """
    Valida le liste parsate e le separa in valide/invalide.
    Le liste invalide includono i dati completi per il reprocessing.
    
    Args:
        extended_lists_file: File con liste parsate (extendedLists format)
        complete_data_file: File originale con tutti i dati
        output_valid_file: File output per liste valide
        output_invalid_file: File output per liste invalide
        rules: Regole di validazione
        
    Returns:
        Tuple (valid_count, invalid_count)
    """
    print("=" * 70)
    print(" " * 20 + "VALIDAZIONE LISTE")
    print("=" * 70)
    
    # Carica le liste parsate
    print(f"\n📖 Lettura liste parsate: {extended_lists_file}")
    try:
        with open(extended_lists_file, 'r', encoding='utf-8') as f:
            extended_data = json.load(f)
    except FileNotFoundError:
        print(f"ERRORE: File '{extended_lists_file}' non trovato!")
        return 0, 0
    except json.JSONDecodeError:
        print(f"ERRORE: File non è un JSON valido!")
        return 0, 0
    
    # Carica i dati completi originali (per le invalide)
    print(f"📖 Lettura dati completi: {complete_data_file}")
    try:
        with open(complete_data_file, 'r', encoding='utf-8') as f:
            complete_data = json.load(f)
    except FileNotFoundError:
        print(f"WARNING: File '{complete_data_file}' non trovato. Le liste invalide non avranno dati completi.")
        complete_data = None
    
    print(f"✓ Files caricati")
    print(f"  Liste da validare: {len(extended_data['extendedLists'])}")
    
    # Crea indice per playerId nel file completo
    players_by_id = {}
    if complete_data:
        players_by_id = {p['playerId']: p for p in complete_data.get('players', [])}
    
    # Valida ogni lista
    print(f"\n{'=' * 70}")
    print(" " * 22 + "VALIDAZIONE")
    print(f"{'=' * 70}\n")
    
    valid_lists = []
    invalid_lists = []
    error_types = {}
    
    for i, ext_list in enumerate(extended_data['extendedLists'], 1):
        player_name = ext_list['playerName']
        player_id = ext_list['playerId']
        parsed_list = ext_list['list']
        
        print(f"[{i}/{len(extended_data['extendedLists'])}] {player_name}...", end=" ")
        
        is_valid, errors, stats = validate_parsed_list(parsed_list, rules)
        
        if is_valid:
            print("✓ VALIDA")
            valid_lists.append(ext_list)
        else:
            print(f"✗ INVALIDA ({len(errors)} errori)")
            for error in errors:
                print(f"      → {error}")
                # Traccia tipi di errore
                error_key = error.split(':')[0]
                error_types[error_key] = error_types.get(error_key, 0) + 1
            
            # Prepara entry per liste invalide
            invalid_entry = {
                'playerId': player_id,
                'playerName': player_name,
                'firstName': ext_list.get('firstName', ''),
                'lastName': ext_list.get('lastName', ''),
                'rank': ext_list.get('rank', 0),
                'army': ext_list.get('army', 'Unknown'),
                'detachment': ext_list.get('detachment', 'Unknown'),
                'score': ext_list.get('score', 0),
                'validation_errors': errors,
                'current_stats': stats,
                'parsed_list': parsed_list  # Lista già parsata (potrebbe essere errata)
            }
            
            # Aggiungi dati completi se disponibili
            if players_by_id:
                player_complete = players_by_id.get(player_id)
                if player_complete and player_complete.get('listData'):
                    invalid_entry['listData'] = player_complete['listData']
                    invalid_entry['html_list'] = player_complete['listData'].get('list', '')
            
            invalid_lists.append(invalid_entry)
    
    # Salva liste valide
    valid_output = {
        'eventInfo': extended_data.get('eventInfo', {}),
        'extendedLists': valid_lists,
        'statistics': {
            'totalPlayers': len(extended_data['extendedLists']),
            'validLists': len(valid_lists),
            'invalidLists': len(invalid_lists)
        }
    }
    
    print(f"\nSalvataggio liste valide: {output_valid_file}")
    with open(output_valid_file, 'w', encoding='utf-8') as f:
        json.dump(valid_output, f, ensure_ascii=False, indent=2)
    print("✓ File salvato")
    
    # Salva liste invalide
    if invalid_lists:
        invalid_output = {
            'eventInfo': extended_data.get('eventInfo', {}),
            'summary': {
                'total_lists': len(extended_data['extendedLists']),
                'valid_lists': len(valid_lists),
                'invalid_lists': len(invalid_lists),
                'validation_rate': f"{len(valid_lists) / len(extended_data['extendedLists']) * 100:.1f}%"
            },
            'validation_criteria': {
                'points_range': f'{rules.min_points}-{rules.max_points}',
                'warlords_required': rules.required_warlords,
                'max_enhancements': rules.max_enhancements,
                'min_units': rules.min_units
            },
            'invalid_lists': invalid_lists
        }
        
        print(f"Salvataggio liste invalide: {output_invalid_file}")
        with open(output_invalid_file, 'w', encoding='utf-8') as f:
            json.dump(invalid_output, f, ensure_ascii=False, indent=2)
        print("✓ File salvato")
    
    # Stampa statistiche
    _print_validation_stats(
        len(extended_data['extendedLists']),
        len(valid_lists),
        len(invalid_lists),
        error_types,
        invalid_lists
    )
    
    return len(valid_lists), len(invalid_lists)


def _print_validation_stats(
    total: int,
    valid: int,
    invalid: int,
    error_types: Dict[str, int],
    invalid_lists: List[Dict]
):
    """Stampa statistiche di validazione"""
    print(f"\n{'=' * 70}")
    print(" " * 22 + "STATISTICHE")
    print(f"{'=' * 70}")
    print(f"\nListe totali: {total}")
    print(f"Liste valide: {valid} ({valid / total * 100:.1f}%)")
    print(f"Liste invalide: {invalid} ({invalid / total * 100:.1f}%)")
    
    # Analisi errori
    if invalid_lists:
        print(f"\n{'=' * 70}")
        print(" " * 20 + "ANALISI ERRORI")
        print(f"{'=' * 70}")
        
        print("\nTipologie di errori:")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {error_type}: {count} liste")
        
        print(f"\n{'=' * 70}")
        print(" " * 18 + "TOP 5 LISTE INVALIDE")
        print(f"{'=' * 70}")
        
        for inv in invalid_lists[:5]:
            print(f"\n{inv['rank']}. {inv['playerName']} - {inv['army']}")
            print(f"   Errori: {len(inv['validation_errors'])}")
            for err in inv['validation_errors']:
                print(f"     → {err}")
    
    print(f"\n{'=' * 70}")
    print(" " * 22 + "COMPLETATO!")
    print(f"{'=' * 70}\n")
