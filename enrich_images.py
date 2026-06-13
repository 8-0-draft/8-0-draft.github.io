import os
import sys
import json
import time
import urllib.request
import urllib.parse
import shutil
import argparse
import builtins

def safe_print(*args, **kwargs):
    try:
        builtins.print(*args, **kwargs)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "ascii"
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(arg.encode(encoding, errors="replace").decode(encoding))
            else:
                new_args.append(arg)
        builtins.print(*new_args, **kwargs)

print = safe_print

# ══════════════════════════════ CONFIGURATION ════════════════════════════════
DB_PATH = "final_game_database.json"
BACKUP_DB_PATH = "final_game_database.json.bak"
CACHE_PATH = "wikipedia_image_cache.json"

# Standard Chrome Browser User-Agent to prevent bot-detection blocking
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {"User-Agent": USER_AGENT}

# Thread lock and rate limiting variables
import threading
request_lock = threading.Lock()
last_request_time = 0.0
# ════════════════════════════════════════════════════════════════════════════

def make_request(url):
    """Perform a HTTP GET request with global rate limit compliance and retries."""
    global last_request_time
    
    with request_lock:
        # Enforce minimum 0.35s spacing between requests across all threads
        elapsed = time.time() - last_request_time
        spacing = 0.35
        if elapsed < spacing:
            time.sleep(spacing - elapsed)
        last_request_time = time.time()
        
    req = urllib.request.Request(url, headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            is_429 = "429" in str(e)
            if attempt == 3:
                print(f"\n[Error] Failed to fetch {url} after 4 attempts: {e}")
                return None
            sleep_time = 5.0 * (attempt + 1) if is_429 else 1.0 * (attempt + 1)
            print(f"\n[Warning] Attempt {attempt+1} failed for {url}: {e}. Retrying in {sleep_time}s...")
            time.sleep(sleep_time)
    return None

def batch_direct_lookup(names, cache):
    """Query Wikipedia for multiple pageimages in a single batch request."""
    # Wikipedia API supports querying up to 50 titles at once
    titles_str = "|".join(urllib.parse.quote(name) for name in names)
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={titles_str}&prop=pageimages&pithumbsize=324&format=json"
    
    data = make_request(url)
    if not data or "query" not in data or "pages" not in data["query"]:
        return
        
    pages = data["query"]["pages"]
    # Map back pages to names. Since API can return normalized titles, we match case-insensitively
    # or look at the original titles mapping if provided.
    normalized_map = {}
    if "normalized" in data["query"]:
        for item in data["query"]["normalized"]:
            normalized_map[item["to"]] = item["from"]
            
    for page_id, page_data in pages.items():
        title = page_data.get("title")
        orig_name = normalized_map.get(title, title)
        
        # Match back to our input names (case-insensitive fallback)
        matched_name = None
        for n in names:
            if n.lower() == orig_name.lower() or n.lower() == title.lower():
                matched_name = n
                break
                
        if not matched_name:
            # Try matching by normalized title
            for n in names:
                if urllib.parse.unquote(urllib.parse.quote(n)).lower() == title.lower():
                    matched_name = n
                    break
        
        if matched_name:
            thumbnail = page_data.get("thumbnail")
            if thumbnail and "source" in thumbnail:
                cache[matched_name] = thumbnail["source"]
            else:
                # Direct match had no image; leave unmapped for search fallback
                pass

def search_fallback_lookup(name):
    """Search Wikipedia for the player and retrieve the first search result's image."""
    # 1. Search for "[Name] footballer"
    query = f"{name} footballer"
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
    
    data = make_request(search_url)
    if not data or "query" not in data or "search" not in data["query"] or not data["query"]["search"]:
        # Try without 'footballer' suffix as a last resort
        query = name
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
        data = make_request(search_url)
        if not data or "query" not in data or "search" not in data["query"] or not data["query"]["search"]:
            return None
            
    title = data["query"]["search"][0]["title"]
    
    # 2. Get the pageimage for the found title
    img_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&pithumbsize=324&format=json"
    img_data = make_request(img_url)
    if not img_data or "query" not in img_data or "pages" not in img_data["query"]:
        return None
        
    pages = img_data["query"]["pages"]
    page_data = list(pages.values())[0]
    thumbnail = page_data.get("thumbnail")
    if thumbnail and "source" in thumbnail:
        return thumbnail["source"]
    return None

def load_db():
    print(f"Loading database from {DB_PATH}...")
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    # Create backup first
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_DB_PATH)
        print(f"Backup created at {BACKUP_DB_PATH}")
        
    print(f"Saving enriched database to {DB_PATH}...")
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    print("Database saved successfully!")

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            try:
                cache = json.load(f)
                print(f"Loaded cache from {CACHE_PATH} ({len(cache)} entries)")
                return cache
            except Exception:
                print(f"Warning: Cache file {CACHE_PATH} was corrupted, starting fresh.")
    return {}

