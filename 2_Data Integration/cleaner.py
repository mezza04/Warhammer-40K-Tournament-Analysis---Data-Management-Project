"""
Step 5 del pipeline: pulizia dei dati.
"""
import json
from typing import Dict, Tuple, Optional, List, Callable
from pathlib import Path

def create_correction_dict():
    """
    Crea un dizionario per correggere i nomi delle unità errati.
    """
    corrections = {
        "Arco-Flagellants": "Arco-flagellants",
        "Crucible's Reach": "",
        "Immolator Madeline": "Immolator",
        "Callidus Assassin Orator Superior Amalia": "Callidus Assassin",
        "Junith Eruita Purifier Charity": "Junith Eruita",
        "Palatine Refutation of Dross": "Palatine",
        "Castigator Prioress Sabine": "Castigator",
        "Morvenn Vahl Ringing Purity": "Morvenn Vahl",
        "Castigator Statuary Tender Honest": "Castigator",
        "Imagifier The Feral": "Imagifier",
        "Mortifier The Fool": "Mortifiers",
        "Mortifier The Forsaking": "Mortifiers",
        "Mortifier The Refulgent Bulwark": "Mortifiers",
        "Paragon Warsuits": "Paragon Warsuits",
        "Gaunt's Ghosts": "Gaunt's Ghosts",
        "Gauntâ€™s Ghosts": "Gaunt's Ghosts",
        "Gaunt’s Ghosts": "Gaunt's Ghosts",
        "Emperor's Champion": "Emperor's Champion",
        "Emperorâ€™s Champion": "Emperor's Champion",
        "Emperor’s Champion": "Emperor's Champion",
        "Be'lakor": "Be'lakor",
        "Beâ€™lakor": "Be'lakor",
        "Beâ€™lakor: Pyramid Head": "Be'lakor",
        "Be’lakor: Pyramid Head": "Be'lakor",
        "Be’lakor": "Be'lakor",
        "Fluxmaster: Pinhead": "Fluxmaster",
        "Screamers: Beetlejuices": "Screamers",
        "Seekers: Murder Cheerleaders": "Seekers",
        "Beasts of Nurgle â€˜Bincentâ€™": "Beasts of Nurgle",
        "Beasts of Nurgle 'Bincent'": "Beasts of Nurgle",
        "Beasts of Nurgle â€˜Hamieâ€™": "Beasts of Nurgle",
        "Beasts of Nurgle 'Hamie'": "Beasts of Nurgle",
        "Beasts of Nurgle â€˜Scamtavoâ€™": "Beasts of Nurgle",
        "Beasts of Nurgle 'Scamtavo'": "Beasts of Nurgle",
        "Beasts of Nurgle ‘Bincent’": "Beasts of Nurgle",
        "Beasts of Nurgle ‘Hamie’": "Beasts of Nurgle",
        "Beasts of Nurgle ‘Scamtavo’": "Beasts of Nurgle",
        "Knight Despoiler â€˜Bobâ€™": "Knight Despoiler",
        "Knight Despoiler 'Bob'": "Knight Despoiler",
        "Knight Despoiler â€˜Pew Pewâ€™": "Knight Despoiler",
        "Knight Despoiler 'Pew Pew'": "Knight Despoiler",
        "Knight Despoiler â€˜Rustyâ€™": "Knight Despoiler",
        "Knight Despoiler 'Rusty'": "Knight Despoiler",
        "Knight Despoiler ‘Pew Pew’": "Knight Despoiler",
        "Knight Despoiler ‘Rusty’": "Knight Despoiler",
        "Knight Despoiler ‘Bob’": "Knight Despoiler",
        "Nurglings â€˜Goatsâ€™": "Nurglings",
        "Nurglings 'Goats'": "Nurglings",
        "Nurglings â€˜MVPsâ€™": "Nurglings",
        "Nurglings 'MVPs'": "Nurglings",
        "Nurglings ‘Goats’": "Nurglings",
        "Nurglings ‘MVPs’": "Nurglings",
        "Plaguebearers ‘Fungal’": "Plaguebearers",
        "Plaguebearers â€˜Fungalâ€™": "Plaguebearers",
        "Plaguebearers 'Fungal'": "Plaguebearers",
        "Plaguebearers ‘Fungal’": "Plaguebearers",
        "War Dog Karnivore â€˜Bloodyâ€™": "War Dog Karnivore",
        "War Dog Karnivore 'Bloody'": "War Dog Karnivore",
        "War Dog Karnivore â€˜Carnageâ€™": "War Dog Karnivore",
        "War Dog Karnivore 'Carnage'": "War Dog Karnivore",
        "War Dog Karnivore â€˜Slaughterâ€™": "War Dog Karnivore",
        "War Dog Karnivore 'Slaughter'": "War Dog Karnivore",
        "War Dog Karnivore ‘Slaughter’": "War Dog Karnivore",
        "War Dog Karnivore ‘Carnage’": "War Dog Karnivore",
        "War Dog Karnivore ‘Bloody’": "War Dog Karnivore",
        "Orator Superior Amalia - - Junith Eruita": "Junith Eruita",
        "Statuary Tender Honest - - Imagifier": "Imagifier",
        "Canoness Ascendent Yaeno - Jump Pack Canoness": "Jump Pack Canoness",
        "Canoness Yda - Canoness -": "Canoness",
        "Prioress Sabine - Morvenn Vahl": "Morvenn Vahl",
        "Purifier Charity - Palatine": "Palatine",
        "Crucible's Reach - - Immolator": "Immolator",
        "Refutation of Dross - - Castigator": "Castigator",
        "Ringing Purity - - Castigator": "Castigator",
        "The Feral - - Mortifier": "Mortifier",
        "The Fool - - Mortifier": "Mortifier",
        "The Forsaking - - Mortifier": "Mortifier",
        "The Refulgent Bulwark - Paragon Warsuits": "Paragon Warsuits",
        "Madeline - Callidus Assassin": "Callidus Assassin",
        "Khârn the Betrayer": "Kharn the Betrayer",
        "Ûthar the Destined": "Ûthar the Destined",
        "Von Ryan’s Leapers": "Von Ryan's Leapers",
        "C’tan Shard of the Nightbringer": "C'tan Shard of the Nightbringer",
        "Beasts of Nurgle: Pennywise": "Beasts of Nurgle",
        "Nurglings: George A Romero": "Nurglings",
        "Bloodthirster: Ozzy Osbourne": "Bloodthirster",
        "Accursed Cultists: Texas Chainsaw masacre": "Accursed Cultists",
        "Chaos Lord in Terminator Armour: Jason Vorhees": "Chaos Lord in Terminator Armour",
        "Cultist Mob: chucky": "Cultist Mob",
        "Dark Commune: Leather Face": "Dark Commune",
        "Warp Talons: Freddy Krueguer": "Warp Talons",
        "Battle Sister Squad": "Battle Sisters Squad",
        "Celestian Sacresancts": "Celestian Sacresants",
        "Mortifier": "Mortifiers",
        "Zephyrim": "Zephyrim Squad",
        "Sword Brethren": "Sword Brethren Squad",
        "Lion El’Jonson": "Lion El'Jonson",
        "Foetid Bloat-drone with heavy blight launcher": "Foetid Bloat-Drone",
        "Myphitic Blight-haulers": "Myphitic Blight-hauler",
        "Agrondax, The Sleepless Harbinger [Technomancer]": "Technomancer",
        "Will of Markenezan [Canoptek Reanimator]": "Canoptek Reanimator",
        "Shades of Markenezan [Canoptek Wraiths]": "Canoptek Wraiths",
        "Sentinels of Agrondax [Cryptothralls]": "Cryptothralls",
        "Stellar Remnants [Doomsday Ark] 1": "Doomsday Ark",
        "Fury of the Stars [Doomsday Ark] 2": "Doomsday Ark",
        "The Harvester [Doomsday Ark] 3": "Doomsday Ark",
        "Tholaraskh’s Reach [Lokhust Heavy Destroyers]": "Lokhust Heavy Destroyers",
        "Gameskh, The Obsessed [Ophydian Destroyers]": "Ophydian Destroyers",
        "Baraka’s 1st Phalanx [Skorpekh Destroyers]": "Skorpekh Destroyers",
        "Baraka’s 2nd Phalanx [Skorpekh Destroyers]": "Skorpekh Destroyers",
        "Voice of the Triarch [Triarch Praetorians]": "Triarch Praetorians",
        "Vulkan He’stan": "Vulkan He'stan",
        "Hatshepsut, Phaerakh of the Markenezan Dynasty [Catacomb Command Barge]": "Catacomb Command Barge",
        "Jump Pack Canoness": "Canoness with Jump Pack",
        "Black Templars Repulsor Executioner": "Repulsor Executioner",
        "Black Templars Impulsor": "Impulsor",
        "Piranhas": "Piranha",
        "Tholaraskh, Night’s Whisper [Lokhust Lord]": "Lokhust Lord",
        "Kheminar, First Tendril of Tholaraskh [Hexmark Destroyer] (BLACK)": "Hexmark Destroyer",
        "Daemon Prince of Tzeentch (185 Points) « Ariane Aimé Abanius »": "Daemon Prince of Tzeentch",
        "Exalted Sorcerer (80 Points) « Ithak Mirco »": "Exalted Sorcerer",
        "Exalted Sorcerer (95 Points) « Balloo Eracne »": "Exalted Sorcerer",
        "Exalted Sorcerer (110 Points) « Anklagon ‘avalanche’ Bouga »": "Exalted Sorcerer",
        "Sorcerer (85 Points) « Mister Z ´Little poney’ Bearsoul »": "Sorcerer",
        "Tzaangor Shaman (60 Points) « Mani ´Grimdark Loukas »": "Tzaangor Shaman",
        "Cadian Castellan (55 Points) - “Duncan Idaho, The Swordmaster”": "Cadian Castellan",
        "Cadian Castellan (55 Points) - “Gurney Halleck, Warmaster”": "Cadian Castellan",
        "Cadian Command Squad (65 Points) - “Atreides Command Squad”": "Cadian Command Squad",
        "Catachan Command Squad (65 Points) - “Fremen Sietch War Council”": "Catachan Command Squad",
        "Ogryn Bodyguard (40 Points) - “Drim, Fremen Sietch Brute”": "Ogryn Bodyguard",
        "Ogryn Bodyguard (40 Points) - “Drot, Fremen Sietch Brute”": "Ogryn Bodyguard",
        "Ogryn Bodyguard (40 Points) - “Nott, Fremen Sietch Brute”": "Ogryn Bodyguard",
        "Rogal Dorn Commander (275 Points) - “Naib Stilgar Command Vehicle”": "Rogal Dorn Commander",
        "Rogal Dorn Commander (275 Points) - “Thufir Hawat Mobile Processor”": "Rogal Dorn Commander",
        "Cadian Shock Troops (120 Points) - “Atreides Troopers”": "Cadian Shock Troops",
        "Catachan Jungle Fighters (65 Points) - “Fremen Sietch Fighters”": "Catachan Jungle Fighters",
        "Chimera (85 Points) - “Atreides Armoured Spice Harvester”": "Chimera",
        "Kasrkin (110 Points) - “Fedaykin Fremen Death Commandos”": "Kasrkin",
        "Benefictus (70 points) Big Head Todd": "Benefictus",
        "Benefictus (70 points) Wee Head Tim": "Benefictus",
        "Jackal Alphus (55 points) Sandy": "Jackal Alphus",
        "Locus (45 points) Stabby Patty": "Locus",
        "Nexos (60 points) I'm not even supposed to be here today": "Nexos",
        "Patriarch (75 points) Gridjsydrb": "Patriarch",
        "Primus (90 points) Mi Primo, como stai": "Primus",
        "Reductus Saboteur (65 points) Boom Boom McGee": "Reductus Saboteur",
        "Reductus Saboteur (65 points) 9 fingers Alice": "Reductus Saboteur",
        "Sanctus (50 points) Scary Larry": "Sanctus",
        "Duke Sliscus, The Serpent (Archon)" : "Archon",
        "The Veilwalker (Shadowseer)" : "Shadowseer",
    }
    
    return corrections

