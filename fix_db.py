import json
import os
import shutil

# ==========================================
# CONFIGURAZIONE PERCORSI
# ==========================================
FILE_PATH = r"C:\Users\lucag\8a0\final_game_database.json"
BACKUP_PATH = r"C:\Users\lucag\8a0\final_game_database_with_managerss.json.bak"

# ==========================================
# DIZIONARIO COMPLETO E AGGIORNATO DI NORMALIZZAZIONE
# ==========================================
TEAM_NAME_MAP = {
    # Milan
    "Associazione Calcio Milan": "Milan",
    "AC Milan": "Milan",
    
    # Inter
    "Football Club Internazionale Milano S.p.A.": "Inter",
    "Inter Milan": "Inter",
    "Internazionale": "Inter",
    
    # Juventus
    "Juventus Football Club": "Juventus",
    "Juventus FC": "Juventus",
    
    # Napoli
    "Società Sportiva Calcio Napoli": "Napoli",
    "SSC Napoli": "Napoli",
    
    # Lazio
    "Società Sportiva Lazio S.p.A.": "Lazio",
    "SS Lazio": "Lazio",
    
    # Roma
    "AS Roma": "Roma",
    "Associazione Sportiva Roma": "Roma",
    
    # Atalanta
    "Atalanta Bergamasca Calcio S.p.a.": "Atalanta",
    
    # Bologna
    "Bologna Football Club 1909": "Bologna",
    
    # Real Madrid
    "Real Madrid Club de Fútbol": "Real Madrid",
    "Real Madrid CF": "Real Madrid",
    
    # Barcelona
    "Futbol Club Barcelona": "Barcelona",
    "FC Barcelona": "Barcelona",
    
    # Atletico Madrid
    "Club Atlético de Madrid S.A.D.": "Atletico Madrid",
    "Atlético Madrid": "Atletico Madrid",
    
    # Sevilla
    "Sevilla Fútbol Club S.A.D.": "Sevilla",
    "Sevilla FC": "Sevilla",
    
    # Real Sociedad
    "Real Sociedad de Fútbol S.A.D.": "Real Sociedad",
    
    # Girona
    "Girona Fútbol Club S. A. D.": "Girona",
    
    # Villarreal
    "Villarreal Club de Fútbol S.A.D.": "Villarreal",
    
    # Bayern
    "FC Bayern München": "Bayern Munich",
    "Bayern München": "Bayern Munich",
    
    # Stuttgart
    "Verein für Bewegungsspiele Stuttgart 1893": "VfB Stuttgart",
    "VfB Stuttgart": "VfB Stuttgart",
    
    # Leipzig
    "RasenBallsport Leipzig": "RB Leipzig",
    "RB Leipzig": "RB Leipzig",
    
    # Arsenal
    "Arsenal Football Club": "Arsenal",
    
    # Chelsea
    "Chelsea Football Club": "Chelsea",
    
    # Liverpool
    "Liverpool Football Club": "Liverpool",
    
    # Newcastle
    "Newcastle United Football Club": "Newcastle United",
    
    # Tottenham
    "Tottenham Hotspur Football Club": "Tottenham",
    "Tottenham Hotspur": "Tottenham",
    
    # Monaco
    "Association sportive de Monaco Football Club": "AS Monaco",
    
    # PSG
    "Paris Saint-Germain Football Club": "Paris Saint-Germain",
    "PSG": "Paris Saint-Germain",
    
    # Lille
    "Lille Olympique Sporting Club": "Lille",
    "Lille OSC": "Lille",
    
    # Ajax
    "AFC Ajax Amsterdam": "Ajax",
    
    # Feyenoord
    "Feyenoord Rotterdam": "Feyenoord",
    
    # Benfica
    "Sport Lisboa e Benfica": "Benfica",
    
    # Sporting CP
    "Sporting Clube de Portugal": "Sporting CP",
    
    # Porto
    "Futebol Clube do Porto": "Porto",
    "FC Porto": "Porto",
    
    # Celtic
    "The Celtic Football Club": "Celtic",
    
    # Club Brugge
    "Club Brugge Koninklijke Voetbalvereniging": "Club Brugge",
    
    # Galatasaray
    "Galatasaray Spor Kulübü": "Galatasaray",
    
    # Stella Rossa
    "Fudbalski klub Crvena zvezda Beograd": "Red Star Belgrade",
    "Red Star Belgrade": "Red Star Belgrade",
    
    # Union Berlin
    "1. Fußballclub Union Berlin": "Union Berlin",
    
    # Young Boys
    "Berner Sport Club Young Boys": "Young Boys",
    
    # Eintracht
    "Eintracht Frankfurt Fußball AG": "Eintracht Frankfurt",
    
    # Copenhagen
    "Football Club København": "FC Copenhagen",
    
    # Bodo/Glimt
    "Fotballklubben Bodø/Glimt": "Bodo/Glimt",
    
    # Salzburg
    "Fußballclub Red Bull Salzburg": "RB Salzburg",
    "RB Salzburg": "RB Salzburg",
    
    # Dinamo Zagreb
    "GNK Dinamo Zagreb": "Dinamo Zagreb",
    
    # Olympiacos
    "Olympiakos Syndesmos Filathlon Peiraios": "Olympiacos",
    
    # Marseille
    "Olympique de Marseille": "Marseille",
    
    # Lens
    "Racing Club de Lens": "Lens",
    
    # Rangers
    "Rangers Football Club": "Rangers",
    
    # Antwerp
    "Royal Antwerp Football Club": "Royal Antwerp",
    
    # Union SG
    "Royale Union Saint-Gilloise": "Union SG",
    
    # Braga
    "Sporting Clube de Braga": "Braga",
    "SC Braga": "Braga",
    
    # Slavia
    "SK Slavia Praha, a.s.": "Slavia Praha",
    
    # Sturm Graz
    "Sportklub Puntigamer Sturm Graz": "Sturm Graz",
    
    # Brest
    "Stade brestois 29": "Brest",
    
    # Sparta Prague
    "AC Sparta Praha, a. s.": "Sparta Prague",
    "Sparta Prague": "Sparta Prague"
}

