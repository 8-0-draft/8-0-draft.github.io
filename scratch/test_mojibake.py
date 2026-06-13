import json
import os

INPUT_DB = "final_game_database_with_managers.json"

def test_decoding():
    with open(INPUT_DB, 'r', encoding='utf-8') as f:
        db = json.load(f)

    # Let's find unique team names containing bad characters
    bad_teams = set()
    for p in db:
        team = p.get("team_name", "")
        if any(c in team for c in ['Ã', 'Â', 'Å', 'Š', 'š', 'ž', 'Ž', 'Ÿ', 'œ', 'æ', '']):
            bad_teams.add(team)

    print("Found bad teams:")
    for team in sorted(list(bad_teams))[:15]:
        print(f"Original: {team}")
        
        # Test 1: UTF-8 to cp1252 / latin1
        repaired = None
        for enc in ['cp1252', 'latin1', 'cp1250', 'cp1254']:
            try:
                # We encode the string to bytes using the faulty decoder's assumed encoding
                # then decode using the correct UTF-8 encoding
                candidate = team.encode(enc).decode('utf-8')
                if candidate != team:
                    print(f"  -> Decoded with {enc}: {candidate}")
                    repaired = candidate
                    break
            except Exception:
                pass
                
        # If it failed, let's try double-encoding or special replacements
        if not repaired:
            # Let's see the hex bytes of the team name
            hex_bytes = [hex(ord(c)) for c in team]
            print(f"  Hex: {hex_bytes}")

if __name__ == "__main__":
    test_decoding()
