import json

INPUT_DB = "final_game_database_with_managers.json"

def scan_mojibake():
    with open(INPUT_DB, 'r', encoding='utf-8') as f:
        db = json.load(f)

    mojibake_chars = ['Ã¼', 'Ã¶', 'Ã¤', 'ÃŸ', 'Ã©', 'Ã¨', 'Ã¡', 'Ã­', 'Ã³', 'Ãº', 'Ã±', 'Ã§', 'Ã‰', 'Ãˆ', 'ÅŸ', 'ÅŸ', 'Ã ', 'Å\x9f']
    
    found_teams = set()
    found_players = set()
    
    for p in db:
        team = p.get("team_name", "")
        name = p.get("name", "")
        
        # Check team name
        for char in mojibake_chars:
            if char in team:
                found_teams.add(team)
                break
                
        # Check player name
        for char in mojibake_chars:
            if char in name:
                found_players.add((name, team, p.get("year")))
                break

    print(f"Found {len(found_teams)} teams with mojibake:")
    for team in sorted(list(found_teams)):
        print(f"  - {team}")

    print(f"\nFound {len(found_players)} players with mojibake (displaying first 10):")
    for item in sorted(list(found_players))[:10]:
        print(f"  - {item[0]} (Team: {item[1]}, Year: {item[2]})")

if __name__ == "__main__":
    scan_mojibake()
