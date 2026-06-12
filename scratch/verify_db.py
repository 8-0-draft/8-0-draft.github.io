import json
import sys

db_path = "final_game_database.json"

try:
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    sys.exit(1)

print(f"Total players in database: {len(data)}")

ratings = [p.get("overall_rating") for p in data]
missing_rating = [p for p in data if "overall_rating" not in p]
null_rating = [p for p in data if p.get("overall_rating") is None]

print(f"Missing rating key: {len(missing_rating)}")
print(f"Null rating: {len(null_rating)}")
print(f"Min rating: {min(ratings)}, Max rating: {max(ratings)}")

# Spot-check Christian Pulisic
pulisics = [p for p in data if "pulisic" in p.get("name", "").lower()]
print("\nSpot check: Christian Pulisic")
for p in pulisics:
    print(f"Year: {p.get('year')} | Team: {p.get('team_name')} | Tier: {p.get('tier')} | Rating: {p.get('overall_rating')} | Positions: {p.get('primary_position')} {p.get('secondary_positions')}")

# Spot-check Erling Haaland
haalands = [p for p in data if "haaland" in p.get("name", "").lower()]
print("\nSpot check: Erling Haaland")
for p in haalands:
    print(f"Year: {p.get('year')} | Team: {p.get('team_name')} | Tier: {p.get('tier')} | Rating: {p.get('overall_rating')} | Positions: {p.get('primary_position')} {p.get('secondary_positions')}")

# Spot-check Lionel Messi
messis = [p for p in data if "messi" in p.get("name", "").lower() and p.get("year") in (2009, 2011, 2015, 2019, 2021)]
print("\nSpot check: Lionel Messi")
for p in messis:
    print(f"Year: {p.get('year')} | Team: {p.get('team_name')} | Tier: {p.get('tier')} | Rating: {p.get('overall_rating')} | Positions: {p.get('primary_position')} {p.get('secondary_positions')}")

# Spot-check Cristiano Ronaldo
ronaldos = [p for p in data if "ronaldo" in p.get("name", "").lower() and "cristiano" in p.get("name", "").lower() and p.get("year") in (2008, 2014, 2017, 2018, 2021)]
print("\nSpot check: Cristiano Ronaldo")
for p in ronaldos:
    print(f"Year: {p.get('year')} | Team: {p.get('team_name')} | Tier: {p.get('tier')} | Rating: {p.get('overall_rating')} | Positions: {p.get('primary_position')} {p.get('secondary_positions')}")
