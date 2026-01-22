#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EmailChecker.py
For: the Immortal Emperor Manipulator of humans lI_Isekai_Il
Purpose:
- Read emails from file (default: email.txt) or via --email
- Check EA existence
- If EA linked -> check Microsoft availability
- Save results under:
    - ea_not_available/         (email NOT linked to EA)
    - not_available_email/      (EA linked but Microsoft NOT available)
    - available/                (EA linked and Microsoft available)
- Print a summary for each result.

Requirements:
    pip install requests
"""
from __future__ import annotations
import argparse
import json
import os
import time
import re
import random
from typing import Dict, Any
import requests
import shutil
from colorama import init, Fore

init(autoreset=True)

def print_emperor_banner():
    terminal_width = shutil.get_terminal_size().columns
    border = "=" * terminal_width

    lines = [
        "The Immortal Emperor The Manipulator of Humans",
        "The one and The only Vampire lI_Isekai_Il | lI-Isekai-Il.",
        "The Emperor of kings"
    ]

    print(Fore.YELLOW + border)
    for line in lines:
        print(Fore.YELLOW + line.center(terminal_width))
    print(Fore.YELLOW + border)

print_emperor_banner()

# ---------------- Configuration ----------------
EA_CHECK_URL = "https://signin.ea.com/p/ajax/user/checkEmailExisted"
EA_REFERER_PAGE = "https://signin.ea.com/p/juno/create"
MS_CHECK_URL = "https://signup.live.com/API/CheckAvailableSigninNames"
MS_REFERER_PAGE = "https://signup.live.com/"

# Folder structure
DIR_EA_NOT_AVAILABLE = "ea_not_available"
DIR_NOT_AVAILABLE_EMAIL = "not_available_email"
DIR_AVAILABLE = "available"
RESULT_DIR = "results"

# Default email file
DEFAULT_EMAIL_FILE = "email.txt"

# Headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "DNT": "1",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": EA_REFERER_PAGE,
}

MS_HEADERS = {
    "User-Agent": DEFAULT_HEADERS["User-Agent"],
    "Accept": "application/json",
    "Content-Type": "application/json; charset=utf-8",
    "Referer": MS_REFERER_PAGE,
}

# ------------------------------------------------

def ensure_dirs():
    """Create necessary directories."""
    os.makedirs(DIR_EA_NOT_AVAILABLE, exist_ok=True)
    os.makedirs(DIR_NOT_AVAILABLE_EMAIL, exist_ok=True)
    os.makedirs(DIR_AVAILABLE, exist_ok=True)
    os.makedirs(RESULT_DIR, exist_ok=True)

def safe_filename(email: str) -> str:
    s = email.strip().lower()
    s = s.replace("@", "_at_").replace(".", "_dot_")
    s = re.sub(r"[^a-z0-9_]", "_", s)
    return s

def now_ts() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

class EmailChecker:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update(DEFAULT_HEADERS)

    def _delay_retry(self):
        """Random delay between 3–5 seconds to prevent rate limits."""
        t = random.uniform(3.0, 5.0)
        time.sleep(t)

    def refresh_ea_cookies(self):
        try:
            self.s.get(EA_REFERER_PAGE, timeout=15)
            self.s.headers.update({"Referer": EA_REFERER_PAGE})
            return True
        except Exception:
            return False

    def refresh_ms_cookies(self):
        try:
            self.s.get(MS_REFERER_PAGE, headers=MS_HEADERS, timeout=15)
            return True
        except Exception:
            return False

    def check_ea_email(self, email: str) -> Dict[str, Any]:
        """
        Check if email is linked to EA account using the correct API format.
        Request format: ?requestorId=portal&email=<email>&_=<timestamp>
        Response format: {"status": false, "message": "register_email_existed", ...}
        """
        params = {
            "requestorId": "portal",
            "email": email,
            "_": str(int(time.time() * 1000))
        }
        
        for attempt in range(3):
            try:
                r = self.s.get(EA_CHECK_URL, params=params, timeout=20)
                
                # Handle rate limiting
                if r.status_code == 429:
                    reset_time = int(r.headers.get('ratelimit-reset', 60))
                    print(f"  [!] Rate limit hit, waiting {reset_time} seconds...")
                    time.sleep(reset_time)
                    continue
                    
                status = {"status_code": r.status_code, "headers": dict(r.headers)}
                
                try:
                    body = r.json()
                except Exception:
                    body = {"raw_text": r.text[:1000]}
                
                if r.status_code == 200:
                    return {"ok": True, "response": body, "meta": status}
                else:
                    print(f"  [!] EA check failed with status {r.status_code}, retrying...")
                    self.refresh_ea_cookies()
                    self._delay_retry()
                    
            except Exception as e:
                print(f"  [!] EA check error (attempt {attempt + 1}): {e}")
                self._delay_retry()
                continue
                
        return {"ok": False, "response": {}, "meta": {"status_code": 0, "headers": {}}}

    def interpret_ea_response(self, body: Any) -> Dict[str, Any]:
        """
        Interpret EA response based on actual API format:
        {"status": false, "message": "register_email_existed", ...} = email exists (linked to EA)
        {"status": true, "message": "register_email_not_existed", ...} = email doesn't exist
        """
        if not isinstance(body, dict):
            return {"exists": False, "reason": "not_a_dict"}

        # Check the actual message field from EA API
        msg = body.get("message", "").lower()
        
        # EA returns "register_email_existed" when email is already registered
        if "register_email_existed" in msg or msg == "register_email_existed":
            return {"exists": True, "reason": "EA message: register_email_existed"}
        
        # EA returns "register_email_not_existed" when email is not registered
        if "register_email_not_existed" in msg or msg == "register_email_not_existed":
            return {"exists": False, "reason": "EA message: register_email_not_existed"}

        # Fallback: check status field
        status = body.get("status")
        if status is False and "existed" in msg:
            return {"exists": True, "reason": "status=false with existed message"}
        if status is True and "not_existed" in msg:
            return {"exists": False, "reason": "status=true with not_existed message"}

        # Heuristic fallback
        text = json.dumps(body).lower()
        if "existed" in text and "not" not in text:
            return {"exists": True, "reason": "text_heuristic_positive"}
        if "not_existed" in text or "does not exist" in text:
            return {"exists": False, "reason": "text_heuristic_negative"}
            
        return {"exists": False, "reason": "no_clear_indicator"}

    def check_ms_name(self, email: str) -> Dict[str, Any]:
        payload = {
            "includeSuggestions": True,
            "signInName": email,
            "uiflvr": 1001,
            "scid": 100118,
            "uaid": "auto",
            "hpgid": 200225
        }
        
        for attempt in range(3):
            try:
                r = self.s.post(MS_CHECK_URL, headers=MS_HEADERS, json=payload, timeout=25)
                
                # Handle rate limiting
                if r.status_code == 429:
                    reset_time = int(r.headers.get('ratelimit-reset', 60))
                    print(f"  [!] MS rate limit hit, waiting {reset_time} seconds...")
                    time.sleep(reset_time)
                    continue
                    
                status = {"status_code": r.status_code, "headers": dict(r.headers)}
                
                try:
                    body = r.json()
                except Exception:
                    body = {"raw_text": r.text[:1000]}
                
                if r.status_code == 200:
                    return {"ok": True, "response": body, "meta": status}
                else:
                    print(f"  [!] MS check failed with status {r.status_code}, retrying...")
                    self.refresh_ms_cookies()
                    self._delay_retry()
                    
            except Exception as e:
                print(f"  [!] MS check error (attempt {attempt + 1}): {e}")
                self._delay_retry()
                continue
                
        return {"ok": False, "response": {}, "meta": {"status_code": 0, "headers": {}}}

    def interpret_ms_response(self, body: Any) -> Dict[str, Any]:
        if not isinstance(body, dict):
            return {"available": None, "reason": "not_a_dict"}

        if "isAvailable" in body:
            return {"available": bool(body["isAvailable"]), "reason": "field:isAvailable"}
        if body.get("suggestions"):
            return {"available": False, "reason": "has_suggestions"}
            
        text = json.dumps(body).lower()
        if "notavailable" in text or "already" in text or "taken" in text:
            return {"available": False, "reason": "text_negative"}
        if "available" in text and "not" not in text:
            return {"available": True, "reason": "text_positive"}
            
        return {"available": None, "reason": "unknown"}

    def process_email(self, email: str) -> Dict[str, Any]:
        email = email.strip()
        result = {
            "email": email,
            "timestamp": now_ts(),
            "ea_check": None,
            "ea_interpret": None,
            "ms_check": None,
            "ms_interpret": None,
            "final_folder": None,
            "note": None
        }

        # Step 1: EA check
        ea = self.check_ea_email(email)
        result["ea_check"] = ea
        ea_interp = self.interpret_ea_response(ea.get("response", {}))
        result["ea_interpret"] = ea_interp

        if not ea.get("ok") or not ea_interp.get("exists"):
            folder = DIR_EA_NOT_AVAILABLE
            result["final_folder"] = folder
            result["note"] = "EA not linked or error"
        else:
            ms = self.check_ms_name(email)
            result["ms_check"] = ms
            ms_interp = self.interpret_ms_response(ms.get("response", {}))
            result["ms_interpret"] = ms_interp
            
            if ms_interp.get("available") is True:
                folder = DIR_AVAILABLE
                result["final_folder"] = folder
                result["note"] = "EA linked and Microsoft available"
            else:
                folder = DIR_NOT_AVAILABLE_EMAIL
                result["final_folder"] = folder
                result["note"] = "EA linked but Microsoft not available"

        # Save JSON
        base = safe_filename(email)
        fname = f"{base}_{int(time.time())}.json"
        dest = os.path.join(result["final_folder"], fname)
        
        # Ensure folder exists
        os.makedirs(result["final_folder"], exist_ok=True)
        
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Print decorated summary
        print("────────────────────")
        if result["final_folder"] == DIR_EA_NOT_AVAILABLE:
            print(f" {email}")
            print(" EA Not Linked")
            print(" Hotmail/MSN: Skipped (EA Not Linked)")
        elif result["final_folder"] == DIR_NOT_AVAILABLE_EMAIL:
            print(f" {email}")
            print(" EA Linked")
            print(" Hotmail: Not Available")
            print(" MSN: Skipped")
        elif result["final_folder"] == DIR_AVAILABLE:
            print(f" {email}")
            print(" EA Linked")
            print(" Hotmail: Available")
            print(" MSN: Available")
        print(f"Saved: {dest}")
        print("────────────────────\n")
        return result

# ---------------- CLI ----------------
def read_emails_from_file(path: str) -> list[str]:
    if not os.path.isfile(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [x.strip() for x in f if x.strip()]

def main():
    ensure_dirs()
    parser = argparse.ArgumentParser(description="EA + Microsoft Email Checker")
    parser.add_argument("--email", "-e", help="Single email to check")
    parser.add_argument("--file", "-f", help="File containing emails (default: email.txt)")
    parser.add_argument("--delay", "-d", type=float, default=0.6, help="Delay between emails")
    args = parser.parse_args()

    if args.email:
        emails = [args.email.strip()]
    else:
        file_path = args.file or DEFAULT_EMAIL_FILE
        emails = read_emails_from_file(file_path)
        if not emails:
            print(f"No emails found in '{file_path}'")
            return

    checker = EmailChecker()
    for idx, em in enumerate(emails, 1):
        print(f"[{idx}/{len(emails)}] Processing: {em}")
        try:
            checker.process_email(em)
            time.sleep(args.delay)
        except KeyboardInterrupt:
            print("\n Interrupted by user.")
            break
        except Exception as e:
            print(f" Error on {em}: {e}")

if __name__ == "__main__":
    main()