"""
Step 4 del pipeline: merge + validazione + separazione.
"""
import json
from validator import validate_and_separate


def merge_warhammer_lists(
    base_file: str = 'warhammer_extended_lists.json',
    reparsed_file: str = 'warhammer_reparsed_lists.json',
    manual_file: str = 'warhammer_manual_lists.json',
    output_file: str = 'warhammer_merged_lists.json',
    auto_validate: bool = True
):
    """
    Unisce i file JSON di Warhammer lists.
    
    Args:
        base_file: File base con tutte le liste parsate
        reparsed_file: File con liste riprocessate
        manual_file: File con liste corrette manualmente
        output_file: File output con liste unite
        auto_validate: Se True, valida automaticamente e separa le liste
    """
    print("=" * 70)
    print(" " * 20 + "MERGE WARHAMMER LISTS")
    print("=" * 70)
    
    # Carica i file JSON
    print(f"\n📖 Caricamento files...")
    
    try:
        with open(base_file, 'r', encoding='utf-8') as f:
            extended_data = json.load(f)
        print(f"  ✓ {base_file}: {len(extended_data['extendedLists'])} giocatori")
    except FileNotFoundError:
        print(f"ERRORE: File '{base_file}' non trovato!")
        return
    
    try:
        with open(reparsed_file, 'r', encoding='utf-8') as f:
            reparsed_data = json.load(f)
        print(f"  ✓ {reparsed_file}: {len(reparsed_data.get('extendedLists', []))} giocatori")
    except FileNotFoundError:
        print(f"WARNING: File '{reparsed_file}' non trovato, skip")
        reparsed_data = {'extendedLists': []}
    
    try:
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_data = json.load(f)
        print(f"  ✓ {manual_file}: {len(manual_data.get('extendedLists', []))} giocatori")
    except FileNotFoundError:
        print(f"WARNING: File '{manual_file}' non trovato, skip")
        manual_data = {'extendedLists': []}
    
    # Crea una copia della lista base
    merged_lists = extended_data['extendedLists'].copy()
    
    # Funzione per creare la chiave unica (rank, playerName)
    def get_key(player):
        return (player['rank'], player['playerName'])
    
    # Crea un dizionario con chiave (rank, playerName) per accesso rapido
    merged_dict = {get_key(player): i for i, player in enumerate(merged_lists)}
    
    print(f"\n{'=' * 70}")
    print(" " * 25 + "MERGING")
    print(f"{'=' * 70}\n")
    
    # Prima sostituzione: reparsed_lists
    replaced_reparsed = 0
    if reparsed_data.get('extendedLists'):
        print(f"Elaborazione reparsed_lists ({len(reparsed_data['extendedLists'])} giocatori)...")
        for player in reparsed_data['extendedLists']:
            key = get_key(player)
            if key in merged_dict:
                idx = merged_dict[key]
                merged_lists[idx] = player
                replaced_reparsed += 1
                print(f"  ✓ Sostituito: Rank {player['rank']} - {player['playerName']}")
        print(f"Sostituiti {replaced_reparsed} giocatori da reparsed_lists\n")
    
    # Seconda sostituzione: manual_lists
    replaced_manual = 0
    if manual_data.get('extendedLists'):
        print(f"Elaborazione manual_lists ({len(manual_data['extendedLists'])} giocatori)...")
        for player in manual_data['extendedLists']:
            key = get_key(player)
            if key in merged_dict:
                idx = merged_dict[key]
                merged_lists[idx] = player
                replaced_manual += 1
                print(f"  ✓ Sostituito: Rank {player['rank']} - {player['playerName']}")
        print(f"Sostituiti {replaced_manual} giocatori da manual_lists\n")
    
    # Crea il risultato finale
    final_data = {
        "eventInfo": extended_data['eventInfo'],
        "extendedLists": merged_lists,
        "statistics": {
            "totalPlayers": len(merged_lists),
            "replacedFromReparsed": replaced_reparsed,
            "replacedFromManual": replaced_manual,
            "totalReplacements": replaced_reparsed + replaced_manual
        }
    }
    
    # Salva il file unito
    print(f"Salvataggio file unito: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ File salvato")
    
    print(f"\n{'=' * 70}")
    print(" " * 25 + "STATISTICHE")
    print(f"{'=' * 70}")
    print(f"\nGiocatori totali: {len(merged_lists)}")
    print(f"Sostituzioni da reparsed: {replaced_reparsed}")
    print(f"Sostituzioni da manual: {replaced_manual}")
    print(f"Totale sostituzioni: {replaced_reparsed + replaced_manual}")
    
    print(f"\n{'=' * 70}")
    print(" " * 25 + "COMPLETATO!")
    print(f"{'=' * 70}")
    print(f"\n✓ File output: {output_file}")
    
    # Auto-validazione se richiesta
    if auto_validate:
        print("\n" + "=" * 70)
        print("AVVIO AUTO-VALIDAZIONE")
        print("=" * 70)
        
        # Per il merge, usiamo il base_file come complete_data
        # (anche se non ha i dati raw, è il migliore che abbiamo)
        valid_count, invalid_count = validate_and_separate(
            extended_lists_file=output_file,
            complete_data_file=base_file,
            output_valid_file='warhammer_final_valid.json',
            output_invalid_file='warhammer_final_invalid.json'
        )
        
        print(f"\n✓ {valid_count} liste valide → warhammer_final_valid.json")
        if invalid_count > 0:
            print(f"{invalid_count} liste ancora invalide → warhammer_final_invalid.json")
            print(f"   Queste richiedono correzione manuale")
        else:
            print(f"TUTTE LE LISTE SONO VALIDE!")


# FUNZIONE DI ATTIVAZIONE
if __name__ == "__main__":
    # Parametri standard
    merge_warhammer_lists(
        base_file='warhammer_extended_lists.json',
        reparsed_file='warhammer_reparsed_lists.json',
        manual_file='warhammer_manual_lists.json',
        output_file='warhammer_merged_lists.json',
        auto_validate=True
    )