def save_cache(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Enrich modern players in game database with Wikipedia images.")
    parser.add_argument("--limit", type=int, default=None, help="Limit the number of players to enrich (for testing).")
    parser.add_argument("--reset-cache", action="store_true", help="Clear cache and start over.")
    args = parser.parse_args()

    db = load_db()
    
    # Identify unique modern players (year >= 2013) that do not have an image_url
    modern_players = [p for p in db if p.get("year", 0) >= 2013 and not p.get("image_url")]
    unique_names = sorted(list(set(p["name"] for p in modern_players)))
    
    print(f"Found {len(modern_players)} player records matching modern era criteria.")
    print(f"Identified {len(unique_names)} unique player names to fetch.")
    
    if args.reset_cache and os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
        print("Cache reset successfully.")
        
    cache = load_cache()
    
    # Filter unique names that are not in cache
    names_to_process = [name for name in unique_names if name not in cache]
    
    if args.limit:
        names_to_process = names_to_process[:args.limit]
        print(f"Limited processing to {len(names_to_process)} players.")
        
    if not names_to_process:
        print("All unique players are already cached! Proceeding directly to update the database.")
    else:
        print(f"Starting enrichment for {len(names_to_process)} players...")
        
        # --- PHASE 1: BATCH DIRECT LOOKUP ---
        print("\n--- Phase 1: Batch Direct Lookup (50 at a time) ---")
        batch_size = 50
        batches = [names_to_process[i:i + batch_size] for i in range(0, len(names_to_process), batch_size)]
        
        for idx, batch in enumerate(batches):
            print(f"Direct Lookup Batch {idx+1}/{len(batches)} ({len(batch)} players)...")
            batch_direct_lookup(batch, cache)
            save_cache(cache)
            
        # --- PHASE 2: SEARCH FALLBACK LOOKUP ---
        # Any name that is not in the cache now means it returned no image in the direct lookup
        remaining_names = [name for name in names_to_process if name not in cache]
        print(f"\n--- Phase 2: Parallel Search Fallback Lookup for remaining {len(remaining_names)} players ---")
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def worker(name_to_search):
            try:
                return name_to_search, search_fallback_lookup(name_to_search)
            except Exception:
                return name_to_search, None

        success_count = 0
        fail_count = 0
        
        # We use a pool of 8 threads to fetch images concurrently
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(worker, name): name for name in remaining_names}
            
            for idx, future in enumerate(as_completed(futures)):
                name, img_url = future.result()
                if img_url:
                    cache[name] = img_url
                    success_count += 1
                    status = "[OK] Found image!"
                else:
                    cache[name] = None
                    fail_count += 1
                    status = "[FAILED] No image found."
                
                print(f"[{idx+1}/{len(remaining_names)}] '{name}': {status}")
                
                # Save cache periodically
                if (idx + 1) % 20 == 0:
                    save_cache(cache)
                    
        save_cache(cache)
        print(f"\nPhase 2 completed. Successes: {success_count}, Fails: {fail_count}")

    # --- UPDATE DATABASE WITH CACHED IMAGES ---
    print("\nUpdating database records with cached image URLs...")
    updated_records_count = 0
    total_images_in_db = 0
    
    for player in db:
        if player.get("year", 0) >= 2013:
            name = player["name"]
            if name in cache and cache[name]:
                player["image_url"] = cache[name]
                updated_records_count += 1
                
        if player.get("image_url"):
            total_images_in_db += 1
            
    print(f"Updated {updated_records_count} modern player records in memory.")
    print(f"Total players with image_url in DB: {total_images_in_db}/{len(db)}")
    
    save_db(db)
    print("Done!")

if __name__ == "__main__":
    main()
