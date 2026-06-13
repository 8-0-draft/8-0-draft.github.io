import json
import os
import shutil

DB_FILES = ["final_game_database.json", "final_game_database_with_managers.json"]

def fix_string(s):
    if not isinstance(s, str):
        return s
    
    # Common mojibake characters in our database
    # Ã¼ -> ü, Ã¶ -> ö, Ã¤ -> ä, ÃŸ -> ß, Ã© -> é, Ã¨ -> è, Ã¡ -> á, Ã­ -> í, Ã³ -> ó, Ãº -> ú, Ã± -> ñ, Ã§ -> ç
    # also cyrillic encoding issues, e.g. Ñ„ÑƒÑ‚Ð±Ð¾Ð»ÑŒÐ½Ñ‹Ð¹
    # We check if typical UTF-8 signature bytes (decoded as CP1252) are present
    if any(c in s for c in ['Ã', 'Â', 'Å', 'Æ', 'Ç', 'Ð', 'Ñ', 'Ö', '×', 'Ø', 'Š', 'š', 'ž', 'Ž', 'Ÿ', 'œ', 'æ']):
        # Try encoding back to CP1252 / Latin-1 bytes and decoding as UTF-8
        for enc in ['cp1252', 'latin1', 'cp1250', 'cp1254']:
            try:
                candidate = s.encode(enc).decode('utf-8')
                if candidate != s:
                    return candidate
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
                
    # Direct replacement for specific stubborn characters/words if they fail the auto-fix
    # Let's handle some typical names like "BeŠiktaŠ" -> "Beşiktaş"
    replacements = {
        "BeŠiktaŠ": "Beşiktaş",
        "Bešiktaš": "Beşiktaş",
        "BeŠiktaŠ Jimnastik Kulšbš": "Beşiktaş Jimnastik Kulübü",
        "Bešiktaš Jimnastik Kulübü": "Beşiktaş Jimnastik Kulübü",
        "Besiktas": "Beşiktaş",
        "MÃ¼nchen": "München",
        "Mnchen": "München",
        "FuÃŸball": "Fußball",
        "Fuball": "Fußball"
    }
    for old, new in replacements.items():
        if old in s:
            s = s.replace(old, new)
            
    return s

def repair_db_file(filepath):
    if not os.path.exists(filepath):
        print(f"File {filepath} not found. Skipping.")
        return

    # Backup first
    backup_path = filepath + ".mojibake_bak"
    shutil.copyfile(filepath, backup_path)
    print(f"Backed up {filepath} to {backup_path}")

    with open(filepath, 'r', encoding='utf-8') as f:
        db = json.load(f)

    changes = []
    
    # Recursively process list of dicts
    for idx, entry in enumerate(db):
        for key in list(entry.keys()):
            val = entry[key]
            if isinstance(val, str):
                fixed_val = fix_string(val)
                if fixed_val != val:
                    changes.append((key, val, fixed_val))
                    entry[key] = fixed_val
            elif isinstance(val, list):
                new_list = []
                for item in val:
                    if isinstance(item, str):
                        fixed_item = fix_string(item)
                        if fixed_item != item:
                            changes.append((key + "[]", item, fixed_item))
                            new_list.append(fixed_item)
                        else:
                            new_list.append(item)
                    else:
                        new_list.append(item)
                entry[key] = new_list

    # Save repaired file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

    print(f"Repaired {filepath}. Total string fixes applied: {len(changes)}")
    # Print sample of changes safely
    print("Sample fixes:")
    for change in changes[:15]:
        c_from = repr(change[1]).encode('ascii', errors='backslashreplace').decode('ascii')
        c_to = repr(change[2]).encode('ascii', errors='backslashreplace').decode('ascii')
        print(f"  Field '{change[0]}': {c_from} -> {c_to}")

def main():
    for filepath in DB_FILES:
        repair_db_file(filepath)

if __name__ == "__main__":
    main()
