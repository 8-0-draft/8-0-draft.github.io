import json
import os

INPUT_DB = "final_game_database_with_managers.json"

def main():
    if not os.path.exists(INPUT_DB):
        print(f"Error: {INPUT_DB} not found!")
        return

    with open(INPUT_DB, 'r', encoding='utf-8') as f:
        db = json.load(f)

    # Gather all unique team-year pairs for players
    player_teams = set()
    # Track manager information for each team-year pair
    managers_map = {}

    for entry in db:
        team = entry.get("team_name")
        year = entry.get("year")
        pos = entry.get("primary_position")
        
        if not team or year is None:
            continue
            
        if pos == "MGR":
            managers_map[(team, year)] = {
                "manager_name": entry.get("name"),
                "bonus_malus": entry.get("overall_rating")
            }
        else:
            player_teams.add((team, year))

    # Identify teams without managers
    no_managers = []
    # Identify teams with managers
    with_managers_pre = []
    with_managers_post = []

    # Sort player_teams to have stable order
    for team, year in sorted(player_teams):
        mgr_info = managers_map.get((team, year))
        if not mgr_info:
            no_managers.append({
                "team_name": team,
                "year": year
            })
        else:
            item = {
                "team_name": team,
                "year": year,
                "manager_name": mgr_info["manager_name"],
                "bonus_malus": mgr_info["bonus_malus"]
            }
            if year >= 2023:
                with_managers_post.append(item)
            else:
                with_managers_pre.append(item)

    # Write files
    with open("teams_without_managers.json", "w", encoding="utf-8") as f:
        json.dump(no_managers, f, ensure_ascii=False, indent=2)

    with open("teams_managers_pre_2023.json", "w", encoding="utf-8") as f:
        json.dump(with_managers_pre, f, ensure_ascii=False, indent=2)

    with open("teams_managers_post_2023.json", "w", encoding="utf-8") as f:
        json.dump(with_managers_post, f, ensure_ascii=False, indent=2)

    # Print summary statistics
    print(f"TOTAL_TEAMS_WITHOUT_MANAGERS: {len(no_managers)}")
    print(f"TOTAL_TEAMS_WITH_MANAGERS_PRE_2023: {len(with_managers_pre)}")
    print(f"TOTAL_TEAMS_WITH_MANAGERS_POST_2023: {len(with_managers_post)}")
    
    # Print sample of no managers
    print("\nSAMPLE_WITHOUT_MANAGERS:")
    for item in no_managers[:10]:
        print(f"  - {item['team_name']} ({item['year']})")
        
    # Print sample of pre-2023
    print("\nSAMPLE_PRE_2023:")
    for item in with_managers_pre[:3]:
        print(f"  - {item['team_name']} ({item['year']}): {item['manager_name']} (Rating: {item['bonus_malus']})")

    # Print sample of post-2023
    print("\nSAMPLE_POST_2023:")
    for item in with_managers_post[:3]:
        print(f"  - {item['team_name']} ({item['year']}): {item['manager_name']} (Rating: {item['bonus_malus']})")

if __name__ == "__main__":
    main()