def fix_and_overwrite():
    if not os.path.exists(FILE_PATH):
        print(f"❌ Errore: Il file {FILE_PATH} non esiste.")
        return

    # 1. Creazione Backup di Sicurezza
    shutil.copy2(FILE_PATH, BACKUP_PATH)
    print(f"✓ Backup creato in: {BACKUP_PATH}")

    # 2. Caricamento Database
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)

    cleaned_db = []
    seen_managers = set()
    replacements_count = 0
    managers_fixed = 0

    for item in db:
        # Recupera il nome attuale della squadra eliminando spazi bianchi iniziali/finali
        current_team = item.get("team_name", "").strip()
        
        # Sostituzione se presente nel mega dizionario
        if current_team in TEAM_NAME_MAP:
            target_name = TEAM_NAME_MAP[current_team]
            if current_team != target_name:
                item["team_name"] = target_name
                replacements_count += 1
        
        team_normalized = item.get("team_name", "")
        year = item.get("year")

        # Se è un giocatore, lo salviamo e andiamo avanti
        if item.get("primary_position") != "MGR":
            cleaned_db.append(item)
            continue

        # --- GESTIONE LOGICA ALLENATORI ---
        manager_name = item.get("name", "")

        # Correzioni Storiche Post-2023
        if team_normalized == "Celtic" and year == 2023:
            item["name"] = "Ange Postecoglou"
            item["overall_rating"] = 3
            managers_fixed += 1
        elif team_normalized == "Omonia Nicosia" and year == 2026:
            item["name"] = "Valdas Dambrauskas"
            item["overall_rating"] = 0
            managers_fixed += 1
        elif team_normalized == "Sheriff Tiraspol" and year == 2026:
            continue  # Rimuove il record sballato
        
        # Ribilanciamento Valutazioni
        elif team_normalized == "Bayern Munich" and year == 2024 and manager_name == "Thomas Tuchel":
            item["overall_rating"] = -1
            managers_fixed += 1
        elif team_normalized == "Inter" and year == 2024 and manager_name == "Simone Inzaghi":
            item["overall_rating"] = 2
            managers_fixed += 1
        elif team_normalized == "Manchester City" and year == 2025 and manager_name == "Pep Guardiola":
            item["overall_rating"] = 2
            managers_fixed += 1
        elif team_normalized == "Borussia Dortmund" and year == 2024 and manager_name == "Edin Terzić":
            item["overall_rating"] = 2
            managers_fixed += 1
        elif team_normalized == "Paris Saint-Germain" and manager_name == "Luis Enrique" and year in [2024, 2025, 2026]:
            item["overall_rating"] = 1
            managers_fixed += 1

        # Deduping degli allenatori per evitare doppie pescate
        mgr_key = f"{team_normalized}_{year}"
        if mgr_key not in seen_managers:
            seen_managers.add(mgr_key)
            cleaned_db.append(item)

    # 3. Sovrascrittura file originale
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cleaned_db, f, indent=4, ensure_ascii=False)

    print("\n🚀 Operazione Correttiva Riuscita!")
    print(f"🔄 Nomi di squadre sostituiti/unificati nel DB: {replacements_count}")
    print(f"🛠️ Logiche e rating di allenatori post-2023 aggiornati: {managers_fixed}")
    print(f"📊 Numero totale di record puliti salvati nel file originale: {len(cleaned_db)}")

if __name__ == "__main__":
    fix_and_overwrite()