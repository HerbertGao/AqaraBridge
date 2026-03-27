#!/usr/bin/env python3
"""
Semi-automated device mapping generator for AqaraBridge.

Fetches device models and resources from Aqara developer API,
matches them against PARAMS_TEMPLATES, and generates MODEL_REGISTRY entries.

Usage:
    # Fetch all devices and resources (requires valid cookie)
    python scripts/generate_mapping.py --fetch --cookie "Token=...; Userid=...; currentSid=..."

    # Generate registry from cached data
    python scripts/generate_mapping.py --generate

    # Validate existing registry against API data
    python scripts/generate_mapping.py --validate
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

CACHE_DIR = Path(__file__).parent / "cache"
DEVICES_CACHE = CACHE_DIR / "devices.json"
RESOURCES_DIR = CACHE_DIR / "resources"

API_BASE = "https://developer.aqara.com/open-server/console/resource"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "lang": "zh",
}


# ======================== API Fetching ========================


def fetch_devices(cookie: str, userid: str) -> list:
    """Fetch all device models from Aqara API."""
    url = f"{API_BASE}/query?page=1&pageSize=500&keyword=&server=1"
    resp = requests.get(url, headers={**HEADERS, "userid": userid},
                        cookies=_parse_cookie(cookie))
    resp.raise_for_status()
    data = resp.json()
    if data["code"] != 0:
        raise RuntimeError(f"API error: {data['message']}")
    devices = data["result"]["data"]
    print(f"Fetched {len(devices)} devices")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEVICES_CACHE, "w") as f:
        json.dump(devices, f, ensure_ascii=False, indent=2)
    return devices


def fetch_resources(cookie: str, userid: str, models: list[str]):
    """Fetch resource details for each model, with caching."""
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    cookies = _parse_cookie(cookie)

    for i, model in enumerate(models):
        cache_file = RESOURCES_DIR / f"{model}.json"
        if cache_file.exists():
            continue

        url = f"{API_BASE}/query/detail?subjectModel={model}"
        try:
            resp = requests.get(url, headers={**HEADERS, "userid": userid},
                                cookies=cookies)
            resp.raise_for_status()
            data = resp.json()
            resources = data.get("result", []) or []
        except Exception as e:
            print(f"  [{i+1}/{len(models)}] {model}: ERROR {e}")
            resources = []

        with open(cache_file, "w") as f:
            json.dump(resources, f, ensure_ascii=False, indent=2)

        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{len(models)}] fetched...")
            time.sleep(0.5)

    print(f"All {len(models)} resource files cached")


def _parse_cookie(cookie_str: str) -> dict:
    """Parse cookie string into dict."""
    cookies = {}
    for item in cookie_str.split(";"):
        item = item.strip()
        if "=" in item:
            k, v = item.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


# ======================== Template Matching ========================

# Resource patterns that identify device types
TEMPLATE_RULES = [
    # Curtains
    {
        "name": "cover_curtain_battery",
        "required": ["1.1.85", "14.4.85"],
        "has_any": ["8.0.2001"],
        "priority": 10,
    },
    {
        "name": "cover_curtain",
        "required": ["1.1.85", "14.4.85"],
        "priority": 9,
    },
    # Climate (P3 style)
    {
        "name": "climate_p3",
        "required": ["14.32.85", "8.0.2116", "3.1.85"],
        "priority": 10,
    },
    # Lights: RGB with color
    {
        "name": "light_rgb",
        "required": ["14.8.85", "14.1.85", "14.2.85"],
        "has_none": ["0.13.85"],
        "priority": 8,
    },
    {
        "name": "light_rgbw_dimmer",
        "required": ["14.8.85", "14.1.85", "14.2.85", "0.13.85"],
        "priority": 8,
    },
    # Lights: CCT with 14.x
    {
        "name": "light_cct_14x",
        "required": ["14.1.85", "14.2.85"],
        "has_none": ["14.8.85"],
        "priority": 7,
    },
    # Lights: CCT with 1.x
    {
        "name": "light_cct_1x",
        "required": ["1.7.85", "1.9.85"],
        "priority": 7,
    },
    # Presence FP1 style
    {
        "name": "sensor_presence_fp1",
        "required": ["3.51.85", "13.27.85"],
        "priority": 9,
    },
    # Motion with detect_time
    {
        "name": "sensor_motion_precision",
        "required": ["3.1.85", "8.0.2115"],
        "priority": 8,
    },
    # Motion with lux
    {
        "name": "sensor_motion_lux",
        "required": ["3.1.85"],
        "has_any": ["0.3.85", "0.4.85"],
        "match_attr": "motion_status",
        "priority": 7,
    },
    # Basic motion
    {
        "name": "sensor_motion",
        "required": ["3.1.85"],
        "match_attr": "motion_status",
        "priority": 6,
    },
    # Door sensors
    {
        "name": "sensor_door",
        "required": ["3.1.85"],
        "match_attr": "contact_status",
        "priority": 6,
    },
    # Smoke
    {
        "name": "sensor_smoke",
        "required": ["13.1.85"],
        "match_attr": "smoke",
        "priority": 7,
    },
    # Water leak
    {
        "name": "sensor_water_leak",
        "required": ["3.1.85"],
        "match_attr": "water_leak",
        "priority": 6,
    },
    # Cube
    {
        "name": "cube",
        "required": ["13.1.85"],
        "match_attr": "cube_status",
        "priority": 8,
    },
    # Switch with power (plug style)
    {
        "name": "plug_with_power",
        "required": ["4.1.85", "0.12.85", "0.13.85"],
        "has_none": ["4.2.85"],
        "match_attr": "plug_or_switch",
        "priority": 5,
    },
    # Multi-channel switch with power
    {
        "name": "switch_multi_neutral",
        "required": ["4.1.85", "4.2.85", "0.12.85"],
        "priority": 5,
    },
    # Multi-channel switch without power
    {
        "name": "switch_multi_no_neutral",
        "required": ["4.1.85", "4.2.85"],
        "has_none": ["0.12.85"],
        "priority": 4,
    },
    # Single switch with power
    {
        "name": "switch_1_neutral",
        "required": ["4.1.85", "0.12.85"],
        "has_none": ["4.2.85", "14.1.85", "1.1.85", "1.7.85"],
        "priority": 4,
    },
    # Single switch without power
    {
        "name": "switch_1_no_neutral",
        "required": ["4.1.85"],
        "has_none": ["4.2.85", "0.12.85", "14.1.85", "1.1.85", "1.7.85", "3.1.85", "3.51.85"],
        "priority": 3,
    },
    # TH sensor with pressure
    {
        "name": "sensor_th_pressure",
        "required": ["0.1.85", "0.2.85", "0.3.85"],
        "match_attr": "temperature",
        "priority": 6,
    },
    # TH sensor basic
    {
        "name": "sensor_th",
        "required": ["0.1.85", "0.2.85"],
        "has_none": ["0.3.85"],
        "match_attr": "temperature",
        "priority": 5,
    },
    # Button (wireless switch)
    {
        "name": "button_single",
        "required": ["13.1.85"],
        "match_attr": "switch_status",
        "has_none": ["4.1.85"],
        "priority": 5,
    },
    # Gateway (no params - catch all for gateway models)
    {
        "name": "gateway_no_params",
        "match_model": r"lumi\.gateway\.",
        "priority": 1,
    },
]


def match_template(model: str, resources: list) -> tuple:
    """Match a device to a template based on its resources.

    Returns: (template_name, confidence, overrides_dict)
    """
    res_ids = {r["resourceId"] for r in resources}
    res_attrs = {r.get("attr", "") for r in resources}

    if not resources:
        return None, 0, {}

    best_match = None
    best_priority = -1

    for rule in TEMPLATE_RULES:
        # Check model pattern
        if "match_model" in rule:
            if not re.search(rule["match_model"], model):
                continue

        # Check required resources
        required = rule.get("required", [])
        if not all(r in res_ids for r in required):
            continue

        # Check has_any
        if "has_any" in rule:
            if not any(r in res_ids for r in rule["has_any"]):
                continue

        # Check has_none
        if "has_none" in rule:
            if any(r in res_ids for r in rule["has_none"]):
                continue

        # Check attribute pattern
        if "match_attr" in rule:
            attr_pattern = rule["match_attr"]
            if attr_pattern == "motion_status":
                if "motion_status" not in res_attrs:
                    continue
            elif attr_pattern == "contact_status":
                if not any("contact" in a or "magnet" in a for a in res_attrs):
                    continue
            elif attr_pattern == "smoke":
                if not any("smoke" in a or "alarm" in a for a in res_attrs):
                    continue
            elif attr_pattern == "water_leak":
                if not any("leak" in a or "flood" in a for a in res_attrs):
                    continue
            elif attr_pattern == "cube_status":
                if "cube_status" not in res_attrs:
                    continue
            elif attr_pattern == "plug_or_switch":
                if not any("plug" in a or "power_status" in a or "ctrl_ch0" in a
                           for a in res_attrs):
                    continue
            elif attr_pattern == "temperature":
                if not any("temperature" in a for a in res_attrs):
                    continue
            elif attr_pattern == "switch_status":
                if not any("switch_status" in a for a in res_attrs):
                    continue

        priority = rule.get("priority", 0)
        if priority > best_priority:
            best_priority = priority
            best_match = rule["name"]

    if not best_match:
        return None, 0, {}

    # Detect channel count for multi-channel templates
    overrides = {}
    if "multi" in best_match or best_match == "button_single":
        ch_ids = sorted([r for r in res_ids if re.match(r"4\.\d+\.85$", r)])
        if len(ch_ids) > 1:
            ch_count = len(ch_ids)
            if best_match == "button_single":
                # Actually multi-button
                btn_ids = sorted([r for r in res_ids if re.match(r"13\.\d+\.85$", r)])
                if len(btn_ids) > 1:
                    best_match = "button_multi"
                    overrides["ch_count"] = len(btn_ids)
            else:
                overrides["ch_count"] = ch_count
        elif "multi" in best_match:
            overrides["ch_count"] = 2  # default

    confidence = best_priority * 10
    return best_match, confidence, overrides


# ======================== Code Generation ========================


def generate_registry(devices: list) -> str:
    """Generate MODEL_REGISTRY Python code from device data."""
    lines = []
    unmatched = []
    matched_count = 0

    for dev in sorted(devices, key=lambda d: d["subjectModel"]):
        model = dev["subjectModel"]
        name_en = dev.get("nameEn", dev.get("name", ""))

        # Load cached resources
        res_file = RESOURCES_DIR / f"{model}.json"
        if res_file.exists():
            with open(res_file) as f:
                resources = json.load(f)
        else:
            resources = []

        template, confidence, overrides = match_template(model, resources)

        if template is None:
            unmatched.append((model, name_en, [r["resourceId"] for r in resources]))
            continue

        matched_count += 1
        mfg = "Aqara"
        if "xiaomi" in name_en.lower() or model.startswith("lumi.sensor_") and "v1" in model:
            mfg = "Xiaomi"

        override_str = ""
        if overrides:
            override_str = f", {overrides}"

        line = f'    "{model}": ("{mfg}", "{name_en}", "", "{template}"{override_str}),'
        lines.append(line)

    output = f"# Generated: {matched_count} matched, {len(unmatched)} unmatched\n\n"
    output += "MODEL_REGISTRY = {\n"
    output += "\n".join(lines)
    output += "\n}\n"

    if unmatched:
        output += "\n# ===== UNMATCHED DEVICES (need manual review) =====\n"
        for model, name, res_ids in unmatched:
            output += f"# {model} | {name} | resources: {res_ids}\n"

    return output


# ======================== Validation ========================


def validate_registry():
    """Compare generated templates against existing MODEL_REGISTRY."""
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # We can't import directly due to HA deps, so parse the file
    mapping_file = project_root / "custom_components/aqara_bridge/core/aiot_mapping.py"
    content = mapping_file.read_text()

    # Extract model names from MODEL_REGISTRY
    existing_models = set(re.findall(r'"((?:lumi|aqara)\.[a-zA-Z0-9_.]+)":\s*\(', content))
    print(f"Existing models in registry: {len(existing_models)}")

    # Load cached devices
    if not DEVICES_CACHE.exists():
        print("No cached devices. Run --fetch first.")
        return

    with open(DEVICES_CACHE) as f:
        devices = json.load(f)

    api_models = {d["subjectModel"] for d in devices}
    print(f"API models: {len(api_models)}")

    missing = api_models - existing_models
    extra = existing_models - api_models
    print(f"Missing from registry: {len(missing)}")
    print(f"In registry but not in API: {len(extra)}")

    if missing:
        print("\nMissing models:")
        for m in sorted(missing):
            dev = next((d for d in devices if d["subjectModel"] == m), {})
            print(f"  {m}: {dev.get('nameEn', '?')}")


# ======================== Main ========================


def main():
    parser = argparse.ArgumentParser(description="Generate AqaraBridge device mapping")
    parser.add_argument("--fetch", action="store_true", help="Fetch devices and resources from API")
    parser.add_argument("--generate", action="store_true", help="Generate MODEL_REGISTRY code")
    parser.add_argument("--validate", action="store_true", help="Validate existing registry")
    parser.add_argument("--cookie", type=str, help="Cookie string for API auth")
    parser.add_argument("--userid", type=str, help="User ID for API", default="")
    args = parser.parse_args()

    if args.fetch:
        if not args.cookie:
            print("--cookie required for --fetch")
            sys.exit(1)
        # Extract userid from cookie if not provided
        userid = args.userid
        if not userid:
            m = re.search(r"Userid=([^;]+)", args.cookie)
            if m:
                userid = m.group(1)

        devices = fetch_devices(args.cookie, userid)
        models = [d["subjectModel"] for d in devices]
        fetch_resources(args.cookie, userid, models)

    if args.generate:
        if not DEVICES_CACHE.exists():
            print("No cached devices. Run --fetch first.")
            sys.exit(1)
        with open(DEVICES_CACHE) as f:
            devices = json.load(f)
        code = generate_registry(devices)
        output_file = CACHE_DIR / "generated_registry.py"
        with open(output_file, "w") as f:
            f.write(code)
        print(f"Generated registry written to {output_file}")
        print(code[:2000])

    if args.validate:
        validate_registry()

    if not (args.fetch or args.generate or args.validate):
        parser.print_help()


if __name__ == "__main__":
    main()
