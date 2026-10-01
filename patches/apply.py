"""Apply all LMArenaBridge patches for Railway deployment."""
import os

SRC = "/app/src"

def patch_main():
    path = os.path.join(SRC, "main.py")
    with open(path) as f:
        c = f.read()
    old_etract = '# Etract models\n            debug_print("Etracting models from page...")'
    new_etract = '''# Etract models via model-catalog API
            debug_print("Etracting models from model-catalog API...")
            try:
                catalog_data = await page.evaluate("""async () => {
                    const r = await fetch('/netjs-api/model-catalog');
                    return await r.tet();
                }""")
                catalog = json.loads(catalog_data)
                models = []
                for arena_group in catalog:
                    for m in arena_group.get("models", []):
                        if m.get("userSelectable"):
                            models.append(m)
                if models:
                    save_models(models)
                    debug_print(f"Saved {len(models)} models from catalog API")
            ecept Eception as e:
                debug_print(f"Error etracting models: {e}")'''
    if old_etract in c:
        c = c.replace(old_etract, new_etract)
        print("Patched model etraction")
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
    c = c.replace(
        '        _m().debug_print("Camoufo proy: reCAPTCHA mint failed for anonymous signup.")\n        return None',
        '        _m().debug_print("reCAPTCHA mint failed, continuing.")\n        recaptcha_token = ""'
    )
    with open(path, "w") as f:
        f.write(c)
    print("Patched recaptcha")

if __name__ == "__main__":
    patch_main()
    patch_recaptcha()
    print("All patches applied!")
