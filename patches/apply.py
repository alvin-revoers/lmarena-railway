"""Robust patch for LMArenaBridge model extraction."""
import os
import re

SRC = "/app/src"

def patch_main():
    path = os.path.join(SRC, "main.py")
    with open(path) as f:
        c = f.read()

    # Use regex to find and replace the model extraction block
    # Matches from "# Extract models" to the except block
    pattern = r'# Extract models\n.*?debug_print\(f"\\u274c Error extracting models: \{e\}"\)'

    new_code = '''# Extract models via model-catalog API
            debug_print("Extracting models from model-catalog API...")
            try:
                catalog_data = await page.evaluate("""async () => {
                    const r = await fetch('/nextjs-api/model-catalog');
                    return await r.text();
                }""")
                catalog = json.loads(catalog_data)
                models = []
                for arena_group in catalog:
                    for m in arena_group.get("models", []):
                        if m.get("userSelectable"):
                            models.append(m)
                if models:
                    save_models(models)
                    debug_print(f"\\u2705 Saved {len(models)} models from catalog API")
                else:
                    debug_print("\\u26a0\\ufe0f No selectable models in catalog")
            except Exception as e:
                debug_print(f"\\u274c Error extracting models from catalog: {e}")'''

    new_c, count = re.subn(pattern, lambda m: new_code, c, flags=re.DOTALL)
    if count > 0:
        print(f"Patched model extraction ({count} replacement)")
        with open(path, "w") as f:
            f.write(new_c)
    else:
        print("WARNING: model extraction pattern not found, trying fallback")
        # Fallback: try simple string replacement of the debug line
        if 'debug_print("Extracting models from page...")' in c:
            c = c.replace(
                'debug_print("Extracting models from page...")',
                'debug_print("Extracting models from model-catalog API...")\n'
                '            try:\n'
                '                catalog_data = await page.evaluate("""async () => { const r = await fetch(\'/nextjs-api/model-catalog\'); return await r.text(); }""")\n'
                '                _catalog = json.loads(catalog_data)\n'
                '                _models = [m for g in _catalog for m in g.get("models", []) if m.get("userSelectable")]\n'
                '                save_models(_models)\n'
                '                debug_print(f"Saved {len(_models)} models")\n'
                '            except Exception as e:\n'
                '                debug_print(f"Catalog error: {e}")\n'
                '            # Original code below (disabled):\n'
                '            debug_print("OLD CODE DISABLED")\n'
                '            if False:'
            )
            with open(path, "w") as f:
                f.write(c)
            print("Applied fallback patch")

def patch_recaptcha():
    path = os.path.join(SRC, "recaptcha.py")
    with open(path) as f:
        c = f.read()
    c = c.replace(
        "    if not turnstile_token or not provisional_user_id:",
        "    if not provisional_user_id:"
    )
    with open(path, "w") as f:
        f.write(c)
    print("Patched recaptcha")

if __name__ == "__main__":
    patch_main()
    patch_recaptcha()
    print("Done!")
