"""Patch: fetch models via direct HTTP, bypass browser Cloudflare issues."""
import os
import re


SRC = "/app/src"


def patch_main():
    path = os.path.join(SRC, "main.py")
    with open(path) as f:
        c = f.read()
    
    # Add httpx import if not present
    if "import httpx" not in c:
        c = c.replace("import json", "import json\nimport httpx")
        print("Added httpx import")
    
    # Find the get_initial_data function and inject HTTP model fetch
    # We add it right after the function definition
    old_sig = "async def get_initial_data():"
    new_sig = '''async def get_initial_data():
    # PATCH: Try direct HTTP fetch for models first (bypass browser)
    try:
        async with httpx.AsyncClient(timeout=30.0) as _hc:
            _r = await _hc.get("https://arena.ai/nextjs-api/model-catalog")
            if _r.status_code == 200:
                _catalog = _r.json()
                _models = []
                for _g in _catalog:
                    for _m in _g.get("models", []):
                        if _m.get("userSelectable"):
                            _models.append(_m)
                if _models:
                    save_models(_models)
                    print(f"PATCH: Saved {len(_models)} models via direct HTTP")
    except Exception as _e:
        print(f"PATCH: Direct HTTP model fetch failed: {_e}")'''
    
    if old_sig in c and "PATCH: Try direct HTTP fetch" not in c:
        c = c.replace(old_sig, new_sig)
        print("Injected HTTP model fetch")
    else:
        print("WARNING: get_initial_data not found or already patched")
    
    # PATCH 2: Bypass reCAPTCHA requirement - allow empty tokens
    # Replace the HTTPException raise with a warning and empty token
    old_raise = '''                if not recaptcha_token:
                    debug_print("\\u274c Cannot proceed, failed to get reCAPTCHA token.")
                    raise HTTPException(
                        status_code=503,
                        detail="Service Unavailable: Failed to acquire reCAPTCHA token. The bridge server may be blocked."
                    )'''
    new_raise = '''                if not recaptcha_token:
                    debug_print("\\u26a0\\ufe0f No reCAPTCHA token, proceeding with empty token.")
                    recaptcha_token = ""'''
    if old_raise in c:
        c = c.replace(old_raise, new_raise)
        print("Bypassed reCAPTCHA requirement")
    else:
        print("WARNING: reCAPTCHA raise pattern not found")
    
    with open(path, "w") as f:
        f.write(c)


def patch_recaptcha():
    path = os.path.join(SRC, "recaptcha.py")
    with open(path) as f:
        c = f.read()
    if "if not turnstile_token or not provisional_user_id:" in c:
        c = c.replace(
            "    if not turnstile_token or not provisional_user_id:",
            "    if not provisional_user_id:"
        )
        print("Patched recaptcha")
    with open(path, "w") as f:
        f.write(c)


if __name__ == "__main__":
    patch_main()
    patch_recaptcha()
    print("Done!")
