"""
Step 3 del pipeline: reparse liste invalide + validazione + separazione.
"""
import re
import json
from typing import Dict, Tuple
from validator import validate_parsed_list, validate_and_separate


# SECONDO STEP DI PARSING PER LE LISTE ANCORA INCORRETTE

def parse_simple_list_format(html_text: str) -> Dict:
    """Parser alternativo 1"""
    if not html_text or not isinstance(html_text, str):
        return {'characters': [], 'battleline': [], 'dedicated_transports': [], 'other_datasheets': []}
    
    clean_text = re.sub(r'<br\s*/?>', '\n', html_text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
    
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
        line_upper = line.upper()
        
        if line_upper in ['CHARACTER', 'CHARACTERS']:
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
        elif line_upper in ['DEDICATED TRANSPORTS', 'DEDICATED TRANSPORT']:
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
        
        unit_match = re.match(r'^(\d+)x?\s+(.+?)\s*\((\d+)\s*(?:pts|points?)\)\s*$', line, re.IGNORECASE)
        if unit_match and current_section:
            if current_unit:
                result[current_section].append(current_unit)
            
            unit_name = unit_match.group(2).strip()
            points = int(unit_match.group(3))
            
            current_unit = {
                'name': unit_name,
                'points': points,
                'enhancements': [],
                'is_warlord': False
            }
            i += 1
            continue
        
        if current_unit and (stripped := line.strip()).startswith(('•', '◦')):
            content = stripped[1:].strip()
            if 'warlord' in content.lower():
                current_unit['is_warlord'] = True
            elif 'enhancement:' in content.lower():
                enh = content.split(':', 1)[1].strip() if ':' in content else content
                current_unit['enhancements'].append(enh)
        
        i += 1
    
    if current_unit and current_section:
        result[current_section].append(current_unit)
    
    return result


def parse_char_prefix_format(html_text: str) -> Dict:
    """Parser alternativo 2"""
    if not html_text or not isinstance(html_text, str):
        return {'characters': [], 'battleline': [], 'dedicated_transports': [], 'other_datasheets': []}
    
    clean_text = re.sub(r'<br\s*/?>', '\n', html_text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
    
    result = {
        'characters': [],
        'battleline': [],
        'dedicated_transports': [],
        'other_datasheets': []
    }
    
    current_section = None
    current_unit = None
    
    for line in lines:
        char_match = re.match(r'^Char\d+:\s*(.+)', line, re.IGNORECASE)
        if char_match:
            if current_unit and current_section:
                result[current_section].append(current_unit)
            
            rest = char_match.group(1).strip()
            points_match = re.search(r'\((\d+)\s*(?:pts|points?)\)', rest)
            if points_match:
                unit_name = rest[:points_match.start()].strip()
                unit_name = re.sub(r'^\d+x?\s+', '', unit_name)
                points = int(points_match.group(1))
                
                current_unit = {
                    'name': unit_name,
                    'points': points,
                    'enhancements': [],
                    'is_warlord': False
                }
                current_section = 'characters'
            continue
        
        unit_match = re.match(r'^(\d+)x?\s+(.+?)\s*\((\d+)\s*(?:pts|points?)\)', line, re.IGNORECASE)
        if unit_match:
            if current_unit and current_section:
                result[current_section].append(current_unit)
            
            unit_name = unit_match.group(2).strip()
            points = int(unit_match.group(3))
            
            current_unit = {
                'name': unit_name,
                'points': points,
                'enhancements': [],
                'is_warlord': False
            }
            
            if not current_section:
                current_section = 'other_datasheets'
            continue
        
        if current_unit:
            if 'warlord' in line.lower():
                current_unit['is_warlord'] = True
            if 'enhancement:' in line.lower():
                enh = line.split(':', 1)[1].strip() if ':' in line else line
                current_unit['enhancements'].append(enh)
    
    if current_unit and current_section:
        result[current_section].append(current_unit)
    
    return result


def parse_indented_format(html_text: str) -> Dict:
    """Parser alternativo 3"""
    if not html_text or not isinstance(html_text, str):
        return {'characters': [], 'battleline': [], 'dedicated_transports': [], 'other_datasheets': []}
    
    clean_text = re.sub(r'<br\s*/?>', '\n', html_text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    lines = [l for l in clean_text.split('\n') if l.strip()]
    
    result = {
        'characters': [],
        'battleline': [],
        'dedicated_transports': [],
        'other_datasheets': []
    }
    
    current_unit = None
    current_section = 'other_datasheets'
    
    for line in lines:
        stripped = line.strip()
        
        name_match = re.match(r'^(.+?)\s*-\s*(.+?)\s*\((\d+)\s*(?:pts|points?)?\)', stripped)
        if name_match:
            if current_unit:
                result[current_section].append(current_unit)
            
            name = name_match.group(1).strip()
            unit_type = name_match.group(2).strip()
            points = int(name_match.group(3))
            
            current_unit = {
                'name': f"{name} - {unit_type}",
                'points': points,
                'enhancements': [],
                'is_warlord': False
            }
            continue
        
        if current_unit and ('enhancement:' in stripped.lower() or 'e:' in stripped.lower()):
            current_unit['enhancements'].append(stripped)
    
    if current_unit:
        result[current_section].append(current_unit)
    
    return result


def parse_dune_format(html_text: str) -> Dict:
    """Parser alternativo 4"""
    if not html_text or not isinstance(html_text, str):
        return {'characters': [], 'battleline': [], 'dedicated_transports': [], 'other_datasheets': []}
    
    clean_text = re.sub(r'<br\s*/?>', '\n', html_text)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    lines = [l.strip() for l in clean_text.split('\n') if l.strip()]
    
    result = {
        'characters': [],
        'battleline': [],
        'dedicated_transports': [],
        'other_datasheets': []
    }
    
    current_section = None
    current_unit = None
    
    for line in lines:
        line_upper = line.upper()
        
        if line_upper == 'CHARACTERS':
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'characters'
            current_unit = None
            continue
        elif line_upper == 'BATTLELINE':
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'battleline'
            current_unit = None
            continue
        elif line_upper == 'DEDICATED TRANSPORTS':
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'dedicated_transports'
            current_unit = None
            continue
        elif line_upper.startswith('OTHER'):
            if current_unit and current_section:
                result[current_section].append(current_unit)
            current_section = 'other_datasheets'
            current_unit = None
            continue
        
        unit_match = re.match(r'^(.+?)\s*\((\d+)\s*(?:Points?|pts)\)\s*-\s*"(.+?)"', line, re.IGNORECASE)
        if unit_match and current_section:
            if current_unit:
                result[current_section].append(current_unit)
            
            name = unit_match.group(1).strip()
            points = int(unit_match.group(2))
            
            current_unit = {
                'name': name,
                'points': points,
                'enhancements': [],
                'is_warlord': False
            }
            continue
        
        if current_unit and line.startswith('•'):
            content = line[1:].strip()
            if 'warlord' in content.lower():
                current_unit['is_warlord'] = True
    
    if current_unit and current_section:
        result[current_section].append(current_unit)
    
    return result


def parse_with_fallback(html_text: str) -> Tuple[Dict, bool, str]:
    """
    Prova tutti i parser alternativi fino a trovare una lista valida.
    Usa il validatore centralizzato.
    
    Returns:
        (parsed_list, is_valid, parser_used)
    """
    parsers = [
        ("simple_format", parse_simple_list_format),
        ("char_prefix", parse_char_prefix_format),
        ("indented", parse_indented_format),
        ("dune_format", parse_dune_format)
    ]
    
    for parser_name, parser_func in parsers:
        parsed = parser_func(html_text)
        is_valid, errors, _ = validate_parsed_list(parsed)
        
        if is_valid:
            return parsed, True, parser_name
    
    # Se nessun parser funziona, restituisci il risultato del primo
    parsed = parse_simple_list_format(html_text)
    return parsed, False, "simple_format_failed"


def reparse_invalid_lists(
    input_file: str = 'warhammer_invalid_for_reparse.json',
    output_file: str = 'warhammer_reparsed_lists.json',
    auto_validate: bool = True
):
    """
    Riprocessa le liste invalide con parser alternativi.
    Opzionalmente valida e separa automaticamente.
    """
    print("=" * 70)
    print(" " * 18 + "REPARSE INVALID LISTS")
    print("=" * 70)
    
    # Carica il file con le liste invalide
    print(f"\nLettura file: {input_file}")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERRORE: File '{input_file}' non trovato!")
        return
    except json.JSONDecodeError:
        print(f"ERRORE: File non è un JSON valido!")
        return
    
    invalid_lists = data['invalid_lists']
    print(f"✓ File caricato: {len(invalid_lists)} liste da riprocessare")
    
    # Riprocessa ogni lista
    print(f"\n{'=' * 70}")
    print(" " * 20 + "REPROCESSAMENTO")
    print(f"{'=' * 70}\n")
    
    extended_lists = []
    parser_stats = {}
    
    for i, invalid_list in enumerate(invalid_lists, 1):
        player_name = invalid_list['playerName']
        player_id = invalid_list['playerId']
        html_list = invalid_list.get('html_list', '')
        
        print(f"[{i}/{len(invalid_lists)}] Reparsing {player_name}...", end=" ")
        
        if not html_list:
            print("✗ Nessun HTML disponibile")
            continue
        
        # Prova il parsing con fallback
        parsed, is_valid, parser_used = parse_with_fallback(html_list)
        
        # Statistiche parser
        parser_stats[parser_used] = parser_stats.get(parser_used, 0) + 1
        
        # Crea l'entry nel formato standard
        entry = {
            'playerId': player_id,
            'playerName': player_name,
            'firstName': invalid_list.get('firstName', ''),
            'lastName': invalid_list.get('lastName', ''),
            'rank': invalid_list.get('rank', 0),
            'army': invalid_list.get('army', 'Unknown'),
            'detachment': invalid_list.get('detachment', 'Unknown'),
            'score': invalid_list.get('score', 0),
            'list': parsed,
            'path': invalid_list.get('listData', {}).get('path', []),
            'tags': invalid_list.get('listData', {}).get('tags', [])
        }
        
        extended_lists.append(entry)
        
        if is_valid:
            total_units = sum(len(cat) for cat in parsed.values())
            total_points = sum(u.get('points', 0) for cat in parsed.values() for u in cat)
            print(f"✓ {parser_used} ({total_units} unità, {total_points} pts)")
        else:
            _, errors, _ = validate_parsed_list(parsed)
            print(f"✗ {parser_used} - ANCORA INVALIDA: {', '.join(errors[:2])}")
    
    # Salva risultati
    output_data = {
        'eventInfo': data.get('eventInfo', {}),
        'extendedLists': extended_lists,
        'statistics': {
            'totalPlayers': len(invalid_lists),
            'listsParsed': len(extended_lists),
            'listsSkipped': len(invalid_lists) - len(extended_lists),
            'parserUsage': parser_stats
        }
    }
    
    print(f"\nSalvataggio risultati: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print("✓ File salvato")
    
    # Statistiche
    print(f"\n{'=' * 70}")
    print(" " * 22 + "STATISTICHE")
    print(f"{'=' * 70}")
    print(f"\nListe riprocessate: {len(extended_lists)}")
    print(f"\nUtilizzo parser:")
    for parser, count in sorted(parser_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {parser}: {count}")
    
    print(f"\n{'=' * 70}")
    print(" " * 22 + "COMPLETATO!")
    print(f"{'=' * 70}")
    print(f"\n✓ File output: {output_file}")
    
    # Auto-validazione se richiesta
    if auto_validate:
        print("\n" + "=" * 70)
        print("AVVIO AUTO-VALIDAZIONE")
        print("=" * 70)
        
        # Nota: non abbiamo il file completo originale, quindi passiamo None
        # Il validatore gestirà l'assenza del file completo
        valid_count, invalid_count = validate_and_separate(
            extended_lists_file=output_file,
            complete_data_file=input_file,  # Usa il file invalide come fallback
            output_valid_file='warhammer_reparsed_valid.json',
            output_invalid_file='warhammer_still_invalid.json'
        )
        
        print(f"\n✓ {valid_count} liste valide → warhammer_reparsed_valid.json")
        print(f"✓ {invalid_count} liste ancora invalide → warhammer_still_invalid.json")

# FUNZIONE DI ATTIVAZIONE
if __name__ == "__main__":
    input_file = 'warhammer_invalid_for_reparse.json'
    output_file = 'warhammer_reparsed_lists.json'
    
    # Reparse con auto-validazione
    reparse_invalid_lists(input_file, output_file, auto_validate=True)