def fix_unit_names(input_file, output_file):
    """
    Corregge i nomi delle unità nel file JSON.
    """
    
    # Carica il file JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    corrections = create_correction_dict()
    
    # Contatori
    total_corrections = 0
    units_corrected = set()
    
    # Itera su tutte le liste
    for player_list in data.get('extendedLists', []):
        list_data = player_list.get('list', {})
        
        # Categorie da correggere
        categories = ['characters', 'battleline', 'dedicated_transports', 'other_datasheets']
        
        for category in categories:
            units = list_data.get(category, [])
            
            for unit in units:
                original_name = unit.get('name', '')
                
                # Controlla se il nome necessita correzione
                if original_name in corrections:
                    corrected_name = corrections[original_name]
                    
                    # Se la correzione è una stringa vuota, rimuovi l'unità
                    if corrected_name == "":
                        units.remove(unit)
                        total_corrections += 1
                        units_corrected.add(f"{original_name} → [RIMOSSA]")
                    else:
                        unit['name'] = corrected_name
                        total_corrections += 1
                        units_corrected.add(f"{original_name} → {corrected_name}")
    
    # Salva il file corretto
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Correzioni completate!")
    print(f"  - Correzioni applicate: {total_corrections}")
    print(f"  - Unità uniche corrette: {len(units_corrected)}")
    print(f"  - File salvato: {output_file}")
    
    if units_corrected:
        print(f"\nCorrezioni applicate:")
        for correction in sorted(units_corrected):
            print(f"  - {correction}")
    
    return total_corrections

# FUNZIONE DI ATTIVAZIONE
if __name__ == "__main__":
    input_file = "warhammer_final_valid.json"
    output_file = "warhammer_final_cleaned.json"
    
    try:
        fix_unit_names(input_file, output_file)
    except FileNotFoundError as e:
        print(f"Errore: File non trovato - {e}")
    except json.JSONDecodeError as e:
        print(f"Errore: JSON non valido - {e}")
    except Exception as e:
        print(f"Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()