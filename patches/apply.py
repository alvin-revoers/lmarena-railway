"""Apply LMArenaBridge patches for Railway."""
import os
import re
    
SRC = "/app/src"
    
    
def patch_main():
    path = os.path.join(SRC, "main.py")
    with open(path) as f:
        c = f.read()
    
    # Patch 1: Replace broken initialModels regex with model-catalog API
    old_code = """            # Extract models
            debug_print("Extracting models from page...")
            try:
                page_body = await page.content()
                match = re.search(r'{\\"initialModels\\":(\\[.*?\\]),\\"initialModel[A-Z]Id', page_body, re.DOTALL)
                if match:
                    models_json = match.group(1).encode().decode('unicode_escape')
                    models = json.loads(models_json)
                    save_models(models)
                    debug_print(f"\\u2705 Saved {len(models)} models")
                else:
                    debug_print("\\u26a0\\ufe0f Could not find models in page")
            except Exception as e:
                debug_print(f"\\u274c Error extracting models: {e}")"""
    
    new_code = """            # Extract models via model-catalog API
            debug_print("Extracting models from model-catalog API...")
            try:
                catalog_data = await page.evaluate(\"\"\"async () => {
                    const r = await fetch('/nextjs-api/model-catalog');
                    return await r.text();
                }\"\"\")
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
                debug_print(f"\\u274c Error extracting models from catalog: {e}")"""
    
    if old_code in c:
        c = c.replace(old_code, new_code)
        print("Patched model extraction")
    else:
        print("WARNING: model extraction pattern not found")
    
    with open(path, "w") as f:
        f.write(c)
    
    
def patch_recaptcha():
    path = os.path.join(SRC, "recaptcha.py")
    with open(path) as f:
        c = f.read()
    c = c.replace(
        "    if not turnstile_token or not provisional_user_id:\n        return None",
        "    if not provisional_user_id:\n        return None"
    )
    with open(path, "w") as f:
        f.write(c)
    print("Patched recaptcha")
    
    
if __name__ == "__main__":
    patch_main()
    patch_recaptcha()
    print("Done!")
