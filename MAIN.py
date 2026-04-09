import base64
import csv
import json
import os
import secrets
import textwrap
import zlib
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo, available_timezones
except Exception:
    ZoneInfo = None
    def available_timezones():
        return set()

import requests
import rsa
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle

BG = "#000000"
CARD = "#0b0b0b"
TEXT = "#b1bad3"
SUBTEXT = "#8f9bb3"
GREEN = "#00e701"
RED = "#ff4e4e"
BLUE = "#3498db"
PURPLE = "#9b59b6"
ORANGE = "#e67e22"
Window.clearcolor = get_color_from_hex(BG)

PRIVATE_KEY_FILE = "shv_admin_private.pem"
PUBLIC_KEY_FILE = "shv_admin_public.pem"
LICENSE_DB_FILE = "synapse_licenses_db.json"
REVOKED_EXPORT_FILE = "synapse_revoked_licenses.json"
AUTHORITY_BACKUP_FILE = "synapse_authority_backup.ctp"
LICENSE_LIST_BACKUP_FILE = "synapse_license_list_backup.ctlist"
FULL_BACKUP_FILE = "synapse_full_backup.ctfull"
GITHUB_CONFIG_FILE = "synapse_github_upload_config.json"
BACKUP_BUNDLE_APP = "sh_vertex_admin_panel"

DEFAULT_GITHUB_UPLOAD = {
    "owner": "therealwolfman97",
    "repo": "SH-VERTEX-ADMIN-PANEL",
    "branch": "main",
    "path": "LICENSING/APPS/REVOCATIONS/synapse-revo.json",
    "token": "",
}

DEFAULT_AUTHORITY_PRIVATE_PEM = r'''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA5KyY9ak9h6baCa1BE/N7aEUU8G68NDWB2CDrBSsEVmfD4LEl
eV9kcI/SZXk7VTpxAzAED/hRBCkEx7X6INeIP7P83PB2TRSoBObfk7WaiiV0VKbg
S/ZgIHuOzwxszJLBWd8xQ3f9AK1ODHT7WQK+Hsco9KPyD2C43bC56nTFe2vUtRVW
o7HqPcDhiJvyeQXUf/TsJIwi2/biNhVLfaeHsPoS0D524a6pSqJEiCST/GLb+Et9
c5y8clNryMU1fjw1SIb6TYXpOYB24JtLX/jTNpC9pDLMcGuUoxQ8ck5ja6kdxn27
qvW6I6BXpeIFgU1e8gs26h0PX+VJBfNl9AS6HwIDAQABAoIBAFlkfYEfUU3btIWu
5G9bseTviIF7EHiqaCFosOc6yz3J36FRLtCVMWrtVjbT3xVwvKgd16C0lls1e8hk
g6zeBMW+Yz2thNmaFxqfdExGZGzXunOzLqCTZj2cf5XCCjAouIwc+6Gf4NgoZ4fo
HS/NKixW99Q22NQZH/uN8AfO8TpPDgmU41ehei87Jwgu52dl1hkgmdacNHNfOjgF
5AZ2O16V1j2c0v6RzjAu0vaDEJpf2PCkj+pis/k8VwqmIdyEfktcQ7h1he0SrZ++
hRo71h74+/k4EUdK6gH4Et23uwjg+SpAjNg0/NR7iPXfvD7yhvq5QoSYnrSU0AuM
2IpAExkCgYEA/6pGj97kuhpwhICfEMoQccnv1aTPi/+dh1DgDV2wmzqFxs/m5NSH
nfoWbrkdKPsXjJRLW8jC4Bpe6dmEieMSgo4ED4RyI4JyN5s+Y/LzZmudba0Jg9pw
6y/QpJPMWOKaaYbOc51/xxYguUz4kE/7d8Bti4iNTPO1v1SF+ayQjXkCgYEA5PlF
ljIQqdpn9TJqiD0RYRpEOuoD6hOa7JjLiu7N7nztYuoVWEqbkqbTTJ6uNvw7yKdC
XtdgPBnrUmA8HRuvulqtxg+qgO+9znPhi2S31yx0gm4UjKKq5Qk5V7rovEOPb4ON
BD8lAr23M6eM0nhDXrH9n7s96zWjFq1TnyjOVlcCgYEAwK6j32otF9U1V6dYOl8P
ZbK7flhn0ysingjl0yz5HQROLjgh2/QRAY6puWjqASi75sccxF/Z/uvg/H1i1ki8
eohtpwQ6wWhejGoD62/+4QHZ8/6lXSoUUCwJIwAA0jx2A3IFxjy9QF3866qG6rxc
2TO9W5veYlCKeVhKYJEdoIECgYB62IYOC/RGvKfTtGXVjDX7y9TZat4IwtX2pA9o
DbEsh5fw3rfu87A94QUycVv0oiUNBTelnJXECP/o5Tq7PzRrneTng1Yt8PH7hs52
M+YyKmaj551cypU3Zlh+igf9oZ2d7Y1Fvv8DVneo3fa+oMk8T/BLt3CD9fX2360i
kgkJ5wKBgD6IKHyqW44EWkOEJ2xsmACMWmxPdtsi2O9degkFchKNN4Ji945pLtWJ
7uelCyEGJ3WkrqT3zXknAfu9MDlUElRKoR1P1qEAanE9ZssLWT++s6nx8oi9tsKU
Haohpq3OUYj4Si3upDIQWnEuBMynQ7+VAwXqrPdDdFsZWlTDmKT9
-----END RSA PRIVATE KEY-----
'''
DEFAULT_AUTHORITY_PUBLIC_PEM = r'''-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEA5KyY9ak9h6baCa1BE/N7aEUU8G68NDWB2CDrBSsEVmfD4LEleV9k
cI/SZXk7VTpxAzAED/hRBCkEx7X6INeIP7P83PB2TRSoBObfk7WaiiV0VKbgS/Zg
IHuOzwxszJLBWd8xQ3f9AK1ODHT7WQK+Hsco9KPyD2C43bC56nTFe2vUtRVWo7Hq
PcDhiJvyeQXUf/TsJIwi2/biNhVLfaeHsPoS0D524a6pSqJEiCST/GLb+Et9c5y8
clNryMU1fjw1SIb6TYXpOYB24JtLX/jTNpC9pDLMcGuUoxQ8ck5ja6kdxn27qvW6
I6BXpeIFgU1e8gs26h0PX+VJBfNl9AS6HwIDAQAB
-----END RSA PUBLIC KEY-----
'''

def ensure_default_authority_files():
    priv_path = file_path(PRIVATE_KEY_FILE)
    pub_path = file_path(PUBLIC_KEY_FILE)
    if not os.path.exists(priv_path):
        with open(priv_path, 'wb') as f:
            f.write(DEFAULT_AUTHORITY_PRIVATE_PEM.encode('utf-8'))
    if not os.path.exists(pub_path):
        with open(pub_path, 'wb') as f:
            f.write(DEFAULT_AUTHORITY_PUBLIC_PEM.encode('utf-8'))


def utc_now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def app_data_dir():
    app = App.get_running_app()
    if app and getattr(app, "user_data_dir", None):
        path = app.user_data_dir
    else:
        path = os.path.join(os.path.expanduser("~"), ".sh_vertex_admin_panel")
    os.makedirs(path, exist_ok=True)
    return path


def file_path(name):
    return os.path.join(app_data_dir(), name)


def downloads_base_dir():
    candidates = [
        "/storage/emulated/0/Download",
        "/sdcard/Download",
        os.path.join(os.path.expanduser("~"), "Download"),
    ]
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except Exception:
            continue
    fallback = app_data_dir()
    os.makedirs(fallback, exist_ok=True)
    return fallback


def admin_export_dir(*parts):
    path = os.path.join(downloads_base_dir(), "SH Vertex Admin Panel", "Licensing", "Synapse", *parts)
    os.makedirs(path, exist_ok=True)
    return path



def _timestamped_export_path(directory, filename):
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(filename)
    return os.path.join(directory, f"{base}_{stamp}{ext}")


def list_backup_files(directory, suffixes):
    candidates = []
    suffixes = tuple(str(s).lower() for s in (suffixes or []))
    try:
        for name in os.listdir(directory):
            lower = name.lower()
            if suffixes and not lower.endswith(suffixes):
                continue
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                candidates.append(path)
    except Exception:
        return []
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates


def authority_backup_dir():
    return admin_export_dir("Authority Backups")


def authority_backup_export_path():
    return _timestamped_export_path(authority_backup_dir(), AUTHORITY_BACKUP_FILE)


def list_authority_backup_files():
    return list_backup_files(authority_backup_dir(), [".ctp", ".shva", ".ctfull"])


def license_list_backup_dir():
    return admin_export_dir("License List Backups")


def license_list_backup_export_path():
    return _timestamped_export_path(license_list_backup_dir(), LICENSE_LIST_BACKUP_FILE)


def list_license_list_backup_files():
    return list_backup_files(license_list_backup_dir(), [".ctlist", ".json", ".txt", ".ctfull"])


def full_backup_dir():
    return admin_export_dir("Full Backups")


def full_backup_export_path():
    return _timestamped_export_path(full_backup_dir(), FULL_BACKUP_FILE)


def list_full_backup_files():
    return list_backup_files(full_backup_dir(), [".ctfull", ".ctp", ".shva", ".ctlist"])


def revocation_backup_dir():
    return admin_export_dir("Revocation Jsons")


def revocation_export_path():
    return _timestamped_export_path(revocation_backup_dir(), REVOKED_EXPORT_FILE)


def list_revocation_backup_files():
    return list_backup_files(revocation_backup_dir(), [".json", ".txt"])


def license_export_dir():
    return admin_export_dir("License Exports")


def license_export_path():
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return os.path.join(license_export_dir(), f"licenses_export_{stamp}.csv")


def github_config_path():
    return file_path(GITHUB_CONFIG_FILE)


def load_github_upload_config():
    data = load_json(github_config_path(), {})
    merged = dict(DEFAULT_GITHUB_UPLOAD)
    if isinstance(data, dict):
        for key in ("owner", "repo", "branch", "path"):
            value = str(data.get(key, "")).strip()
            if value:
                merged[key] = value
    return merged


def save_github_upload_config(data):
    clean = {}
    for key in ("owner", "repo", "branch", "path"):
        clean[key] = str(data.get(key, DEFAULT_GITHUB_UPLOAD.get(key, ""))).strip()
    save_json(github_config_path(), clean)


def build_github_raw_url(owner, repo, branch, path):
    owner = str(owner).strip().strip("/")
    repo = str(repo).strip().strip("/")
    branch = str(branch).strip().strip("/") or "main"
    path = str(path).strip().lstrip("/")
    if not owner or not repo or not path:
        return ""
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def info_popup(title, message):
    content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
    lbl = Label(
        text=message,
        color=get_color_from_hex(TEXT),
        halign="left",
        valign="top",
        text_size=(dp(300), None),
        size_hint_y=None,
    )
    lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", max(val[1], dp(80))))
    btn = RoundedButton(
        text="OK",
        size_hint_y=None,
        height=dp(46),
        bg_hex=GREEN,
    )
    content.add_widget(lbl)
    content.add_widget(btn)
    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.9, 0.6),
        separator_color=get_color_from_hex(GREEN),
        background_color=get_color_from_hex(CARD),
    )
    btn.bind(on_release=popup.dismiss)
    popup.open()


def copy_to_clipboard(label, value):
    Clipboard.copy(value or "")
    info_popup("Copied", f"{label} copied to clipboard.")


def paste_clipboard_into(widget):
    try:
        widget.text = Clipboard.paste() or ""
    except Exception as e:
        info_popup("Paste failed", str(e))


def paste_clipboard_into(widget):
    try:
        widget.text = Clipboard.paste() or ""
    except Exception as e:
        info_popup("Paste failed", str(e))



def _rewrite_default_authority_files():
    priv_path = file_path(PRIVATE_KEY_FILE)
    pub_path = file_path(PUBLIC_KEY_FILE)
    os.makedirs(os.path.dirname(priv_path), exist_ok=True)
    with open(priv_path, 'wb') as f:
        f.write(DEFAULT_AUTHORITY_PRIVATE_PEM.encode('utf-8'))
    with open(pub_path, 'wb') as f:
        f.write(DEFAULT_AUTHORITY_PUBLIC_PEM.encode('utf-8'))


def _stash_corrupt_authority_file(path):
    try:
        if os.path.exists(path):
            stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            os.replace(path, path + f'.corrupt_{stamp}')
    except Exception:
        pass


def load_existing_keypair():
    ensure_default_authority_files()
    priv_path = file_path(PRIVATE_KEY_FILE)
    pub_path = file_path(PUBLIC_KEY_FILE)
    if not (os.path.exists(priv_path) and os.path.exists(pub_path)):
        return None, None

    try:
        with open(priv_path, 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
        with open(pub_path, 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
        return public_key, private_key
    except Exception:
        _stash_corrupt_authority_file(priv_path)
        _stash_corrupt_authority_file(pub_path)
        try:
            _rewrite_default_authority_files()
            with open(priv_path, 'rb') as f:
                private_key = rsa.PrivateKey.load_pkcs1(f.read())
            with open(pub_path, 'rb') as f:
                public_key = rsa.PublicKey.load_pkcs1(f.read())
            return public_key, private_key
        except Exception:
            return None, None


def initialize_authority_keypair():
    ensure_default_authority_files()
    return load_existing_keypair()


def _pbkdf(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=32)


def _xor_stream(key: bytes, data: bytes) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < len(data):
        block = hashlib.sha256(key + counter.to_bytes(4, "big")).digest()
        take = min(len(block), len(data) - len(out))
        chunk = data[len(out):len(out)+take]
        out.extend(bytes(a ^ b for a, b in zip(chunk, block[:take])))
        counter += 1
    return bytes(out)



def build_secure_backup_blob(password: str, bundle_type: str, payload: dict):
    if not password:
        raise ValueError("Backup password is required.")
    raw_payload = {
        "schema": 2,
        "app": BACKUP_BUNDLE_APP,
        "bundle_type": bundle_type,
        "exported_at": utc_now_iso(),
        "payload": payload,
    }
    raw = canonical_json(raw_payload)
    salt = os.urandom(16)
    enc_key = _pbkdf(password, salt)
    ciphertext = _xor_stream(enc_key, raw)
    mac = hmac.new(enc_key, salt + ciphertext, hashlib.sha256).digest()
    bundle = {
        "schema": 2,
        "app": BACKUP_BUNDLE_APP,
        "bundle_type": bundle_type,
        "salt": base64.urlsafe_b64encode(salt).decode("ascii"),
        "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),
        "mac": base64.urlsafe_b64encode(mac).decode("ascii"),
    }
    return json.dumps(bundle, indent=2)


def parse_secure_backup_blob(blob_text: str, password: str):
    if not blob_text.strip():
        raise ValueError("Backup text is empty.")
    if not password:
        raise ValueError("Backup password is required.")
    bundle = json.loads(blob_text)
    salt = base64.urlsafe_b64decode(bundle["salt"].encode("ascii"))
    ciphertext = base64.urlsafe_b64decode(bundle["ciphertext"].encode("ascii"))
    mac = base64.urlsafe_b64decode(bundle["mac"].encode("ascii"))
    enc_key = _pbkdf(password, salt)
    expected = hmac.new(enc_key, salt + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError("Backup password is incorrect or backup is corrupted.")
    raw = _xor_stream(enc_key, ciphertext)
    data = json.loads(raw.decode("utf-8"))
    if isinstance(data, dict) and "payload" in data and "bundle_type" in data:
        return data
    legacy_payload = {}
    if "private_key_pem" in data:
        legacy_payload["private_key_pem"] = data.get("private_key_pem", "")
    if "public_key_pem" in data:
        legacy_payload["public_key_pem"] = data.get("public_key_pem", "")
    if "licenses" in data:
        legacy_payload["licenses"] = data.get("licenses", [])
    if "revoked_bundle" in data:
        legacy_payload["revoked_bundle"] = data.get("revoked_bundle", {})
    return {
        "schema": data.get("schema", 1),
        "app": data.get("app", BACKUP_BUNDLE_APP),
        "bundle_type": "legacy_full_backup",
        "exported_at": data.get("exported_at", ""),
        "payload": legacy_payload,
    }


def build_authority_backup_blob(password: str):
    public_key, private_key = load_existing_keypair()
    if not public_key or not private_key:
        raise ValueError("No authority loaded. Initialize or import authority first.")
    payload = {
        "private_key_pem": private_key.save_pkcs1("PEM").decode("utf-8"),
        "public_key_pem": public_key.save_pkcs1("PEM").decode("utf-8"),
    }
    return build_secure_backup_blob(password, "authority_only", payload)


def build_license_list_backup_blob(password: str, records):
    payload = {
        "licenses": records,
    }
    return build_secure_backup_blob(password, "license_list_only", payload)


def build_full_backup_blob(password: str, records):
    public_key, private_key = load_existing_keypair()
    if not public_key or not private_key:
        raise ValueError("No authority loaded. Initialize or import authority first.")
    revoked_bundle = build_revocation_bundle(records, private_key)
    payload = {
        "private_key_pem": private_key.save_pkcs1("PEM").decode("utf-8"),
        "public_key_pem": public_key.save_pkcs1("PEM").decode("utf-8"),
        "licenses": records,
        "revoked_bundle": revoked_bundle,
    }
    return build_secure_backup_blob(password, "full_backup", payload)


def sign_payload(private_key, payload_dict):
    sig = rsa.sign(canonical_json(payload_dict), private_key, "SHA-256")
    return base64.urlsafe_b64encode(sig).decode("ascii")


def verify_signature(public_key, payload_dict, sig_b64):
    try:
        sig = base64.urlsafe_b64decode(sig_b64.encode("ascii"))
        rsa.verify(canonical_json(payload_dict), sig, public_key)
        return True
    except Exception:
        return False


def encode_activation_code(payload_dict, signature_b64):
    blob = {"p": payload_dict, "s": signature_b64}
    raw = canonical_json(blob)
    compressed = zlib.compress(raw, level=9)
    token = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    chunks = textwrap.wrap(token, 24)
    return "SYN6A-" + ".".join(chunks)


def decode_activation_code(code):
    cleaned = code.strip().replace("\n", "").replace(" ", "")
    if cleaned.startswith("SYN6A-") or cleaned.startswith("CTP6A-"):
        cleaned = cleaned[6:]
    cleaned = cleaned.replace(".", "")
    cleaned += "=" * ((4 - len(cleaned) % 4) % 4)
    raw = base64.urlsafe_b64decode(cleaned.encode("ascii"))
    data = json.loads(zlib.decompress(raw).decode("utf-8"))
    return data["p"], data["s"]


def build_revocation_bundle(records, private_key):
    revoked_ids = sorted([r["license_id"] for r in records if r.get("status") == "revoked"])
    payload = {
        "app": "synapse_by_shv",
        "version": 1,
        "updated_at": utc_now_iso(),
        "revoked_ids": revoked_ids,
    }
    signature = sign_payload(private_key, payload)
    return {"payload": payload, "signature": signature}


class LicenseStore:
    def __init__(self):
        self.path = file_path(LICENSE_DB_FILE)
        self.records = load_json(self.path, [])

    def save(self):
        save_json(self.path, self.records)

    def add(self, record):
        self.records.insert(0, record)
        self.save()

    def update(self, license_id, updater):
        for rec in self.records:
            if rec["license_id"] == license_id:
                updater(rec)
                self.save()
                return True
        return False

    def delete(self, license_id):
        before = len(self.records)
        self.records = [rec for rec in self.records if rec.get("license_id") != license_id]
        changed = len(self.records) != before
        if changed:
            self.save()
        return changed

    def delete_many(self, license_ids):
        wanted = {str(x) for x in (license_ids or []) if str(x)}
        if not wanted:
            return 0
        before = len(self.records)
        self.records = [rec for rec in self.records if rec.get("license_id") not in wanted]
        removed = before - len(self.records)
        if removed:
            self.save()
        return removed

    def find(self, license_id):
        for rec in self.records:
            if rec["license_id"] == license_id:
                return rec
        return None



class RoundedButton(Button):
    def __init__(self, bg_hex=GREEN, text_color=None, radius=16, border_hex=None, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        super().__init__(**kwargs)
        self._bg_hex = bg_hex
        self._radius = dp(radius)
        self._border_hex = border_hex or self._derive_neon_border(bg_hex)
        self._inset = dp(2)
        if text_color is None:
            text_color = (0, 0, 0, 1) if bg_hex == GREEN else (1, 1, 1, 1)
        self.color = text_color
        self.bold = True
        with self.canvas.before:
            Color(rgba=get_color_from_hex(self._border_hex))
            self._border_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
            Color(rgba=get_color_from_hex(bg_hex))
            self._rounded_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[max(dp(4), self._radius - self._inset)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _derive_neon_border(self, bg_hex):
        color = str(bg_hex or '').lower()
        if color == str(RED).lower():
            return '#ff8f8f'
        if color == str(BLUE).lower():
            return '#6ed1ff'
        if color == str(PURPLE).lower():
            return '#d39cff'
        if color == str(ORANGE).lower():
            return '#ffbf73'
        if color == str(GREEN).lower():
            return '#8cff7c'
        return '#52ffd9'

    def _update_bg(self, *_):
        self._border_bg.pos = self.pos
        self._border_bg.size = self.size
        self._border_bg.radius = [self._radius]
        self._rounded_bg.pos = (self.x + self._inset, self.y + self._inset)
        self._rounded_bg.size = (max(0, self.width - self._inset * 2), max(0, self.height - self._inset * 2))
        self._rounded_bg.radius = [max(dp(4), self._radius - self._inset)]


class SectionCard(BoxLayout):
    def __init__(self, title, subtitle="", **kwargs):
        super().__init__(orientation="vertical", spacing=dp(8), padding=dp(12), size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter("height"))
        from kivy.graphics import Color, RoundedRectangle
        with self.canvas.before:
            Color(rgba=get_color_from_hex(CARD))
            self._bg = RoundedRectangle(radius=[18], pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        title_lbl = Label(
            text=title,
            bold=True,
            color=get_color_from_hex(TEXT),
            font_size='20sp',
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle",
            text_size=(dp(320), None),
        )
        self.add_widget(title_lbl)

        if subtitle:
            subtitle_lbl = Label(
                text=subtitle,
                color=get_color_from_hex(SUBTEXT),
                size_hint_y=None,
                halign="left",
                valign="middle",
                text_size=(dp(320), None),
            )
            subtitle_lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(18), val[1])))
            self.add_widget(subtitle_lbl)

    def _update_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size


def make_label(text, color=TEXT, bold=False, height=dp(24)):
    return Label(
        text=text,
        color=get_color_from_hex(color),
        bold=bold,
        size_hint_y=None,
        height=height,
        halign="left",
        valign="middle",
        text_size=(dp(320), None),
    )


def make_input(hint="", multiline=False, readonly=False, password=False):
    return TextInput(
        hint_text=hint,
        multiline=multiline,
        readonly=readonly,
        password=password,
        size_hint_y=None,
        height=dp(46) if not multiline else dp(100),
        background_color=get_color_from_hex("#111111"),
        foreground_color=get_color_from_hex(TEXT),
        cursor_color=(1, 0, 0, 1),
        cursor_width='2sp',
        selection_color=(0.22, 0.68, 0.95, 0.35),
        hint_text_color=get_color_from_hex(SUBTEXT),
        padding=[dp(10), dp(12), dp(10), dp(12)],
    )


def make_button(text, color=GREEN):
    return RoundedButton(
        text=text,
        size_hint_y=None,
        height=dp(46),
        bg_hex=color,
        text_color=(0, 0, 0, 1) if color == GREEN else (1, 1, 1, 1),
    )


def make_nav_button(text):
    btn = RoundedButton(
        text=text,
        size_hint=(1, None),
        height=dp(42),
        bg_hex="#182432",
        text_color=get_color_from_hex(TEXT),
    )
    return btn


class LicenseManagerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = LicenseStore()
        self.public_key = None
        self.private_key = None
        self._load_error = ""
        try:
            self.public_key, self.private_key = load_existing_keypair()
        except Exception as e:
            self._load_error = str(e)
        self.github_config = load_github_upload_config()
        self._last_license_id = ""
        self.add_widget(BoxLayout())
        Clock.schedule_once(self.safe_build_ui, 0)

    def safe_build_ui(self, *_):
        try:
            self.build_ui()
        except Exception as e:
            self.show_build_error(e)

    def show_build_error(self, error):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        card = SectionCard('Synapse Licensing Error', 'The APK prevented this module from loading normally. Use Retry after the patch or backup/import authority again if old key files were corrupted.')
        err_text = str(error or self._load_error or 'Unknown error')
        card.add_widget(make_label('Details: ' + err_text[:500], color=RED, height=dp(72)))
        if self._load_error:
            card.add_widget(make_label('Authority load note: ' + self._load_error[:500], color=ORANGE, height=dp(72)))
        retry_btn = make_button('Retry Loading', GREEN)
        retry_btn.bind(on_release=lambda *_: self.safe_build_ui())
        card.add_widget(retry_btn)
        root.add_widget(card)
        self.add_widget(root)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))

        top_bar = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        title_lbl = Label(
            text="Synapse Licensing Interface",
            color=get_color_from_hex(TEXT),
            bold=True,
            halign="left",
            valign="middle",
            font_size='18sp',
        )
        title_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        top_bar.add_widget(title_lbl)
        exit_btn = make_button("EXIT", RED)
        exit_btn.size_hint_x = None
        exit_btn.width = dp(100)
        exit_btn.bind(on_release=lambda *_: App.get_running_app().stop())
        top_bar.add_widget(exit_btn)
        root.add_widget(top_bar)

        nav_grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(92))
        self.tab_buttons = {}
        self.tab_titles = {
            "dashboard": "Dashboard",
            "authority": "Authority",
            "generate": "Generate",
            "licenses": "Licenses",
            "revocations": "Revocations",
        }
        for key in ("dashboard", "authority", "generate", "licenses", "revocations"):
            btn = make_nav_button(self.tab_titles[key])
            btn.bind(on_release=lambda *_ , tab_key=key: self.switch_tab(tab_key))
            self.tab_buttons[key] = btn
            nav_grid.add_widget(btn)
        root.add_widget(nav_grid)

        self.content_host = BoxLayout()
        root.add_widget(self.content_host)
        self.add_widget(root)

        self.tab_views = {
            "dashboard": self.build_dashboard_view(),
            "authority": self.build_authority_view(),
            "generate": self.build_generate_view(),
            "licenses": self.build_licenses_view(),
            "revocations": self.build_revocation_view(),
        }

        self.switch_tab("dashboard")
        self.update_authority_status()
        self.refresh_dashboard()
        self.refresh_license_list()
        self.refresh_revocation_box()

    def switch_tab(self, key):
        if not hasattr(self, "content_host"):
            return
        self.content_host.clear_widgets()
        view = self.tab_views.get(key)
        if view is not None:
            self.content_host.add_widget(view)

        active_bg = get_color_from_hex(GREEN)
        inactive_bg = get_color_from_hex("#141a22")
        active_text = (0, 0, 0, 1)
        inactive_text = get_color_from_hex(TEXT)
        for btn_key, btn in self.tab_buttons.items():
            if btn_key == key:
                btn.background_color = active_bg
                btn.color = active_text
            else:
                btn.background_color = inactive_bg
                btn.color = inactive_text

    def switch_license_subtab(self, key):
        if not hasattr(self, 'license_subtab_host'):
            return
        self.license_subtab_host.clear_widgets()
        if key == 'tools':
            self.license_subtab_host.add_widget(self.license_tools_view)
        else:
            self.license_subtab_host.add_widget(self.license_list_view)
        active_bg = get_color_from_hex(GREEN)
        inactive_bg = get_color_from_hex("#141a22")
        active_text = (0, 0, 0, 1)
        inactive_text = get_color_from_hex(TEXT)
        for btn_key, btn in getattr(self, 'license_subtab_buttons', {}).items():
            if btn_key == key:
                btn.background_color = active_bg
                btn.color = active_text
            else:
                btn.background_color = inactive_bg
                btn.color = inactive_text

    def build_dashboard_view(self):
        scroll = ScrollView(do_scroll_x=False)
        self.dashboard_box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])
        self.dashboard_box.bind(minimum_height=self.dashboard_box.setter("height"))
        scroll.add_widget(self.dashboard_box)
        return scroll


    def build_authority_view(self):
        scroll = ScrollView(do_scroll_x=False)
        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])
        box.bind(minimum_height=box.setter("height"))

        card = SectionCard("Authority only backup", "Share the same signing authority across apps without replacing this app's local license list.")
        self.auth_status_label = make_label("", color=SUBTEXT, height=dp(44))
        card.add_widget(self.auth_status_label)

        card.add_widget(make_label("Backup Password"))
        self.backup_password_input = make_input("Enter backup password")
        card.add_widget(self.backup_password_input)

        row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        init_btn = make_button("Initialize Authority", UI_CYAN)
        copy_pub_btn = make_button("Copy Public Key PEM", UI_CYAN)
        row1.add_widget(init_btn)
        row1.add_widget(copy_pub_btn)
        init_btn.bind(on_release=lambda *_: self.initialize_authority())
        copy_pub_btn.bind(on_release=lambda *_: self.copy_public_key())
        card.add_widget(row1)

        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        gen_backup_btn = make_button("Generate Authority Backup", GREEN)
        copy_backup_btn = make_button("Copy Authority Backup", UI_CYAN)
        row2.add_widget(gen_backup_btn)
        row2.add_widget(copy_backup_btn)
        gen_backup_btn.bind(on_release=lambda *_: self.generate_authority_backup())
        copy_backup_btn.bind(on_release=lambda *_: copy_to_clipboard("Authority backup", getattr(self, "backup_output", make_input()).text if hasattr(self, "backup_output") else ""))
        card.add_widget(row2)

        self.backup_output = make_input("Generated encrypted authority-only backup will appear here", multiline=True, readonly=True)
        self.backup_output.height = dp(220)
        card.add_widget(self.backup_output)

        row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_backup_btn = make_button("Save Authority File", UI_CYAN)
        import_backup_btn = make_button("Import Authority", GREEN)
        row3.add_widget(save_backup_btn)
        row3.add_widget(import_backup_btn)
        save_backup_btn.bind(on_release=lambda *_: self.save_authority_backup())
        import_backup_btn.bind(on_release=lambda *_: self.import_authority_backup())
        card.add_widget(row3)

        card.add_widget(make_label("Paste Authority Backup To Import"))
        self.import_backup_input = make_input("Paste encrypted authority backup here", multiline=True)
        self.import_backup_input.height = dp(180)
        card.add_widget(self.import_backup_input)

        row4 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        paste_btn = make_button("Paste", UI_CYAN)
        import_file_btn = make_button("Import Auth File", UI_CYAN)
        paste_btn.bind(on_release=lambda *_: self.paste_backup_from_clipboard())
        import_file_btn.bind(on_release=lambda *_: self.open_auth_file_picker())
        row4.add_widget(paste_btn)
        row4.add_widget(import_file_btn)
        card.add_widget(row4)
        box.add_widget(card)

        full_card = SectionCard("Full backup", "Back up authority + this app's local license list + a revocation snapshot in one encrypted file.")
        full_card.add_widget(make_label("Uses the same backup password above.", color=SUBTEXT, height=dp(28)))

        full_row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        gen_full_btn = make_button("Generate Full Backup", GREEN)
        copy_full_btn = make_button("Copy Full Backup", UI_CYAN)
        gen_full_btn.bind(on_release=lambda *_: self.generate_full_backup())
        copy_full_btn.bind(on_release=lambda *_: copy_to_clipboard("Full backup", getattr(self, "full_backup_output", make_input()).text if hasattr(self, "full_backup_output") else ""))
        full_row1.add_widget(gen_full_btn)
        full_row1.add_widget(copy_full_btn)
        full_card.add_widget(full_row1)

        self.full_backup_output = make_input("Generated encrypted full backup will appear here", multiline=True, readonly=True)
        self.full_backup_output.height = dp(220)
        full_card.add_widget(self.full_backup_output)

        full_row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_full_btn = make_button("Save Full Backup", UI_CYAN)
        import_full_btn = make_button("Import Full Backup", GREEN)
        save_full_btn.bind(on_release=lambda *_: self.save_full_backup())
        import_full_btn.bind(on_release=lambda *_: self.import_full_backup())
        full_row2.add_widget(save_full_btn)
        full_row2.add_widget(import_full_btn)
        full_card.add_widget(full_row2)

        full_card.add_widget(make_label("Paste Full Backup To Import"))
        self.import_full_backup_input = make_input("Paste encrypted full backup here", multiline=True)
        self.import_full_backup_input.height = dp(180)
        full_card.add_widget(self.import_full_backup_input)

        full_row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        paste_full_btn = make_button("Paste", UI_CYAN)
        import_full_file_btn = make_button("Import Full File", UI_CYAN)
        paste_full_btn.bind(on_release=lambda *_: self.paste_full_backup_from_clipboard())
        import_full_file_btn.bind(on_release=lambda *_: self.open_full_backup_file_picker())
        full_row3.add_widget(paste_full_btn)
        full_row3.add_widget(import_full_file_btn)
        full_card.add_widget(full_row3)
        box.add_widget(full_card)

        scroll.add_widget(box)
        return scroll

    def build_generate_view(self):
        scroll = ScrollView(do_scroll_x=False)
        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])
        box.bind(minimum_height=box.setter("height"))

        card = SectionCard("Generate activation code", "Create device-bound Demo / Pro licenses for Synapse")
        self.device_input = make_input("Device Code (ex: SYN-DEV-1234ABCD5678)")
        self.tier_spinner = Spinner(text="pro", values=("demo", "pro"), size_hint_y=None, height=dp(46))
        self.source_spinner = Spinner(text="crypto", values=("crypto", "bank", "promo", "partner", "personal", "test"), size_hint_y=None, height=dp(46))
        self.customer_name_input = make_input("Customer name")
        self.customer_email_input = make_input("Customer email (optional)")
        self.label_input = make_input("Internal label / tag (optional)")
        self.note_input = make_input("Notes (optional)", multiline=True)
        self.expiry_input = make_input("Expiry date YYYY-MM-DD (optional)")

        for title, widget in [
            ("Device Code", self.device_input),
            ("Tier", self.tier_spinner),
            ("Payment Method", self.source_spinner),
            ("Customer Name", self.customer_name_input),
            ("Customer Email", self.customer_email_input),
            ("Label", self.label_input),
            ("Note", self.note_input),
            ("Expiry", self.expiry_input),
        ]:
            card.add_widget(make_label(title))
            card.add_widget(widget)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        gen_btn = make_button("Generate License")
        clear_btn = make_button("Clear", UI_CYAN)
        gen_btn.bind(on_release=lambda *_: self.generate_license())
        clear_btn.bind(on_release=lambda *_: self.clear_generate_form())
        row.add_widget(gen_btn)
        row.add_widget(clear_btn)
        card.add_widget(row)

        test_btn = make_button("Generate 7-Day Test Pro", UI_CYAN)
        test_btn.bind(on_release=lambda *_: self.generate_test_license())
        card.add_widget(test_btn)

        self.generated_code_input = make_input("Generated activation code will appear here", multiline=True, readonly=True)
        self.generated_code_input.height = dp(160)
        card.add_widget(make_label("Activation Code"))
        card.add_widget(self.generated_code_input)

        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        copy_btn = make_button("Copy Code", UI_CYAN)
        copy_id_btn = make_button("Copy License ID", UI_CYAN)
        copy_btn.bind(on_release=lambda *_: copy_to_clipboard("Activation code", self.generated_code_input.text))
        copy_id_btn.bind(on_release=lambda *_: copy_to_clipboard("License ID", self._last_license_id))
        row2.add_widget(copy_btn)
        row2.add_widget(copy_id_btn)
        card.add_widget(row2)

        box.add_widget(card)
        scroll.add_widget(box)
        return scroll


    def build_licenses_view(self):
        root = BoxLayout(orientation='vertical', spacing=dp(8), padding=[0, dp(4), 0, dp(4)])

        tab_row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(46))
        self.license_subtab_buttons = {}
        for key, title in (("tools", "Tools"), ("list", "License List")):
            btn = make_nav_button(title)
            btn.bind(on_release=lambda *_ , tab_key=key: self.switch_license_subtab(tab_key))
            self.license_subtab_buttons[key] = btn
            tab_row.add_widget(btn)
        root.add_widget(tab_row)

        self.license_subtab_host = BoxLayout()
        root.add_widget(self.license_subtab_host)

        tools_scroll = ScrollView(do_scroll_x=False, scroll_type=['bars', 'content'], bar_width=dp(6))
        tools_outer = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])
        tools_outer.bind(minimum_height=tools_outer.setter('height'))

        backup_card = SectionCard("License list backup", "Back up or restore only this app's local license list. Shared authority stays untouched.")
        backup_row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        gen_backup_btn = make_button("Generate License Backup", GREEN)
        copy_backup_btn = make_button("Copy License Backup", UI_CYAN)
        gen_backup_btn.bind(on_release=lambda *_: self.generate_license_list_backup())
        copy_backup_btn.bind(on_release=lambda *_: copy_to_clipboard("License list backup", getattr(self, "license_backup_output", make_input()).text if hasattr(self, "license_backup_output") else ""))
        backup_row1.add_widget(gen_backup_btn)
        backup_row1.add_widget(copy_backup_btn)
        backup_card.add_widget(backup_row1)

        self.license_backup_output = make_input("Generated encrypted license-list backup will appear here", multiline=True, readonly=True)
        self.license_backup_output.height = dp(160)
        backup_card.add_widget(self.license_backup_output)

        backup_row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_backup_btn = make_button("Save License Backup", UI_CYAN)
        import_backup_btn = make_button("Import License Backup", GREEN)
        save_backup_btn.bind(on_release=lambda *_: self.save_license_list_backup())
        import_backup_btn.bind(on_release=lambda *_: self.import_license_list_backup())
        backup_row2.add_widget(save_backup_btn)
        backup_row2.add_widget(import_backup_btn)
        backup_card.add_widget(backup_row2)

        backup_card.add_widget(make_label("Paste License Backup To Import"))
        self.import_license_backup_input = make_input("Paste encrypted license-list backup here", multiline=True)
        self.import_license_backup_input.height = dp(140)
        backup_card.add_widget(self.import_license_backup_input)

        backup_row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        paste_btn = make_button("Paste", UI_CYAN)
        import_file_btn = make_button("Import Backup File", UI_CYAN)
        paste_btn.bind(on_release=lambda *_: self.paste_license_backup_from_clipboard())
        import_file_btn.bind(on_release=lambda *_: self.open_license_backup_file_picker())
        backup_row3.add_widget(paste_btn)
        backup_row3.add_widget(import_file_btn)
        backup_card.add_widget(backup_row3)
        tools_outer.add_widget(backup_card)
        tools_scroll.add_widget(tools_outer)
        self.license_tools_view = tools_scroll

        search_card = SectionCard("License search", "Search, filter, export, or delete test keys")
        self.search_input = make_input("Search by ID / customer / email / device / label / payment")
        self.search_input.height = dp(42)
        self.search_input.bind(text=lambda *_: self.refresh_license_list())
        search_card.add_widget(self.search_input)

        filters = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(42))
        self.license_status_spinner = Spinner(text="all", values=("all", "active", "revoked"), size_hint_y=None, height=dp(42))
        self.license_tier_spinner = Spinner(text="all", values=("all", "demo", "pro"), size_hint_y=None, height=dp(42))
        self.license_source_spinner = Spinner(text="all", values=("all", "crypto", "bank", "promo", "partner", "personal", "test"), size_hint_y=None, height=dp(42))
        self.license_sort_spinner = Spinner(text="newest", values=("newest", "oldest", "tier", "status"), size_hint_y=None, height=dp(42))
        self.license_status_spinner.bind(text=lambda *_: self.refresh_license_list())
        self.license_tier_spinner.bind(text=lambda *_: self.refresh_license_list())
        self.license_source_spinner.bind(text=lambda *_: self.refresh_license_list())
        self.license_sort_spinner.bind(text=lambda *_: self.refresh_license_list())
        filters.add_widget(self.license_status_spinner)
        filters.add_widget(self.license_tier_spinner)
        filters.add_widget(self.license_source_spinner)
        filters.add_widget(self.license_sort_spinner)
        search_card.add_widget(filters)

        actions = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(44))
        export_btn = make_button("Export Visible CSV", UI_CYAN)
        delete_filtered_btn = make_button("Delete Visible", RED)
        export_btn.bind(on_release=lambda *_: self.export_visible_licenses_csv())
        delete_filtered_btn.bind(on_release=lambda *_: self.confirm_delete_visible_licenses())
        actions.add_widget(export_btn)
        actions.add_widget(delete_filtered_btn)
        search_card.add_widget(actions)
        search_card.add_widget(make_label("Tip: set Source = test before using Delete Visible.", color=SUBTEXT, height=dp(24)))

        list_scroll = ScrollView(do_scroll_x=False, scroll_type=['bars', 'content'], bar_width=dp(6))
        list_outer = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])
        list_outer.bind(minimum_height=list_outer.setter('height'))
        list_outer.add_widget(search_card)
        results_card = SectionCard("License list", "Tap Details to inspect, copy, revoke, or restore.")
        self.license_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])
        self.license_box.bind(minimum_height=self.license_box.setter("height"))
        results_card.add_widget(self.license_box)
        list_outer.add_widget(results_card)
        list_scroll.add_widget(list_outer)
        self.license_list_view = list_scroll

        self.switch_license_subtab('list')
        return root

    def build_revocation_view(self):
        scroll = ScrollView(do_scroll_x=False)
        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])
        box.bind(minimum_height=box.setter("height"))

        card = SectionCard("Revocation export", "Generate, save, copy, or manually import the signed revoked list for the customer app.")
        export_btn = make_button("Generate Signed Revocation File")
        export_btn.bind(on_release=lambda *_: self.refresh_revocation_box())
        card.add_widget(export_btn)

        self.revocation_output = make_input("", multiline=True, readonly=True)
        self.revocation_output.height = dp(220)
        card.add_widget(self.revocation_output)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_btn = make_button("Save synapse_revoked_licenses.json", UI_CYAN)
        copy_btn = make_button("Copy JSON", UI_CYAN)
        save_btn.bind(on_release=lambda *_: self.save_revocation_bundle())
        copy_btn.bind(on_release=lambda *_: copy_to_clipboard("Revocation JSON", self.revocation_output.text))
        row.add_widget(save_btn)
        row.add_widget(copy_btn)
        card.add_widget(row)

        pub_btn = make_button("Copy Public Key PEM", UI_CYAN)
        pub_btn.bind(on_release=lambda *_: self.copy_public_key())
        card.add_widget(pub_btn)

        card.add_widget(make_label("Paste Revocation JSON To Import"))
        self.import_revocation_input = make_input("Paste signed revocation JSON here", multiline=True)
        self.import_revocation_input.height = dp(180)
        card.add_widget(self.import_revocation_input)

        row_import = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(46))
        paste_btn = make_button("Paste", UI_CYAN)
        import_btn = make_button("Import JSON", GREEN)
        import_file_btn = make_button("Import File", UI_CYAN)
        paste_btn.bind(on_release=lambda *_: self.paste_revocation_from_clipboard())
        import_btn.bind(on_release=lambda *_: self.import_revocation_bundle())
        import_file_btn.bind(on_release=lambda *_: self.open_revocation_file_picker())
        row_import.add_widget(paste_btn)
        row_import.add_widget(import_btn)
        row_import.add_widget(import_file_btn)
        card.add_widget(row_import)
        box.add_widget(card)

        gh = SectionCard("GitHub upload", "Store the revocation JSON online so customer apps can read the fixed raw URL")
        self.github_owner_input = make_input("GitHub owner / username")
        self.github_repo_input = make_input("Repository name")
        self.github_branch_input = make_input("Branch", readonly=False)
        self.github_path_input = make_input("Path inside repo (ex: synapse_revoked_licenses.json)")
        self.github_token_input = make_input("GitHub token with contents:write access")
        self.github_raw_url_input = make_input("Raw URL", readonly=True)

        self.github_owner_input.text = self.github_config.get('owner', '')
        self.github_repo_input.text = self.github_config.get('repo', '')
        self.github_branch_input.text = self.github_config.get('branch', 'main') or 'main'
        self.github_path_input.text = self.github_config.get('path', REVOKED_EXPORT_FILE) or REVOKED_EXPORT_FILE
        self.github_token_input.text = self.github_config.get('token', '')

        for title, widget in [
            ("Owner", self.github_owner_input),
            ("Repo", self.github_repo_input),
            ("Branch", self.github_branch_input),
            ("Path", self.github_path_input),
            ("Token", self.github_token_input),
            ("Raw URL", self.github_raw_url_input),
        ]:
            gh.add_widget(make_label(title))
            gh.add_widget(widget)
            if widget is self.github_token_input:
                paste_token_btn = make_button("Paste Token", UI_CYAN)
                paste_token_btn.height = dp(40)
                paste_token_btn.bind(on_release=lambda *_: paste_clipboard_into(self.github_token_input))
                gh.add_widget(paste_token_btn)
            if widget is self.github_token_input:
                paste_token_btn = make_button("Paste Token", UI_CYAN)
                paste_token_btn.height = dp(40)
                paste_token_btn.bind(on_release=lambda *_: paste_clipboard_into(self.github_token_input))
                gh.add_widget(paste_token_btn)

        for widget in (self.github_owner_input, self.github_repo_input, self.github_branch_input, self.github_path_input):
            widget.bind(text=self.update_github_raw_url)
        self.update_github_raw_url()

        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_cfg_btn = make_button("Save Upload Settings", UI_CYAN)
        upload_btn = make_button("Upload Revocation JSON", GREEN)
        save_cfg_btn.bind(on_release=lambda *_: self.save_github_settings())
        upload_btn.bind(on_release=lambda *_: self.upload_revocation_to_github())
        row2.add_widget(save_cfg_btn)
        row2.add_widget(upload_btn)
        gh.add_widget(row2)
        box.add_widget(gh)

        scroll.add_widget(box)
        return scroll

    def update_authority_status(self):
        if hasattr(self, "auth_status_label"):
            if self.public_key and self.private_key:
                self.auth_status_label.text = f"Authority loaded. Public key fingerprint: {hashlib.sha256(self.public_key.save_pkcs1('PEM')).hexdigest()[:16].upper()}"
                self.auth_status_label.color = get_color_from_hex(GREEN)
            else:
                self.auth_status_label.text = "No authority loaded. Import your backup or initialize authority."
                self.auth_status_label.color = get_color_from_hex(RED)

    def require_authority(self):
        if self.public_key and self.private_key:
            return True
        info_popup("Authority required", "No signing authority is loaded. Import your authority backup or initialize authority first.")
        return False

    def initialize_authority(self):
        if self.public_key and self.private_key:
            info_popup("Authority exists", "This device already has an authority loaded.")
            return
        try:
            self.public_key, self.private_key = initialize_authority_keypair()
            self.update_authority_status()
            self.refresh_dashboard()
            info_popup("Authority initialized", "A new signing authority was created on this device. Back it up immediately.")
        except Exception as e:
            info_popup("Initialize failed", str(e))


    def copy_public_key(self):
        if not self.require_authority():
            return
        copy_to_clipboard("Public key PEM", self.public_key.save_pkcs1("PEM").decode("utf-8"))

    def _refresh_everything(self):
        self.refresh_dashboard()
        self.refresh_license_list()
        self.refresh_revocation_box()

    def _write_authority_payload(self, payload):
        private_pem = str(payload.get("private_key_pem", "")).strip()
        public_pem = str(payload.get("public_key_pem", "")).strip()
        if not private_pem or not public_pem:
            raise ValueError("Backup does not contain a valid authority keypair.")
        with open(file_path(PRIVATE_KEY_FILE), "wb") as f:
            f.write(private_pem.encode("utf-8"))
        with open(file_path(PUBLIC_KEY_FILE), "wb") as f:
            f.write(public_pem.encode("utf-8"))
        self.public_key, self.private_key = load_existing_keypair()
        self.update_authority_status()

    def _write_license_payload(self, payload):
        records = payload.get("licenses", [])
        if not isinstance(records, list):
            raise ValueError("Backup does not contain a valid license list.")
        save_json(file_path(LICENSE_DB_FILE), records)
        self.store = LicenseStore()

    def _apply_revocation_bundle_to_store(self, bundle):
        if not isinstance(bundle, dict):
            raise ValueError("Revocation JSON is invalid.")
        payload = bundle.get("payload") if isinstance(bundle.get("payload"), dict) else bundle
        revoked_ids = payload.get("revoked_ids", []) if isinstance(payload, dict) else []
        revoked_ids = {str(x).strip() for x in revoked_ids if str(x).strip()}
        changed = False
        if revoked_ids:
            for rec in self.store.records:
                lid = str(rec.get("license_id", "")).strip()
                if lid in revoked_ids and rec.get("status") != "revoked":
                    rec["status"] = "revoked"
                    rec["revoked_at"] = utc_now_iso()
                    changed = True
            if changed:
                self.store.save()
        save_json(file_path(REVOKED_EXPORT_FILE), bundle)
        return len(revoked_ids), changed

    def _finish_authority_import(self, bundle):
        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}
        self._write_authority_payload(payload)
        self._refresh_everything()

    def _finish_license_list_import(self, bundle):
        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}
        self._write_license_payload(payload)
        self._refresh_everything()

    def _finish_full_backup_import(self, bundle):
        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}
        self._write_authority_payload(payload)
        self._write_license_payload(payload)
        revoked_bundle = payload.get("revoked_bundle", {})
        if revoked_bundle:
            self._apply_revocation_bundle_to_store(revoked_bundle)
        self._refresh_everything()

    def _paste_into_widget(self, widget, empty_message="There is no backup content in the clipboard."):
        try:
            pasted = Clipboard.paste() or ""
            if not pasted.strip():
                info_popup("Clipboard empty", empty_message)
                return
            widget.text = pasted
        except Exception as e:
            info_popup("Paste failed", str(e))

    def _open_backup_file_picker(self, title_text, folder, backup_files, on_select):
        if not backup_files:
            info_popup("No backup file found", f"No backup file was found in:\n{folder}")
            return

        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))
        title = Label(
            text=f"Select backup file from:\n{folder}",
            color=get_color_from_hex(TEXT),
            halign="left",
            valign="middle",
            text_size=(dp(300), None),
            size_hint_y=None,
        )
        title.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(48), val[1] + dp(8))))
        content.add_widget(title)

        scroll = ScrollView(do_scroll_x=False, size_hint=(1, 1))
        file_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        file_box.bind(minimum_height=file_box.setter("height"))

        popup = Popup(
            title=title_text,
            content=content,
            size_hint=(0.92, 0.8),
            separator_color=get_color_from_hex(GREEN),
            background_color=get_color_from_hex(CARD),
        )

        for path in backup_files:
            name = os.path.basename(path)
            try:
                stamp = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
            except Exception:
                stamp = "Unknown time"
            btn = RoundedButton(
                text=f"{name}\n{stamp}",
                size_hint_y=None,
                height=dp(68),
                halign="left",
                valign="middle",
                text_size=(dp(260), None),
                bg_hex="#182432",
                text_color=get_color_from_hex(TEXT),
            )
            btn.bind(on_release=lambda *_ , selected_path=path, pop=popup: on_select(selected_path, pop))
            file_box.add_widget(btn)

        scroll.add_widget(file_box)
        content.add_widget(scroll)

        close_btn = make_button("Close", RED)
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def generate_authority_backup(self):
        if not self.require_authority():
            return
        try:
            blob = build_authority_backup_blob(self.backup_password_input.text.strip())
            self.backup_output.text = blob
            info_popup("Backup generated", "Encrypted authority-only backup generated successfully.")
        except Exception as e:
            info_popup("Backup failed", str(e))

    def save_authority_backup(self):
        text = self.backup_output.text.strip() if hasattr(self, "backup_output") else ""
        if not text:
            info_popup("Nothing to save", "Generate an authority backup first.")
            return
        path = authority_backup_export_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        info_popup("Saved", f"Authority backup saved to:\n{path}")

    def import_authority_backup(self):
        try:
            blob_text = self.import_backup_input.text.strip()
            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())
            self._finish_authority_import(bundle)
            info_popup("Import successful", "Authority backup imported successfully. Local license list was not changed.")
        except Exception as e:
            info_popup("Import failed", str(e))

    def paste_backup_from_clipboard(self):
        self._paste_into_widget(self.import_backup_input)

    def open_auth_file_picker(self):
        self._open_backup_file_picker("Import Auth File", authority_backup_dir(), list_authority_backup_files(), self.import_authority_from_file)

    def import_authority_from_file(self, backup_path, popup=None):
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                blob_text = f.read().strip()
            if hasattr(self, "import_backup_input"):
                self.import_backup_input.text = blob_text
            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())
            self._finish_authority_import(bundle)
            if popup is not None:
                popup.dismiss()
            info_popup("Import successful", f"Authority file imported successfully from:\n{backup_path}\n\nLocal license list was not changed.")
        except Exception as e:
            info_popup("Import failed", str(e))

    def generate_license_list_backup(self):
        try:
            blob = build_license_list_backup_blob(self.backup_password_input.text.strip(), self.store.records)
            self.license_backup_output.text = blob
            info_popup("Backup generated", "Encrypted license-list backup generated successfully.")
        except Exception as e:
            info_popup("Backup failed", str(e))

    def save_license_list_backup(self):
        text = self.license_backup_output.text.strip() if hasattr(self, "license_backup_output") else ""
        if not text:
            info_popup("Nothing to save", "Generate a license-list backup first.")
            return
        path = license_list_backup_export_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        info_popup("Saved", f"License-list backup saved to:\n{path}")

    def import_license_list_backup(self):
        try:
            blob_text = self.import_license_backup_input.text.strip()
            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())
            self._finish_license_list_import(bundle)
            info_popup("Import successful", "License-list backup imported successfully. Authority keys were not changed.")
        except Exception as e:
            info_popup("Import failed", str(e))

    def paste_license_backup_from_clipboard(self):
        self._paste_into_widget(self.import_license_backup_input)

    def open_license_backup_file_picker(self):
        self._open_backup_file_picker("Import License Backup", license_list_backup_dir(), list_license_list_backup_files(), self.import_license_backup_from_file)

    def import_license_backup_from_file(self, backup_path, popup=None):
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                blob_text = f.read().strip()
            if hasattr(self, "import_license_backup_input"):
                self.import_license_backup_input.text = blob_text
            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())
            self._finish_license_list_import(bundle)
            if popup is not None:
                popup.dismiss()
            info_popup("Import successful", f"License-list backup imported successfully from:\n{backup_path}")
        except Exception as e:
            info_popup("Import failed", str(e))

    def generate_full_backup(self):
        if not self.require_authority():
            return
        try:
            blob = build_full_backup_blob(self.backup_password_input.text.strip(), self.store.records)
            self.full_backup_output.text = blob
            info_popup("Backup generated", "Encrypted full backup generated successfully.")
        except Exception as e:
            info_popup("Backup failed", str(e))

    def save_full_backup(self):
        text = self.full_backup_output.text.strip() if hasattr(self, "full_backup_output") else ""
        if not text:
            info_popup("Nothing to save", "Generate a full backup first.")
            return
        path = full_backup_export_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        info_popup("Saved", f"Full backup saved to:\n{path}")

    def import_full_backup(self):
        try:
            blob_text = self.import_full_backup_input.text.strip()
            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())
            self._finish_full_backup_import(bundle)
            info_popup("Import successful", "Full backup imported successfully.")
        except Exception as e:
            info_popup("Import failed", str(e))

    def paste_full_backup_from_clipboard(self):
        self._paste_into_widget(self.import_full_backup_input)

    def open_full_backup_file_picker(self):
        self._open_backup_file_picker("Import Full Backup", full_backup_dir(), list_full_backup_files(), self.import_full_backup_from_file)

    def import_full_backup_from_file(self, backup_path, popup=None):
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                blob_text = f.read().strip()
            if hasattr(self, "import_full_backup_input"):
                self.import_full_backup_input.text = blob_text
            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())
            self._finish_full_backup_import(bundle)
            if popup is not None:
                popup.dismiss()
            info_popup("Import successful", f"Full backup imported successfully from:\n{backup_path}")
        except Exception as e:
            info_popup("Import failed", str(e))

    def paste_revocation_from_clipboard(self):
        self._paste_into_widget(self.import_revocation_input, "There is no revocation JSON in the clipboard.")

    def open_revocation_file_picker(self):
        self._open_backup_file_picker("Import Revocation JSON", revocation_backup_dir(), list_revocation_backup_files(), self.import_revocation_from_file)

    def import_revocation_from_file(self, backup_path, popup=None):
        try:
            with open(backup_path, "r", encoding="utf-8") as f:
                blob_text = f.read().strip()
            if hasattr(self, "import_revocation_input"):
                self.import_revocation_input.text = blob_text
            self._finish_revocation_import(blob_text)
            if popup is not None:
                popup.dismiss()
        except Exception as e:
            info_popup("Import failed", str(e))

    def _finish_revocation_import(self, blob_text):
        bundle = json.loads(blob_text)
        revoked_count, matched_updates = self._apply_revocation_bundle_to_store(bundle)
        self._refresh_everything()
        info_popup("Revocation import complete", f"Imported revocation JSON with {revoked_count} revoked ID(s). Matching local licenses updated: {'yes' if matched_updates else 'no'}.")

    def import_revocation_bundle(self):
        try:
            blob_text = self.import_revocation_input.text.strip()
            self._finish_revocation_import(blob_text)
        except Exception as e:
            info_popup("Import failed", str(e))

    def get_compact_device_label(self, device_code):
            device_code = str(device_code or '').strip()
            if not device_code:
                return 'No device'
            return device_code[-8:] if len(device_code) > 8 else device_code

    def get_compact_issued_label(self, issued_at):
            txt = str(issued_at or '').strip()
            if not txt:
                return 'No issue date'
            return txt.replace('T', ' ')[:16].replace('Z', '')

    def show_license_details(self, rec):
            details = [
                f"License ID: {rec.get('license_id', '')}",
                f"Tier: {str(rec.get('tier', '')).upper()}",
                f"Status: {str(rec.get('status', 'active')).upper()}",
                f"Payment: {rec.get('payment_method', rec.get('source', ''))}",
                f"Customer: {rec.get('customer_name', '') or '-'}",
                f"Email: {rec.get('customer_email', '') or '-'}",
                f"Device Code: {rec.get('device_code', '') or 'Not bound'}",
                f"Issued: {rec.get('issued_at', '')}",
            ]
            if rec.get('expiry'):
                details.append(f"Expiry: {rec.get('expiry')}")
            if rec.get('label'):
                details.append(f"Label: {rec.get('label')}")
            if rec.get('customer_note'):
                details.append(f"Note: {rec.get('customer_note')}")

            content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
            body = Label(
                text='\n'.join(details),
                color=get_color_from_hex(TEXT),
                halign='left',
                valign='top',
                text_size=(dp(300), None),
                size_hint_y=None,
            )
            body.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(dp(120), val[1])))
            content.add_widget(body)

            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
            copy_id_btn = make_button('Copy ID', UI_CYAN)
            copy_code_btn = make_button('Copy Code', UI_CYAN)
            delete_btn = make_button('Delete', RED)
            row.add_widget(copy_id_btn)
            row.add_widget(copy_code_btn)
            row.add_widget(delete_btn)
            content.add_widget(row)

            close_btn = make_button('Close', UI_CYAN)
            content.add_widget(close_btn)

            popup = Popup(
                title='License Details',
                content=content,
                size_hint=(0.92, 0.68),
                separator_color=get_color_from_hex(GREEN),
                background_color=get_color_from_hex(CARD),
            )
            copy_id_btn.bind(on_release=lambda *_: copy_to_clipboard('License ID', rec.get('license_id', '')))
            copy_code_btn.bind(on_release=lambda *_: copy_to_clipboard('Activation code', rec.get('activation_code', '')))
            delete_btn.bind(on_release=lambda *_: self.confirm_delete_license(rec.get('license_id', ''), popup))
            close_btn.bind(on_release=popup.dismiss)
            popup.open()

    def collect_github_settings(self):
            return {
                'owner': self.github_owner_input.text.strip(),
                'repo': self.github_repo_input.text.strip(),
                'branch': self.github_branch_input.text.strip() or 'main',
                'path': self.github_path_input.text.strip().lstrip('/'),
                'token': self.github_token_input.text.strip(),
            }

    def update_github_raw_url(self, *_):
            if not hasattr(self, 'github_raw_url_input'):
                return
            cfg = self.collect_github_settings() if hasattr(self, 'github_owner_input') else dict(self.github_config)
            self.github_raw_url_input.text = build_github_raw_url(cfg.get('owner', ''), cfg.get('repo', ''), cfg.get('branch', 'main'), cfg.get('path', REVOKED_EXPORT_FILE))

    def save_github_settings(self):
            cfg = self.collect_github_settings()
            save_github_upload_config(cfg)
            self.github_config = load_github_upload_config()
            self.update_github_raw_url()
            info_popup('Saved', 'GitHub upload settings saved on this admin device.')

    def upload_revocation_to_github(self):
            if not self.require_authority():
                return
            cfg = self.collect_github_settings()
            missing = [name for name, value in [('owner', cfg['owner']), ('repo', cfg['repo']), ('branch', cfg['branch']), ('path', cfg['path']), ('token', cfg['token'])] if not value]
            if missing:
                info_popup('Missing fields', f"Fill these GitHub fields first: {', '.join(missing)}")
                return

            bundle = build_revocation_bundle(self.store.records, self.private_key)
            payload_text = json.dumps(bundle, indent=2)
            api_url = f"https://api.github.com/repos/{cfg['owner']}/{cfg['repo']}/contents/{cfg['path']}"
            headers = {
                'Accept': 'application/vnd.github+json',
                'Authorization': f"Bearer {cfg['token']}",
                'X-GitHub-Api-Version': '2022-11-28',
            }
            body = {
                'message': f"Update revoked licenses at {utc_now_iso()}",
                'content': base64.b64encode(payload_text.encode('utf-8')).decode('ascii'),
                'branch': cfg['branch'],
            }
            try:
                existing = requests.get(api_url, headers=headers, timeout=20)
                if existing.status_code == 200:
                    existing_data = existing.json()
                    if existing_data.get('sha'):
                        body['sha'] = existing_data['sha']
                elif existing.status_code not in (404,):
                    raise RuntimeError(f"GitHub lookup failed: {existing.status_code} {existing.text[:180]}")

                resp = requests.put(api_url, headers=headers, json=body, timeout=25)
                if resp.status_code not in (200, 201):
                    raise RuntimeError(f"GitHub upload failed: {resp.status_code} {resp.text[:220]}")

                save_github_upload_config(cfg)
                self.github_config = load_github_upload_config()
                self.refresh_revocation_box()
                self.update_github_raw_url()
                info_popup('Uploaded', f"Revocation file uploaded successfully to:\n{self.github_raw_url_input.text}")
            except Exception as e:
                info_popup('Upload failed', str(e))

    def build_and_store_license(self, tier, source, device_code, customer_name='', customer_email='', label='', note='', expiry=''):
            if tier not in ('demo', 'pro'):
                raise ValueError('Choose demo or pro.')
            if source not in ('crypto', 'bank', 'promo', 'partner', 'personal', 'test'):
                raise ValueError('Choose one of the payment/source types.')
            if not device_code:
                raise ValueError("Enter the customer's Device Code from the app.")

            license_id = 'SYN-' + secrets.token_hex(4).upper()
            payload = {
                'app': 'synapse_by_shv',
                'schema': 1,
                'license_id': license_id,
                'tier': tier,
                'payment_method': source,
                'source': source,
                'device_code': device_code,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'label': label,
                'issued_at': utc_now_iso(),
            }
            if note:
                payload['note'] = note
            if expiry:
                payload['expires_at'] = expiry

            signature = sign_payload(self.private_key, payload)
            activation_code = encode_activation_code(payload, signature)
            record = {
                'license_id': license_id,
                'tier': tier,
                'source': source,
                'payment_method': source,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'device_code': device_code,
                'label': label,
                'customer_note': note,
                'expiry': expiry,
                'expires_at': expiry,
                'issued_at': payload['issued_at'],
                'status': 'active',
                'activation_code': activation_code,
                'license_bundle': {'payload': payload, 'signature': signature},
                'signature_valid': verify_signature(self.public_key, payload, signature),
            }
            self.store.add(record)
            self._last_license_id = license_id
            self.generated_code_input.text = activation_code
            self.refresh_dashboard()
            self.refresh_license_list()
            self.refresh_revocation_box()
            return record


    def generate_test_license(self):
            if not self.require_authority():
                return
            try:
                device_code = self.device_input.text.strip().upper()
                if not device_code:
                    raise ValueError("Enter the customer's Device Code before generating a test license.")
                expiry = self.expiry_input.text.strip() or (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
                label = self.label_input.text.strip() or 'Internal Test'
                note = self.note_input.text.strip() or 'Admin-generated test key'
                self.build_and_store_license('pro', 'test', device_code, customer_name=self.customer_name_input.text.strip() or 'Internal Test', customer_email=self.customer_email_input.text.strip(), label=label, note=note, expiry=expiry)
                info_popup('Test license generated', '7-day style test Pro license created successfully. Change the expiry field first if you want a different end date.')
            except Exception as e:
                info_popup('Test license failed', str(e))

    def refresh_dashboard(self):
        if not hasattr(self, "dashboard_box"):
            return
        self.dashboard_box.clear_widgets()
        records = self.store.records
        total = len(records)
        active = len([r for r in records if r.get("status") == "active"])
        revoked = len([r for r in records if r.get("status") == "revoked"])
        demo = len([r for r in records if r.get("tier") == "demo"])
        pro = len([r for r in records if r.get("tier") == "pro"])


        authority_card = SectionCard("Authority status")
        if self.public_key and self.private_key:
            authority_card.add_widget(make_label("Authority loaded", GREEN))
            authority_card.add_widget(make_label(f"Data folder: {app_data_dir()}", height=dp(38)))
        else:
            authority_card.add_widget(make_label("No authority loaded. Import your backup or initialize authority.", RED, height=dp(38)))
            if getattr(self, '_load_error', ''):
                authority_card.add_widget(make_label(f"Recovered from authority load issue: {self._load_error[:120]}", ORANGE, height=dp(38)))
        self.dashboard_box.add_widget(authority_card)

        stats = SectionCard("License totals")
        for t in [
            f"Total licenses: {total}",
            f"Active: {active}",
            f"Revoked: {revoked}",
            f"Demo: {demo}",
            f"Pro: {pro}",
        ]:
            stats.add_widget(make_label(t, GREEN if "Active" in t else (RED if "Revoked" in t else TEXT)))
        self.dashboard_box.add_widget(stats)

        latest = SectionCard("Latest issued")
        if records:
            for rec in records[:8]:
                latest.add_widget(make_label(
                    f"{rec['license_id']}  |  {rec['tier']}  |  {rec.get('customer_name','-')}  |  {rec.get('status','active')}",
                    height=dp(22),
                ))
        else:
            latest.add_widget(make_label("No licenses yet."))
        self.dashboard_box.add_widget(latest)

    def get_filtered_license_records(self):
        query = (self.search_input.text or "").strip().lower() if hasattr(self, "search_input") else ""
        status_filter = getattr(getattr(self, 'license_status_spinner', None), 'text', 'all').strip().lower()
        tier_filter = getattr(getattr(self, 'license_tier_spinner', None), 'text', 'all').strip().lower()
        source_filter = getattr(getattr(self, 'license_source_spinner', None), 'text', 'all').strip().lower()
        sort_mode = getattr(getattr(self, 'license_sort_spinner', None), 'text', 'newest').strip().lower()

        visible = []
        for rec in self.store.records:
            hay = " ".join([
                rec.get("license_id", ""),
                rec.get("device_code", ""),
                rec.get("tier", ""),
                rec.get("source", ""),
                rec.get("label", ""),
                rec.get("customer_note", ""),
                rec.get("status", ""),
            ]).lower()
            if query and query not in hay:
                continue
            if status_filter != 'all' and str(rec.get('status', 'active')).lower() != status_filter:
                continue
            if tier_filter != 'all' and str(rec.get('tier', '')).lower() != tier_filter:
                continue
            if source_filter != 'all' and str(rec.get('source', '')).lower() != source_filter:
                continue
            visible.append(rec)

        if sort_mode == 'oldest':
            visible.sort(key=lambda r: str(r.get('issued_at', '')))
        elif sort_mode == 'tier':
            visible.sort(key=lambda r: (str(r.get('tier', '')), str(r.get('issued_at', ''))), reverse=False)
            visible.reverse()
        elif sort_mode == 'status':
            visible.sort(key=lambda r: (str(r.get('status', 'active')), str(r.get('issued_at', ''))), reverse=False)
            visible.reverse()
        else:
            visible.sort(key=lambda r: str(r.get('issued_at', '')), reverse=True)
        return visible

    def export_visible_licenses_csv(self):
        records = self.get_filtered_license_records()
        if not records:
            info_popup("Nothing to export", "There are no visible licenses to export with the current filters.")
            return
        export_path = license_export_path()
        fieldnames = [
            "license_id",
            "tier",
            "status",
            "source",
            "payment_method",
            "customer_name",
            "customer_email",
            "device_code",
            "label",
            "customer_note",
            "issued_at",
            "expiry",
            "expires_at",
            "revoked_at",
            "signature_valid",
        ]
        with open(export_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                row = {name: rec.get(name, "") for name in fieldnames}
                writer.writerow(row)
        info_popup("Exported", f"Visible licenses exported successfully to:\n{export_path}")

    def confirm_delete_license(self, license_id, parent_popup=None):
        rec = self.store.find(license_id)
        if not rec:
            info_popup("Not found", "That license could not be found anymore.")
            return

        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        message = Label(
            text=f"Delete this license permanently?\n\n{license_id}\n{str(rec.get('tier', '')).upper()} • {str(rec.get('status', 'active')).upper()}\n\nUse delete mainly for test keys and clutter. Revoked licenses removed from the database will also disappear from future revocation exports.",
            color=get_color_from_hex(TEXT),
            halign="left",
            valign="top",
            text_size=(dp(300), None),
            size_hint_y=None,
        )
        message.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(140), val[1])))
        content.add_widget(message)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        cancel_btn = make_button("Cancel", UI_CYAN)
        delete_btn = make_button("Delete", RED)
        row.add_widget(cancel_btn)
        row.add_widget(delete_btn)
        content.add_widget(row)

        popup = Popup(
            title="Delete License",
            content=content,
            size_hint=(0.92, 0.62),
            separator_color=get_color_from_hex(RED),
            background_color=get_color_from_hex(CARD),
        )

        cancel_btn.bind(on_release=popup.dismiss)

        def do_delete(*_):
            removed = self.store.delete(license_id)
            popup.dismiss()
            if parent_popup is not None:
                parent_popup.dismiss()
            if removed:
                self.refresh_dashboard()
                self.refresh_license_list()
                self.refresh_revocation_box()
                info_popup("Deleted", f"{license_id} was deleted from the license database.")
            else:
                info_popup("Not found", "That license could not be found anymore.")

        delete_btn.bind(on_release=do_delete)
        popup.open()

    def confirm_delete_visible_licenses(self):
        records = self.get_filtered_license_records()
        if not records:
            info_popup("Nothing to delete", "There are no visible licenses to delete with the current filters.")
            return

        count = len(records)
        ids = [rec.get("license_id", "") for rec in records if rec.get("license_id")]

        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        message = Label(
            text=f"Delete all {count} currently visible licenses?\n\nThis is best used after narrowing the list to test keys with search and filters. Any revoked licenses deleted here will also disappear from future revocation exports.",
            color=get_color_from_hex(TEXT),
            halign="left",
            valign="top",
            text_size=(dp(300), None),
            size_hint_y=None,
        )
        message.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(130), val[1])))
        content.add_widget(message)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        cancel_btn = make_button("Cancel", UI_CYAN)
        delete_btn = make_button("Delete Visible", RED)
        row.add_widget(cancel_btn)
        row.add_widget(delete_btn)
        content.add_widget(row)

        popup = Popup(
            title="Delete Visible Licenses",
            content=content,
            size_hint=(0.92, 0.58),
            separator_color=get_color_from_hex(RED),
            background_color=get_color_from_hex(CARD),
        )

        cancel_btn.bind(on_release=popup.dismiss)

        def do_delete(*_):
            removed = self.store.delete_many(ids)
            popup.dismiss()
            self.refresh_dashboard()
            self.refresh_license_list()
            self.refresh_revocation_box()
            info_popup("Deleted", f"Deleted {removed} visible license(s).")

        delete_btn.bind(on_release=do_delete)
        popup.open()

    def refresh_license_list(self):
        if not hasattr(self, "license_box"):
            return

        self.license_box.clear_widgets()
        visible = self.get_filtered_license_records()

        if not visible:
            self.license_box.add_widget(make_label("No matching licenses found."))
            return

        for rec in visible:
            status = str(rec.get('status', 'active')).upper()
            source = str(rec.get('source', '')).upper()
            device_short = self.get_compact_device_label(rec.get('device_code', ''))
            issued_short = self.get_compact_issued_label(rec.get('issued_at', ''))
            subtitle = f"{source}  •  {status}"
            if rec.get('label'):
                subtitle += f"  •  {rec.get('label')}"

            card = SectionCard(f"{rec['license_id']}  •  {rec['tier'].upper()}", subtitle)
            card.add_widget(make_label(f"Device suffix: {device_short}  •  Issued: {issued_short}", height=dp(22)))
            if rec.get('expiry'):
                card.add_widget(make_label(f"Expiry: {rec.get('expiry')}", height=dp(22)))

            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
            details_btn = make_button("Details", UI_CYAN)
            id_btn = make_button("Copy ID", UI_CYAN)
            revoke_btn = make_button("Revoke" if rec.get("status") != "revoked" else "Restore", RED if rec.get("status") != "revoked" else PURPLE)

            details_btn.bind(on_release=lambda *_ , record=rec: self.show_license_details(record))
            id_btn.bind(on_release=lambda *_ , lid=rec["license_id"]: copy_to_clipboard("License ID", lid))
            revoke_btn.bind(on_release=lambda *_ , lid=rec["license_id"], status=rec.get("status"): self.toggle_revoke(lid, status))

            row.add_widget(details_btn)
            row.add_widget(id_btn)
            row.add_widget(revoke_btn)
            card.add_widget(row)
            self.license_box.add_widget(card)

    def refresh_revocation_box(self):
        if not hasattr(self, "revocation_output"):
            return
        if not self.private_key:
            self.revocation_output.text = ""
            return
        bundle = build_revocation_bundle(self.store.records, self.private_key)
        self.revocation_output.text = json.dumps(bundle, indent=2)

    def clear_generate_form(self):
        self.device_input.text = ""
        self.tier_spinner.text = "pro"
        self.source_spinner.text = "crypto"
        self.customer_name_input.text = ""
        self.customer_email_input.text = ""
        self.label_input.text = ""
        self.note_input.text = ""
        self.expiry_input.text = ""
        self.generated_code_input.text = ""
        self._last_license_id = ""

    def generate_license(self):
        if not self.require_authority():
            return
        try:
            tier = self.tier_spinner.text.strip()
            source = self.source_spinner.text.strip()
            device_code = self.device_input.text.strip().upper()
            label = self.label_input.text.strip()
            note = self.note_input.text.strip()
            expiry = self.expiry_input.text.strip()
            self.build_and_store_license(tier, source, device_code, customer_name=self.customer_name_input.text.strip(), customer_email=self.customer_email_input.text.strip(), label=label, note=note, expiry=expiry)
            info_popup("License generated", f"{tier.upper()} license created successfully.")
        except Exception as e:
            info_popup("License failed", str(e))

    def toggle_revoke(self, license_id, status):
        target = "revoked" if status != "revoked" else "active"
        self.store.update(
            license_id,
            lambda rec: rec.update({"status": target, "revoked_at": utc_now_iso() if target == "revoked" else ""}),
        )
        self.refresh_dashboard()
        self.refresh_license_list()
        self.refresh_revocation_box()
        info_popup("License updated", f"{license_id} is now {target.upper()}.")

    def save_revocation_bundle(self):
        if not self.require_authority():
            return
        bundle = build_revocation_bundle(self.store.records, self.private_key)
        path = revocation_export_path()
        save_json(path, bundle)
        save_json(file_path(REVOKED_EXPORT_FILE), bundle)
        self.refresh_revocation_box()
        info_popup("Saved", f"Revocation file saved to:\n{path}")



# --- Embedded Casino Tools Pro Licensing Module ---
_CTP_MODULE_SOURCE = '\nimport base64\nimport csv\nimport json\nimport os\nimport secrets\nimport textwrap\nimport zlib\nimport hashlib\nimport hmac\nfrom datetime import datetime, timedelta\n\nimport requests\nimport rsa\nfrom kivy.app import App\nfrom kivy.clock import Clock\nfrom kivy.core.clipboard import Clipboard\nfrom kivy.core.window import Window\nfrom kivy.metrics import dp\nfrom kivy.utils import get_color_from_hex\nfrom kivy.uix.boxlayout import BoxLayout\nfrom kivy.uix.button import Button\nfrom kivy.uix.gridlayout import GridLayout\nfrom kivy.uix.label import Label\nfrom kivy.uix.popup import Popup\nfrom kivy.uix.scrollview import ScrollView\nfrom kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager\nfrom kivy.uix.spinner import Spinner\nfrom kivy.uix.textinput import TextInput\nfrom kivy.graphics import Color, RoundedRectangle\n\nBG = "#000000"\nCARD = "#0b0b0b"\nTEXT = "#b1bad3"\nSUBTEXT = "#8f9bb3"\nGREEN = "#00e701"\nRED = "#ff4e4e"\nBLUE = "#3498db"\nPURPLE = "#9b59b6"\nORANGE = "#e67e22"\nWindow.clearcolor = get_color_from_hex(BG)\n\nPRIVATE_KEY_FILE = "license_private.pem"\nPUBLIC_KEY_FILE = "license_public.pem"\nLICENSE_DB_FILE = "licenses_db.json"\nREVOKED_EXPORT_FILE = "revoked_licenses.json"\nAUTHORITY_BACKUP_FILE = "authority_backup.ctp"\nLICENSE_LIST_BACKUP_FILE = "license_list_backup.ctlist"\nFULL_BACKUP_FILE = "full_backup.ctfull"\nGITHUB_CONFIG_FILE = "github_upload_config.json"\nBACKUP_BUNDLE_APP = "casino_tools_license_manager"\n\nDEFAULT_GITHUB_UPLOAD = {\n    "owner": "therealwolfman97",\n    "repo": "casino-tools-revocations",\n    "branch": "main",\n    "path": REVOKED_EXPORT_FILE,\n    "token": "",\n}\n\n\ndef utc_now_iso():\n    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"\n\n\ndef app_data_dir():\n    app = App.get_running_app()\n    if app and getattr(app, "user_data_dir", None):\n        path = app.user_data_dir\n    else:\n        path = os.path.join(os.path.expanduser("~"), ".casino_tools_license_manager")\n    os.makedirs(path, exist_ok=True)\n    return path\n\n\ndef file_path(name):\n    return os.path.join(app_data_dir(), name)\n\n\ndef downloads_base_dir():\n    candidates = [\n        "/storage/emulated/0/Download",\n        "/sdcard/Download",\n        os.path.join(os.path.expanduser("~"), "Download"),\n    ]\n    for path in candidates:\n        try:\n            os.makedirs(path, exist_ok=True)\n            return path\n        except Exception:\n            continue\n    fallback = app_data_dir()\n    os.makedirs(fallback, exist_ok=True)\n    return fallback\n\n\ndef admin_export_dir(*parts):\n    path = os.path.join(downloads_base_dir(), "Casino Tools Pro Admin", *parts)\n    os.makedirs(path, exist_ok=True)\n    return path\n\n\n\ndef _timestamped_export_path(directory, filename):\n    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")\n    base, ext = os.path.splitext(filename)\n    return os.path.join(directory, f"{base}_{stamp}{ext}")\n\n\ndef list_backup_files(directory, suffixes):\n    candidates = []\n    suffixes = tuple(str(s).lower() for s in (suffixes or []))\n    try:\n        for name in os.listdir(directory):\n            lower = name.lower()\n            if suffixes and not lower.endswith(suffixes):\n                continue\n            path = os.path.join(directory, name)\n            if os.path.isfile(path):\n                candidates.append(path)\n    except Exception:\n        return []\n    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)\n    return candidates\n\n\ndef authority_backup_dir():\n    return admin_export_dir("Authority Backups")\n\n\ndef authority_backup_export_path():\n    return _timestamped_export_path(authority_backup_dir(), AUTHORITY_BACKUP_FILE)\n\n\ndef list_authority_backup_files():\n    return list_backup_files(authority_backup_dir(), [".ctp", ".shva", ".ctfull"])\n\n\ndef license_list_backup_dir():\n    return admin_export_dir("License List Backups")\n\n\ndef license_list_backup_export_path():\n    return _timestamped_export_path(license_list_backup_dir(), LICENSE_LIST_BACKUP_FILE)\n\n\ndef list_license_list_backup_files():\n    return list_backup_files(license_list_backup_dir(), [".ctlist", ".json", ".txt", ".ctfull"])\n\n\ndef full_backup_dir():\n    return admin_export_dir("Full Backups")\n\n\ndef full_backup_export_path():\n    return _timestamped_export_path(full_backup_dir(), FULL_BACKUP_FILE)\n\n\ndef list_full_backup_files():\n    return list_backup_files(full_backup_dir(), [".ctfull", ".ctp", ".shva", ".ctlist"])\n\n\ndef revocation_backup_dir():\n    return admin_export_dir("Revocation Jsons")\n\n\ndef revocation_export_path():\n    return _timestamped_export_path(revocation_backup_dir(), REVOKED_EXPORT_FILE)\n\n\ndef list_revocation_backup_files():\n    return list_backup_files(revocation_backup_dir(), [".json", ".txt"])\n\n\ndef license_export_dir():\n    return admin_export_dir("License Exports")\n\n\ndef license_export_path():\n    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")\n    return os.path.join(license_export_dir(), f"licenses_export_{stamp}.csv")\n\n\ndef github_config_path():\n    return file_path(GITHUB_CONFIG_FILE)\n\n\ndef load_github_upload_config():\n    data = load_json(github_config_path(), {})\n    merged = dict(DEFAULT_GITHUB_UPLOAD)\n    if isinstance(data, dict):\n        for key in ("owner", "repo", "branch", "path"):\n            value = str(data.get(key, "")).strip()\n            if value:\n                merged[key] = value\n    return merged\n\n\ndef save_github_upload_config(data):\n    clean = {}\n    for key in ("owner", "repo", "branch", "path"):\n        clean[key] = str(data.get(key, DEFAULT_GITHUB_UPLOAD.get(key, ""))).strip()\n    save_json(github_config_path(), clean)\n\n\ndef build_github_raw_url(owner, repo, branch, path):\n    owner = str(owner).strip().strip("/")\n    repo = str(repo).strip().strip("/")\n    branch = str(branch).strip().strip("/") or "main"\n    path = str(path).strip().lstrip("/")\n    if not owner or not repo or not path:\n        return ""\n    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"\n\n\ndef load_json(path, default):\n    try:\n        with open(path, "r", encoding="utf-8") as f:\n            return json.load(f)\n    except Exception:\n        return default\n\n\ndef save_json(path, data):\n    os.makedirs(os.path.dirname(path), exist_ok=True)\n    with open(path, "w", encoding="utf-8") as f:\n        json.dump(data, f, indent=2, ensure_ascii=False)\n\n\ndef canonical_json(data):\n    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")\n\n\ndef info_popup(title, message):\n    content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))\n    lbl = Label(\n        text=message,\n        color=get_color_from_hex(TEXT),\n        halign="left",\n        valign="top",\n        text_size=(dp(300), None),\n        size_hint_y=None,\n    )\n    lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", max(val[1], dp(80))))\n    btn = RoundedButton(\n        text="OK",\n        size_hint_y=None,\n        height=dp(46),\n        bg_hex=GREEN,\n    )\n    content.add_widget(lbl)\n    content.add_widget(btn)\n    popup = Popup(\n        title=title,\n        content=content,\n        size_hint=(0.9, 0.6),\n        separator_color=get_color_from_hex(GREEN),\n        background_color=get_color_from_hex(CARD),\n    )\n    btn.bind(on_release=popup.dismiss)\n    popup.open()\n\n\ndef copy_to_clipboard(label, value):\n    Clipboard.copy(value or "")\n    info_popup("Copied", f"{label} copied to clipboard.")\n\n\n\ndef load_existing_keypair():\n    priv_path = file_path(PRIVATE_KEY_FILE)\n    pub_path = file_path(PUBLIC_KEY_FILE)\n    if os.path.exists(priv_path) and os.path.exists(pub_path):\n        with open(priv_path, "rb") as f:\n            private_key = rsa.PrivateKey.load_pkcs1(f.read())\n        with open(pub_path, "rb") as f:\n            public_key = rsa.PublicKey.load_pkcs1(f.read())\n        return public_key, private_key\n    return None, None\n\n\ndef initialize_authority_keypair():\n    priv_path = file_path(PRIVATE_KEY_FILE)\n    pub_path = file_path(PUBLIC_KEY_FILE)\n    if os.path.exists(priv_path) or os.path.exists(pub_path):\n        raise RuntimeError("Authority already exists on this device.")\n    public_key, private_key = rsa.newkeys(2048)\n    with open(priv_path, "wb") as f:\n        f.write(private_key.save_pkcs1("PEM"))\n    with open(pub_path, "wb") as f:\n        f.write(public_key.save_pkcs1("PEM"))\n    return public_key, private_key\n\n\ndef _pbkdf(password: str, salt: bytes) -> bytes:\n    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=32)\n\n\ndef _xor_stream(key: bytes, data: bytes) -> bytes:\n    out = bytearray()\n    counter = 0\n    while len(out) < len(data):\n        block = hashlib.sha256(key + counter.to_bytes(4, "big")).digest()\n        take = min(len(block), len(data) - len(out))\n        chunk = data[len(out):len(out)+take]\n        out.extend(bytes(a ^ b for a, b in zip(chunk, block[:take])))\n        counter += 1\n    return bytes(out)\n\n\n\ndef build_secure_backup_blob(password: str, bundle_type: str, payload: dict):\n    if not password:\n        raise ValueError("Backup password is required.")\n    raw_payload = {\n        "schema": 2,\n        "app": BACKUP_BUNDLE_APP,\n        "bundle_type": bundle_type,\n        "exported_at": utc_now_iso(),\n        "payload": payload,\n    }\n    raw = canonical_json(raw_payload)\n    salt = os.urandom(16)\n    enc_key = _pbkdf(password, salt)\n    ciphertext = _xor_stream(enc_key, raw)\n    mac = hmac.new(enc_key, salt + ciphertext, hashlib.sha256).digest()\n    bundle = {\n        "schema": 2,\n        "app": BACKUP_BUNDLE_APP,\n        "bundle_type": bundle_type,\n        "salt": base64.urlsafe_b64encode(salt).decode("ascii"),\n        "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),\n        "mac": base64.urlsafe_b64encode(mac).decode("ascii"),\n    }\n    return json.dumps(bundle, indent=2)\n\n\ndef parse_secure_backup_blob(blob_text: str, password: str):\n    if not blob_text.strip():\n        raise ValueError("Backup text is empty.")\n    if not password:\n        raise ValueError("Backup password is required.")\n    bundle = json.loads(blob_text)\n    salt = base64.urlsafe_b64decode(bundle["salt"].encode("ascii"))\n    ciphertext = base64.urlsafe_b64decode(bundle["ciphertext"].encode("ascii"))\n    mac = base64.urlsafe_b64decode(bundle["mac"].encode("ascii"))\n    enc_key = _pbkdf(password, salt)\n    expected = hmac.new(enc_key, salt + ciphertext, hashlib.sha256).digest()\n    if not hmac.compare_digest(mac, expected):\n        raise ValueError("Backup password is incorrect or backup is corrupted.")\n    raw = _xor_stream(enc_key, ciphertext)\n    data = json.loads(raw.decode("utf-8"))\n    if isinstance(data, dict) and "payload" in data and "bundle_type" in data:\n        return data\n    legacy_payload = {}\n    if "private_key_pem" in data:\n        legacy_payload["private_key_pem"] = data.get("private_key_pem", "")\n    if "public_key_pem" in data:\n        legacy_payload["public_key_pem"] = data.get("public_key_pem", "")\n    if "licenses" in data:\n        legacy_payload["licenses"] = data.get("licenses", [])\n    if "revoked_bundle" in data:\n        legacy_payload["revoked_bundle"] = data.get("revoked_bundle", {})\n    return {\n        "schema": data.get("schema", 1),\n        "app": data.get("app", BACKUP_BUNDLE_APP),\n        "bundle_type": "legacy_full_backup",\n        "exported_at": data.get("exported_at", ""),\n        "payload": legacy_payload,\n    }\n\n\ndef build_authority_backup_blob(password: str):\n    public_key, private_key = load_existing_keypair()\n    if not public_key or not private_key:\n        raise ValueError("No authority loaded. Initialize or import authority first.")\n    payload = {\n        "private_key_pem": private_key.save_pkcs1("PEM").decode("utf-8"),\n        "public_key_pem": public_key.save_pkcs1("PEM").decode("utf-8"),\n    }\n    return build_secure_backup_blob(password, "authority_only", payload)\n\n\ndef build_license_list_backup_blob(password: str, records):\n    payload = {\n        "licenses": records,\n    }\n    return build_secure_backup_blob(password, "license_list_only", payload)\n\n\ndef build_full_backup_blob(password: str, records):\n    public_key, private_key = load_existing_keypair()\n    if not public_key or not private_key:\n        raise ValueError("No authority loaded. Initialize or import authority first.")\n    revoked_bundle = build_revocation_bundle(records, private_key)\n    payload = {\n        "private_key_pem": private_key.save_pkcs1("PEM").decode("utf-8"),\n        "public_key_pem": public_key.save_pkcs1("PEM").decode("utf-8"),\n        "licenses": records,\n        "revoked_bundle": revoked_bundle,\n    }\n    return build_secure_backup_blob(password, "full_backup", payload)\n\n\ndef sign_payload(private_key, payload_dict):\n    sig = rsa.sign(canonical_json(payload_dict), private_key, "SHA-256")\n    return base64.urlsafe_b64encode(sig).decode("ascii")\n\n\ndef verify_signature(public_key, payload_dict, sig_b64):\n    try:\n        sig = base64.urlsafe_b64decode(sig_b64.encode("ascii"))\n        rsa.verify(canonical_json(payload_dict), sig, public_key)\n        return True\n    except Exception:\n        return False\n\n\ndef encode_activation_code(payload_dict, signature_b64):\n    blob = {"p": payload_dict, "s": signature_b64}\n    raw = canonical_json(blob)\n    compressed = zlib.compress(raw, level=9)\n    token = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")\n    chunks = textwrap.wrap(token, 24)\n    return "CTP6A-" + ".".join(chunks)\n\n\ndef decode_activation_code(code):\n    cleaned = code.strip().replace("\\n", "").replace(" ", "")\n    if cleaned.startswith("CTP6A-"):\n        cleaned = cleaned[6:]\n    cleaned = cleaned.replace(".", "")\n    cleaned += "=" * ((4 - len(cleaned) % 4) % 4)\n    raw = base64.urlsafe_b64decode(cleaned.encode("ascii"))\n    data = json.loads(zlib.decompress(raw).decode("utf-8"))\n    return data["p"], data["s"]\n\n\ndef build_revocation_bundle(records, private_key):\n    revoked_ids = sorted([r["license_id"] for r in records if r.get("status") == "revoked"])\n    payload = {\n        "app": "casino_tools_pro",\n        "version": 1,\n        "updated_at": utc_now_iso(),\n        "revoked_ids": revoked_ids,\n    }\n    signature = sign_payload(private_key, payload)\n    return {"payload": payload, "signature": signature}\n\n\nclass LicenseStore:\n    def __init__(self):\n        self.path = file_path(LICENSE_DB_FILE)\n        self.records = load_json(self.path, [])\n\n    def save(self):\n        save_json(self.path, self.records)\n\n    def add(self, record):\n        self.records.insert(0, record)\n        self.save()\n\n    def update(self, license_id, updater):\n        for rec in self.records:\n            if rec["license_id"] == license_id:\n                updater(rec)\n                self.save()\n                return True\n        return False\n\n    def delete(self, license_id):\n        before = len(self.records)\n        self.records = [rec for rec in self.records if rec.get("license_id") != license_id]\n        changed = len(self.records) != before\n        if changed:\n            self.save()\n        return changed\n\n    def delete_many(self, license_ids):\n        wanted = {str(x) for x in (license_ids or []) if str(x)}\n        if not wanted:\n            return 0\n        before = len(self.records)\n        self.records = [rec for rec in self.records if rec.get("license_id") not in wanted]\n        removed = before - len(self.records)\n        if removed:\n            self.save()\n        return removed\n\n    def find(self, license_id):\n        for rec in self.records:\n            if rec["license_id"] == license_id:\n                return rec\n        return None\n\n\n\nclass RoundedButton(Button):\n    def __init__(self, bg_hex=GREEN, text_color=None, radius=16, **kwargs):\n        kwargs.setdefault("background_normal", "")\n        kwargs.setdefault("background_down", "")\n        kwargs.setdefault("background_color", (0, 0, 0, 0))\n        super().__init__(**kwargs)\n        self._bg_hex = bg_hex\n        if text_color is None:\n            text_color = (0, 0, 0, 1) if bg_hex == GREEN else (1, 1, 1, 1)\n        self.color = text_color\n        self.bold = True\n        with self.canvas.before:\n            Color(rgba=get_color_from_hex(bg_hex))\n            self._rounded_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])\n        self.bind(pos=self._update_bg, size=self._update_bg)\n\n    def _update_bg(self, *_):\n        self._rounded_bg.pos = self.pos\n        self._rounded_bg.size = self.size\n\n\n\nclass SectionCard(BoxLayout):\n    def __init__(self, title, subtitle="", **kwargs):\n        super().__init__(orientation="vertical", spacing=dp(8), padding=dp(12), size_hint_y=None, **kwargs)\n        self.bind(minimum_height=self.setter("height"))\n        from kivy.graphics import Color, RoundedRectangle\n        with self.canvas.before:\n            Color(rgba=get_color_from_hex(CARD))\n            self._bg = RoundedRectangle(radius=[18], pos=self.pos, size=self.size)\n        self.bind(pos=self._update_bg, size=self._update_bg)\n\n        title_lbl = Label(\n            text=title,\n            bold=True,\n            color=get_color_from_hex(TEXT),\n            size_hint_y=None,\n            height=dp(24),\n            halign="left",\n            valign="middle",\n            text_size=(dp(320), None),\n        )\n        self.add_widget(title_lbl)\n\n        if subtitle:\n            subtitle_lbl = Label(\n                text=subtitle,\n                color=get_color_from_hex(SUBTEXT),\n                size_hint_y=None,\n                halign="left",\n                valign="middle",\n                text_size=(dp(320), None),\n            )\n            subtitle_lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(18), val[1])))\n            self.add_widget(subtitle_lbl)\n\n    def _update_bg(self, *_):\n        self._bg.pos = self.pos\n        self._bg.size = self.size\n\n\ndef make_label(text, color=TEXT, bold=False, height=dp(24)):\n    return Label(\n        text=text,\n        color=get_color_from_hex(color),\n        bold=bold,\n        size_hint_y=None,\n        height=height,\n        halign="left",\n        valign="middle",\n        text_size=(dp(320), None),\n    )\n\n\ndef make_input(hint="", multiline=False, readonly=False, password=False):\n    return TextInput(\n        hint_text=hint,\n        multiline=multiline,\n        readonly=readonly,\n        password=password,\n        size_hint_y=None,\n        height=dp(46) if not multiline else dp(100),\n        background_color=get_color_from_hex("#111111"),\n        foreground_color=get_color_from_hex(TEXT),\n        cursor_color=get_color_from_hex(GREEN),\n        hint_text_color=get_color_from_hex(SUBTEXT),\n        padding=[dp(10), dp(12), dp(10), dp(12)],\n    )\n\n\ndef make_button(text, color=GREEN):\n    return RoundedButton(\n        text=text,\n        size_hint_y=None,\n        height=dp(46),\n        bg_hex=color,\n        text_color=(0, 0, 0, 1) if color == GREEN else (1, 1, 1, 1),\n    )\n\n\ndef make_nav_button(text):\n    btn = RoundedButton(\n        text=text,\n        size_hint=(1, None),\n        height=dp(44),\n        bg_hex="#182432",\n        text_color=get_color_from_hex(TEXT),\n        radius=22,\n    )\n    return btn\n\n\nclass LicenseManagerScreen(Screen):\n    def __init__(self, **kwargs):\n        super().__init__(**kwargs)\n        self.store = LicenseStore()\n        self.public_key, self.private_key = load_existing_keypair()\n        self.github_config = load_github_upload_config()\n        self._last_license_id = ""\n        self.add_widget(BoxLayout())\n        Clock.schedule_once(self.build_ui, 0)\n\n\n    def build_ui(self, *_):\n        self.clear_widgets()\n        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))\n\n        top_bar = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))\n        title_lbl = Label(\n            text="Casino Tools License Manager",\n            color=get_color_from_hex(TEXT),\n            bold=True,\n            halign="left",\n            valign="middle",\n            font_size=\'18sp\',\n        )\n        title_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))\n        top_bar.add_widget(title_lbl)\n        exit_btn = make_button("EXIT", RED)\n        exit_btn.size_hint_x = None\n        exit_btn.width = dp(100)\n        exit_btn.bind(on_release=lambda *_: App.get_running_app().stop())\n        top_bar.add_widget(exit_btn)\n        root.add_widget(top_bar)\n\n        nav_grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(92))\n        self.tab_buttons = {}\n        self.tab_titles = {\n            "dashboard": "Dashboard",\n            "authority": "Authority",\n            "generate": "Generate",\n            "licenses": "Licenses",\n            "revocations": "Revocations",\n        }\n        for key in ("dashboard", "authority", "generate", "licenses", "revocations"):\n            btn = make_nav_button(self.tab_titles[key])\n            btn.bind(on_release=lambda *_ , tab_key=key: self.switch_tab(tab_key))\n            self.tab_buttons[key] = btn\n            nav_grid.add_widget(btn)\n        root.add_widget(nav_grid)\n\n        self.content_host = BoxLayout()\n        root.add_widget(self.content_host)\n        self.add_widget(root)\n\n        self.tab_views = {\n            "dashboard": self.build_dashboard_view(),\n            "authority": self.build_authority_view(),\n            "generate": self.build_generate_view(),\n            "licenses": self.build_licenses_view(),\n            "revocations": self.build_revocation_view(),\n        }\n\n        self.switch_tab("dashboard")\n        self.update_authority_status()\n        self.refresh_dashboard()\n        self.refresh_license_list()\n        self.refresh_revocation_box()\n\n    def switch_tab(self, key):\n        if not hasattr(self, "content_host"):\n            return\n        self.content_host.clear_widgets()\n        view = self.tab_views.get(key)\n        if view is not None:\n            self.content_host.add_widget(view)\n\n        active_bg = get_color_from_hex(GREEN)\n        inactive_bg = get_color_from_hex("#24364a")\n        active_text = (0, 0, 0, 1)\n        inactive_text = get_color_from_hex(TEXT)\n        for btn_key, btn in self.tab_buttons.items():\n            if btn_key == key:\n                btn.background_color = active_bg\n                btn.color = active_text\n            else:\n                btn.background_color = inactive_bg\n                btn.color = inactive_text\n\n    def switch_license_subtab(self, key):\n        if not hasattr(self, \'license_subtab_host\'):\n            return\n        self.license_subtab_host.clear_widgets()\n        if key == \'tools\':\n            self.license_subtab_host.add_widget(self.license_tools_view)\n        else:\n            self.license_subtab_host.add_widget(self.license_list_view)\n        active_bg = get_color_from_hex(GREEN)\n        inactive_bg = get_color_from_hex("#24364a")\n        active_text = (0, 0, 0, 1)\n        inactive_text = get_color_from_hex(TEXT)\n        for btn_key, btn in getattr(self, \'license_subtab_buttons\', {}).items():\n            if btn_key == key:\n                btn.background_color = active_bg\n                btn.color = active_text\n            else:\n                btn.background_color = inactive_bg\n                btn.color = inactive_text\n\n    def build_dashboard_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        self.dashboard_box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        self.dashboard_box.bind(minimum_height=self.dashboard_box.setter("height"))\n        scroll.add_widget(self.dashboard_box)\n        return scroll\n\n\n    def build_authority_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        box.bind(minimum_height=box.setter("height"))\n\n        card = SectionCard("Authority only backup", "Share the same signing authority across apps without replacing this app\'s local license list.")\n        self.auth_status_label = make_label("", color=SUBTEXT, height=dp(44))\n        card.add_widget(self.auth_status_label)\n\n        card.add_widget(make_label("Backup Password"))\n        self.backup_password_input = make_input("Enter backup password")\n        card.add_widget(self.backup_password_input)\n\n        row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        init_btn = make_button("Initialize Authority", UI_CYAN)\n        copy_pub_btn = make_button("Copy Public Key PEM", UI_CYAN)\n        row1.add_widget(init_btn)\n        row1.add_widget(copy_pub_btn)\n        init_btn.bind(on_release=lambda *_: self.initialize_authority())\n        copy_pub_btn.bind(on_release=lambda *_: self.copy_public_key())\n        card.add_widget(row1)\n\n        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_backup_btn = make_button("Generate Authority Backup", GREEN)\n        copy_backup_btn = make_button("Copy Authority Backup", UI_CYAN)\n        row2.add_widget(gen_backup_btn)\n        row2.add_widget(copy_backup_btn)\n        gen_backup_btn.bind(on_release=lambda *_: self.generate_authority_backup())\n        copy_backup_btn.bind(on_release=lambda *_: copy_to_clipboard("Authority backup", getattr(self, "backup_output", make_input()).text if hasattr(self, "backup_output") else ""))\n        card.add_widget(row2)\n\n        self.backup_output = make_input("Generated encrypted authority-only backup will appear here", multiline=True, readonly=True)\n        self.backup_output.height = dp(220)\n        card.add_widget(self.backup_output)\n\n        row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_backup_btn = make_button("Save Authority File", UI_CYAN)\n        import_backup_btn = make_button("Import Authority", GREEN)\n        row3.add_widget(save_backup_btn)\n        row3.add_widget(import_backup_btn)\n        save_backup_btn.bind(on_release=lambda *_: self.save_authority_backup())\n        import_backup_btn.bind(on_release=lambda *_: self.import_authority_backup())\n        card.add_widget(row3)\n\n        card.add_widget(make_label("Paste Authority Backup To Import"))\n        self.import_backup_input = make_input("Paste encrypted authority backup here", multiline=True)\n        self.import_backup_input.height = dp(180)\n        card.add_widget(self.import_backup_input)\n\n        row4 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        paste_btn = make_button("Paste", UI_CYAN)\n        import_file_btn = make_button("Import Auth File", UI_CYAN)\n        paste_btn.bind(on_release=lambda *_: self.paste_backup_from_clipboard())\n        import_file_btn.bind(on_release=lambda *_: self.open_auth_file_picker())\n        row4.add_widget(paste_btn)\n        row4.add_widget(import_file_btn)\n        card.add_widget(row4)\n        box.add_widget(card)\n\n        full_card = SectionCard("Full backup", "Back up authority + this app\'s local license list + a revocation snapshot in one encrypted file.")\n        full_card.add_widget(make_label("Uses the same backup password above.", color=SUBTEXT, height=dp(28)))\n\n        full_row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_full_btn = make_button("Generate Full Backup", GREEN)\n        copy_full_btn = make_button("Copy Full Backup", UI_CYAN)\n        gen_full_btn.bind(on_release=lambda *_: self.generate_full_backup())\n        copy_full_btn.bind(on_release=lambda *_: copy_to_clipboard("Full backup", getattr(self, "full_backup_output", make_input()).text if hasattr(self, "full_backup_output") else ""))\n        full_row1.add_widget(gen_full_btn)\n        full_row1.add_widget(copy_full_btn)\n        full_card.add_widget(full_row1)\n\n        self.full_backup_output = make_input("Generated encrypted full backup will appear here", multiline=True, readonly=True)\n        self.full_backup_output.height = dp(220)\n        full_card.add_widget(self.full_backup_output)\n\n        full_row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_full_btn = make_button("Save Full Backup", UI_CYAN)\n        import_full_btn = make_button("Import Full Backup", GREEN)\n        save_full_btn.bind(on_release=lambda *_: self.save_full_backup())\n        import_full_btn.bind(on_release=lambda *_: self.import_full_backup())\n        full_row2.add_widget(save_full_btn)\n        full_row2.add_widget(import_full_btn)\n        full_card.add_widget(full_row2)\n\n        full_card.add_widget(make_label("Paste Full Backup To Import"))\n        self.import_full_backup_input = make_input("Paste encrypted full backup here", multiline=True)\n        self.import_full_backup_input.height = dp(180)\n        full_card.add_widget(self.import_full_backup_input)\n\n        full_row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        paste_full_btn = make_button("Paste", UI_CYAN)\n        import_full_file_btn = make_button("Import Full File", UI_CYAN)\n        paste_full_btn.bind(on_release=lambda *_: self.paste_full_backup_from_clipboard())\n        import_full_file_btn.bind(on_release=lambda *_: self.open_full_backup_file_picker())\n        full_row3.add_widget(paste_full_btn)\n        full_row3.add_widget(import_full_file_btn)\n        full_card.add_widget(full_row3)\n        box.add_widget(full_card)\n\n        scroll.add_widget(box)\n        return scroll\n\n    def build_generate_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        box.bind(minimum_height=box.setter("height"))\n\n        card = SectionCard("Generate activation code", "Create device-bound Demo / Pro / Pro+ licenses")\n        self.device_input = make_input("Device Code (ex: CTP6-DEV-83F1A7C9)")\n        self.tier_spinner = Spinner(text="pro", values=("demo", "pro", "pro_plus"), size_hint_y=None, height=dp(46))\n        self.source_spinner = Spinner(text="crypto", values=("crypto", "bank", "promo", "partner", "personal", "test"), size_hint_y=None, height=dp(46))\n        self.label_input = make_input("Label (optional)")\n        self.note_input = make_input("Customer note / payment note (optional)", multiline=True)\n        self.expiry_input = make_input("Expiry date YYYY-MM-DD (optional)")\n\n        for title, widget in [\n            ("Device Code", self.device_input),\n            ("Tier", self.tier_spinner),\n            ("Payment / Source", self.source_spinner),\n            ("Label", self.label_input),\n            ("Note", self.note_input),\n            ("Expiry", self.expiry_input),\n        ]:\n            card.add_widget(make_label(title))\n            card.add_widget(widget)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_btn = make_button("Generate License")\n        clear_btn = make_button("Clear", UI_CYAN)\n        gen_btn.bind(on_release=lambda *_: self.generate_license())\n        clear_btn.bind(on_release=lambda *_: self.clear_generate_form())\n        row.add_widget(gen_btn)\n        row.add_widget(clear_btn)\n        card.add_widget(row)\n\n        test_btn = make_button("Generate 7-Day Test Pro+", UI_CYAN)\n        test_btn.bind(on_release=lambda *_: self.generate_test_license())\n        card.add_widget(test_btn)\n\n        self.generated_code_input = make_input("Generated activation code will appear here", multiline=True, readonly=True)\n        self.generated_code_input.height = dp(160)\n        card.add_widget(make_label("Activation Code"))\n        card.add_widget(self.generated_code_input)\n\n        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        copy_btn = make_button("Copy Code", UI_CYAN)\n        copy_id_btn = make_button("Copy License ID", UI_CYAN)\n        copy_btn.bind(on_release=lambda *_: copy_to_clipboard("Activation code", self.generated_code_input.text))\n        copy_id_btn.bind(on_release=lambda *_: copy_to_clipboard("License ID", self._last_license_id))\n        row2.add_widget(copy_btn)\n        row2.add_widget(copy_id_btn)\n        card.add_widget(row2)\n\n        box.add_widget(card)\n        scroll.add_widget(box)\n        return scroll\n\n\n    def build_licenses_view(self):\n        root = BoxLayout(orientation=\'vertical\', spacing=dp(8), padding=[0, dp(4), 0, dp(4)])\n\n        tab_row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(46))\n        self.license_subtab_buttons = {}\n        for key, title in (("tools", "Tools"), ("list", "License List")):\n            btn = make_nav_button(title)\n            btn.bind(on_release=lambda *_ , tab_key=key: self.switch_license_subtab(tab_key))\n            self.license_subtab_buttons[key] = btn\n            tab_row.add_widget(btn)\n        root.add_widget(tab_row)\n\n        self.license_subtab_host = BoxLayout()\n        root.add_widget(self.license_subtab_host)\n\n        # Tools subtab\n        tools_scroll = ScrollView(do_scroll_x=False, scroll_type=[\'bars\', \'content\'], bar_width=dp(6))\n        tools_outer = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])\n        tools_outer.bind(minimum_height=tools_outer.setter(\'height\'))\n\n        backup_card = SectionCard("License list backup")\n        backup_row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_backup_btn = make_button("Generate Backup", GREEN)\n        copy_backup_btn = make_button("Copy Backup", UI_CYAN)\n        gen_backup_btn.bind(on_release=lambda *_: self.generate_license_list_backup())\n        copy_backup_btn.bind(on_release=lambda *_: copy_to_clipboard("License list backup", getattr(self, "license_backup_output", make_input()).text if hasattr(self, "license_backup_output") else ""))\n        backup_row1.add_widget(gen_backup_btn)\n        backup_row1.add_widget(copy_backup_btn)\n        backup_card.add_widget(backup_row1)\n\n        self.license_backup_output = make_input("Generated encrypted license-list backup will appear here", multiline=True, readonly=True)\n        self.license_backup_output.height = dp(160)\n        backup_card.add_widget(self.license_backup_output)\n\n        backup_row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_backup_btn = make_button("Save Backup", UI_CYAN)\n        import_backup_btn = make_button("Import Backup", GREEN)\n        save_backup_btn.bind(on_release=lambda *_: self.save_license_list_backup())\n        import_backup_btn.bind(on_release=lambda *_: self.import_license_list_backup())\n        backup_row2.add_widget(save_backup_btn)\n        backup_row2.add_widget(import_backup_btn)\n        backup_card.add_widget(backup_row2)\n\n        self.import_license_backup_input = make_input("Paste encrypted license-list backup here", multiline=True)\n        self.import_license_backup_input.height = dp(120)\n        backup_card.add_widget(self.import_license_backup_input)\n\n        backup_row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        paste_btn = make_button("Paste", UI_CYAN)\n        import_file_btn = make_button("Import File", UI_CYAN)\n        paste_btn.bind(on_release=lambda *_: self.paste_license_backup_from_clipboard())\n        import_file_btn.bind(on_release=lambda *_: self.open_license_backup_file_picker())\n        backup_row3.add_widget(paste_btn)\n        backup_row3.add_widget(import_file_btn)\n        backup_card.add_widget(backup_row3)\n        tools_outer.add_widget(backup_card)\n        tools_scroll.add_widget(tools_outer)\n        self.license_tools_view = tools_scroll\n\n        search_card = SectionCard("License filters")\n        self.search_input = make_input("Search by ID / device / label / payment / notes")\n        self.search_input.height = dp(42)\n        self.search_input.bind(text=lambda *_: self.refresh_license_list())\n        search_card.add_widget(self.search_input)\n\n        filters = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(42))\n        self.license_status_spinner = Spinner(text="all", values=("all", "active", "revoked"), size_hint_y=None, height=dp(42))\n        self.license_tier_spinner = Spinner(text="all", values=("all", "demo", "pro", "pro_plus"), size_hint_y=None, height=dp(42))\n        self.license_source_spinner = Spinner(text="all", values=("all", "crypto", "bank", "promo", "partner", "personal", "test"), size_hint_y=None, height=dp(42))\n        self.license_sort_spinner = Spinner(text="newest", values=("newest", "oldest", "tier", "status"), size_hint_y=None, height=dp(42))\n        self.license_status_spinner.bind(text=lambda *_: self.refresh_license_list())\n        self.license_tier_spinner.bind(text=lambda *_: self.refresh_license_list())\n        self.license_source_spinner.bind(text=lambda *_: self.refresh_license_list())\n        self.license_sort_spinner.bind(text=lambda *_: self.refresh_license_list())\n        filters.add_widget(self.license_status_spinner)\n        filters.add_widget(self.license_tier_spinner)\n        filters.add_widget(self.license_source_spinner)\n        filters.add_widget(self.license_sort_spinner)\n        search_card.add_widget(filters)\n\n        actions = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(44))\n        export_btn = make_button("Export Visible CSV", UI_CYAN)\n        delete_filtered_btn = make_button("Delete Visible", RED)\n        export_btn.height = dp(44)\n        delete_filtered_btn.height = dp(44)\n        export_btn.bind(on_release=lambda *_: self.export_visible_licenses_csv())\n        delete_filtered_btn.bind(on_release=lambda *_: self.confirm_delete_visible_licenses())\n        actions.add_widget(export_btn)\n        actions.add_widget(delete_filtered_btn)\n        search_card.add_widget(actions)\n\n        hint = make_label("Tip: set Source = test before using Delete Visible.", color=SUBTEXT, height=dp(24))\n        search_card.add_widget(hint)\n\n        # List subtab\n        list_scroll = ScrollView(do_scroll_x=False, scroll_type=[\'bars\', \'content\'], bar_width=dp(6))\n        list_outer = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])\n        list_outer.bind(minimum_height=list_outer.setter(\'height\'))\n        list_outer.add_widget(search_card)\n        results_card = SectionCard("License list", "Tap Details to inspect, copy, revoke, or restore.")\n        self.license_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])\n        self.license_box.bind(minimum_height=self.license_box.setter("height"))\n        results_card.add_widget(self.license_box)\n        list_outer.add_widget(results_card)\n        list_scroll.add_widget(list_outer)\n        self.license_list_view = list_scroll\n\n        self.switch_license_subtab(\'list\')\n        return root\n\n\n    def build_revocation_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        box.bind(minimum_height=box.setter("height"))\n\n        card = SectionCard("Revocation export", "Generate, save, copy, or manually import the signed revoked list for the customer app.")\n        export_btn = make_button("Generate Signed Revocation File")\n        export_btn.bind(on_release=lambda *_: self.refresh_revocation_box())\n        card.add_widget(export_btn)\n\n        self.revocation_output = make_input("", multiline=True, readonly=True)\n        self.revocation_output.height = dp(220)\n        card.add_widget(self.revocation_output)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_btn = make_button("Save revoked_licenses.json", UI_CYAN)\n        copy_btn = make_button("Copy JSON", UI_CYAN)\n        save_btn.bind(on_release=lambda *_: self.save_revocation_bundle())\n        copy_btn.bind(on_release=lambda *_: copy_to_clipboard("Revocation JSON", self.revocation_output.text))\n        row.add_widget(save_btn)\n        row.add_widget(copy_btn)\n        card.add_widget(row)\n\n        pub_btn = make_button("Copy Public Key PEM", UI_CYAN)\n        pub_btn.bind(on_release=lambda *_: self.copy_public_key())\n        card.add_widget(pub_btn)\n\n        card.add_widget(make_label("Paste Revocation JSON To Import"))\n        self.import_revocation_input = make_input("Paste signed revocation JSON here", multiline=True)\n        self.import_revocation_input.height = dp(180)\n        card.add_widget(self.import_revocation_input)\n\n        row_import = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(46))\n        paste_btn = make_button("Paste", UI_CYAN)\n        import_btn = make_button("Import JSON", GREEN)\n        import_file_btn = make_button("Import File", UI_CYAN)\n        paste_btn.bind(on_release=lambda *_: self.paste_revocation_from_clipboard())\n        import_btn.bind(on_release=lambda *_: self.import_revocation_bundle())\n        import_file_btn.bind(on_release=lambda *_: self.open_revocation_file_picker())\n        row_import.add_widget(paste_btn)\n        row_import.add_widget(import_btn)\n        row_import.add_widget(import_file_btn)\n        card.add_widget(row_import)\n        box.add_widget(card)\n\n        gh = SectionCard("GitHub upload", "Store the revocation JSON online so customer apps can read the fixed raw URL")\n        self.github_owner_input = make_input("GitHub owner / username")\n        self.github_repo_input = make_input("Repository name")\n        self.github_branch_input = make_input("Branch", readonly=False)\n        self.github_path_input = make_input("Path inside repo (ex: revoked_licenses.json)")\n        self.github_token_input = make_input("GitHub token with contents:write access")\n        self.github_raw_url_input = make_input("Raw URL", readonly=True)\n\n        self.github_owner_input.text = self.github_config.get(\'owner\', \'\')\n        self.github_repo_input.text = self.github_config.get(\'repo\', \'\')\n        self.github_branch_input.text = self.github_config.get(\'branch\', \'main\') or \'main\'\n        self.github_path_input.text = self.github_config.get(\'path\', REVOKED_EXPORT_FILE) or REVOKED_EXPORT_FILE\n        self.github_token_input.text = self.github_config.get(\'token\', \'\')\n\n        for title, widget in [\n            ("Owner", self.github_owner_input),\n            ("Repo", self.github_repo_input),\n            ("Branch", self.github_branch_input),\n            ("Path", self.github_path_input),\n            ("Token", self.github_token_input),\n            ("Raw URL", self.github_raw_url_input),\n        ]:\n            gh.add_widget(make_label(title))\n            gh.add_widget(widget)\n\n        for widget in (self.github_owner_input, self.github_repo_input, self.github_branch_input, self.github_path_input):\n            widget.bind(text=self.update_github_raw_url)\n        self.update_github_raw_url()\n\n        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_cfg_btn = make_button("Save Upload Settings", UI_CYAN)\n        upload_btn = make_button("Upload Revocation JSON", GREEN)\n        save_cfg_btn.bind(on_release=lambda *_: self.save_github_settings())\n        upload_btn.bind(on_release=lambda *_: self.upload_revocation_to_github())\n        row2.add_widget(save_cfg_btn)\n        row2.add_widget(upload_btn)\n        gh.add_widget(row2)\n        box.add_widget(gh)\n\n        scroll.add_widget(box)\n        return scroll\n\n    def update_authority_status(self):\n        if hasattr(self, "auth_status_label"):\n            if self.public_key and self.private_key:\n                self.auth_status_label.text = f"Authority loaded. Public key fingerprint: {hashlib.sha256(self.public_key.save_pkcs1(\'PEM\')).hexdigest()[:16].upper()}"\n                self.auth_status_label.color = get_color_from_hex(GREEN)\n            else:\n                self.auth_status_label.text = "No authority loaded. Import your backup or initialize authority."\n                self.auth_status_label.color = get_color_from_hex(RED)\n\n    def require_authority(self):\n        if self.public_key and self.private_key:\n            return True\n        info_popup("Authority required", "No signing authority is loaded. Import your authority backup or initialize authority first.")\n        return False\n\n    def initialize_authority(self):\n        if self.public_key and self.private_key:\n            info_popup("Authority exists", "This device already has an authority loaded.")\n            return\n        try:\n            self.public_key, self.private_key = initialize_authority_keypair()\n            self.update_authority_status()\n            self.refresh_dashboard()\n            info_popup("Authority initialized", "A new signing authority was created on this device. Back it up immediately.")\n        except Exception as e:\n            info_popup("Initialize failed", str(e))\n\n\n    def copy_public_key(self):\n        if not self.require_authority():\n            return\n        copy_to_clipboard("Public key PEM", self.public_key.save_pkcs1("PEM").decode("utf-8"))\n\n    def _refresh_everything(self):\n        self.refresh_dashboard()\n        self.refresh_license_list()\n        self.refresh_revocation_box()\n\n    def _write_authority_payload(self, payload):\n        private_pem = str(payload.get("private_key_pem", "")).strip()\n        public_pem = str(payload.get("public_key_pem", "")).strip()\n        if not private_pem or not public_pem:\n            raise ValueError("Backup does not contain a valid authority keypair.")\n        with open(file_path(PRIVATE_KEY_FILE), "wb") as f:\n            f.write(private_pem.encode("utf-8"))\n        with open(file_path(PUBLIC_KEY_FILE), "wb") as f:\n            f.write(public_pem.encode("utf-8"))\n        self.public_key, self.private_key = load_existing_keypair()\n        self.update_authority_status()\n\n    def _write_license_payload(self, payload):\n        records = payload.get("licenses", [])\n        if not isinstance(records, list):\n            raise ValueError("Backup does not contain a valid license list.")\n        save_json(file_path(LICENSE_DB_FILE), records)\n        self.store = LicenseStore()\n\n    def _apply_revocation_bundle_to_store(self, bundle):\n        if not isinstance(bundle, dict):\n            raise ValueError("Revocation JSON is invalid.")\n        payload = bundle.get("payload") if isinstance(bundle.get("payload"), dict) else bundle\n        revoked_ids = payload.get("revoked_ids", []) if isinstance(payload, dict) else []\n        revoked_ids = {str(x).strip() for x in revoked_ids if str(x).strip()}\n        changed = False\n        if revoked_ids:\n            for rec in self.store.records:\n                lid = str(rec.get("license_id", "")).strip()\n                if lid in revoked_ids and rec.get("status") != "revoked":\n                    rec["status"] = "revoked"\n                    rec["revoked_at"] = utc_now_iso()\n                    changed = True\n            if changed:\n                self.store.save()\n        save_json(file_path(REVOKED_EXPORT_FILE), bundle)\n        return len(revoked_ids), changed\n\n    def _finish_authority_import(self, bundle):\n        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}\n        self._write_authority_payload(payload)\n        self._refresh_everything()\n\n    def _finish_license_list_import(self, bundle):\n        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}\n        self._write_license_payload(payload)\n        self._refresh_everything()\n\n    def _finish_full_backup_import(self, bundle):\n        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}\n        self._write_authority_payload(payload)\n        self._write_license_payload(payload)\n        revoked_bundle = payload.get("revoked_bundle", {})\n        if revoked_bundle:\n            self._apply_revocation_bundle_to_store(revoked_bundle)\n        self._refresh_everything()\n\n    def _paste_into_widget(self, widget, empty_message="There is no backup content in the clipboard."):\n        try:\n            pasted = Clipboard.paste() or ""\n            if not pasted.strip():\n                info_popup("Clipboard empty", empty_message)\n                return\n            widget.text = pasted\n        except Exception as e:\n            info_popup("Paste failed", str(e))\n\n    def _open_backup_file_picker(self, title_text, folder, backup_files, on_select):\n        if not backup_files:\n            info_popup("No backup file found", f"No backup file was found in:\\n{folder}")\n            return\n\n        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))\n        title = Label(\n            text=f"Select backup file from:\\n{folder}",\n            color=get_color_from_hex(TEXT),\n            halign="left",\n            valign="middle",\n            text_size=(dp(300), None),\n            size_hint_y=None,\n        )\n        title.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(48), val[1] + dp(8))))\n        content.add_widget(title)\n\n        scroll = ScrollView(do_scroll_x=False, size_hint=(1, 1))\n        file_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)\n        file_box.bind(minimum_height=file_box.setter("height"))\n\n        popup = Popup(\n            title=title_text,\n            content=content,\n            size_hint=(0.92, 0.8),\n            separator_color=get_color_from_hex(GREEN),\n            background_color=get_color_from_hex(CARD),\n        )\n\n        for path in backup_files:\n            name = os.path.basename(path)\n            try:\n                stamp = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")\n            except Exception:\n                stamp = "Unknown time"\n            btn = RoundedButton(\n                text=f"{name}\\n{stamp}",\n                size_hint_y=None,\n                height=dp(68),\n                halign="left",\n                valign="middle",\n                text_size=(dp(260), None),\n                bg_hex="#182432",\n                text_color=get_color_from_hex(TEXT),\n            )\n            btn.bind(on_release=lambda *_ , selected_path=path, pop=popup: on_select(selected_path, pop))\n            file_box.add_widget(btn)\n\n        scroll.add_widget(file_box)\n        content.add_widget(scroll)\n\n        close_btn = make_button("Close", RED)\n        close_btn.bind(on_release=popup.dismiss)\n        content.add_widget(close_btn)\n        popup.open()\n\n    def generate_authority_backup(self):\n        if not self.require_authority():\n            return\n        try:\n            blob = build_authority_backup_blob(self.backup_password_input.text.strip())\n            self.backup_output.text = blob\n            info_popup("Backup generated", "Encrypted authority-only backup generated successfully.")\n        except Exception as e:\n            info_popup("Backup failed", str(e))\n\n    def save_authority_backup(self):\n        text = self.backup_output.text.strip() if hasattr(self, "backup_output") else ""\n        if not text:\n            info_popup("Nothing to save", "Generate an authority backup first.")\n            return\n        path = authority_backup_export_path()\n        with open(path, "w", encoding="utf-8") as f:\n            f.write(text)\n        info_popup("Saved", f"Authority backup saved to:\\n{path}")\n\n    def import_authority_backup(self):\n        try:\n            blob_text = self.import_backup_input.text.strip()\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_authority_import(bundle)\n            info_popup("Import successful", "Authority backup imported successfully. Local license list was not changed.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_backup_from_clipboard(self):\n        self._paste_into_widget(self.import_backup_input)\n\n    def open_auth_file_picker(self):\n        self._open_backup_file_picker("Import Auth File", authority_backup_dir(), list_authority_backup_files(), self.import_authority_from_file)\n\n    def import_authority_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_backup_input"):\n                self.import_backup_input.text = blob_text\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_authority_import(bundle)\n            if popup is not None:\n                popup.dismiss()\n            info_popup("Import successful", f"Authority file imported successfully from:\\n{backup_path}\\n\\nLocal license list was not changed.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def generate_license_list_backup(self):\n        try:\n            blob = build_license_list_backup_blob(self.backup_password_input.text.strip(), self.store.records)\n            self.license_backup_output.text = blob\n            info_popup("Backup generated", "Encrypted license-list backup generated successfully.")\n        except Exception as e:\n            info_popup("Backup failed", str(e))\n\n    def save_license_list_backup(self):\n        text = self.license_backup_output.text.strip() if hasattr(self, "license_backup_output") else ""\n        if not text:\n            info_popup("Nothing to save", "Generate a license-list backup first.")\n            return\n        path = license_list_backup_export_path()\n        with open(path, "w", encoding="utf-8") as f:\n            f.write(text)\n        info_popup("Saved", f"License-list backup saved to:\\n{path}")\n\n    def import_license_list_backup(self):\n        try:\n            blob_text = self.import_license_backup_input.text.strip()\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_license_list_import(bundle)\n            info_popup("Import successful", "License-list backup imported successfully. Authority keys were not changed.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_license_backup_from_clipboard(self):\n        self._paste_into_widget(self.import_license_backup_input)\n\n    def open_license_backup_file_picker(self):\n        self._open_backup_file_picker("Import License Backup", license_list_backup_dir(), list_license_list_backup_files(), self.import_license_backup_from_file)\n\n    def import_license_backup_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_license_backup_input"):\n                self.import_license_backup_input.text = blob_text\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_license_list_import(bundle)\n            if popup is not None:\n                popup.dismiss()\n            info_popup("Import successful", f"License-list backup imported successfully from:\\n{backup_path}")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def generate_full_backup(self):\n        if not self.require_authority():\n            return\n        try:\n            blob = build_full_backup_blob(self.backup_password_input.text.strip(), self.store.records)\n            self.full_backup_output.text = blob\n            info_popup("Backup generated", "Encrypted full backup generated successfully.")\n        except Exception as e:\n            info_popup("Backup failed", str(e))\n\n    def save_full_backup(self):\n        text = self.full_backup_output.text.strip() if hasattr(self, "full_backup_output") else ""\n        if not text:\n            info_popup("Nothing to save", "Generate a full backup first.")\n            return\n        path = full_backup_export_path()\n        with open(path, "w", encoding="utf-8") as f:\n            f.write(text)\n        info_popup("Saved", f"Full backup saved to:\\n{path}")\n\n    def import_full_backup(self):\n        try:\n            blob_text = self.import_full_backup_input.text.strip()\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_full_backup_import(bundle)\n            info_popup("Import successful", "Full backup imported successfully.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_full_backup_from_clipboard(self):\n        self._paste_into_widget(self.import_full_backup_input)\n\n    def open_full_backup_file_picker(self):\n        self._open_backup_file_picker("Import Full Backup", full_backup_dir(), list_full_backup_files(), self.import_full_backup_from_file)\n\n    def import_full_backup_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_full_backup_input"):\n                self.import_full_backup_input.text = blob_text\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_full_backup_import(bundle)\n            if popup is not None:\n                popup.dismiss()\n            info_popup("Import successful", f"Full backup imported successfully from:\\n{backup_path}")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_revocation_from_clipboard(self):\n        self._paste_into_widget(self.import_revocation_input, "There is no revocation JSON in the clipboard.")\n\n    def open_revocation_file_picker(self):\n        self._open_backup_file_picker("Import Revocation JSON", revocation_backup_dir(), list_revocation_backup_files(), self.import_revocation_from_file)\n\n    def import_revocation_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_revocation_input"):\n                self.import_revocation_input.text = blob_text\n            self._finish_revocation_import(blob_text)\n            if popup is not None:\n                popup.dismiss()\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def _finish_revocation_import(self, blob_text):\n        bundle = json.loads(blob_text)\n        revoked_count, matched_updates = self._apply_revocation_bundle_to_store(bundle)\n        self._refresh_everything()\n        info_popup("Revocation import complete", f"Imported revocation JSON with {revoked_count} revoked ID(s). Matching local licenses updated: {\'yes\' if matched_updates else \'no\'}.")\n\n    def import_revocation_bundle(self):\n        try:\n            blob_text = self.import_revocation_input.text.strip()\n            self._finish_revocation_import(blob_text)\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def get_compact_device_label(self, device_code):\n            device_code = str(device_code or \'\').strip()\n            if not device_code:\n                return \'No device\'\n            return device_code[-8:] if len(device_code) > 8 else device_code\n\n    def get_compact_issued_label(self, issued_at):\n            txt = str(issued_at or \'\').strip()\n            if not txt:\n                return \'No issue date\'\n            return txt.replace(\'T\', \' \')[:16].replace(\'Z\', \'\')\n\n    def show_license_details(self, rec):\n            details = [\n                f"License ID: {rec.get(\'license_id\', \'\')}",\n                f"Tier: {str(rec.get(\'tier\', \'\')).upper()}",\n                f"Status: {str(rec.get(\'status\', \'active\')).upper()}",\n                f"Source: {rec.get(\'source\', \'\')}",\n                f"Device Code: {rec.get(\'device_code\', \'\') or \'Not bound\'}",\n                f"Issued: {rec.get(\'issued_at\', \'\')}",\n            ]\n            if rec.get(\'expiry\'):\n                details.append(f"Expiry: {rec.get(\'expiry\')}")\n            if rec.get(\'label\'):\n                details.append(f"Label: {rec.get(\'label\')}")\n            if rec.get(\'customer_note\'):\n                details.append(f"Note: {rec.get(\'customer_note\')}")\n\n            content = BoxLayout(orientation=\'vertical\', padding=dp(12), spacing=dp(10))\n            body = Label(\n                text=\'\\n\'.join(details),\n                color=get_color_from_hex(TEXT),\n                halign=\'left\',\n                valign=\'top\',\n                text_size=(dp(300), None),\n                size_hint_y=None,\n            )\n            body.bind(texture_size=lambda inst, val: setattr(inst, \'height\', max(dp(120), val[1])))\n            content.add_widget(body)\n\n            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n            copy_id_btn = make_button(\'Copy ID\', UI_CYAN)\n            copy_code_btn = make_button(\'Copy Code\', UI_CYAN)\n            delete_btn = make_button(\'Delete\', RED)\n            row.add_widget(copy_id_btn)\n            row.add_widget(copy_code_btn)\n            row.add_widget(delete_btn)\n            content.add_widget(row)\n\n            close_btn = make_button(\'Close\', UI_CYAN)\n            content.add_widget(close_btn)\n\n            popup = Popup(\n                title=\'License Details\',\n                content=content,\n                size_hint=(0.92, 0.68),\n                separator_color=get_color_from_hex(GREEN),\n                background_color=get_color_from_hex(CARD),\n            )\n            copy_id_btn.bind(on_release=lambda *_: copy_to_clipboard(\'License ID\', rec.get(\'license_id\', \'\')))\n            copy_code_btn.bind(on_release=lambda *_: copy_to_clipboard(\'Activation code\', rec.get(\'activation_code\', \'\')))\n            delete_btn.bind(on_release=lambda *_: self.confirm_delete_license(rec.get(\'license_id\', \'\'), popup))\n            close_btn.bind(on_release=popup.dismiss)\n            popup.open()\n\n    def collect_github_settings(self):\n            return {\n                \'owner\': self.github_owner_input.text.strip(),\n                \'repo\': self.github_repo_input.text.strip(),\n                \'branch\': self.github_branch_input.text.strip() or \'main\',\n                \'path\': self.github_path_input.text.strip().lstrip(\'/\'),\n                \'token\': self.github_token_input.text.strip(),\n            }\n\n    def update_github_raw_url(self, *_):\n            if not hasattr(self, \'github_raw_url_input\'):\n                return\n            cfg = self.collect_github_settings() if hasattr(self, \'github_owner_input\') else dict(self.github_config)\n            self.github_raw_url_input.text = build_github_raw_url(cfg.get(\'owner\', \'\'), cfg.get(\'repo\', \'\'), cfg.get(\'branch\', \'main\'), cfg.get(\'path\', REVOKED_EXPORT_FILE))\n\n    def save_github_settings(self):\n            cfg = self.collect_github_settings()\n            save_github_upload_config(cfg)\n            self.github_config = load_github_upload_config()\n            self.update_github_raw_url()\n            info_popup(\'Saved\', \'GitHub upload settings saved on this admin device.\')\n\n    def upload_revocation_to_github(self):\n            if not self.require_authority():\n                return\n            cfg = self.collect_github_settings()\n            missing = [name for name, value in [(\'owner\', cfg[\'owner\']), (\'repo\', cfg[\'repo\']), (\'branch\', cfg[\'branch\']), (\'path\', cfg[\'path\']), (\'token\', cfg[\'token\'])] if not value]\n            if missing:\n                info_popup(\'Missing fields\', f"Fill these GitHub fields first: {\', \'.join(missing)}")\n                return\n\n            bundle = build_revocation_bundle(self.store.records, self.private_key)\n            payload_text = json.dumps(bundle, indent=2)\n            api_url = f"https://api.github.com/repos/{cfg[\'owner\']}/{cfg[\'repo\']}/contents/{cfg[\'path\']}"\n            headers = {\n                \'Accept\': \'application/vnd.github+json\',\n                \'Authorization\': f"Bearer {cfg[\'token\']}",\n                \'X-GitHub-Api-Version\': \'2022-11-28\',\n            }\n            body = {\n                \'message\': f"Update revoked licenses at {utc_now_iso()}",\n                \'content\': base64.b64encode(payload_text.encode(\'utf-8\')).decode(\'ascii\'),\n                \'branch\': cfg[\'branch\'],\n            }\n            try:\n                existing = requests.get(api_url, headers=headers, timeout=20)\n                if existing.status_code == 200:\n                    existing_data = existing.json()\n                    if existing_data.get(\'sha\'):\n                        body[\'sha\'] = existing_data[\'sha\']\n                elif existing.status_code not in (404,):\n                    raise RuntimeError(f"GitHub lookup failed: {existing.status_code} {existing.text[:180]}")\n\n                resp = requests.put(api_url, headers=headers, json=body, timeout=25)\n                if resp.status_code not in (200, 201):\n                    raise RuntimeError(f"GitHub upload failed: {resp.status_code} {resp.text[:220]}")\n\n                save_github_upload_config(cfg)\n                self.github_config = load_github_upload_config()\n                self.refresh_revocation_box()\n                self.update_github_raw_url()\n                info_popup(\'Uploaded\', f"Revocation file uploaded successfully to:\\n{self.github_raw_url_input.text}")\n            except Exception as e:\n                info_popup(\'Upload failed\', str(e))\n\n    def build_and_store_license(self, tier, source, device_code, label=\'\', note=\'\', expiry=\'\'):\n            if tier not in (\'demo\', \'pro\', \'pro_plus\'):\n                raise ValueError(\'Choose demo, pro, or pro_plus.\')\n            if source not in (\'crypto\', \'bank\', \'promo\', \'partner\', \'personal\', \'test\'):\n                raise ValueError(\'Choose one of the payment/source types.\')\n            if not device_code:\n                raise ValueError("Enter the customer\'s Device Code from the app.")\n\n            license_id = \'LIC-\' + secrets.token_hex(4).upper()\n            payload = {\n                \'app\': \'casino_tools_pro\',\n                \'schema\': 1,\n                \'license_id\': license_id,\n                \'tier\': tier,\n                \'source\': source,\n                \'device_code\': device_code,\n                \'label\': label,\n                \'issued_at\': utc_now_iso(),\n            }\n            if note:\n                payload[\'note\'] = note\n            if expiry:\n                payload[\'expires_at\'] = expiry\n\n            signature = sign_payload(self.private_key, payload)\n            activation_code = encode_activation_code(payload, signature)\n            record = {\n                \'license_id\': license_id,\n                \'tier\': tier,\n                \'source\': source,\n                \'device_code\': device_code,\n                \'label\': label,\n                \'customer_note\': note,\n                \'expiry\': expiry,\n                \'expires_at\': expiry,\n                \'issued_at\': payload[\'issued_at\'],\n                \'status\': \'active\',\n                \'activation_code\': activation_code,\n                \'signature_valid\': verify_signature(self.public_key, payload, signature),\n            }\n            self.store.add(record)\n            self._last_license_id = license_id\n            self.generated_code_input.text = activation_code\n            self.refresh_dashboard()\n            self.refresh_license_list()\n            self.refresh_revocation_box()\n            return record\n\n    def generate_test_license(self):\n            if not self.require_authority():\n                return\n            try:\n                device_code = self.device_input.text.strip().upper()\n                if not device_code:\n                    raise ValueError("Enter the customer\'s Device Code before generating a test license.")\n                expiry = self.expiry_input.text.strip() or (datetime.utcnow() + timedelta(days=7)).strftime(\'%Y-%m-%d\')\n                label = self.label_input.text.strip() or \'Internal Test\'\n                note = self.note_input.text.strip() or \'Admin-generated test key\'\n                self.build_and_store_license(\'pro_plus\', \'test\', device_code, label=label, note=note, expiry=expiry)\n                info_popup(\'Test license generated\', \'7-day style test Pro+ license created successfully. Change the expiry field first if you want a different end date.\')\n            except Exception as e:\n                info_popup(\'Test license failed\', str(e))\n\n    def refresh_dashboard(self):\n        if not hasattr(self, "dashboard_box"):\n            return\n        self.dashboard_box.clear_widgets()\n        records = self.store.records\n        total = len(records)\n        active = len([r for r in records if r.get("status") == "active"])\n        revoked = len([r for r in records if r.get("status") == "revoked"])\n        demo = len([r for r in records if r.get("tier") == "demo"])\n        pro = len([r for r in records if r.get("tier") == "pro"])\n        pro_plus = len([r for r in records if r.get("tier") == "pro_plus"])\n\n        authority_card = SectionCard("Authority status")\n        if self.public_key and self.private_key:\n            authority_card.add_widget(make_label("Authority loaded", GREEN))\n            authority_card.add_widget(make_label(f"Data folder: {app_data_dir()}", height=dp(38)))\n        else:\n            authority_card.add_widget(make_label("No authority loaded. Import your backup or initialize authority.", RED, height=dp(38)))\n        self.dashboard_box.add_widget(authority_card)\n\n        stats = SectionCard("License totals")\n        for t in [\n            f"Total licenses: {total}",\n            f"Active: {active}",\n            f"Revoked: {revoked}",\n            f"Demo: {demo}",\n            f"Pro: {pro}",\n            f"Pro+: {pro_plus}",\n        ]:\n            stats.add_widget(make_label(t, GREEN if "Active" in t else (RED if "Revoked" in t else TEXT)))\n        self.dashboard_box.add_widget(stats)\n\n        latest = SectionCard("Latest issued")\n        if records:\n            for rec in records[:8]:\n                latest.add_widget(make_label(\n                    f"{rec[\'license_id\']}  |  {rec[\'tier\']}  |  {rec.get(\'source\',\'\')}  |  {rec.get(\'status\',\'active\')}",\n                    height=dp(22),\n                ))\n        else:\n            latest.add_widget(make_label("No licenses yet."))\n        self.dashboard_box.add_widget(latest)\n\n    def get_filtered_license_records(self):\n        query = (self.search_input.text or "").strip().lower() if hasattr(self, "search_input") else ""\n        status_filter = getattr(getattr(self, \'license_status_spinner\', None), \'text\', \'all\').strip().lower()\n        tier_filter = getattr(getattr(self, \'license_tier_spinner\', None), \'text\', \'all\').strip().lower()\n        source_filter = getattr(getattr(self, \'license_source_spinner\', None), \'text\', \'all\').strip().lower()\n        sort_mode = getattr(getattr(self, \'license_sort_spinner\', None), \'text\', \'newest\').strip().lower()\n\n        visible = []\n        for rec in self.store.records:\n            hay = " ".join([\n                rec.get("license_id", ""),\n                rec.get("device_code", ""),\n                rec.get("tier", ""),\n                rec.get("source", ""),\n                rec.get("label", ""),\n                rec.get("customer_note", ""),\n                rec.get("status", ""),\n            ]).lower()\n            if query and query not in hay:\n                continue\n            if status_filter != \'all\' and str(rec.get(\'status\', \'active\')).lower() != status_filter:\n                continue\n            if tier_filter != \'all\' and str(rec.get(\'tier\', \'\')).lower() != tier_filter:\n                continue\n            if source_filter != \'all\' and str(rec.get(\'source\', \'\')).lower() != source_filter:\n                continue\n            visible.append(rec)\n\n        if sort_mode == \'oldest\':\n            visible.sort(key=lambda r: str(r.get(\'issued_at\', \'\')))\n        elif sort_mode == \'tier\':\n            visible.sort(key=lambda r: (str(r.get(\'tier\', \'\')), str(r.get(\'issued_at\', \'\'))), reverse=False)\n            visible.reverse()\n        elif sort_mode == \'status\':\n            visible.sort(key=lambda r: (str(r.get(\'status\', \'active\')), str(r.get(\'issued_at\', \'\'))), reverse=False)\n            visible.reverse()\n        else:\n            visible.sort(key=lambda r: str(r.get(\'issued_at\', \'\')), reverse=True)\n        return visible\n\n    def export_visible_licenses_csv(self):\n        records = self.get_filtered_license_records()\n        if not records:\n            info_popup("Nothing to export", "There are no visible licenses to export with the current filters.")\n            return\n        export_path = license_export_path()\n        fieldnames = [\n            "license_id",\n            "tier",\n            "status",\n            "source",\n            "device_code",\n            "label",\n            "customer_note",\n            "issued_at",\n            "expiry",\n            "expires_at",\n            "revoked_at",\n            "signature_valid",\n        ]\n        with open(export_path, "w", encoding="utf-8", newline="") as f:\n            writer = csv.DictWriter(f, fieldnames=fieldnames)\n            writer.writeheader()\n            for rec in records:\n                row = {name: rec.get(name, "") for name in fieldnames}\n                writer.writerow(row)\n        info_popup("Exported", f"Visible licenses exported successfully to:\\n{export_path}")\n\n    def confirm_delete_license(self, license_id, parent_popup=None):\n        rec = self.store.find(license_id)\n        if not rec:\n            info_popup("Not found", "That license could not be found anymore.")\n            return\n\n        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))\n        message = Label(\n            text=f"Delete this license permanently?\\n\\n{license_id}\\n{str(rec.get(\'tier\', \'\')).upper()} • {str(rec.get(\'status\', \'active\')).upper()}\\n\\nUse delete mainly for test keys and clutter. Revoked licenses removed from the database will also disappear from future revocation exports.",\n            color=get_color_from_hex(TEXT),\n            halign="left",\n            valign="top",\n            text_size=(dp(300), None),\n            size_hint_y=None,\n        )\n        message.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(140), val[1])))\n        content.add_widget(message)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        cancel_btn = make_button("Cancel", UI_CYAN)\n        delete_btn = make_button("Delete", RED)\n        row.add_widget(cancel_btn)\n        row.add_widget(delete_btn)\n        content.add_widget(row)\n\n        popup = Popup(\n            title="Delete License",\n            content=content,\n            size_hint=(0.92, 0.62),\n            separator_color=get_color_from_hex(RED),\n            background_color=get_color_from_hex(CARD),\n        )\n\n        cancel_btn.bind(on_release=popup.dismiss)\n\n        def do_delete(*_):\n            removed = self.store.delete(license_id)\n            popup.dismiss()\n            if parent_popup is not None:\n                parent_popup.dismiss()\n            if removed:\n                self.refresh_dashboard()\n                self.refresh_license_list()\n                self.refresh_revocation_box()\n                info_popup("Deleted", f"{license_id} was deleted from the license database.")\n            else:\n                info_popup("Not found", "That license could not be found anymore.")\n\n        delete_btn.bind(on_release=do_delete)\n        popup.open()\n\n    def confirm_delete_visible_licenses(self):\n        records = self.get_filtered_license_records()\n        if not records:\n            info_popup("Nothing to delete", "There are no visible licenses to delete with the current filters.")\n            return\n\n        count = len(records)\n        ids = [rec.get("license_id", "") for rec in records if rec.get("license_id")]\n\n        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))\n        message = Label(\n            text=f"Delete all {count} currently visible licenses?\\n\\nThis is best used after narrowing the list to test keys with search and filters. Any revoked licenses deleted here will also disappear from future revocation exports.",\n            color=get_color_from_hex(TEXT),\n            halign="left",\n            valign="top",\n            text_size=(dp(300), None),\n            size_hint_y=None,\n        )\n        message.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(130), val[1])))\n        content.add_widget(message)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        cancel_btn = make_button("Cancel", UI_CYAN)\n        delete_btn = make_button("Delete Visible", RED)\n        row.add_widget(cancel_btn)\n        row.add_widget(delete_btn)\n        content.add_widget(row)\n\n        popup = Popup(\n            title="Delete Visible Licenses",\n            content=content,\n            size_hint=(0.92, 0.58),\n            separator_color=get_color_from_hex(RED),\n            background_color=get_color_from_hex(CARD),\n        )\n\n        cancel_btn.bind(on_release=popup.dismiss)\n\n        def do_delete(*_):\n            removed = self.store.delete_many(ids)\n            popup.dismiss()\n            self.refresh_dashboard()\n            self.refresh_license_list()\n            self.refresh_revocation_box()\n            info_popup("Deleted", f"Deleted {removed} visible license(s).")\n\n        delete_btn.bind(on_release=do_delete)\n        popup.open()\n\n    def refresh_license_list(self):\n        if not hasattr(self, "license_box"):\n            return\n\n        self.license_box.clear_widgets()\n        visible = self.get_filtered_license_records()\n\n        if not visible:\n            self.license_box.add_widget(make_label("No matching licenses found."))\n            return\n\n        for rec in visible:\n            status = str(rec.get(\'status\', \'active\')).upper()\n            source = str(rec.get(\'source\', \'\')).upper()\n            device_short = self.get_compact_device_label(rec.get(\'device_code\', \'\'))\n            issued_short = self.get_compact_issued_label(rec.get(\'issued_at\', \'\'))\n            subtitle = f"{source}  •  {status}"\n            if rec.get(\'label\'):\n                subtitle += f"  •  {rec.get(\'label\')}"\n\n            card = SectionCard(f"{rec[\'license_id\']}  •  {rec[\'tier\'].upper()}", subtitle)\n            card.add_widget(make_label(f"Device suffix: {device_short}  •  Issued: {issued_short}", height=dp(22)))\n            if rec.get(\'expiry\'):\n                card.add_widget(make_label(f"Expiry: {rec.get(\'expiry\')}", height=dp(22)))\n\n            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))\n            details_btn = make_button("Details", UI_CYAN)\n            id_btn = make_button("Copy ID", UI_CYAN)\n            revoke_btn = make_button("Revoke" if rec.get("status") != "revoked" else "Restore", RED if rec.get("status") != "revoked" else PURPLE)\n\n            details_btn.bind(on_release=lambda *_ , record=rec: self.show_license_details(record))\n            id_btn.bind(on_release=lambda *_ , lid=rec["license_id"]: copy_to_clipboard("License ID", lid))\n            revoke_btn.bind(on_release=lambda *_ , lid=rec["license_id"], status=rec.get("status"): self.toggle_revoke(lid, status))\n\n            row.add_widget(details_btn)\n            row.add_widget(id_btn)\n            row.add_widget(revoke_btn)\n            card.add_widget(row)\n            self.license_box.add_widget(card)\n\n    def refresh_revocation_box(self):\n        if not hasattr(self, "revocation_output"):\n            return\n        if not self.private_key:\n            self.revocation_output.text = ""\n            return\n        bundle = build_revocation_bundle(self.store.records, self.private_key)\n        self.revocation_output.text = json.dumps(bundle, indent=2)\n\n    def clear_generate_form(self):\n        self.device_input.text = ""\n        self.tier_spinner.text = "pro"\n        self.source_spinner.text = "crypto"\n        self.label_input.text = ""\n        self.note_input.text = ""\n        self.expiry_input.text = ""\n        self.generated_code_input.text = ""\n        self._last_license_id = ""\n\n    def generate_license(self):\n        if not self.require_authority():\n            return\n        try:\n            tier = self.tier_spinner.text.strip()\n            source = self.source_spinner.text.strip()\n            device_code = self.device_input.text.strip().upper()\n            label = self.label_input.text.strip()\n            note = self.note_input.text.strip()\n            expiry = self.expiry_input.text.strip()\n            self.build_and_store_license(tier, source, device_code, label=label, note=note, expiry=expiry)\n            info_popup("License generated", f"{tier.upper()} license created successfully.")\n        except Exception as e:\n            info_popup("License failed", str(e))\n\n    def toggle_revoke(self, license_id, status):\n        target = "revoked" if status != "revoked" else "active"\n        self.store.update(\n            license_id,\n            lambda rec: rec.update({"status": target, "revoked_at": utc_now_iso() if target == "revoked" else ""}),\n        )\n        self.refresh_dashboard()\n        self.refresh_license_list()\n        self.refresh_revocation_box()\n        info_popup("License updated", f"{license_id} is now {target.upper()}.")\n\n    def save_revocation_bundle(self):\n        if not self.require_authority():\n            return\n        bundle = build_revocation_bundle(self.store.records, self.private_key)\n        path = revocation_export_path()\n        save_json(path, bundle)\n        save_json(file_path(REVOKED_EXPORT_FILE), bundle)\n        self.refresh_revocation_box()\n        info_popup("Saved", f"Revocation file saved to:\\n{path}")\n\n\nclass LicenseManagerApp(App):\n    def build(self):\n        self.title = "Casino Tools License Manager"\n        sm = ScreenManager(transition=FadeTransition())\n        sm.add_widget(LicenseManagerScreen(name="main"))\n        return sm\n\n\nif __name__ == "__main__":\n    LicenseManagerApp().run()\n'
_CTP_NS = {'__name__': '_shv_ctp_module'}
exec(_CTP_MODULE_SOURCE, _CTP_NS)
_CTP_NS.update({
    'UI_CYAN': BLUE,
    'UI_GREEN': GREEN,
    'UI_PURPLE': PURPLE,
    'UI_ORANGE': ORANGE,
    'UI_RED': RED,
    'UI_TEAL': BLUE,
    'UI_BLUE': BLUE,
    'UI_TEXT': TEXT,
    'UI_SUBTEXT': SUBTEXT,
    'UI_BG': BG,
    'UI_CARD': CARD,
})
_CTP_NS['RoundedButton'] = RoundedButton
_CTP_NS['make_button'] = make_button
_CTP_NS['make_nav_button'] = make_nav_button
CasinoToolsLicenseManagerScreen = _CTP_NS['LicenseManagerScreen']






from kivy.animation import Animation

# --- Admin panel enhancements: darker neon buttons, dashboard, vault, customers, activity, releases, authority status ---

ADMIN_ACTIVITY_FILE = 'admin_activity_log.json'
RELEASE_TRACKER_FILE = 'release_tracker.json'
CUSTOMER_OVERRIDES_FILE = 'customer_overrides.json'

DARK_GREEN_FILL = '#103f1f'
DARK_RED_FILL = '#541919'
DARK_BLUE_FILL = '#122b52'
DARK_PURPLE_FILL = '#38204b'
DARK_ORANGE_FILL = '#5a3213'
DARK_NEUTRAL_FILL = '#151d28'


def _button_fill_for(color_hex):
    color = str(color_hex or '').lower()
    if color == str(RED).lower():
        return DARK_RED_FILL
    if color == str(BLUE).lower():
        return DARK_BLUE_FILL
    if color == str(PURPLE).lower():
        return DARK_PURPLE_FILL
    if color == str(ORANGE).lower():
        return DARK_ORANGE_FILL
    if color == str(GREEN).lower():
        return DARK_GREEN_FILL
    return DARK_NEUTRAL_FILL


def _button_border_for(color_hex):
    color = str(color_hex or '').lower()
    if color == str(RED).lower():
        return '#ff8d8d'
    if color == str(BLUE).lower():
        return '#66b8ff'
    if color == str(PURPLE).lower():
        return '#c89cff'
    if color == str(ORANGE).lower():
        return '#ffbe74'
    if color == str(GREEN).lower():
        return '#8dff96'
    return '#56ffd8'


class RoundedButton(Button):
    def __init__(self, bg_hex=GREEN, text_color=None, radius=16, border_hex=None, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        super().__init__(**kwargs)
        self._accent_hex = str(bg_hex or GREEN)
        self._fill_hex = _button_fill_for(self._accent_hex)
        self._border_hex = border_hex or _button_border_for(self._accent_hex)
        self._radius = dp(radius)
        self._inset = dp(2)
        if text_color is None:
            text_color = get_color_from_hex(TEXT)
        self.color = text_color
        self.bold = True
        with self.canvas.before:
            Color(rgba=get_color_from_hex(self._border_hex))
            self._border_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
            Color(rgba=get_color_from_hex(self._fill_hex))
            self._rounded_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[max(dp(4), self._radius - self._inset)])
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *_):
        self._border_bg.pos = self.pos
        self._border_bg.size = self.size
        self._border_bg.radius = [self._radius]
        self._rounded_bg.pos = (self.x + self._inset, self.y + self._inset)
        self._rounded_bg.size = (max(0, self.width - self._inset * 2), max(0, self.height - self._inset * 2))
        self._rounded_bg.radius = [max(dp(4), self._radius - self._inset)]


def make_button(text, color=GREEN):
    return RoundedButton(
        text=text,
        size_hint_y=None,
        height=dp(46),
        bg_hex=color,
        text_color=get_color_from_hex(TEXT),
    )


def make_nav_button(text):
    return RoundedButton(
        text=text,
        size_hint=(1, None),
        height=dp(42),
        bg_hex=BLUE,
        text_color=get_color_from_hex(TEXT),
    )


# Re-bind embedded module buttons to the darker neon style.
_CTP_NS['RoundedButton'] = RoundedButton
_CTP_NS['make_button'] = make_button
_CTP_NS['make_nav_button'] = make_nav_button
CasinoToolsLicenseManagerScreen = _CTP_NS['LicenseManagerScreen']


# ---- admin persistence helpers ----
def admin_data_path(name):
    return os.path.join(app_data_dir(), name)


def load_activity_log():
    data = load_json(admin_data_path(ADMIN_ACTIVITY_FILE), [])
    return data if isinstance(data, list) else []


def save_activity_log(entries):
    save_json(admin_data_path(ADMIN_ACTIVITY_FILE), entries)


def log_admin_activity(product, action, details=''):
    entries = load_activity_log()
    entries.insert(0, {
        'timestamp': utc_now_iso(),
        'product': str(product or 'System'),
        'action': str(action or '').strip(),
        'details': str(details or '').strip(),
    })
    save_activity_log(entries[:500])


def load_release_tracker():
    data = load_json(admin_data_path(RELEASE_TRACKER_FILE), [])
    return data if isinstance(data, list) else []


def save_release_tracker(entries):
    save_json(admin_data_path(RELEASE_TRACKER_FILE), entries)


def load_customer_overrides():
    data = load_json(admin_data_path(CUSTOMER_OVERRIDES_FILE), {})
    return data if isinstance(data, dict) else {}


def save_customer_overrides(data):
    save_json(admin_data_path(CUSTOMER_OVERRIDES_FILE), data)


def _safe_records(path):
    data = load_json(path, [])
    return data if isinstance(data, list) else []


def synapse_license_records():
    return _safe_records(file_path(LICENSE_DB_FILE))


def ctp_license_records():
    return _safe_records(admin_data_path(_CTP_NS.get('LICENSE_DB_FILE', 'licenses_db.json')))


def latest_file_from(paths):
    paths = [p for p in (paths or []) if p and os.path.exists(p)]
    if not paths:
        return ''
    return max(paths, key=lambda x: os.path.getmtime(x))


def short_time(ts):
    try:
        raw = str(ts or '').strip().replace('Z', '+00:00')
        if not raw:
            return ''
        dt = datetime.fromisoformat(raw)
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return str(ts or '')


def file_stamp(path):
    try:
        return datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
    except Exception:
        return 'Never'


def file_size_text(path):
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f'{size} B'
        if size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        return f'{size / (1024 * 1024):.2f} MB'
    except Exception:
        return '--'


def authority_fingerprint(pem_path):
    try:
        with open(pem_path, 'rb') as f:
            raw = f.read()
        return hashlib.sha256(raw).hexdigest()[:16].upper()
    except Exception:
        return 'Not loaded'


def product_backup_categories(product):
    if product == 'Synapse':
        return [
            ('Authority Backups', authority_backup_dir()),
            ('Full Backups', full_backup_dir()),
            ('License-List Backups', license_list_backup_dir()),
            ('Revocation Jsons', revocation_backup_dir()),
        ]
    return [
        ('Authority Backups', _CTP_NS['authority_backup_dir']()),
        ('Full Backups', _CTP_NS['full_backup_dir']()),
        ('License-List Backups', _CTP_NS['license_list_backup_dir']()),
        ('Revocation Jsons', _CTP_NS['revocation_backup_dir']()),
    ]


def product_summary(product):
    if product == 'Synapse':
        records = synapse_license_records()
        pub_path = file_path(PUBLIC_KEY_FILE)
        authority_loaded = os.path.exists(pub_path)
        backup_dirs = [authority_backup_dir(), full_backup_dir(), license_list_backup_dir(), revocation_backup_dir()]
    else:
        records = ctp_license_records()
        pub_path = admin_data_path(_CTP_NS.get('PUBLIC_KEY_FILE', 'license_public.pem'))
        authority_loaded = os.path.exists(pub_path)
        backup_dirs = [_CTP_NS['authority_backup_dir'](), _CTP_NS['full_backup_dir'](), _CTP_NS['license_list_backup_dir'](), _CTP_NS['revocation_backup_dir']()]
    active = len([r for r in records if str(r.get('status', 'active')).lower() == 'active'])
    revoked = len([r for r in records if str(r.get('status', '')).lower() == 'revoked'])
    latest_paths = []
    for d in backup_dirs:
        try:
            latest_paths.extend([os.path.join(d, n) for n in os.listdir(d)])
        except Exception:
            pass
    latest = latest_file_from(latest_paths)
    return {
        'product': product,
        'active': active,
        'revoked': revoked,
        'licenses': len(records),
        'authority_loaded': authority_loaded,
        'fingerprint': authority_fingerprint(pub_path),
        'last_backup': file_stamp(latest) if latest else 'Never',
    }


def aggregated_customer_rows():
    rows = []
    overrides = load_customer_overrides()
    for product, records in (('Synapse', synapse_license_records()), ('Casino Tools Pro', ctp_license_records())):
        for rec in records:
            lid = str(rec.get('license_id', '')).strip()
            if not lid:
                continue
            ov = overrides.get(lid, {}) if isinstance(overrides, dict) else {}
            name = str(ov.get('name') or rec.get('customer_name') or rec.get('label') or 'Unnamed Customer').strip()
            contact = str(ov.get('contact') or rec.get('customer_email') or '').strip()
            note = str(ov.get('note') or rec.get('note') or rec.get('customer_note') or '').strip()
            rows.append({
                'license_id': lid,
                'product': product,
                'tier': str(rec.get('tier', '')).upper(),
                'status': str(rec.get('status', 'active')).upper(),
                'payment': str(rec.get('source', '')).strip(),
                'issued_at': str(rec.get('issued_at', '') or rec.get('created_at', '')).strip(),
                'name': name,
                'contact': contact,
                'note': note,
                'device_code': str(rec.get('device_code', '')).strip(),
            })
    rows.sort(key=lambda r: r.get('issued_at', ''), reverse=True)
    return rows


def export_customers_csv(rows):
    if not rows:
        return ''
    out_dir = admin_export_dir('Customers')
    path = os.path.join(out_dir, f'customers_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['product', 'license_id', 'name', 'contact', 'tier', 'status', 'payment', 'issued_at', 'device_code', 'note'])
        writer.writeheader()
        writer.writerows(rows)
    return path


def export_activity_csv(rows):
    if not rows:
        return ''
    out_dir = admin_export_dir('Activity Logs')
    path = os.path.join(out_dir, f'activity_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv')
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'product', 'action', 'details'])
        writer.writeheader()
        writer.writerows(rows)
    return path


def show_placeholder(title):
    info_popup(title, f'{title} is reserved for the next phase of SH Vertex Admin Panel.')


# ---- activity log wrappers for both licensing managers ----
def _patch_manager_logging(cls, product_name):
    if getattr(cls, '_shv_activity_patch_done', False):
        return

    def wrap(method_name, builder):
        old = getattr(cls, method_name, None)
        if not callable(old):
            return
        def wrapped(self, *args, **kwargs):
            result = old(self, *args, **kwargs)
            try:
                action, details = builder(self, result, args, kwargs)
                if action:
                    log_admin_activity(product_name, action, details)
            except Exception:
                pass
            return result
        setattr(cls, method_name, wrapped)

    wrap('build_and_store_license', lambda self, result, args, kwargs: ('License generated', getattr(self, '_last_license_id', '') or str(args[2] if len(args) > 2 else ''))) 
    wrap('toggle_revoke', lambda self, result, args, kwargs: (('License restored' if len(args) > 1 and str(args[1]).lower() == 'revoked' else 'License revoked'), str(args[0] if args else ''))) 
    wrap('save_authority_backup', lambda self, result, args, kwargs: ('Authority backup saved', 'Authority-only backup created'))
    wrap('save_license_list_backup', lambda self, result, args, kwargs: ('License-list backup saved', 'License-list backup created'))
    wrap('save_full_backup', lambda self, result, args, kwargs: ('Full backup saved', 'Full backup created'))
    wrap('save_revocation_bundle', lambda self, result, args, kwargs: ('Revocation export saved', 'Signed revocation JSON exported'))
    wrap('import_authority_backup', lambda self, result, args, kwargs: ('Authority backup imported', 'Authority imported from paste'))
    wrap('import_license_list_backup', lambda self, result, args, kwargs: ('License-list backup imported', 'License list imported from paste'))
    wrap('import_full_backup', lambda self, result, args, kwargs: ('Full backup imported', 'Full backup imported from paste'))
    cls._shv_activity_patch_done = True


_patch_manager_logging(LicenseManagerScreen, 'Synapse')
_patch_manager_logging(CasinoToolsLicenseManagerScreen, 'Casino Tools Pro')


def build_stat_chip(value, label, accent=GREEN):
    card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(68), padding=dp(8), spacing=dp(2))
    with card.canvas.before:
        Color(rgba=get_color_from_hex(CARD))
        card._bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(16)])
        Color(rgba=get_color_from_hex(_button_border_for(accent)))
        card._bar = RoundedRectangle(pos=card.pos, size=(dp(3), card.height), radius=[dp(2)])
    def _upd(*_):
        card._bg.pos = card.pos
        card._bg.size = card.size
        card._bar.pos = card.pos
        card._bar.size = (dp(3), card.height)
    card.bind(pos=_upd, size=_upd)
    v = Label(text=str(value), color=get_color_from_hex(TEXT), bold=True, font_size='18sp', size_hint_y=None, height=dp(28))
    l = Label(text=str(label), color=get_color_from_hex(SUBTEXT), font_size='13sp', size_hint_y=None, height=dp(18))
    card.add_widget(v)
    card.add_widget(l)
    return card


def build_top_title(text, size='28sp'):
    lbl = Label(text=text, color=get_color_from_hex(TEXT), bold=True, font_size=size, size_hint_y=None, height=dp(56), halign='center', valign='middle')
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    return lbl


def _apply_admin_title_animation(label):
    try:
        from kivy.animation import Animation
        Animation.cancel_all(label)
        label.opacity = 1.0
        anim = Animation(opacity=0.78, duration=1.35, t='in_out_sine') + Animation(opacity=1.0, duration=1.35, t='in_out_sine')
        anim.repeat = True
        anim.start(label)
    except Exception:
        pass


def build_screen_header(title, subtitle='', back_target='home', extra=None):
    box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(96), spacing=dp(8))
    title_lbl = Label(text=title, color=get_color_from_hex(TEXT), bold=True, font_size='24sp', size_hint_y=None, height=dp(42), halign='center', valign='middle')
    title_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    box.add_widget(title_lbl)
    if subtitle:
        sub_lbl = Label(text=subtitle, color=get_color_from_hex(SUBTEXT), font_size='12sp', size_hint_y=None, height=dp(18), halign='center', valign='middle')
        sub_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        box.add_widget(sub_lbl)
    row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
    if back_target:
        back_btn = make_button('Back', UI_CYAN)
        back_btn.bind(on_release=lambda *_: setattr(App.get_running_app().root, 'current', back_target))
        row.add_widget(back_btn)
    if extra:
        for label, target in extra:
            btn = make_button(label, UI_CYAN)
            btn.bind(on_release=lambda *_ , t=target: setattr(App.get_running_app().root, 'current', t) if isinstance(t, str) else t())
            row.add_widget(btn)
    box.add_widget(row)
    return box


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        from kivy.graphics import Color as _GC, Rectangle as _GR
        root = BoxLayout(orientation='vertical', padding=[dp(40), 0, dp(40), 0], spacing=0)
        root.add_widget(Widget())

        # Large SHV monogram
        self.logo_lbl = Label(
            text='SHV',
            color=(0, 0.91, 0, 0),
            bold=True,
            font_size='78sp',
            size_hint_y=None,
            height=dp(96),
            halign='center',
        )
        self.logo_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.logo_lbl)

        # Thin neon divider bar
        self._bar = Widget(size_hint_y=None, height=dp(3))
        with self._bar.canvas:
            self._bar_color_obj = _GC(rgba=(0, 0.91, 0, 0))
            self._bar_rect_obj = _GR(pos=self._bar.pos, size=self._bar.size)
        self._bar.bind(pos=self._upd_bar, size=self._upd_bar)
        root.add_widget(self._bar)

        root.add_widget(Widget(size_hint_y=None, height=dp(12)))

        # Company name
        self.title_lbl = Label(
            text='SH VERTEX TECHNOLOGIES',
            color=(1, 1, 1, 0),
            bold=True,
            font_size='15sp',
            size_hint_y=None,
            height=dp(26),
            halign='center',
        )
        self.title_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.title_lbl)

        # Sub label
        self.sub_lbl = Label(
            text='Admin Panel',
            color=(0.69, 0.73, 0.89, 0),
            font_size='13sp',
            size_hint_y=None,
            height=dp(22),
            halign='center',
        )
        self.sub_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        root.add_widget(self.sub_lbl)

        root.add_widget(Widget(size_hint_y=None, height=dp(18)))

        # Animated loading dots
        dot_row = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(10))
        dot_row.add_widget(Widget())
        self._dots = []
        for _ in range(3):
            d = Label(text='•', color=(0, 0.91, 0, 0), font_size='22sp', size_hint_x=None, width=dp(22))
            self._dots.append(d)
            dot_row.add_widget(d)
        dot_row.add_widget(Widget())
        root.add_widget(dot_row)

        root.add_widget(Widget())
        self.add_widget(root)
        self._do_splash_anim()

    def _upd_bar(self, *_):
        self._bar_rect_obj.pos = self._bar.pos
        self._bar_rect_obj.size = self._bar.size

    def _do_splash_anim(self):
        # SHV logo: fade in
        Animation(color=(0, 0.91, 0, 1), d=0.55, t='out_quad').start(self.logo_lbl)
        # Bar appears right after logo
        def _show_bar(*_): self._bar_color_obj.rgba = (0, 0.91, 0, 1)
        Clock.schedule_once(_show_bar, 0.5)
        # Company name fades in
        Animation(color=(1, 1, 1, 1), d=0.45, t='out_quad').start(self.title_lbl)
        Animation(color=(0.69, 0.73, 0.89, 1), d=0.55, t='out_quad').start(self.sub_lbl)
        # Staggered dots
        for i, dot in enumerate(self._dots):
            def _show(dt, d=dot):
                (Animation(color=(0, 0.91, 0, 1), d=0.25) + Animation(color=(0, 0.5, 0, 0.6), d=0.25)).start(d)
            Clock.schedule_once(_show, 0.75 + i * 0.2)
        # Navigate after the startup sound has had time to finish.
        startup_len = 0.0
        try:
            app = App.get_running_app()
            startup_len = float(getattr(app, '_admin_last_startup_duration', 0.0) or 0.0)
            if startup_len <= 0:
                startup_path = _resolve_admin_sound_path('shv startup.wav', 'shvstartup.wav')
                if startup_path:
                    probe = SoundLoader.load(startup_path)
                    startup_len = float(getattr(probe, 'length', 0.0) or 0.0)
                    if probe is not None:
                        try:
                            probe.unload()
                        except Exception:
                            pass
        except Exception:
            startup_len = 0.0
        hold_for = max(2.0, 0.75 + startup_len + 0.2)
        Clock.schedule_once(lambda *_: setattr(self.manager, 'current', 'home'), hold_for)

class AdminHomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        self.scroll = ScrollView(do_scroll_x=False)
        self.root_box = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(18)], spacing=dp(10), size_hint_y=None)
        self.root_box.bind(minimum_height=self.root_box.setter('height'))
        self.scroll.add_widget(self.root_box)
        self.add_widget(self.scroll)
        self.refresh_ui()

    def refresh_ui(self, *_):
        self.root_box.clear_widgets()
        title_lbl = build_top_title('SH VERTEX ADMIN PANEL', '30sp')
        self.root_box.add_widget(title_lbl)
        _apply_admin_title_animation(title_lbl)

        syn = product_summary('Synapse')
        ctp = product_summary('Casino Tools Pro')
        dash = SectionCard('PRODUCT DASHBOARD', 'Central view of active licenses, authority health, and the latest backup across products.')
        for summary, accent, screen_name in ((syn, GREEN, 'synapse_manager'), (ctp, PURPLE, 'casino_manager')):
            card = SectionCard(summary['product'], f"Authority: {'Loaded' if summary['authority_loaded'] else 'Missing'}  •  Fingerprint: {summary['fingerprint']}")
            grid = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(72))
            grid.add_widget(build_stat_chip(summary['active'], 'Active', accent))
            grid.add_widget(build_stat_chip(summary['revoked'], 'Revoked', RED))
            grid.add_widget(build_stat_chip(summary['licenses'], 'Total', BLUE))
            grid.add_widget(build_stat_chip(summary['last_backup'], 'Last Backup', UI_CYAN))
            card.add_widget(grid)
            open_btn = make_button(f"Open {summary['product']}", accent)
            open_btn.bind(on_release=lambda *_ , s=screen_name: setattr(self.manager, 'current', s))
            card.add_widget(open_btn)
            dash.add_widget(card)
        self.root_box.add_widget(dash)

        synapse_summary = synapse_project_summary()
        synapse_card = SectionCard('SYNAPSE', 'Embedded internal workspace tools for long-term use inside the admin panel.')
        syn_stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
        syn_stats.add_widget(build_stat_chip(synapse_summary['total'], 'Projects', GREEN))
        syn_stats.add_widget(build_stat_chip(synapse_summary['active'], 'Active', BLUE))
        syn_stats.add_widget(build_stat_chip(synapse_summary['latest'], 'Updated', UI_CYAN))
        synapse_card.add_widget(syn_stats)
        syn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        syn_projects_btn = make_button('Projects', GREEN)
        syn_time_btn = make_button('Universal Time', UI_CYAN)
        syn_projects_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'synapse_projects'))
        syn_time_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'synapse_universal_time'))
        syn_row.add_widget(syn_projects_btn)
        syn_row.add_widget(syn_time_btn)
        synapse_card.add_widget(syn_row)
        self.root_box.add_widget(synapse_card)

        quick = SectionCard('QUICK ACTIONS', 'Fast access to daily work inside the company control center.')
        quick_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        quick_grid.bind(minimum_height=quick_grid.setter('height'))
        grid_actions = [
            ('Synapse Generate', lambda: App.get_running_app().open_product_manager('synapse_manager', 'generate'), GREEN),
            ('CTP Generate', lambda: App.get_running_app().open_product_manager('casino_manager', 'generate'), GREEN),
            ('Backup Vault', lambda: setattr(self.manager, 'current', 'backup_vault'), BLUE),
            ('Customers', lambda: setattr(self.manager, 'current', 'customers'), BLUE),
            ('Activity Log', lambda: setattr(self.manager, 'current', 'activity'), BLUE),
            ('Releases', lambda: setattr(self.manager, 'current', 'releases'), BLUE),
        ]
        for label, fn, color in grid_actions:
            btn = make_button(label, color)
            btn.bind(on_release=lambda *_ , f=fn: f())
            quick_grid.add_widget(btn)
        quick.add_widget(quick_grid)
        backup_btn = make_button('App Data Backup', UI_CYAN)
        backup_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'app_data_backup'))
        quick.add_widget(backup_btn)
        self.root_box.add_widget(quick)

        modules = SectionCard('COMPANY MODULES', 'Live sections plus placeholders for future internal tools, documents, notes, and operations.')
        rows = [
            ('Licensing', lambda: setattr(self.manager, 'current', 'licensing')),
            ('Backup Vault', lambda: setattr(self.manager, 'current', 'backup_vault')),
            ('Authority Status', lambda: setattr(self.manager, 'current', 'authority_status')),
            ('Customers', lambda: setattr(self.manager, 'current', 'customers')),
            ('Releases', lambda: setattr(self.manager, 'current', 'releases')),
            ('Documents', lambda: setattr(self.manager, 'current', 'docs')),
            ('Notes', lambda: show_placeholder('Notes')),
            ('Internal Tools', lambda: show_placeholder('Internal Tools')),
        ]
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for label, fn in rows:
            btn = make_button(label, PURPLE if label in ('Documents', 'Notes', 'Internal Tools') else BLUE)
            btn.bind(on_release=lambda *_ , f=fn: f())
            grid.add_widget(btn)
        modules.add_widget(grid)
        self.root_box.add_widget(modules)

        # --- Websites section (above Exit) ---
        try:
            _sites_data = [normalize_website_entry(x) for x in load_websites_db()]
        except Exception:
            _sites_data = []
        _total_pages = sum(len(s.get('pages', [])) for s in _sites_data)
        websites_card = SectionCard('WEBSITES', 'Track domains, repos, and HTML page contents for company sites and future web projects.')
        _ws_stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
        _ws_stats.add_widget(build_stat_chip(len(_sites_data), 'Sites', GREEN))
        _ws_stats.add_widget(build_stat_chip(_total_pages, 'Pages', BLUE))
        _ws_latest = _sites_data[0].get('updated_at', '--') if _sites_data else '--'
        _ws_stats.add_widget(build_stat_chip(_ws_latest[-5:] if _ws_latest != '--' else '--', 'Updated', UI_CYAN))
        websites_card.add_widget(_ws_stats)
        _ws_open_btn = make_button('Open Websites', UI_CYAN)
        _ws_open_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'websites'))
        websites_card.add_widget(_ws_open_btn)
        self.root_box.add_widget(websites_card)
        # --- End Websites section ---

        ops = SectionCard('Exit', 'Close the admin app when you are done.')
        exit_btn = make_button('Exit', RED)
        def _confirm_exit(*_):
            app = App.get_running_app()
            on_confirm = getattr(app, 'play_exit_sound_then_stop', app.stop) if app else (lambda: None)
            _confirm_action_popup('Exit App', 'Close SH Vertex Admin Panel?', 'Exit', RED, on_confirm)
        exit_btn.bind(on_release=_confirm_exit)
        ops.add_widget(exit_btn)
        self.root_box.add_widget(ops)


class LicensingHubScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(14)], spacing=dp(10))
        root.add_widget(build_screen_header('Licensing', 'Company-wide product licensing, vaults, authorities, and product modules.', 'home'))
        card = SectionCard('Sections', 'Move between live licensing modules and management views.')
        sections = [
            ('Apps', 'apps', GREEN),
            ('Backup Vault', 'backup_vault', BLUE),
            ('Authority Status', 'authority_status', PURPLE),
            ('Activity Log', 'activity', ORANGE),
        ]
        for label, target, color in sections:
            btn = make_button(label, color)
            btn.bind(on_release=lambda *_ , t=target: setattr(self.manager, 'current', t))
            card.add_widget(btn)
        root.add_widget(card)
        root.add_widget(Widget())
        self.add_widget(root)


class LicensingAppsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        self.scroll = ScrollView(do_scroll_x=False)
        self.root_box = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(16)], spacing=dp(10), size_hint_y=None)
        self.root_box.bind(minimum_height=self.root_box.setter('height'))
        self.scroll.add_widget(self.root_box)
        self.add_widget(self.scroll)
        self.refresh_ui()

    def refresh_ui(self, *_):
        self.root_box.clear_widgets()
        self.root_box.add_widget(build_screen_header('Apps', 'Each product keeps its own authority, license list, and revocation lane.', 'licensing', [('Home', 'home')]))
        for summary, screen_name, color in ((product_summary('Synapse'), 'synapse_manager', GREEN), (product_summary('Casino Tools Pro'), 'casino_manager', PURPLE)):
            card = SectionCard(summary['product'], f"Authority {'Loaded' if summary['authority_loaded'] else 'Missing'}  •  Fingerprint {summary['fingerprint']}")
            stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
            stats.add_widget(build_stat_chip(summary['active'], 'Active', color))
            stats.add_widget(build_stat_chip(summary['revoked'], 'Revoked', RED))
            stats.add_widget(build_stat_chip(summary['last_backup'], 'Last Backup', UI_CYAN))
            card.add_widget(stats)
            open_btn = make_button(f'Open {summary["product"]}', color)
            open_btn.bind(on_release=lambda *_ , s=screen_name: setattr(self.manager, 'current', s))
            card.add_widget(open_btn)
            self.root_box.add_widget(card)


class BackupVaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        self.scroll = ScrollView(do_scroll_x=False)
        self.root_box = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(18)], spacing=dp(10), size_hint_y=None)
        self.root_box.bind(minimum_height=self.root_box.setter('height'))
        self.scroll.add_widget(self.root_box)
        self.add_widget(self.scroll)
        self.refresh_ui()

    def refresh_ui(self, *_):
        self.root_box.clear_widgets()
        self.root_box.add_widget(build_screen_header('Backup Vault', 'Central vault for authority backups, full backups, license-list backups, and revocation exports.', 'home', [('Licensing', 'licensing')]))
        top = SectionCard('Vault Actions', 'Open product managers to create new backups, then return here to review the latest saved files.')
        syn_btn = make_button('Open Synapse Vault', GREEN)
        ctp_btn = make_button('Open Casino Tools Vault', UI_CYAN)
        syn_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'synapse_manager'))
        ctp_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'casino_manager'))
        top.add_widget(syn_btn)
        top.add_widget(ctp_btn)
        self.root_box.add_widget(top)
        for product, color in (('Synapse', GREEN), ('Casino Tools Pro', PURPLE)):
            pcard = SectionCard(product, 'Latest files across all backup categories for this product.')
            for label, directory in product_backup_categories(product):
                files = []
                try:
                    files = [os.path.join(directory, n) for n in os.listdir(directory) if os.path.isfile(os.path.join(directory, n))]
                except Exception:
                    files = []
                latest = latest_file_from(files)
                sub = SectionCard(label, f"Count: {len(files)}")
                if latest:
                    sub.add_widget(make_label(f'Latest: {os.path.basename(latest)}', height=dp(22)))
                    sub.add_widget(make_label(f'Saved: {file_stamp(latest)}  •  Size: {file_size_text(latest)}', color=SUBTEXT, height=dp(22)))
                    copy_btn = make_button('Copy Latest Path', color)
                    copy_btn.bind(on_release=lambda *_ , p=latest, lbl=label: copy_to_clipboard(f'{product} {lbl} path', p))
                    sub.add_widget(copy_btn)
                else:
                    sub.add_widget(make_label('No files saved yet.', color=SUBTEXT, height=dp(22)))
                pcard.add_widget(sub)
            self.root_box.add_widget(pcard)


class CustomersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_list, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
        root.add_widget(build_screen_header('Customers', 'Combined customer/license view across Synapse and Casino Tools Pro.', 'home'))
        tools = SectionCard('Customer Database', 'Search or enrich customer records without opening each product manager separately.')
        self.customer_search = make_input('Search customer / product / license / contact')
        self.customer_search.bind(text=lambda *_: self.refresh_list())
        tools.add_widget(self.customer_search)
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        export_btn = make_button('Export CSV', UI_CYAN)
        refresh_btn = make_button('Refresh', UI_CYAN)
        export_btn.bind(on_release=lambda *_: self.export_rows())
        refresh_btn.bind(on_release=lambda *_: self.refresh_list())
        row.add_widget(export_btn)
        row.add_widget(refresh_btn)
        tools.add_widget(row)
        root.add_widget(tools)
        self.scroll = ScrollView(do_scroll_x=False)
        self.customer_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.customer_box.bind(minimum_height=self.customer_box.setter('height'))
        self.scroll.add_widget(self.customer_box)
        root.add_widget(self.scroll)
        self.add_widget(root)
        self.refresh_list()

    def filtered_rows(self):
        query = str(getattr(self, 'customer_search', None).text if hasattr(self, 'customer_search') else '').strip().lower()
        rows = aggregated_customer_rows()
        if not query:
            return rows
        out = []
        for row in rows:
            hay = ' '.join(str(row.get(k, '')) for k in ('product', 'license_id', 'name', 'contact', 'tier', 'status', 'payment', 'note')).lower()
            if query in hay:
                out.append(row)
        return out

    def edit_customer(self, row):
        overrides = load_customer_overrides()
        lid = row['license_id']
        current = overrides.get(lid, {})
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        name_in = make_input('Name'); name_in.text = current.get('name', row.get('name', ''))
        contact_in = make_input('Contact'); contact_in.text = current.get('contact', row.get('contact', ''))
        note_in = make_input('Note', multiline=True); note_in.text = current.get('note', row.get('note', ''))
        for title, widget in (('Customer Name', name_in), ('Contact', contact_in), ('Internal Note', note_in)):
            content.add_widget(make_label(title))
            content.add_widget(widget)
        row_btn = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_btn = make_button('Save', GREEN)
        cancel_btn = make_button('Cancel', RED)
        row_btn.add_widget(save_btn)
        row_btn.add_widget(cancel_btn)
        content.add_widget(row_btn)
        popup = Popup(title='Edit Customer Info', content=content, size_hint=(0.92, 0.74), background_color=get_color_from_hex(CARD))
        def do_save(*_):
            overrides[lid] = {'name': name_in.text.strip(), 'contact': contact_in.text.strip(), 'note': note_in.text.strip()}
            save_customer_overrides(overrides)
            popup.dismiss()
            self.refresh_list()
            log_admin_activity(row.get('product', 'Customer'), 'Customer record updated', lid)
        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def export_rows(self):
        path = export_customers_csv(self.filtered_rows())
        if path:
            info_popup('Exported', f'Customer database exported to:\n{path}')
        else:
            info_popup('Nothing to export', 'There are no customer rows to export.')

    def refresh_list(self, *_):
        if not hasattr(self, 'customer_box'):
            return
        self.customer_box.clear_widgets()
        rows = self.filtered_rows()
        if not rows:
            self.customer_box.add_widget(make_label('No customers found.', color=SUBTEXT, height=dp(28)))
            return
        for row in rows:
            card = SectionCard(f"{row['product']}  •  {row['tier']}  •  {row['status']}", f"{row['name']}  •  {row['license_id']}")
            card.add_widget(make_label(f"Contact: {row['contact'] or '--'}  •  Payment: {row['payment'] or '--'}", height=dp(22)))
            card.add_widget(make_label(f"Issued: {short_time(row['issued_at']) or '--'}  •  Device: {row['device_code'] or '--'}", color=SUBTEXT, height=dp(22)))
            if row['note']:
                card.add_widget(make_label(f"Note: {row['note']}", color=SUBTEXT, height=dp(28)))
            btns = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
            edit_btn = make_button('Edit', UI_CYAN)
            copy_btn = make_button('Copy ID', UI_CYAN)
            edit_btn.bind(on_release=lambda *_ , r=row: self.edit_customer(r))
            copy_btn.bind(on_release=lambda *_ , lid=row['license_id']: copy_to_clipboard('License ID', lid))
            btns.add_widget(edit_btn)
            btns.add_widget(copy_btn)
            card.add_widget(btns)
            self.customer_box.add_widget(card)


class ActivityLogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_list, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
        root.add_widget(build_screen_header('Activity Log', 'Track licenses, revocations, backups, imports, and other admin actions.', 'home'))
        tools = SectionCard('Actions', 'Use the activity log to trace what happened inside the admin panel.')
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        export_btn = make_button('Export CSV', UI_CYAN)
        clear_btn = make_button('Clear Log', RED)
        refresh_btn = make_button('Refresh', UI_CYAN)
        export_btn.bind(on_release=lambda *_: self.export_log())
        clear_btn.bind(on_release=lambda *_: self.clear_log())
        refresh_btn.bind(on_release=lambda *_: self.refresh_list())
        row.add_widget(export_btn)
        row.add_widget(clear_btn)
        row.add_widget(refresh_btn)
        tools.add_widget(row)
        root.add_widget(tools)
        self.scroll = ScrollView(do_scroll_x=False)
        self.activity_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.activity_box.bind(minimum_height=self.activity_box.setter('height'))
        self.scroll.add_widget(self.activity_box)
        root.add_widget(self.scroll)
        self.add_widget(root)
        self.refresh_list()

    def export_log(self):
        rows = load_activity_log()
        path = export_activity_csv(rows)
        if path:
            info_popup('Exported', f'Activity log exported to:\n{path}')
        else:
            info_popup('Nothing to export', 'The activity log is empty.')

    def clear_log(self):
        save_activity_log([])
        self.refresh_list()
        info_popup('Cleared', 'Activity log cleared.')

    def refresh_list(self, *_):
        if not hasattr(self, 'activity_box'):
            return
        self.activity_box.clear_widgets()
        rows = load_activity_log()
        if not rows:
            self.activity_box.add_widget(make_label('No activity logged yet.', color=SUBTEXT, height=dp(28)))
            return
        for row in rows:
            card = SectionCard(f"{row.get('product', 'System')}  •  {row.get('action', '')}", short_time(row.get('timestamp', '')))
            if row.get('details'):
                card.add_widget(make_label(row.get('details', ''), color=SUBTEXT, height=dp(28)))
            self.activity_box.add_widget(card)


class ReleaseTrackerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_list, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
        root.add_widget(build_screen_header('Release Tracker', 'Track product versions, build status, repo links, and release notes.', 'home'))
        tools = SectionCard('Build Tracker', 'Record APK builds, release candidates, and production notes for each product.')
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        add_btn = make_button('Add Release', GREEN)
        refresh_btn = make_button('Refresh', UI_CYAN)
        add_btn.bind(on_release=lambda *_: self.open_add_popup())
        refresh_btn.bind(on_release=lambda *_: self.refresh_list())
        row.add_widget(add_btn)
        row.add_widget(refresh_btn)
        tools.add_widget(row)
        root.add_widget(tools)
        self.scroll = ScrollView(do_scroll_x=False)
        self.release_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.release_box.bind(minimum_height=self.release_box.setter('height'))
        self.scroll.add_widget(self.release_box)
        root.add_widget(self.scroll)
        self.add_widget(root)
        self.refresh_list()

    def open_add_popup(self):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        product = Spinner(text='Synapse', values=('Synapse', 'Casino Tools Pro', 'Other'), size_hint_y=None, height=dp(46))
        version = make_input('Version (e.g. v1.0.0)')
        status = Spinner(text='In Progress', values=('In Progress', 'Built', 'Testing', 'Released'), size_hint_y=None, height=dp(46))
        repo = make_input('Repo / workflow link (optional)')
        notes = make_input('Release notes', multiline=True)
        for title, widget in (('Product', product), ('Version', version), ('Status', status), ('Link', repo), ('Notes', notes)):
            content.add_widget(make_label(title))
            content.add_widget(widget)
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_btn = make_button('Save', GREEN)
        cancel_btn = make_button('Cancel', RED)
        row.add_widget(save_btn)
        row.add_widget(cancel_btn)
        content.add_widget(row)
        popup = Popup(title='Add Release Entry', content=content, size_hint=(0.92, 0.84), background_color=get_color_from_hex(CARD))
        def do_save(*_):
            entries = load_release_tracker()
            entries.insert(0, {
                'product': product.text,
                'version': version.text.strip() or 'Unversioned',
                'status': status.text,
                'link': repo.text.strip(),
                'notes': notes.text.strip(),
                'timestamp': utc_now_iso(),
            })
            save_release_tracker(entries)
            log_admin_activity(product.text, 'Release entry saved', version.text.strip() or 'Unversioned')
            popup.dismiss()
            self.refresh_list()
        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def refresh_list(self, *_):
        if not hasattr(self, 'release_box'):
            return
        self.release_box.clear_widgets()
        entries = load_release_tracker()
        if not entries:
            self.release_box.add_widget(make_label('No release entries yet.', color=SUBTEXT, height=dp(28)))
            return
        for idx, row in enumerate(entries):
            card = SectionCard(f"{row.get('product', 'Product')}  •  {row.get('version', '')}", f"{row.get('status', '')}  •  {short_time(row.get('timestamp', ''))}")
            if row.get('link'):
                card.add_widget(make_label(f"Link: {row.get('link')}", color=SUBTEXT, height=dp(22)))
            if row.get('notes'):
                card.add_widget(make_label(f"Notes: {row.get('notes')}", color=SUBTEXT, height=dp(28)))
            row_btn = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
            copy_btn = make_button('Copy Link', UI_CYAN)
            del_btn = make_button('Delete', RED)
            copy_btn.bind(on_release=lambda *_ , txt=row.get('link', ''): copy_to_clipboard('Release link', txt))
            def do_delete(*_, i=idx):
                entries = load_release_tracker()
                if 0 <= i < len(entries):
                    removed = entries.pop(i)
                    save_release_tracker(entries)
                    log_admin_activity(removed.get('product', 'Release'), 'Release entry deleted', removed.get('version', ''))
                    self.refresh_list()
            del_btn.bind(on_release=do_delete)
            row_btn.add_widget(copy_btn)
            row_btn.add_widget(del_btn)
            card.add_widget(row_btn)
            self.release_box.add_widget(card)


class AuthorityStatusScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        self.scroll = ScrollView(do_scroll_x=False)
        self.root_box = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(18)], spacing=dp(10), size_hint_y=None)
        self.root_box.bind(minimum_height=self.root_box.setter('height'))
        self.scroll.add_widget(self.root_box)
        self.add_widget(self.scroll)
        self.refresh_ui()

    def refresh_ui(self, *_):
        self.root_box.clear_widgets()
        self.root_box.add_widget(build_screen_header('Authority Status', 'See the active public-key fingerprints and the latest authority backups before you issue licenses.', 'home'))
        syn_pub = file_path(PUBLIC_KEY_FILE)
        ctp_pub = admin_data_path(_CTP_NS.get('PUBLIC_KEY_FILE', 'license_public.pem'))
        items = [
            ('Synapse', syn_pub, authority_backup_dir(), GREEN, 'synapse_manager'),
            ('Casino Tools Pro', ctp_pub, _CTP_NS['authority_backup_dir'](), PURPLE, 'casino_manager'),
        ]
        for product, pub_path, backup_dir, color, screen_name in items:
            latest = latest_file_from([os.path.join(backup_dir, n) for n in os.listdir(backup_dir)] if os.path.exists(backup_dir) else [])
            card = SectionCard(product, f"Fingerprint: {authority_fingerprint(pub_path)}")
            card.add_widget(make_label(f"Authority Loaded: {'Yes' if os.path.exists(pub_path) else 'No'}", height=dp(22)))
            card.add_widget(make_label(f"Latest Authority Backup: {file_stamp(latest) if latest else 'Never'}", color=SUBTEXT, height=dp(22)))
            btn = make_button(f'Open {product}', color)
            btn.bind(on_release=lambda *_ , s=screen_name: setattr(self.manager, 'current', s))
            card.add_widget(btn)
            self.root_box.add_widget(card)


class DocumentationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(14)], spacing=dp(10))
        root.add_widget(build_screen_header('Documents / How To', 'Copy-ready guide for current products, licensing flows, PEM keys, backups, revocations, and new modules.', 'home', [('Modules', 'company_modules')]))

        quick = SectionCard('Copy Helpers', 'Copy the full guide or the most commonly reused technical sections.')
        row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        copy_full = make_button('Copy Full Guide', GREEN)
        copy_module = make_button('Copy New Module Guide', UI_CYAN)
        row1.add_widget(copy_full)
        row1.add_widget(copy_module)
        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        copy_pem = make_button('Copy PEM Notes', UI_CYAN)
        to_home = make_button('Back Home', UI_CYAN)
        row2.add_widget(copy_pem)
        row2.add_widget(to_home)
        quick.add_widget(row1)
        quick.add_widget(row2)
        root.add_widget(quick)

        guide_card = SectionCard('Full Guide', 'Scrollable in-app documentation. Copy any section with the buttons above.')
        guide_scroll = ScrollView(do_scroll_x=False, scroll_type=['bars', 'content'], bar_width=dp(6))
        guide_label = Label(
            text=ADMIN_PANEL_FULL_GUIDE,
            color=get_color_from_hex(TEXT),
            font_size='13sp',
            halign='left',
            valign='top',
            size_hint_y=None,
        )
        def _sync_guide(*_):
            width = max(dp(240), guide_scroll.width - dp(24))
            guide_label.text_size = (width, None)
            guide_label.texture_update()
            guide_label.height = max(dp(800), guide_label.texture_size[1] + dp(24))
        guide_scroll.bind(size=lambda *_: _sync_guide())
        guide_label.bind(texture_size=lambda *_: _sync_guide())
        Clock.schedule_once(lambda *_: _sync_guide(), 0)
        guide_scroll.add_widget(guide_label)
        guide_card.add_widget(guide_scroll)
        root.add_widget(guide_card)

        copy_full.bind(on_release=lambda *_: copy_to_clipboard('Admin panel guide', ADMIN_PANEL_FULL_GUIDE))
        copy_module.bind(on_release=lambda *_: copy_to_clipboard('New module guide', HOWTO_NEW_MODULE_SECTION))
        copy_pem.bind(on_release=lambda *_: copy_to_clipboard('Public key PEM guide', HOWTO_PEM_SECTION))
        to_home.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))
        self.add_widget(root)

class CompanyModulesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
        root.add_widget(build_screen_header('Company Modules', 'Reserved hub for future SH Vertex internal products and operating tools.', 'home'))
        card = SectionCard('Planned Modules', 'These slots are ready for future growth while the admin app stays your central company control panel.')
        for label in ('Sales', 'Documents', 'Notes', 'Internal Tools', 'Customer CRM', 'Operations'):
            btn = make_button(label, UI_CYAN)
            btn.bind(on_release=lambda *_ , t=label: show_placeholder(t))
            card.add_widget(btn)
        root.add_widget(card)
        root.add_widget(Widget())
        self.add_widget(root)


class SynapseManagerShellScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        nav = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        back_btn = make_button('Back to Apps', UI_CYAN)
        home_btn = make_button('Admin Home', UI_CYAN)
        vault_btn = make_button('Vault', UI_CYAN)
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'apps'))
        home_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))
        vault_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'backup_vault'))
        nav.add_widget(back_btn)
        nav.add_widget(home_btn)
        nav.add_widget(vault_btn)
        root.add_widget(nav)
        self.manager_widget = LicenseManagerScreen()
        root.add_widget(self.manager_widget)
        self.add_widget(root)


class CasinoManagerShellScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        nav = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        back_btn = make_button('Back to Apps', UI_CYAN)
        home_btn = make_button('Admin Home', UI_CYAN)
        vault_btn = make_button('Vault', UI_CYAN)
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'apps'))
        home_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))
        vault_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'backup_vault'))
        nav.add_widget(back_btn)
        nav.add_widget(home_btn)
        nav.add_widget(vault_btn)
        root.add_widget(nav)
        self.manager_widget = CasinoToolsLicenseManagerScreen()
        root.add_widget(self.manager_widget)
        self.add_widget(root)




# ---- authority remove helpers + documentation screen ----
SYNAPSE_REVOCATION_RAW_URL = "https://raw.githubusercontent.com/therealwolfman97/SH-VERTEX-ADMIN-PANEL/main/LICENSING/APPS/REVOCATIONS/synapse-revo.json"
CASINO_TOOLS_REVOCATION_RAW_URL = "https://raw.githubusercontent.com/therealwolfman97/casino-tools-revocations/main/revoked_licenses.json"

HOWTO_PEM_SECTION = """PUBLIC KEY PEM BASICS
1. The licensing manager/admin side owns the PRIVATE KEY.
2. The customer app contains only the PUBLIC KEY PEM.
3. The manager signs license payloads with the private key.
4. The customer app verifies the signature with the public key PEM.
5. If the public key inside the customer APK does not match the manager private key, activation will fail.
6. A fresh production authority means:
   - generate a fresh private/public keypair in the licensing manager
   - copy the new public key PEM
   - rebuild the customer app with that exact public key PEM
7. Never ship the private key inside the customer app.
8. Public key PEM can be shared freely inside the customer app. Private key must stay only inside the manager/admin tool and its backups.
"""

HOWTO_NEW_MODULE_SECTION = """HOW TO CREATE A NEW LICENSING MODULE FOR A NEW APP
1. Decide the product identity:
   - app code, for example my_new_app
   - display name
   - license prefix, for example NEW6A-
   - separate revocation json path
2. Generate a FRESH authority for that product.
   Do not reuse Casino Tools Pro or Synapse authority unless you intentionally want shared control.
3. Customer app side:
   - embed the new public key PEM
   - add a license screen / activation flow
   - add device-code display
   - add check-license-status / clear-license / paste-license helpers
   - define demo / pro / pro+ limits if needed
4. Admin/licensing side:
   - create a dedicated product module
   - keep separate files for:
     private key
     public key
     license DB
     revocation json
     authority backup
     license-list backup
     full backup
5. Backups:
   - Authority backup = keys only
   - License-list backup = license DB only
   - Full backup = keys + DB + revocation snapshot
6. Revocation:
   - export a product-specific revocation json
   - host it at a product-specific raw GitHub URL
   - customer app checks only its own product revocation URL
7. Testing checklist:
   - no-license state defaults to demo if planned
   - demo limits decrease correctly
   - demo lock appears at the correct thresholds
   - demo license activates
   - pro license activates
   - wrong-device license fails
   - wrong-public-key build fails activation
   - revocation disables the correct customer license
8. Release process:
   - archive old test state
   - create fresh production authority
   - rebuild customer app with fresh public key PEM
   - save authority backup
   - save full backup
   - save latest license-list backup
"""

ADMIN_PANEL_FULL_GUIDE = """SH VERTEX ADMIN PANEL - INTERNAL HOW TO

OVERVIEW
This admin panel is the company control center for product licensing and future internal modules.
Current products:
1. Synapse by SHV
2. Casino Tools Pro

PRODUCT BREAKDOWN
A) Synapse by SHV
- Customer app has Demo and Pro.
- Demo limits:
  - 2 projects
  - 10 file generations
  - 10 universal time conversions
- Synapse uses its own licensing authority and its own revocation json.
- Synapse customer app verifies Synapse licenses with the Synapse public key PEM.

B) Casino Tools Pro
- Customer app verifies Casino Tools Pro licenses with the Casino Tools Pro public key PEM.
- Casino Tools Pro keeps its own authority, license list, revocation export, and backups.
- Casino Tools Pro authority must stay separate from Synapse authority.

HOW LICENSING WORKS
1. Customer app shows a device code.
2. Admin/licensing side generates a license bound to that device code.
3. The license payload is signed by the manager private key.
4. Customer app verifies the signature using its embedded public key PEM.
5. If signature, app code, tier, device code, and expiry checks pass, the license activates.
6. Revocation check can later invalidate the license if its license_id appears in the signed revocation bundle.

CURRENT REVOCATION URLS
- Synapse raw revocation URL:
  {syn_url}
- Casino Tools Pro raw revocation URL:
  {ctp_url}

BACKUP TYPES
1. Authority Backup
- Contains only the active private/public keypair and authority metadata.
- Use when you want another manager instance to share signing power without copying the current local license list.
- Best for testing, migration, and shared internal company control.

2. License-List Backup
- Contains only the local license records for that product module.
- Use when you want to restore tracking/history without replacing the active authority.

3. Full Backup
- Contains authority + local license list + revocation snapshot.
- Use for one-shot disaster recovery of a whole product licensing module.

WHEN TO USE WHAT
- Same authority, separate local lists:
  import Authority Backup only
- Restore tracking/history on a manager with the correct authority already loaded:
  import License-List Backup
- Restore everything in one shot:
  import Full Backup

AUTHORITY RESET / TESTING
If you need to test a fresh authority, use the new Remove Active Authority button inside each product authority tab.
This removes the currently loaded authority PEM files from that product module without forcing you to clear app cache/data.
Important:
- removing authority does NOT automatically erase the local license list
- generating a new authority after removal gives that product a new signing identity
- any customer app must be rebuilt with the new matching public key PEM before production use

PUBLIC KEY PEM BASICS
{pem_section}

HOW TO CREATE NEW PRODUCT MODULES
{new_module}

SAFE OPERATING RULES
1. Never mix product authorities.
2. Never ship the private key in a customer app.
3. Always back up a fresh production authority before issuing real customer licenses.
4. Keep product revocation files separate.
5. When changing authority, rebuild the customer app with the new public key PEM.
6. For sold ecosystems, treat that product authority as belonging to that sold ecosystem only.
7. Use the admin panel as the internal umbrella manager, but keep each product as its own security boundary.

RECOMMENDED RELEASE ORDER FOR A NEW PRODUCT
1. Finish customer app licensing UI.
2. Generate fresh production authority in the admin/licensing module.
3. Copy public key PEM.
4. Rebuild customer app with that PEM.
5. Create one test license and activate.
6. Test wrong-device failure.
7. Test revocation.
8. Save authority backup.
9. Save full backup.
10. Save latest license-list backup.
""".format(syn_url=SYNAPSE_REVOCATION_RAW_URL, ctp_url=CASINO_TOOLS_REVOCATION_RAW_URL, pem_section=HOWTO_PEM_SECTION, new_module=HOWTO_NEW_MODULE_SECTION)

def _confirm_action_popup(title, message, confirm_text, confirm_color, on_confirm):
    content = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
    msg = Label(text=message, color=get_color_from_hex(TEXT), halign='left', valign='middle', size_hint_y=None)
    msg.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
    msg.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(dp(90), val[1] + dp(8))))
    content.add_widget(msg)
    row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    cancel_btn = make_button('Cancel', UI_CYAN)
    ok_btn = make_button(confirm_text, confirm_color)
    row.add_widget(cancel_btn)
    row.add_widget(ok_btn)
    content.add_widget(row)
    popup = Popup(title=title, content=content, size_hint=(0.9, 0.48), background_color=get_color_from_hex(CARD))
    cancel_btn.bind(on_release=popup.dismiss)
    def _do(*_):
        popup.dismiss()
        on_confirm()
    ok_btn.bind(on_release=_do)
    popup.open()

class SHVertexAdminPanelApp(App):
    def build(self):
        self.title = 'SH Vertex Admin Panel'
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(AdminHomeScreen(name='home'))
        sm.add_widget(LicensingHubScreen(name='licensing'))
        sm.add_widget(LicensingAppsScreen(name='apps'))
        sm.add_widget(BackupVaultScreen(name='backup_vault'))
        sm.add_widget(CustomersScreen(name='customers'))
        sm.add_widget(ActivityLogScreen(name='activity'))
        sm.add_widget(ReleaseTrackerScreen(name='releases'))
        sm.add_widget(AuthorityStatusScreen(name='authority_status'))
        sm.add_widget(CompanyModulesScreen(name='company_modules'))
        sm.add_widget(DocumentationScreen(name='docs'))
        sm.add_widget(SynapseManagerShellScreen(name='synapse_manager'))
        sm.add_widget(CasinoManagerShellScreen(name='casino_manager'))
        sm.current = 'splash'
        return sm

    def open_product_manager(self, screen_name, tab=None, subtab=None):
        self.root.current = screen_name
        def _open(*_):
            screen = self.root.get_screen(screen_name)
            widget = getattr(screen, 'manager_widget', None)
            if widget and tab and hasattr(widget, 'switch_tab'):
                widget.switch_tab(tab)
            if widget and subtab and hasattr(widget, 'switch_license_subtab'):
                widget.switch_license_subtab(subtab)
        Clock.schedule_once(_open, 0.05)






# ─────────────────────────────────────────────────────────────────────────────
# App Data Backup — global backup for non-licensing JSON data to GitHub
# Backs up: admin_activity_log, customer_overrides, release_tracker,
#           websites_registry, synapse_projects. EXCLUDES all licensing files.
# Each upload creates a NEW timestamped file in Backups/ (never overwrites).
# ─────────────────────────────────────────────────────────────────────────────
WEBSITES_DB_FILE = 'websites_registry.json'
SYNAPSE_PROJECTS_FILE = 'synapse_projects.json'

APP_DATA_BACKUP_CONFIG_FILE = 'app_data_backup_config.json'
APP_DATA_BACKUP_BUNDLE_TYPE = 'app_data_backup'

_APP_DATA_BACKUP_FILES = {
    'activity_log':        ADMIN_ACTIVITY_FILE,
    'customer_overrides':  CUSTOMER_OVERRIDES_FILE,
    'release_tracker':     RELEASE_TRACKER_FILE,
    'websites_registry':   WEBSITES_DB_FILE,
    'synapse_projects':    SYNAPSE_PROJECTS_FILE,
}

_APP_DATA_GITHUB_DEFAULTS = {
    'owner':  'therealwolfman97',
    'repo':   'SH-VERTEX-ADMIN-PANEL',
    'branch': 'main',
    'folder': 'Backups',
    'token':  '',
}


def _app_data_backup_config_path():
    return admin_data_path(APP_DATA_BACKUP_CONFIG_FILE)


def load_app_data_backup_config():
    data = load_json(_app_data_backup_config_path(), {})
    merged = dict(_APP_DATA_GITHUB_DEFAULTS)
    if isinstance(data, dict):
        for k in ('owner', 'repo', 'branch', 'folder', 'token'):
            v = str(data.get(k, '') or '').strip()
            if v:
                merged[k] = v
    return merged


def save_app_data_backup_config(cfg):
    clean = {k: str(cfg.get(k, _APP_DATA_GITHUB_DEFAULTS.get(k, '')) or '').strip()
             for k in ('owner', 'repo', 'branch', 'folder', 'token')}
    save_json(_app_data_backup_config_path(), clean)


def build_app_data_backup_blob(password):
    """Collect all non-licensing JSON files into one encrypted blob."""
    payload = {}
    for key, filename in _APP_DATA_BACKUP_FILES.items():
        path = admin_data_path(filename)
        payload[key] = load_json(path, None)
    payload['backed_up_at'] = utc_now_iso()
    return build_secure_backup_blob(password, APP_DATA_BACKUP_BUNDLE_TYPE, payload)


def restore_app_data_backup_blob(blob_text, password):
    """Decrypt and restore all non-licensing data files."""
    bundle = parse_secure_backup_blob(blob_text, password)
    if bundle.get('bundle_type') != APP_DATA_BACKUP_BUNDLE_TYPE:
        raise ValueError(f"Wrong bundle type: {bundle.get('bundle_type')}. Expected app_data_backup.")
    payload = bundle.get('payload', {})
    restored = []
    for key, filename in _APP_DATA_BACKUP_FILES.items():
        data = payload.get(key)
        if data is not None:
            save_json(admin_data_path(filename), data)
            restored.append(filename)
    return restored, payload.get('backed_up_at', '')


def upload_app_data_backup_to_github(blob_text, cfg):
    """
    Upload blob as a NEW timestamped file under Backups/
    Never overwrites — each backup gets its own filename with timestamp.
    """
    owner  = cfg.get('owner', '').strip()
    repo   = cfg.get('repo', '').strip()
    branch = cfg.get('branch', 'main').strip() or 'main'
    folder = cfg.get('folder', 'Backups').strip().strip('/') or 'Backups'
    token  = cfg.get('token', '').strip()

    if not all([owner, repo, token]):
        raise ValueError('Owner, repo, and token are required.')

    stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'admin_panel_backup_{stamp}.shvbak'
    path = f'{folder}/{filename}'
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    body = {
        'message': f'Admin panel backup {stamp}',
        'content': base64.b64encode(blob_text.encode('utf-8')).decode('ascii'),
        'branch': branch,
    }
    resp = requests.put(api_url, headers=headers, json=body, timeout=30)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f'GitHub upload failed: {resp.status_code} {resp.text[:220]}')
    return path, filename


def list_github_backup_files(cfg):
    """List existing backup files in the Backups folder."""
    owner  = cfg.get('owner', '').strip()
    repo   = cfg.get('repo', '').strip()
    branch = cfg.get('branch', 'main').strip() or 'main'
    folder = cfg.get('folder', 'Backups').strip().strip('/') or 'Backups'
    token  = cfg.get('token', '').strip()

    if not all([owner, repo, token]):
        return []

    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{folder}?ref={branch}'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    try:
        resp = requests.get(api_url, headers=headers, timeout=20)
        if resp.status_code == 200:
            items = resp.json()
            if isinstance(items, list):
                backups = [x for x in items if isinstance(x, dict) and x.get('name', '').endswith('.shvbak')]
                backups.sort(key=lambda x: x.get('name', ''), reverse=True)
                return backups
    except Exception:
        pass
    return []


def fetch_github_backup_content(cfg, download_url):
    """Fetch raw backup file content from GitHub."""
    token = cfg.get('token', '').strip()
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    resp = requests.get(download_url, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f'Fetch failed: {resp.status_code}')
    return resp.text



# ---- embedded Synapse tools (projects + universal time) ----
SYNAPSE_PROJECT_STATUS_VALUES = ['Planning', 'Active', 'Waiting', 'Completed']
SYNAPSE_PROJECT_PRIORITY_VALUES = ['Low', 'Medium', 'High']


def _synapse_projects_store_path():
    return admin_data_path(SYNAPSE_PROJECTS_FILE)


def _synapse_now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M')


def _normalize_synapse_project_entry(item):
    stamp = _synapse_now_str()
    if not isinstance(item, dict):
        item = {}
    item.setdefault('id', str(uuid.uuid4()))
    item['name'] = str(item.get('name', '') or 'Project').strip() or 'Project'
    item['duration'] = str(item.get('duration', '') or '').strip()
    item['client'] = str(item.get('client', '') or '').strip()
    item['description'] = str(item.get('description', '') or '').strip()
    status = str(item.get('status', 'Planning') or 'Planning').strip()
    priority = str(item.get('priority', 'Medium') or 'Medium').strip()
    item['status'] = status if status in SYNAPSE_PROJECT_STATUS_VALUES else 'Planning'
    item['priority'] = priority if priority in SYNAPSE_PROJECT_PRIORITY_VALUES else 'Medium'
    item['created_at'] = str(item.get('created_at', '') or stamp)
    item['updated_at'] = str(item.get('updated_at', '') or item['created_at'] or stamp)
    return item


def load_synapse_project_store():
    data = load_json(_synapse_projects_store_path(), {})
    if not isinstance(data, dict):
        data = {}
    data.setdefault('projects', [])
    projects = []
    for item in data.get('projects', []):
        try:
            projects.append(_normalize_synapse_project_entry(item))
        except Exception:
            pass
    data['projects'] = projects
    return data


def save_synapse_project_store(store):
    if not isinstance(store, dict):
        store = {}
    store.setdefault('projects', [])
    store['projects'] = [_normalize_synapse_project_entry(x) for x in store.get('projects', [])]
    save_json(_synapse_projects_store_path(), store)


def synapse_project_rows():
    return list(load_synapse_project_store().get('projects', []))


def synapse_project_summary():
    rows = synapse_project_rows()
    active = len([r for r in rows if str(r.get('status', '')).strip() == 'Active'])
    latest = ''
    if rows:
        latest = max((str(r.get('updated_at', '') or '') for r in rows), default='')
    return {
        'total': len(rows),
        'active': active,
        'latest': short_time(latest) if latest else 'Never',
    }


def _friendly_zone_label(zone_name):
    raw = str(zone_name or '').strip()
    if not raw:
        return ''
    if raw.startswith('Etc/'):
        return raw
    pretty = raw.replace('_', ' ')
    parts = pretty.split('/')
    if len(parts) >= 2:
        return f"{parts[-1]} ({' / '.join(parts[:-1])})"
    return pretty


def get_admin_timezone_display_values():
    friendly = [
        ('Eastern Time (US & Canada)', 'America/New_York'),
        ('Central Time (US & Canada)', 'America/Chicago'),
        ('Mountain Time (US & Canada)', 'America/Denver'),
        ('Pacific Time (US & Canada)', 'America/Los_Angeles'),
        ('Alaska Time', 'America/Anchorage'),
        ('Hawaii Time', 'Pacific/Honolulu'),
        ('UTC', 'UTC'),
        ('GMT / London', 'Europe/London'),
        ('Central Europe / Berlin', 'Europe/Berlin'),
        ('Eastern Europe / Athens', 'Europe/Athens'),
        ('Moscow', 'Europe/Moscow'),
        ('Dubai', 'Asia/Dubai'),
        ('India / Colombo', 'Asia/Colombo'),
        ('India / Kolkata', 'Asia/Kolkata'),
        ('Bangkok', 'Asia/Bangkok'),
        ('Singapore', 'Asia/Singapore'),
        ('Hong Kong', 'Asia/Hong_Kong'),
        ('China / Shanghai', 'Asia/Shanghai'),
        ('Japan / Tokyo', 'Asia/Tokyo'),
        ('Korea / Seoul', 'Asia/Seoul'),
        ('Australia / Perth', 'Australia/Perth'),
        ('Australia / Sydney', 'Australia/Sydney'),
        ('New Zealand / Auckland', 'Pacific/Auckland'),
        ('Brazil / Sao Paulo', 'America/Sao_Paulo'),
        ('Argentina / Buenos Aires', 'America/Argentina/Buenos_Aires'),
        ('South Africa / Johannesburg', 'Africa/Johannesburg'),
    ]
    values, mapping, used = [], {}, set()
    for label, zone in friendly:
        if zone in used:
            continue
        display = f'{label} • {zone}'
        values.append(display)
        mapping[display] = zone
        used.add(zone)
    try:
        zones = sorted(available_timezones())
    except Exception:
        zones = []
    for zone in zones:
        if zone in used:
            continue
        display = f"{_friendly_zone_label(zone)} • {zone}"
        values.append(display)
        mapping[display] = zone
        used.add(zone)
    if not values:
        fallback = [('UTC • UTC', 'UTC'), ('India / Colombo • Asia/Colombo', 'Asia/Colombo'), ('Eastern Time (US & Canada) • America/New_York', 'America/New_York')]
        values = [item[0] for item in fallback]
        mapping = dict(fallback)
    return values, mapping


ADMIN_TIMEZONE_VALUES, ADMIN_TIMEZONE_MAP = get_admin_timezone_display_values()
_ADMIN_COMMON_TZ_OFFSETS_MINUTES = {
    'UTC': 0,
    'GMT': 0,
    'Etc/UTC': 0,
    'Etc/GMT': 0,
    'Europe/London': 0,
    'Europe/Berlin': 60,
    'Europe/Athens': 120,
    'Europe/Moscow': 180,
    'Asia/Dubai': 240,
    'Asia/Colombo': 330,
    'Asia/Kolkata': 330,
    'Asia/Bangkok': 420,
    'Asia/Singapore': 480,
    'Asia/Hong_Kong': 480,
    'Asia/Shanghai': 480,
    'Asia/Tokyo': 540,
    'Asia/Seoul': 540,
    'Australia/Perth': 480,
    'Australia/Sydney': 600,
    'Pacific/Auckland': 720,
    'America/Sao_Paulo': -180,
    'America/Argentina/Buenos_Aires': -180,
    'Africa/Johannesburg': 120,
    'America/New_York': -300,
    'America/Chicago': -360,
    'America/Denver': -420,
    'America/Los_Angeles': -480,
    'America/Anchorage': -540,
    'Pacific/Honolulu': -600,
}


def _admin_timezone_display_for_zone(zone_name):
    zone_name = str(zone_name or '').strip() or 'UTC'
    for display, zone in ADMIN_TIMEZONE_MAP.items():
        if zone == zone_name:
            return display
    display = f"{_friendly_zone_label(zone_name)} • {zone_name}"
    ADMIN_TIMEZONE_MAP[display] = zone_name
    if display not in ADMIN_TIMEZONE_VALUES:
        ADMIN_TIMEZONE_VALUES.append(display)
    return display


def _admin_resolve_timezone(zone_name):
    zone_name = str(zone_name or 'UTC').strip() or 'UTC'
    if ZoneInfo is not None:
        try:
            return ZoneInfo(zone_name)
        except Exception:
            pass
    offset = _ADMIN_COMMON_TZ_OFFSETS_MINUTES.get(zone_name)
    if offset is not None:
        return timezone(timedelta(minutes=offset), name=zone_name)
    return timezone.utc


def _admin_build_zone_datetime(year_text, month_text, day_text, mode_text, hour_text, minute_text, am_pm_text, zone_name):
    month_values = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    try:
        month = month_values.index(str(month_text).strip() or 'Jan') + 1
    except Exception:
        month = datetime.now().month
    year = int(str(year_text).strip() or datetime.now().year)
    day = int(str(day_text).strip() or 1)
    minute = int(str(minute_text).strip() or 0)
    hour_raw = int(str(hour_text).strip() or 0)
    if str(mode_text).strip() == '12h':
        if str(am_pm_text).strip().upper() == 'PM' and hour_raw < 12:
            hour_raw += 12
        if str(am_pm_text).strip().upper() == 'AM' and hour_raw == 12:
            hour_raw = 0
    dt = datetime(year, month, day, hour_raw, minute)
    return dt.replace(tzinfo=_admin_resolve_timezone(zone_name))


def _admin_format_zone_result(dt_obj, zone_name):
    try:
        off = dt_obj.utcoffset()
        offset_text = ''
        if off is not None:
            total_minutes = int(off.total_seconds() // 60)
            sign = '+' if total_minutes >= 0 else '-'
            total_minutes = abs(total_minutes)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            offset_text = f"UTC{sign}{str(hours).zfill(2)}:{str(minutes).zfill(2)}"
        return f"{dt_obj.strftime('%Y-%b-%d %I:%M %p')}\n{zone_name}\n{offset_text}".strip()
    except Exception:
        return f'{dt_obj}\n{zone_name}'


class AdminSynapseProjectsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
        root.add_widget(build_screen_header('Synapse Projects', 'Embedded project workspace for internal SH Vertex use.', 'home', [('Universal Time', 'synapse_universal_time')]))
        tools = SectionCard('Project Workspace', 'Create and manage long-term internal projects directly inside the admin panel.')
        self.search_input = make_input('Search projects by name, client, status, priority, or description')
        self.search_input.bind(text=lambda *_: self.refresh_ui())
        tools.add_widget(self.search_input)
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        add_btn = make_button('Add Project', GREEN)
        refresh_btn = make_button('Refresh', UI_CYAN)
        add_btn.bind(on_release=lambda *_: self.open_project_popup())
        refresh_btn.bind(on_release=lambda *_: self.refresh_ui())
        row.add_widget(add_btn)
        row.add_widget(refresh_btn)
        tools.add_widget(row)
        root.add_widget(tools)
        self.scroll = ScrollView(do_scroll_x=False)
        self.project_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.project_box.bind(minimum_height=self.project_box.setter('height'))
        self.scroll.add_widget(self.project_box)
        root.add_widget(self.scroll)
        self.add_widget(root)
        self.refresh_ui()

    def filtered_rows(self):
        rows = synapse_project_rows()
        q = str(self.search_input.text if hasattr(self, 'search_input') else '').strip().lower()
        if not q:
            return sorted(rows, key=lambda r: str(r.get('updated_at', '')), reverse=True)
        out = []
        for row in rows:
            hay = ' '.join(str(row.get(k, '')) for k in ('name', 'client', 'description', 'status', 'priority', 'duration')).lower()
            if q in hay:
                out.append(row)
        out.sort(key=lambda r: str(r.get('updated_at', '')), reverse=True)
        return out

    def refresh_ui(self, *_):
        if not hasattr(self, 'project_box'):
            return
        self.project_box.clear_widgets()
        rows = self.filtered_rows()
        summary = synapse_project_summary()
        summary_card = SectionCard('Overview', f"Projects: {summary['total']}  •  Active: {summary['active']}  •  Latest Update: {summary['latest']}")
        jump_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        new_btn = make_button('New Project', GREEN)
        time_btn = make_button('Universal Time', UI_CYAN)
        new_btn.bind(on_release=lambda *_: self.open_project_popup())
        time_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'synapse_universal_time'))
        jump_row.add_widget(new_btn)
        jump_row.add_widget(time_btn)
        summary_card.add_widget(jump_row)
        self.project_box.add_widget(summary_card)
        if not rows:
            empty = SectionCard('No projects yet', 'Create your first embedded Synapse project here.')
            add_btn = make_button('Create Project', GREEN)
            add_btn.bind(on_release=lambda *_: self.open_project_popup())
            empty.add_widget(add_btn)
            self.project_box.add_widget(empty)
            return
        for row in rows:
            card = SectionCard(f"{row.get('name', 'Project')}  •  {row.get('status', 'Planning')}", f"Priority: {row.get('priority', 'Medium')}  •  Updated: {short_time(row.get('updated_at', '')) or '--'}")
            card.add_widget(make_label(f"Client: {row.get('client', '') or '--'}  •  Duration: {row.get('duration', '') or '--'}", height=dp(22)))
            desc = str(row.get('description', '') or '').strip()
            if desc:
                card.add_widget(make_label(desc, color=SUBTEXT, height=dp(40)))
            btns = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
            open_btn = make_button('Details', UI_CYAN)
            edit_btn = make_button('Edit', UI_CYAN)
            del_btn = make_button('Delete', RED)
            open_btn.bind(on_release=lambda *_ , r=row: self.open_project_details(r))
            edit_btn.bind(on_release=lambda *_ , r=row: self.open_project_popup(r))
            del_btn.bind(on_release=lambda *_ , pid=row.get('id', ''): self.confirm_delete_project(pid))
            btns.add_widget(open_btn)
            btns.add_widget(edit_btn)
            btns.add_widget(del_btn)
            card.add_widget(btns)
            self.project_box.add_widget(card)

    def open_project_details(self, row):
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        body = [
            f"Name: {row.get('name', '')}",
            f"Status: {row.get('status', '')}",
            f"Priority: {row.get('priority', '')}",
            f"Client: {row.get('client', '') or '--'}",
            f"Duration: {row.get('duration', '') or '--'}",
            f"Created: {row.get('created_at', '') or '--'}",
            f"Updated: {row.get('updated_at', '') or '--'}",
        ]
        if row.get('description'):
            body.append('')
            body.append(str(row.get('description', '')).strip())
        lbl = Label(text='\n'.join(body), color=get_color_from_hex(TEXT), halign='left', valign='top', text_size=(dp(300), None), size_hint_y=None)
        lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(dp(170), val[1])))
        content.add_widget(lbl)
        row_btn = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        copy_btn = make_button('Copy Summary', UI_CYAN)
        edit_btn = make_button('Edit', UI_CYAN)
        close_btn = make_button('Close', GREEN)
        row_btn.add_widget(copy_btn)
        row_btn.add_widget(edit_btn)
        row_btn.add_widget(close_btn)
        content.add_widget(row_btn)
        popup = Popup(title='Project Details', content=content, size_hint=(0.92, 0.72), background_color=get_color_from_hex(CARD))
        copy_btn.bind(on_release=lambda *_: copy_to_clipboard('Project summary', '\n'.join(body)))
        edit_btn.bind(on_release=lambda *_: (popup.dismiss(), self.open_project_popup(row)))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def open_project_popup(self, row=None):
        row = dict(row or {})
        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        name_in = make_input('Project name'); name_in.text = row.get('name', '')
        client_in = make_input('Client / owner'); client_in.text = row.get('client', '')
        duration_in = make_input('Duration / phase'); duration_in.text = row.get('duration', '')
        status_in = Spinner(text=row.get('status', 'Planning') or 'Planning', values=tuple(SYNAPSE_PROJECT_STATUS_VALUES), size_hint_y=None, height=dp(46))
        priority_in = Spinner(text=row.get('priority', 'Medium') or 'Medium', values=tuple(SYNAPSE_PROJECT_PRIORITY_VALUES), size_hint_y=None, height=dp(46))
        desc_in = make_input('Description', multiline=True); desc_in.height = dp(120); desc_in.text = row.get('description', '')
        for title, widget in [('Project Name', name_in), ('Client / Owner', client_in), ('Duration / Phase', duration_in), ('Status', status_in), ('Priority', priority_in), ('Description', desc_in)]:
            content.add_widget(make_label(title))
            content.add_widget(widget)
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_btn = make_button('Save', GREEN)
        cancel_btn = make_button('Cancel', RED)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup = Popup(title='Edit Project' if row.get('id') else 'New Project', content=content, size_hint=(0.92, 0.92), background_color=get_color_from_hex(CARD))

        def do_save(*_):
            name = name_in.text.strip()
            if not name:
                info_popup('Missing Name', 'Project name is required.')
                return
            store = load_synapse_project_store()
            projects = list(store.get('projects', []))
            stamp = _synapse_now_str()
            if row.get('id'):
                updated = False
                for item in projects:
                    if item.get('id') == row.get('id'):
                        item.update({
                            'name': name,
                            'client': client_in.text.strip(),
                            'duration': duration_in.text.strip(),
                            'status': status_in.text.strip() or 'Planning',
                            'priority': priority_in.text.strip() or 'Medium',
                            'description': desc_in.text.strip(),
                            'updated_at': stamp,
                        })
                        updated = True
                        break
                if action := ('Project updated' if updated else ''):
                    pass
                log_admin_activity('Synapse Projects', 'Project updated', name)
            else:
                projects.append(_normalize_synapse_project_entry({
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'client': client_in.text.strip(),
                    'duration': duration_in.text.strip(),
                    'status': status_in.text.strip() or 'Planning',
                    'priority': priority_in.text.strip() or 'Medium',
                    'description': desc_in.text.strip(),
                    'created_at': stamp,
                    'updated_at': stamp,
                }))
                log_admin_activity('Synapse Projects', 'Project created', name)
            store['projects'] = projects
            save_synapse_project_store(store)
            popup.dismiss()
            self.refresh_ui()
            info_popup('Saved', 'Synapse project saved.')

        save_btn.bind(on_release=do_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_delete_project(self, project_id):
        rows = synapse_project_rows()
        row = next((r for r in rows if r.get('id') == project_id), None)
        if not row:
            info_popup('Missing Project', 'Project no longer exists.')
            return
        def _do_delete():
            store = load_synapse_project_store()
            store['projects'] = [r for r in store.get('projects', []) if r.get('id') != project_id]
            save_synapse_project_store(store)
            log_admin_activity('Synapse Projects', 'Project deleted', row.get('name', 'Project'))
            self.refresh_ui()
        _confirm_action_popup('Delete Project', f"Delete '{row.get('name', 'Project')}' from embedded Synapse projects?", 'Delete', RED, _do_delete)


class AdminSynapseUniversalTimeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
        root.add_widget(build_screen_header('Synapse Universal Time', 'Convert date and time accurately between time zones.', 'home', [('Projects', 'synapse_projects')]))
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        intro = SectionCard('Time Zone Converter', 'Choose the source date/time and convert it into another time zone.')
        box.add_widget(intro)
        month_values = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        day_values = [str(i) for i in range(1, 32)]
        year_values = [str(i) for i in range(2000, 2036)]
        minute_values = [str(i).zfill(2) for i in range(0, 60)]
        values_12h = [str(i).zfill(2) for i in range(1, 13)]
        values_24h = [str(i).zfill(2) for i in range(0, 24)]
        now = datetime.now()
        date_card = SectionCard('Source Date & Time', 'Pick the source date, time mode, and values.')
        row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self._month_spin = Spinner(text=month_values[now.month - 1], values=tuple(month_values), size_hint_y=None, height=dp(46))
        self._day_spin = Spinner(text=str(now.day), values=tuple(day_values), size_hint_y=None, height=dp(46))
        self._year_spin = Spinner(text=str(now.year), values=tuple(year_values), size_hint_y=None, height=dp(46))
        row1.add_widget(self._month_spin); row1.add_widget(self._day_spin); row1.add_widget(self._year_spin)
        date_card.add_widget(row1)
        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        self._mode_spin = Spinner(text='24h', values=('12h', '24h'), size_hint_y=None, height=dp(46))
        self._hour_spin = Spinner(text=str(now.hour).zfill(2), values=tuple(values_24h), size_hint_y=None, height=dp(46))
        self._minute_spin = Spinner(text=str(now.minute).zfill(2), values=tuple(minute_values), size_hint_y=None, height=dp(46))
        self._am_pm_spin = Spinner(text='AM' if now.hour < 12 else 'PM', values=('AM', 'PM'), size_hint_y=None, height=dp(46))
        row2.add_widget(self._mode_spin); row2.add_widget(self._hour_spin); row2.add_widget(self._minute_spin); row2.add_widget(self._am_pm_spin)
        date_card.add_widget(row2)
        box.add_widget(date_card)
        zone_card = SectionCard('Time Zones', 'Choose source and destination zones.')
        self._from_zone = Spinner(text=_admin_timezone_display_for_zone('UTC'), values=tuple(ADMIN_TIMEZONE_VALUES), size_hint_y=None, height=dp(46))
        self._to_zone = Spinner(text=_admin_timezone_display_for_zone('Asia/Colombo'), values=tuple(ADMIN_TIMEZONE_VALUES), size_hint_y=None, height=dp(46))
        zone_card.add_widget(make_label('From time zone'))
        zone_card.add_widget(self._from_zone)
        zone_card.add_widget(make_label('To time zone'))
        zone_card.add_widget(self._to_zone)
        box.add_widget(zone_card)
        result_card = SectionCard('Result', 'Tap Convert to calculate the time in the destination zone.')
        self._time_result_label = Label(text='Pick values and tap Convert.', color=get_color_from_hex(TEXT), halign='left', valign='top', size_hint_y=None)
        self._time_result_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        self._time_result_label.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(dp(120), val[1] + dp(8))))
        result_card.add_widget(self._time_result_label)
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        convert_btn = make_button('Convert', UI_CYAN)
        copy_btn = make_button('Copy Result', UI_CYAN)
        btn_row.add_widget(convert_btn); btn_row.add_widget(copy_btn)
        result_card.add_widget(btn_row)
        box.add_widget(result_card)
        def on_mode_change(_spinner, value):
            if value == '12h':
                self._hour_spin.values = tuple(values_12h)
                current = int(str(self._hour_spin.text or '00').strip() or 0)
                current = current % 12
                current = 12 if current == 0 else current
                self._hour_spin.text = str(current).zfill(2)
                self._am_pm_spin.disabled = False
                self._am_pm_spin.opacity = 1
            else:
                current = int(str(self._hour_spin.text or '00').strip() or 0)
                if self._am_pm_spin.text == 'PM' and current < 12:
                    current += 12
                if self._am_pm_spin.text == 'AM' and current == 12:
                    current = 0
                self._hour_spin.values = tuple(values_24h)
                self._hour_spin.text = str(current).zfill(2)
                self._am_pm_spin.disabled = True
                self._am_pm_spin.opacity = 0.55
        self._mode_spin.bind(text=on_mode_change)
        on_mode_change(self._mode_spin, self._mode_spin.text)
        def do_convert(*_):
            try:
                from_zone = ADMIN_TIMEZONE_MAP.get(self._from_zone.text, 'UTC')
                to_zone = ADMIN_TIMEZONE_MAP.get(self._to_zone.text, 'UTC')
                source_dt = _admin_build_zone_datetime(self._year_spin.text, self._month_spin.text, self._day_spin.text, self._mode_spin.text, self._hour_spin.text, self._minute_spin.text, self._am_pm_spin.text, from_zone)
                target_dt = source_dt.astimezone(_admin_resolve_timezone(to_zone))
                self._time_result_label.text = (
                    f"Source Time\n{_admin_format_zone_result(source_dt, from_zone)}\n\n"
                    f"Destination Time\n{_admin_format_zone_result(target_dt, to_zone)}"
                )
                log_admin_activity('Synapse Universal Time', 'Time conversion run', f'{from_zone} -> {to_zone}')
            except Exception as e:
                self._time_result_label.text = f'Conversion failed:\n{e}'
        convert_btn.bind(on_release=do_convert)
        copy_btn.bind(on_release=lambda *_: copy_to_clipboard('Converted time', self._time_result_label.text))
        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)


class AppDataBackupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cfg = load_app_data_backup_config()
        self._remote_files = []
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        self._cfg = load_app_data_backup_config()
        Clock.schedule_once(self._refresh_token_display, 0)

    def _refresh_token_display(self, *_):
        if hasattr(self, '_token_input'):
            self._token_input.text = self._cfg.get('token', '')

    def build_ui(self, *_):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
        root.add_widget(build_screen_header(
            'App Data Backup',
            'Encrypted backup of activity log, customers, releases, websites, and Synapse projects — NOT licensing keys.',
            'home',
        ))

        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # ── GitHub Settings ──
        cfg_card = SectionCard('GitHub Settings', 'Point to your private repo Backups folder. Each backup is a new timestamped file.')
        self._owner_in  = make_input('Owner (therealwolfman97)')
        self._repo_in   = make_input('Repo (SH-VERTEX-ADMIN-PANEL)')
        self._branch_in = make_input('Branch (main)')
        self._folder_in = make_input('Folder path (Backups)')
        self._token_in  = make_input('GitHub token with contents:write', password=True)
        self._token_input = self._token_in  # alias for refresh

        self._owner_in.text  = self._cfg.get('owner', '')
        self._repo_in.text   = self._cfg.get('repo', '')
        self._branch_in.text = self._cfg.get('branch', 'main') or 'main'
        self._folder_in.text = self._cfg.get('folder', 'Backups') or 'Backups'
        self._token_in.text  = self._cfg.get('token', '')

        for lbl, widget in [
            ('Owner', self._owner_in), ('Repo', self._repo_in),
            ('Branch', self._branch_in), ('Folder', self._folder_in),
            ('Token', self._token_in),
        ]:
            cfg_card.add_widget(make_label(lbl))
            cfg_card.add_widget(widget)
            if widget is self._token_in:
                paste_token_btn = make_button('Paste Token', UI_CYAN)
                paste_token_btn.height = dp(40)
                paste_token_btn.bind(on_release=lambda *_: paste_clipboard_into(self._token_in))
                cfg_card.add_widget(paste_token_btn)

        save_cfg_btn = make_button('Save Settings', UI_CYAN)
        save_cfg_btn.bind(on_release=lambda *_: self._save_settings())
        cfg_card.add_widget(save_cfg_btn)
        box.add_widget(cfg_card)

        # ── Backup password ──
        pass_card = SectionCard('Backup Password', 'Used to encrypt the backup. You must enter this same password when restoring.')
        self._pass_in = make_input('Backup password (required)', password=True)
        pass_card.add_widget(self._pass_in)
        box.add_widget(pass_card)

        # ── Upload ──
        up_card = SectionCard('Upload to GitHub', 'Creates a new timestamped .shvbak file in your Backups folder — never overwrites.')
        up_card.add_widget(make_label('Includes: activity log, customers, releases, websites', color=SUBTEXT, height=dp(22)))
        up_card.add_widget(make_label('Excludes: ALL licensing keys, license lists, revocation files', color=RED, height=dp(22)))
        upload_btn = make_button('Backup & Upload Now', GREEN)
        upload_btn.bind(on_release=lambda *_: self._do_upload())
        up_card.add_widget(upload_btn)
        box.add_widget(up_card)

        # ── Restore ──
        rest_card = SectionCard('Restore from GitHub', 'Lists existing .shvbak files in your repo. Tap one to restore.')
        list_btn = make_button('List Backup Files', UI_CYAN)
        list_btn.bind(on_release=lambda *_: self._list_remote())
        rest_card.add_widget(list_btn)
        self._files_box = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None)
        self._files_box.bind(minimum_height=self._files_box.setter('height'))
        rest_card.add_widget(self._files_box)
        box.add_widget(rest_card)

        # ── Manual paste restore ──
        paste_card = SectionCard('Manual Restore', 'Paste a backup blob directly if you have the raw content.')
        self._paste_in = make_input('Paste .shvbak content here', multiline=True)
        self._paste_in.height = dp(120)
        paste_card.add_widget(self._paste_in)
        paste_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        paste_btn = make_button('Paste from Clipboard', UI_CYAN)
        restore_btn = make_button('Restore from Paste', GREEN)
        paste_btn.bind(on_release=lambda *_: self._paste_from_clip())
        restore_btn.bind(on_release=lambda *_: self._do_restore_paste())
        paste_row.add_widget(paste_btn)
        paste_row.add_widget(restore_btn)
        paste_card.add_widget(paste_row)
        box.add_widget(paste_card)

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def _collect_cfg(self):
        return {
            'owner':  self._owner_in.text.strip(),
            'repo':   self._repo_in.text.strip(),
            'branch': self._branch_in.text.strip() or 'main',
            'folder': self._folder_in.text.strip() or 'Backups',
            'token':  self._token_in.text.strip(),
        }

    def _save_settings(self):
        cfg = self._collect_cfg()
        save_app_data_backup_config(cfg)
        self._cfg = cfg
        info_popup('Saved', 'App data backup settings saved.')

    def _do_upload(self):
        password = self._pass_in.text.strip()
        if not password:
            info_popup('Password required', 'Enter a backup password before uploading.')
            return
        cfg = self._collect_cfg()
        if not cfg['token']:
            info_popup('Token required', 'Enter your GitHub token first.')
            return
        try:
            blob = build_app_data_backup_blob(password)
            path, filename = upload_app_data_backup_to_github(blob, cfg)
            save_app_data_backup_config(cfg)
            self._cfg = cfg
            log_admin_activity('System', 'App data backup uploaded', filename)
            info_popup('Uploaded', f'Backup uploaded successfully.\n\nFile: {filename}\nPath: {path}')
        except Exception as e:
            info_popup('Upload failed', str(e))

    def _list_remote(self):
        cfg = self._collect_cfg()
        if not cfg['token']:
            info_popup('Token required', 'Enter your GitHub token first.')
            return
        try:
            files = list_github_backup_files(cfg)
            self._remote_files = files
            self._files_box.clear_widgets()
            if not files:
                self._files_box.add_widget(make_label('No .shvbak files found in that folder.', color=SUBTEXT, height=dp(28)))
                return
            for item in files[:20]:
                name = item.get('name', '')
                size = item.get('size', 0)
                size_txt = f'{size/1024:.1f} KB' if size > 1024 else f'{size} B'
                btn = make_button(f'{name}  ({size_txt})', PURPLE)
                dl_url = item.get('download_url', '')
                btn.bind(on_release=lambda *_, u=dl_url, n=name: self._confirm_restore(u, n))
                self._files_box.add_widget(btn)
        except Exception as e:
            info_popup('List failed', str(e))

    def _confirm_restore(self, download_url, filename):
        _confirm_action_popup(
            'Restore Backup',
            f'Restore from:\n{filename}\n\nThis will overwrite activity log, customers, releases and websites data. Licensing is untouched.',
            'Restore', ORANGE,
            lambda: self._do_restore_remote(download_url, filename),
        )

    def _do_restore_remote(self, download_url, filename):
        password = self._pass_in.text.strip()
        if not password:
            info_popup('Password required', 'Enter the backup password to decrypt.')
            return
        cfg = self._collect_cfg()
        try:
            blob_text = fetch_github_backup_content(cfg, download_url)
            restored, backed_up_at = restore_app_data_backup_blob(blob_text, password)
            log_admin_activity('System', 'App data backup restored', filename)
            info_popup('Restored', f'Restored from {filename}\nOriginal backup: {backed_up_at}\nFiles: {", ".join(restored)}')
        except Exception as e:
            info_popup('Restore failed', str(e))

    def _paste_from_clip(self):
        try:
            pasted = Clipboard.paste() or ''
            if not pasted.strip():
                info_popup('Clipboard empty', 'Nothing to paste.')
                return
            self._paste_in.text = pasted
        except Exception as e:
            info_popup('Paste failed', str(e))

    def _do_restore_paste(self):
        blob_text = self._paste_in.text.strip()
        if not blob_text:
            info_popup('Nothing to restore', 'Paste a backup blob first.')
            return
        password = self._pass_in.text.strip()
        if not password:
            info_popup('Password required', 'Enter the backup password.')
            return
        _confirm_action_popup(
            'Restore from Paste',
            'Restore activity log, customers, releases and websites from pasted backup? Licensing is untouched.',
            'Restore', ORANGE,
            lambda: self._execute_paste_restore(blob_text, password),
        )

    def _execute_paste_restore(self, blob_text, password):
        try:
            restored, backed_up_at = restore_app_data_backup_blob(blob_text, password)
            log_admin_activity('System', 'App data backup restored from paste', backed_up_at)
            info_popup('Restored', f'Restored successfully.\nOriginal backup: {backed_up_at}\nFiles: {", ".join(restored)}')
        except Exception as e:
            info_popup('Restore failed', str(e))

# ---- Websites module ----
WEBSITES_DB_FILE = 'websites_registry.json'


def website_data_path(name):
    return admin_data_path(name)


def load_websites_db():
    data = load_json(website_data_path(WEBSITES_DB_FILE), [])
    return data if isinstance(data, list) else []


def save_websites_db(items):
    save_json(website_data_path(WEBSITES_DB_FILE), items)


def now_local_stamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M')


def normalize_page_entry(page):
    if not isinstance(page, dict):
        page = {}
    return {
        'id': str(page.get('id') or uuid.uuid4()),
        'title': str(page.get('title', 'Page')).strip() or 'Page',
        'filename': str(page.get('filename', 'index.html')).strip() or 'index.html',
        'html': str(page.get('html', '') or ''),
        'notes': str(page.get('notes', '') or ''),
        'updated_at': str(page.get('updated_at', now_local_stamp())),
    }


def normalize_website_entry(site):
    if not isinstance(site, dict):
        site = {}
    pages = [normalize_page_entry(p) for p in (site.get('pages') or []) if isinstance(p, dict)]
    return {
        'id': str(site.get('id') or uuid.uuid4()),
        'name': str(site.get('name', 'Website')).strip() or 'Website',
        'domain': str(site.get('domain', '')).strip(),
        'details': str(site.get('details', '') or ''),
        'notes': str(site.get('notes', '') or ''),
        'repo': str(site.get('repo', '') or ''),
        'hosting': str(site.get('hosting', '') or ''),
        'updated_at': str(site.get('updated_at', now_local_stamp())),
        'pages': pages,
    }


class WebsitesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sites = []
        Clock.schedule_once(self.build_ui, 0)

    def on_pre_enter(self, *_):
        Clock.schedule_once(self.refresh_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        self.scroll = ScrollView(do_scroll_x=False)
        self.root_box = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(18)], spacing=dp(10), size_hint_y=None)
        self.root_box.bind(minimum_height=self.root_box.setter('height'))
        self.scroll.add_widget(self.root_box)
        self.add_widget(self.scroll)
        self.refresh_ui()

    def refresh_ui(self, *_):
        self.sites = [normalize_website_entry(x) for x in load_websites_db()]
        self.root_box.clear_widgets()
        self.root_box.add_widget(build_screen_header('Websites', 'Track company sites, domains, repos, and page-level HTML so future updates are easier to manage.', 'home'))

        top_card = SectionCard('Website Registry', 'Add websites, store basic details, and manage copy-ready HTML content for each page.')
        add_btn = make_button('Add Website', GREEN)
        add_btn.bind(on_release=lambda *_: self.open_site_editor())
        top_card.add_widget(add_btn)
        top_card.add_widget(make_label(f'Total Websites: {len(self.sites)}', color=SUBTEXT, height=dp(22)))
        self.root_box.add_widget(top_card)

        if not self.sites:
            empty = SectionCard('No websites yet', 'Create your first site entry to track domains, notes, and page HTML here.')
            self.root_box.add_widget(empty)
            return

        for site in self.sites:
            card = SectionCard(site['name'], site['domain'] or 'No domain saved yet')
            stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
            stats.add_widget(build_stat_chip(len(site.get('pages', [])), 'Pages', GREEN))
            stats.add_widget(build_stat_chip(site.get('hosting') or '--', 'Hosting', BLUE))
            stats.add_widget(build_stat_chip(site.get('updated_at', '--')[-5:] if site.get('updated_at') else '--', 'Updated', ORANGE))
            card.add_widget(stats)
            if site.get('details'):
                card.add_widget(make_label(site['details'][:180] + ('...' if len(site['details']) > 180 else ''), color=SUBTEXT, height=dp(42)))
            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
            open_btn = make_button('Open', UI_CYAN)
            edit_btn = make_button('Edit', UI_CYAN)
            add_page_btn = make_button('Add Page', GREEN)
            open_btn.bind(on_release=lambda *_ , sid=site['id']: self.open_site_detail(sid))
            edit_btn.bind(on_release=lambda *_ , sid=site['id']: self.open_site_editor(sid))
            add_page_btn.bind(on_release=lambda *_ , sid=site['id']: self.open_page_editor(sid))
            row.add_widget(open_btn)
            row.add_widget(edit_btn)
            row.add_widget(add_page_btn)
            card.add_widget(row)
            self.root_box.add_widget(card)

    def _save_sites(self):
        save_websites_db(self.sites)

    def _find_site(self, site_id):
        for site in self.sites:
            if site.get('id') == site_id:
                return site
        return None

    def open_site_editor(self, site_id=None):
        site = normalize_website_entry(self._find_site(site_id) or {})
        is_new = not bool(site_id)
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        fields = {}
        for label, key, multiline in [
            ('Website Name', 'name', False),
            ('Domain / URL', 'domain', False),
            ('Repo / Location', 'repo', False),
            ('Hosting / Platform', 'hosting', False),
            ('Basic Details', 'details', True),
            ('Internal Notes', 'notes', True),
        ]:
            content.add_widget(make_label(label, height=dp(22)))
            widget = make_input(multiline=multiline)
            widget.text = str(site.get(key, ''))
            if multiline:
                widget.height = dp(90)
            fields[key] = widget
            content.add_widget(widget)
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_btn = make_button('Save Website', GREEN)
        cancel_btn = make_button('Cancel', UI_CYAN)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup = Popup(title='Add Website' if is_new else 'Edit Website', content=content, size_hint=(0.92, 0.92), background_color=get_color_from_hex(CARD))
        cancel_btn.bind(on_release=popup.dismiss)

        def do_save(*_):
            updated = normalize_website_entry(site)
            for key, widget in fields.items():
                updated[key] = widget.text.strip()
            updated['updated_at'] = now_local_stamp()
            if is_new:
                self.sites.insert(0, updated)
            else:
                for i, existing in enumerate(self.sites):
                    if existing.get('id') == updated['id']:
                        updated['pages'] = existing.get('pages', [])
                        self.sites[i] = updated
                        break
            self._save_sites()
            popup.dismiss()
            self.refresh_ui()
        save_btn.bind(on_release=do_save)
        popup.open()

    def open_site_detail(self, site_id):
        site = self._find_site(site_id)
        if not site:
            info_popup('Missing Website', 'That website entry could not be found.')
            return
        wrapper = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        scroll = ScrollView(do_scroll_x=False)
        body = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        body.bind(minimum_height=body.setter('height'))
        body.add_widget(make_label(f"Domain: {site.get('domain') or '—'}", color=TEXT, height=dp(24)))
        body.add_widget(make_label(f"Repo: {site.get('repo') or '—'}", color=SUBTEXT, height=dp(24)))
        body.add_widget(make_label(f"Hosting: {site.get('hosting') or '—'}", color=SUBTEXT, height=dp(24)))
        if site.get('details'):
            details = make_input(multiline=True, readonly=True)
            details.height = dp(88)
            details.text = site['details']
            body.add_widget(make_label('Basic Details', height=dp(22)))
            body.add_widget(details)
        if site.get('notes'):
            notes = make_input(multiline=True, readonly=True)
            notes.height = dp(88)
            notes.text = site['notes']
            body.add_widget(make_label('Internal Notes', height=dp(22)))
            body.add_widget(notes)
        body.add_widget(make_label('Pages / HTML Contents', height=dp(22)))
        if not site.get('pages'):
            body.add_widget(make_label('No pages added yet.', color=SUBTEXT, height=dp(24)))
        popup = Popup(title=site.get('name', 'Website'), content=wrapper, size_hint=(0.95, 0.95), background_color=get_color_from_hex(CARD))
        for page in site.get('pages', []):
            page_card = SectionCard(page.get('title', 'Page'), f"{page.get('filename', 'index.html')}  •  Updated {page.get('updated_at', '--')}")
            if page.get('notes'):
                page_card.add_widget(make_label(page['notes'], color=SUBTEXT, height=dp(36)))
            html_preview = make_input(multiline=True, readonly=True)
            html_preview.height = dp(140)
            html_preview.text = page.get('html', '')
            page_card.add_widget(html_preview)
            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
            copy_btn = make_button('Copy HTML', UI_CYAN)
            edit_btn = make_button('Edit Page', UI_CYAN)
            delete_btn = make_button('Delete Page', RED)
            copy_btn.bind(on_release=lambda *_ , txt=page.get('html', ''): copy_to_clipboard('HTML content', txt))
            edit_btn.bind(on_release=lambda *_ , sid=site_id, pid=page.get('id'): (popup.dismiss(), self.open_page_editor(sid, pid)))
            delete_btn.bind(on_release=lambda *_ , sid=site_id, pid=page.get('id'): self.delete_page(sid, pid, refresh_popup=lambda: self._reopen_detail_after_delete(popup, sid)))
            row.add_widget(copy_btn)
            row.add_widget(edit_btn)
            row.add_widget(delete_btn)
            page_card.add_widget(row)
            body.add_widget(page_card)
        scroll.add_widget(body)
        wrapper.add_widget(scroll)
        btns = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        add_page = make_button('Add Page', GREEN)
        edit_site = make_button('Edit Website', UI_CYAN)
        delete_site = make_button('Delete Website', RED)
        btns.add_widget(add_page)
        btns.add_widget(edit_site)
        btns.add_widget(delete_site)
        wrapper.add_widget(btns)
        back_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        back_btn = make_button('Back', UI_CYAN)
        back_row.add_widget(back_btn)
        wrapper.add_widget(back_row)
        add_page.bind(on_release=lambda *_: (popup.dismiss(), self.open_page_editor(site_id)))
        edit_site.bind(on_release=lambda *_: (popup.dismiss(), self.open_site_editor(site_id)))
        delete_site.bind(on_release=lambda *_: self.delete_site(site_id, popup))
        back_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _reopen_detail_after_delete(self, popup, site_id):
        popup.dismiss()
        Clock.schedule_once(lambda *_: self.open_site_detail(site_id), 0.05)

    def delete_site(self, site_id, parent_popup=None):
        def _do_delete():
            self.sites = [s for s in self.sites if s.get('id') != site_id]
            self._save_sites()
            if parent_popup is not None:
                parent_popup.dismiss()
            self.refresh_ui()
        _confirm_action_popup('Delete Website', 'Remove this website entry and all of its stored page HTML? This only affects the admin registry.', 'Delete', RED, _do_delete)

    def open_page_editor(self, site_id, page_id=None):
        site = self._find_site(site_id)
        if not site:
            info_popup('Missing Website', 'Create the website entry first before adding pages.')
            return
        page = None
        for item in site.get('pages', []):
            if item.get('id') == page_id:
                page = item
                break
        page = normalize_page_entry(page or {})
        is_new = not bool(page_id)
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        fields = {}
        for label, key, multiline, height in [
            ('Page Title', 'title', False, dp(46)),
            ('HTML Filename', 'filename', False, dp(46)),
            ('Page Notes', 'notes', True, dp(80)),
            ('HTML Content', 'html', True, dp(260)),
        ]:
            content.add_widget(make_label(label, height=dp(22)))
            widget = make_input(multiline=multiline)
            widget.text = str(page.get(key, ''))
            widget.height = height
            fields[key] = widget
            content.add_widget(widget)
        action_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        paste_btn = make_button('Paste HTML', UI_CYAN)
        copy_btn = make_button('Copy HTML', UI_CYAN)
        action_row.add_widget(paste_btn)
        action_row.add_widget(copy_btn)
        content.add_widget(action_row)
        btn_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        save_btn = make_button('Save Page', GREEN)
        cancel_btn = make_button('Cancel', UI_CYAN)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        popup = Popup(title='Add Page' if is_new else 'Edit Page', content=content, size_hint=(0.96, 0.98), background_color=get_color_from_hex(CARD))
        cancel_btn.bind(on_release=popup.dismiss)
        paste_btn.bind(on_release=lambda *_: setattr(fields['html'], 'text', Clipboard.paste() or fields['html'].text))
        copy_btn.bind(on_release=lambda *_: copy_to_clipboard('HTML content', fields['html'].text))

        def do_save(*_):
            updated = normalize_page_entry(page)
            updated['title'] = fields['title'].text.strip() or 'Page'
            updated['filename'] = fields['filename'].text.strip() or 'index.html'
            updated['notes'] = fields['notes'].text
            updated['html'] = fields['html'].text
            updated['updated_at'] = now_local_stamp()
            pages = site.get('pages', [])
            if is_new:
                pages.insert(0, updated)
            else:
                for idx, existing in enumerate(pages):
                    if existing.get('id') == updated['id']:
                        pages[idx] = updated
                        break
            site['updated_at'] = now_local_stamp()
            self._save_sites()
            popup.dismiss()
            self.refresh_ui()
            Clock.schedule_once(lambda *_: self.open_site_detail(site_id), 0.05)
        save_btn.bind(on_release=do_save)
        popup.open()

    def delete_page(self, site_id, page_id, refresh_popup=None):
        site = self._find_site(site_id)
        if not site:
            return
        def _do_delete():
            site['pages'] = [p for p in site.get('pages', []) if p.get('id') != page_id]
            site['updated_at'] = now_local_stamp()
            self._save_sites()
            self.refresh_ui()
            if callable(refresh_popup):
                refresh_popup()
        _confirm_action_popup('Delete Page', 'Delete this page entry and its stored HTML content from the website registry?', 'Delete', RED, _do_delete)


def _admin_home_refresh_ui_websites(self, *_):
    AdminHomeScreen.refresh_ui.__wrapped_original__(self) if hasattr(AdminHomeScreen.refresh_ui, '__wrapped_original__') else None


def _admin_home_refresh_ui_with_websites(self, *_):
    # Websites section is now built directly inside refresh_ui (above Exit).
    # This wrapper is kept for compatibility but is a simple passthrough.
    _original_admin_home_refresh_ui(self, *_)


def _company_modules_build_ui_with_websites(self, *_):
    self.clear_widgets()
    root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
    root.add_widget(build_screen_header('Company Modules', 'Reserved hub for future SH Vertex internal products and operating tools.', 'home'))
    card = SectionCard('Live Internal Modules', 'Use these sections to manage websites, documents, releases, and future company systems.')
    rows = [
        ('Websites', lambda: setattr(self.manager, 'current', 'websites'), GREEN),
        ('Documents', lambda: setattr(self.manager, 'current', 'docs'), PURPLE),
        ('Customers', lambda: setattr(self.manager, 'current', 'customers'), BLUE),
        ('Releases', lambda: setattr(self.manager, 'current', 'releases'), ORANGE),
        ('Sales', lambda: show_placeholder('Sales'), PURPLE),
        ('Notes', lambda: show_placeholder('Notes'), BLUE),
        ('Internal Tools', lambda: show_placeholder('Internal Tools'), PURPLE),
        ('Operations', lambda: show_placeholder('Operations'), ORANGE),
    ]
    grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
    grid.bind(minimum_height=grid.setter('height'))
    for label, fn, color in rows:
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , f=fn: f())
        grid.add_widget(btn)
    card.add_widget(grid)
    root.add_widget(card)
    root.add_widget(Widget())
    self.add_widget(root)


_original_admin_home_refresh_ui = AdminHomeScreen.refresh_ui
AdminHomeScreen.refresh_ui = _admin_home_refresh_ui_with_websites
AdminHomeScreen._admin_home_refresh_ui_with_websites = _admin_home_refresh_ui_with_websites
CompanyModulesScreen.build_ui = _company_modules_build_ui_with_websites
CompanyModulesScreen._company_modules_build_ui = _company_modules_build_ui_with_websites
CompanyModulesScreen._company_modules_build_ui_with_websites = _company_modules_build_ui_with_websites


def _new_admin_build(self):
    self.title = 'SH Vertex Admin Panel'
    sm = ScreenManager(transition=FadeTransition())
    sm.add_widget(SplashScreen(name='splash'))
    sm.add_widget(AdminHomeScreen(name='home'))
    sm.add_widget(LicensingHubScreen(name='licensing'))
    sm.add_widget(LicensingAppsScreen(name='apps'))
    sm.add_widget(BackupVaultScreen(name='backup_vault'))
    sm.add_widget(CustomersScreen(name='customers'))
    sm.add_widget(ActivityLogScreen(name='activity'))
    sm.add_widget(ReleaseTrackerScreen(name='releases'))
    sm.add_widget(AuthorityStatusScreen(name='authority_status'))
    sm.add_widget(CompanyModulesScreen(name='company_modules'))
    sm.add_widget(DocumentationScreen(name='docs'))
    sm.add_widget(AppDataBackupScreen(name='app_data_backup'))
    sm.add_widget(WebsitesScreen(name='websites'))
    sm.add_widget(SynapseManagerShellScreen(name='synapse_manager'))
    sm.add_widget(CasinoManagerShellScreen(name='casino_manager'))
    sm.current = 'splash'
    return sm

SHVertexAdminPanelApp.build = _new_admin_build


# app run moved to end after patch attachments




# ---- APK-safe lazy loading for heavy licensing modules ----
def _apk_safe_synapse_shell_build_ui(self, *_):
    self.clear_widgets()
    self.manager_widget = None
    root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    nav = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    back_btn = make_button('Back to Apps', UI_CYAN)
    home_btn = make_button('Admin Home', UI_CYAN)
    vault_btn = make_button('Vault', UI_CYAN)
    back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'apps'))
    home_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))
    vault_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'backup_vault'))
    nav.add_widget(back_btn)
    nav.add_widget(home_btn)
    nav.add_widget(vault_btn)
    root.add_widget(nav)
    placeholder = SectionCard('Synapse Licensing', 'Loading is deferred until you actually open this screen, which is safer for the packaged APK startup path.')
    placeholder.add_widget(make_label('Open this screen to load the full Synapse licensing interface.', color=SUBTEXT, height=dp(28)))
    self._body_host = BoxLayout()
    self._body_host.add_widget(placeholder)
    root.add_widget(self._body_host)
    self.add_widget(root)

def _apk_safe_synapse_shell_on_pre_enter(self, *_):
    if getattr(self, 'manager_widget', None) is None:
        if hasattr(self, '_body_host'):
            self._body_host.clear_widgets()
            loading = SectionCard('Synapse Licensing', 'Loading the interface...')
            loading.add_widget(make_label('Please wait while the licensing tools initialize.', color=SUBTEXT, height=dp(28)))
            self._body_host.add_widget(loading)

        def _load_widget(*__):
            try:
                self.manager_widget = LicenseManagerScreen()
                if hasattr(self, '_body_host'):
                    self._body_host.clear_widgets()
                    self._body_host.add_widget(self.manager_widget)
            except Exception as e:
                if hasattr(self, '_body_host'):
                    self._body_host.clear_widgets()
                    failed = SectionCard('Synapse Licensing Error', 'The APK hit an initialization error while opening this module.')
                    failed.add_widget(make_label(str(e), color=RED, height=dp(72)))
                    retry_btn = make_button('Retry', GREEN)
                    retry_btn.bind(on_release=lambda *_: _apk_safe_synapse_shell_on_pre_enter(self))
                    failed.add_widget(retry_btn)
                    self._body_host.add_widget(failed)

        Clock.schedule_once(_load_widget, 0)

def _apk_safe_casino_shell_build_ui(self, *_):
    self.clear_widgets()
    self.manager_widget = None
    root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
    nav = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    back_btn = make_button('Back to Apps', UI_CYAN)
    home_btn = make_button('Admin Home', UI_CYAN)
    vault_btn = make_button('Vault', UI_CYAN)
    back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'apps'))
    home_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))
    vault_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'backup_vault'))
    nav.add_widget(back_btn)
    nav.add_widget(home_btn)
    nav.add_widget(vault_btn)
    root.add_widget(nav)
    placeholder = SectionCard('Casino Tools Pro Licensing', 'Loading is deferred until you actually open this screen, which is safer for the packaged APK startup path.')
    placeholder.add_widget(make_label('Open this screen to load the full Casino Tools Pro licensing interface.', color=SUBTEXT, height=dp(28)))
    self._body_host = BoxLayout()
    self._body_host.add_widget(placeholder)
    root.add_widget(self._body_host)
    self.add_widget(root)

def _apk_safe_casino_shell_on_pre_enter(self, *_):
    if getattr(self, 'manager_widget', None) is None:
        if hasattr(self, '_body_host'):
            self._body_host.clear_widgets()
            loading = SectionCard('Casino Tools Pro Licensing', 'Loading the interface...')
            loading.add_widget(make_label('Please wait while the licensing tools initialize.', color=SUBTEXT, height=dp(28)))
            self._body_host.add_widget(loading)

        def _load_widget(*__):
            try:
                self.manager_widget = CasinoToolsLicenseManagerScreen()
                if hasattr(self, '_body_host'):
                    self._body_host.clear_widgets()
                    self._body_host.add_widget(self.manager_widget)
            except Exception as e:
                if hasattr(self, '_body_host'):
                    self._body_host.clear_widgets()
                    failed = SectionCard('Casino Tools Pro Licensing Error', 'The APK hit an initialization error while opening this module.')
                    failed.add_widget(make_label(str(e), color=RED, height=dp(72)))
                    retry_btn = make_button('Retry', GREEN)
                    retry_btn.bind(on_release=lambda *_: _apk_safe_casino_shell_on_pre_enter(self))
                    failed.add_widget(retry_btn)
                    self._body_host.add_widget(failed)

        Clock.schedule_once(_load_widget, 0)

SynapseManagerShellScreen.build_ui = _apk_safe_synapse_shell_build_ui
SynapseManagerShellScreen.on_pre_enter = _apk_safe_synapse_shell_on_pre_enter
CasinoManagerShellScreen.build_ui = _apk_safe_casino_shell_build_ui
CasinoManagerShellScreen.on_pre_enter = _apk_safe_casino_shell_on_pre_enter

SynapseManagerShellScreen._apk_safe_synapse_shell_build_ui = _apk_safe_synapse_shell_build_ui
SynapseManagerShellScreen._apk_safe_synapse_shell_on_pre_enter = _apk_safe_synapse_shell_on_pre_enter
CasinoManagerShellScreen._apk_safe_casino_shell_build_ui = _apk_safe_casino_shell_build_ui
CasinoManagerShellScreen._apk_safe_casino_shell_on_pre_enter = _apk_safe_casino_shell_on_pre_enter

# ---- restore safe local-authority removal for Synapse + Casino Tools Pro ----
SYNAPSE_AUTHORITY_REMOVED_FLAG = "synapse_authority_removed.flag"


def _synapse_authority_removed_flag_path():
    return file_path(SYNAPSE_AUTHORITY_REMOVED_FLAG)


_original_synapse_ensure_default_authority_files = ensure_default_authority_files


def _guarded_synapse_ensure_default_authority_files():
    if os.path.exists(_synapse_authority_removed_flag_path()):
        return
    return _original_synapse_ensure_default_authority_files()


ensure_default_authority_files = _guarded_synapse_ensure_default_authority_files

_original_synapse_initialize_authority_keypair = initialize_authority_keypair


def _guarded_synapse_initialize_authority_keypair():
    flag_path = _synapse_authority_removed_flag_path()
    if os.path.exists(flag_path):
        try:
            os.remove(flag_path)
        except Exception:
            pass
    return _original_synapse_initialize_authority_keypair()


initialize_authority_keypair = _guarded_synapse_initialize_authority_keypair

_original_synapse_write_authority_payload = LicenseManagerScreen._write_authority_payload


def _patched_synapse_write_authority_payload(self, payload):
    result = _original_synapse_write_authority_payload(self, payload)
    flag_path = _synapse_authority_removed_flag_path()
    if os.path.exists(flag_path):
        try:
            os.remove(flag_path)
        except Exception:
            pass
    return result


LicenseManagerScreen._write_authority_payload = _patched_synapse_write_authority_payload


def _make_local_authority_remove_methods(product_label, file_path_func, private_key_name, public_key_name, *, flag_path_func=None):
    def confirm_remove_local_authority(self):
        private_path = file_path_func(private_key_name)
        public_path = file_path_func(public_key_name)
        has_local = any(os.path.exists(p) for p in (private_path, public_path)) or bool(getattr(self, 'public_key', None) or getattr(self, 'private_key', None))
        if not has_local:
            info_popup('No authority loaded', f'No local {product_label} authority is currently stored on this admin device.')
            return

        content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
        message = Label(
            text=(
                f"Remove the local {product_label} authority from this admin device?\n\n"
                "This deletes only the active PEM files for this product on this device. "
                "The local license list stays untouched.\n\n"
                "Type REMOVE below to confirm."
            ),
            color=get_color_from_hex(TEXT),
            halign='left',
            valign='top',
            text_size=(dp(300), None),
            size_hint_y=None,
        )
        message.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(dp(150), val[1])))
        content.add_widget(message)

        confirm_input = make_input('Type REMOVE to confirm')
        content.add_widget(confirm_input)

        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        cancel_btn = make_button('Cancel', UI_CYAN)
        remove_btn = make_button('Remove Local Authority', RED)
        row.add_widget(cancel_btn)
        row.add_widget(remove_btn)
        content.add_widget(row)

        popup = Popup(
            title='Remove Local Authority',
            content=content,
            size_hint=(0.92, 0.66),
            separator_color=get_color_from_hex(RED),
            background_color=get_color_from_hex(CARD),
        )
        cancel_btn.bind(on_release=popup.dismiss)
        remove_btn.bind(on_release=lambda *_: self.perform_remove_local_authority(confirm_input.text, popup))
        popup.open()

    def perform_remove_local_authority(self, confirmation_text='', popup=None):
        if str(confirmation_text or '').strip().upper() != 'REMOVE':
            info_popup('Confirmation required', 'Type REMOVE exactly to delete the local authority files.')
            return

        removed = []
        errors = []
        for key_name in (private_key_name, public_key_name):
            local_path = file_path_func(key_name)
            if os.path.exists(local_path):
                try:
                    os.remove(local_path)
                    removed.append(os.path.basename(local_path))
                except Exception as exc:
                    errors.append(f'{os.path.basename(local_path)}: {exc}')

        if flag_path_func is not None:
            try:
                flag_path = flag_path_func()
                os.makedirs(os.path.dirname(flag_path), exist_ok=True)
                with open(flag_path, 'w', encoding='utf-8') as f:
                    f.write(utc_now_iso())
            except Exception as exc:
                errors.append(f'flag file: {exc}')

        self.public_key = None
        self.private_key = None
        if hasattr(self, '_last_license_id'):
            self._last_license_id = ''

        if popup is not None:
            popup.dismiss()

        for fn_name in ('update_authority_status', 'refresh_dashboard', 'refresh_license_list', 'refresh_revocation_box'):
            fn = getattr(self, fn_name, None)
            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass

        summary = ', '.join(removed) if removed else 'no key files were present'
        message = f'Local {product_label} authority removed. Deleted: {summary}.\n\nLocal license list data was left untouched.'
        if errors:
            message += '\n\nWarnings:\n' + '\n'.join(errors[:5])
        info_popup('Authority removed', message)

    return confirm_remove_local_authority, perform_remove_local_authority


def _patch_authority_view_with_remove_button(screen_cls, make_button_func):
    original_build_authority_view = screen_cls.build_authority_view

    def patched_build_authority_view(self, *args, **kwargs):
        view = original_build_authority_view(self, *args, **kwargs)
        try:
            host_box = view.children[0] if getattr(view, 'children', None) else None
            if host_box is None or not getattr(host_box, 'children', None):
                return view
            authority_card = host_box.children[-1]
            if getattr(authority_card, '_local_authority_remove_added', False):
                return view

            authority_card.add_widget(make_label('Authority removal', color=RED, height=dp(24)))
            authority_card.add_widget(make_label(
                'Use this only when you intentionally want to clear the active authority from this device. Your local license list remains intact.',
                color=SUBTEXT,
                height=dp(50),
            ))
            remove_btn = make_button_func('Remove Local Authority', RED)
            remove_btn.bind(on_release=lambda *_: self.confirm_remove_local_authority())
            authority_card.add_widget(remove_btn)
            authority_card._local_authority_remove_added = True
        except Exception:
            pass
        return view

    screen_cls.build_authority_view = patched_build_authority_view


_syn_confirm_remove, _syn_perform_remove = _make_local_authority_remove_methods(
    'Synapse',
    file_path,
    PRIVATE_KEY_FILE,
    PUBLIC_KEY_FILE,
    flag_path_func=_synapse_authority_removed_flag_path,
)
LicenseManagerScreen.confirm_remove_local_authority = _syn_confirm_remove
LicenseManagerScreen.perform_remove_local_authority = _syn_perform_remove
_patch_authority_view_with_remove_button(LicenseManagerScreen, make_button)


_ctp_confirm_remove, _ctp_perform_remove = _make_local_authority_remove_methods(
    'Casino Tools Pro',
    _CTP_NS['file_path'],
    _CTP_NS['PRIVATE_KEY_FILE'],
    _CTP_NS['PUBLIC_KEY_FILE'],
)
CasinoToolsLicenseManagerScreen.confirm_remove_local_authority = _ctp_confirm_remove
CasinoToolsLicenseManagerScreen.perform_remove_local_authority = _ctp_perform_remove
_patch_authority_view_with_remove_button(CasinoToolsLicenseManagerScreen, _CTP_NS['make_button'])




_ADMIN_SOUND_PATH_CACHE = {}
ADMIN_SOUND_PREFS_FILE = 'admin_sound_prefs.json'
ADMIN_BG_MUSIC_DEFAULT_VOLUME = 0.35


def _admin_sound_prefs_path():
    return file_path(ADMIN_SOUND_PREFS_FILE)


def _load_admin_sound_prefs():
    data = load_json(_admin_sound_prefs_path(), {})
    if not isinstance(data, dict):
        data = {}
    try:
        volume = float(data.get('bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME))
    except Exception:
        volume = ADMIN_BG_MUSIC_DEFAULT_VOLUME
    volume = max(0.0, min(1.0, volume))
    return {
        'bg_music_muted': bool(data.get('bg_music_muted', False)),
        'bg_music_volume': volume,
    }


def _save_admin_sound_prefs(app):
    try:
        payload = {
            'bg_music_muted': bool(getattr(app, '_bg_music_muted', False)),
            'bg_music_volume': float(getattr(app, '_bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME) or ADMIN_BG_MUSIC_DEFAULT_VOLUME),
        }
    except Exception:
        payload = {'bg_music_muted': False, 'bg_music_volume': ADMIN_BG_MUSIC_DEFAULT_VOLUME}
    payload['bg_music_volume'] = max(0.0, min(1.0, float(payload.get('bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME))))
    save_json(_admin_sound_prefs_path(), payload)


def _get_sound_length_seconds(path):
    if not path:
        return 0.0
    try:
        probe = SoundLoader.load(path)
        if probe is not None:
            duration = float(getattr(probe, 'length', 0.0) or 0.0)
            try:
                probe.unload()
            except Exception:
                pass
            if duration > 0:
                return duration
    except Exception:
        pass
    try:
        if str(path).lower().endswith('.wav'):
            import wave
            with wave.open(path, 'rb') as wav_file:
                frames = wav_file.getnframes() or 0
                rate = wav_file.getframerate() or 1
                return float(frames) / float(rate)
    except Exception:
        pass
    return 0.0


def _resolve_admin_sound_path(*candidate_names):
    names = [str(name).strip() for name in candidate_names if str(name).strip()]
    for name in names:
        cached = _ADMIN_SOUND_PATH_CACHE.get(name)
        if cached and os.path.exists(cached):
            return cached
        if os.path.isabs(name) and os.path.exists(name):
            _ADMIN_SOUND_PATH_CACHE[name] = name
            return name
        for base in (
            os.getcwd(),
            os.path.dirname(os.path.abspath(__file__)),
            '/storage/emulated/0/Download',
            '/storage/emulated/0/Download/SH Vertex Admin Panel',
            '/storage/emulated/0',
            '/sdcard/Download',
            '/sdcard',
        ):
            if not base:
                continue
            candidate = os.path.join(base, name)
            if os.path.exists(candidate):
                _ADMIN_SOUND_PATH_CACHE[name] = candidate
                return candidate

    walk_roots = []
    for root in ('/storage/emulated/0', '/sdcard'):
        if os.path.exists(root):
            walk_roots.append(root)
    lowered = {name.lower(): name for name in names}
    for root in walk_roots:
        try:
            for current_root, _dirs, files in os.walk(root):
                for file_name in files:
                    key = str(file_name).strip().lower()
                    if key in lowered:
                        resolved = os.path.join(current_root, file_name)
                        for original_name in names:
                            if key == original_name.lower():
                                _ADMIN_SOUND_PATH_CACHE[original_name] = resolved
                        return resolved
        except Exception:
            continue
    return ''


def _apply_handle_volume(handle, volume):
    try:
        volume = max(0.0, min(1.0, float(volume)))
    except Exception:
        volume = 1.0
    try:
        if not handle:
            return
        kind, obj = handle
        if kind == 'soundloader' and obj is not None:
            obj.volume = volume
        elif kind == 'mediaplayer' and obj is not None:
            obj.setVolume(volume, volume)
    except Exception:
        pass


def _play_admin_sound_with_fallback(path, volume=1.0, loop=False, prefer_mediaplayer=False):
    if not path:
        return None, 0.0

    def _try_soundloader():
        try:
            sound = SoundLoader.load(path)
        except Exception:
            sound = None
        if sound is not None:
            try:
                try:
                    sound.stop()
                except Exception:
                    pass
                if hasattr(sound, 'loop'):
                    try:
                        sound.loop = bool(loop)
                    except Exception:
                        pass
                sound.volume = max(0.0, min(1.0, float(volume)))
                sound.play()
                duration = float(getattr(sound, 'length', 0.0) or 0.0)
                return ('soundloader', sound), duration
            except Exception:
                pass
        return None, 0.0

    def _try_mediaplayer():
        try:
            from jnius import autoclass
            MediaPlayer = autoclass('android.media.MediaPlayer')
            AudioManager = autoclass('android.media.AudioManager')
            player = MediaPlayer()
            player.setAudioStreamType(AudioManager.STREAM_MUSIC)
            player.setDataSource(path)
            player.prepare()
            try:
                player.setLooping(bool(loop))
            except Exception:
                pass
            try:
                vv = max(0.0, min(1.0, float(volume)))
                player.setVolume(vv, vv)
            except Exception:
                pass
            duration = 0.0
            try:
                duration = float(player.getDuration() or 0) / 1000.0
            except Exception:
                duration = 0.0
            player.start()
            return ('mediaplayer', player), duration
        except Exception:
            return None, 0.0

    if prefer_mediaplayer:
        handle, duration = _try_mediaplayer()
        if handle:
            return handle, duration
        return _try_soundloader()

    handle, duration = _try_soundloader()
    if handle:
        return handle, duration
    return _try_mediaplayer()


def _stop_admin_sound_handle(handle):
    try:
        if not handle:
            return
        kind, obj = handle
        if kind == 'soundloader' and obj is not None:
            try:
                obj.stop()
            except Exception:
                pass
        elif kind == 'mediaplayer' and obj is not None:
            try:
                obj.stop()
            except Exception:
                pass
            try:
                obj.release()
            except Exception:
                pass
    except Exception:
        pass


def _admin_play_named_sound_detached(self, *candidate_names, volume=1.0, prefer_mediaplayer=False):
    path = _resolve_admin_sound_path(*candidate_names)
    self._admin_last_sound_path = path or ''
    self._admin_last_sound_backend = 'none'
    if not path:
        return 0.0
    handle, duration = _play_admin_sound_with_fallback(path, volume=volume, loop=False, prefer_mediaplayer=prefer_mediaplayer)
    if handle:
        try:
            self._admin_last_sound_backend = str(handle[0])
        except Exception:
            self._admin_last_sound_backend = 'unknown'
        hold_for = max(0.4, float(duration or 0.0) + 0.35)
        Clock.schedule_once(lambda *_: _stop_admin_sound_handle(handle), hold_for)
    return float(duration or 0.0)


def _admin_start_background_music(self, *_):
    if bool(getattr(self, '_bg_music_muted', False)):
        return 0.0
    path = _resolve_admin_sound_path('backgroundsound.wav', 'background sound.wav')
    self._admin_last_sound_path = path or ''
    if not path:
        return 0.0
    _stop_admin_sound_handle(getattr(self, '_bg_music_handle', None))
    self._bg_music_handle = None
    volume = max(0.0, min(1.0, float(getattr(self, '_bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME) or ADMIN_BG_MUSIC_DEFAULT_VOLUME)))
    handle, duration = _play_admin_sound_with_fallback(path, volume=volume, loop=True, prefer_mediaplayer=True)
    self._bg_music_handle = handle
    if handle:
        try:
            self._admin_last_sound_backend = str(handle[0])
        except Exception:
            self._admin_last_sound_backend = 'unknown'
    return float(duration or 0.0)


def _admin_stop_background_music(self, *_):
    _stop_admin_sound_handle(getattr(self, '_bg_music_handle', None))
    self._bg_music_handle = None


def _admin_apply_background_music_state(self, *_):
    if bool(getattr(self, '_bg_music_muted', False)):
        self.stop_background_music()
        return
    if getattr(self, '_bg_music_handle', None):
        _apply_handle_volume(self._bg_music_handle, getattr(self, '_bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME))
        return
    self.start_background_music()


def _admin_refresh_home_if_visible(self):
    try:
        if self.root and getattr(self.root, 'current', '') == 'home':
            self.root.get_screen('home').refresh_ui()
    except Exception:
        pass


def _admin_toggle_background_music_mute(self, *_):
    self._bg_music_muted = not bool(getattr(self, '_bg_music_muted', False))
    _save_admin_sound_prefs(self)
    self.apply_background_music_state()
    self._admin_refresh_home_if_visible()


def _admin_change_background_music_volume(self, delta, *_):
    try:
        current = float(getattr(self, '_bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME) or ADMIN_BG_MUSIC_DEFAULT_VOLUME)
    except Exception:
        current = ADMIN_BG_MUSIC_DEFAULT_VOLUME
    current = max(0.0, min(1.0, current + float(delta)))
    self._bg_music_volume = current
    _save_admin_sound_prefs(self)
    if not bool(getattr(self, '_bg_music_muted', False)):
        if getattr(self, '_bg_music_handle', None):
            _apply_handle_volume(self._bg_music_handle, self._bg_music_volume)
        else:
            self.start_background_music()
    self._admin_refresh_home_if_visible()


def _admin_app_on_start(self):
    self._exit_in_progress = False
    self._bg_music_handle = None
    self._admin_last_sound_path = ''
    self._admin_last_sound_backend = 'none'
    prefs = _load_admin_sound_prefs()
    self._bg_music_muted = bool(prefs.get('bg_music_muted', False))
    self._bg_music_volume = float(prefs.get('bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME) or ADMIN_BG_MUSIC_DEFAULT_VOLUME)
    startup_path = _resolve_admin_sound_path('shv startup.wav', 'shvstartup.wav')
    startup_len = _get_sound_length_seconds(startup_path)
    self._admin_last_startup_duration = startup_len
    startup_delay = 0.20
    Clock.schedule_once(lambda *_: self.play_startup_sound(), startup_delay)
    if not self._bg_music_muted:
        bg_delay = startup_delay + max(0.0, startup_len) + 0.60
        Clock.schedule_once(lambda *_: self.start_background_music(), bg_delay)


def _admin_on_stop(self):
    self.stop_background_music()


def _admin_play_startup_sound(self, *_):
    startup_len = self._admin_play_named_sound_detached('shv startup.wav', 'shvstartup.wav', volume=1.0, prefer_mediaplayer=True)
    if startup_len > 0:
        self._admin_last_startup_duration = startup_len
    return startup_len


def _admin_test_startup_sound(self, *_):
    had_bg = bool(getattr(self, '_bg_music_handle', None))
    if had_bg:
        self.stop_background_music()
    delay = self._admin_play_named_sound_detached('shv startup.wav', 'shvstartup.wav', volume=1.0, prefer_mediaplayer=False)
    if had_bg and not bool(getattr(self, '_bg_music_muted', False)):
        Clock.schedule_once(lambda *_: self.start_background_music(), max(0.6, float(delay or 0.0) + 0.15))
    path = getattr(self, '_admin_last_sound_path', '') or '(not found)'
    backend = getattr(self, '_admin_last_sound_backend', 'none')
    info_popup('Startup Sound Test', f"Path: {path}\nBackend: {backend}\nDuration: {round(float(delay or 0.0), 2)}s")


def _admin_test_logoff_sound(self, *_):
    had_bg = bool(getattr(self, '_bg_music_handle', None))
    if had_bg:
        self.stop_background_music()
    delay = self._admin_play_named_sound_detached('shvlogoff.wav', 'shv logoff.wav', volume=1.0, prefer_mediaplayer=False)
    if had_bg and not bool(getattr(self, '_bg_music_muted', False)):
        Clock.schedule_once(lambda *_: self.start_background_music(), max(0.6, float(delay or 0.0) + 0.15))
    path = getattr(self, '_admin_last_sound_path', '') or '(not found)'
    backend = getattr(self, '_admin_last_sound_backend', 'none')
    info_popup('Logoff Sound Test', f"Path: {path}\nBackend: {backend}\nDuration: {round(float(delay or 0.0), 2)}s")


def _admin_play_exit_sound_then_stop(self, *_):
    if getattr(self, '_exit_in_progress', False):
        return
    self._exit_in_progress = True
    self.stop_background_music()
    try:
        delay = float(self._admin_play_named_sound_detached('shvlogoff.wav', 'shv logoff.wav', volume=1.0, prefer_mediaplayer=True) or 0.0)
    except Exception:
        delay = 0.0
    wait_time = max(0.35, min(float(delay or 0.0) + 0.10, 6.0)) if delay > 0 else 0.35

    def _final_stop(*__):
        try:
            self.stop()
        finally:
            self._exit_in_progress = False

    Clock.schedule_once(_final_stop, wait_time)


def _admin_home_refresh_ui_with_sound_controls(self, *_):
    _admin_home_refresh_ui_with_websites(self, *_)
    if not hasattr(self, 'root_box'):
        return
    app = App.get_running_app()
    muted = bool(getattr(app, '_bg_music_muted', False)) if app else False
    volume = float(getattr(app, '_bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME) or ADMIN_BG_MUSIC_DEFAULT_VOLUME) if app else ADMIN_BG_MUSIC_DEFAULT_VOLUME
    volume_pct = int(round(volume * 100))

    music_card = SectionCard('BACKGROUND MUSIC', 'Control in-app background music. Mute and volume are remembered next time you open the app.')
    state_text = 'Muted' if muted else 'Playing'
    music_card.add_widget(make_label(f'Status: {state_text}', color=SUBTEXT, height=dp(24)))
    music_card.add_widget(make_label(f'Volume: {volume_pct}%', color=SUBTEXT, height=dp(24)))

    top_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    mute_btn = make_button('Unmute Music' if muted else 'Mute Music', ORANGE if muted else PURPLE)
    test_bg_btn = make_button('Restart Music', UI_CYAN)
    mute_btn.bind(on_release=lambda *_: App.get_running_app().toggle_background_music_mute())
    test_bg_btn.bind(on_release=lambda *_: App.get_running_app().start_background_music() if not getattr(App.get_running_app(), '_bg_music_muted', False) else None)
    top_row.add_widget(mute_btn)
    top_row.add_widget(test_bg_btn)
    music_card.add_widget(top_row)

    vol_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    minus_btn = make_button('Volume -', UI_CYAN)
    plus_btn = make_button('Volume +', GREEN)
    minus_btn.bind(on_release=lambda *_: App.get_running_app().change_background_music_volume(-0.10))
    plus_btn.bind(on_release=lambda *_: App.get_running_app().change_background_music_volume(0.10))
    vol_row.add_widget(minus_btn)
    vol_row.add_widget(plus_btn)
    music_card.add_widget(vol_row)

    self.root_box.add_widget(music_card)


SHVertexAdminPanelApp._admin_play_named_sound_detached = _admin_play_named_sound_detached
SHVertexAdminPanelApp._admin_refresh_home_if_visible = _admin_refresh_home_if_visible
SHVertexAdminPanelApp.on_start = _admin_app_on_start
SHVertexAdminPanelApp.on_stop = _admin_on_stop
SHVertexAdminPanelApp.play_startup_sound = _admin_play_startup_sound
SHVertexAdminPanelApp.play_exit_sound_then_stop = _admin_play_exit_sound_then_stop
SHVertexAdminPanelApp.start_background_music = _admin_start_background_music
SHVertexAdminPanelApp.stop_background_music = _admin_stop_background_music
SHVertexAdminPanelApp.apply_background_music_state = _admin_apply_background_music_state
SHVertexAdminPanelApp.toggle_background_music_mute = _admin_toggle_background_music_mute
SHVertexAdminPanelApp.change_background_music_volume = _admin_change_background_music_volume
SHVertexAdminPanelApp.test_startup_sound = _admin_test_startup_sound
SHVertexAdminPanelApp.test_logoff_sound = _admin_test_logoff_sound
AdminHomeScreen.refresh_ui = _admin_home_refresh_ui_with_sound_controls
AdminHomeScreen._admin_home_refresh_ui_with_sound_controls = _admin_home_refresh_ui_with_sound_controls



# ---- premium UI overhaul patch (UI only; logic preserved) ----
try:
    from kivy.animation import Animation
except Exception:
    Animation = None
from kivy.graphics import Color as _UIColor, RoundedRectangle as _UIRoundedRectangle, Line as _UILine, Ellipse as _UIEllipse

UI_BLACK  = '#000000'   # pure AMOLED black
UI_CARD   = '#0d0d0d'   # card surface
UI_CARD_2 = '#111111'   # stat chip surface
UI_MUTE   = '#64748b'   # muted secondary text
UI_TEXT   = '#e2e8f0'   # primary text
UI_GREEN  = '#00c8b4'   # TEAL — primary action (confirm / generate)
UI_TEAL   = '#00c8b4'   # alias
UI_CYAN   = '#1e3a50'   # SLATE — secondary / nav / copy
UI_PURPLE = '#1e3a50'   # SLATE — was noisy purple
UI_RED    = '#f43f5e'   # ROSE  — danger only (exit / delete / revoke)
UI_ORANGE = '#1e3a50'   # SLATE — was noisy orange
UI_LINE   = '#1a2533'   # subtle border
UI_SOFT   = '#0a0f14'   # disabled fill

# keep compatibility with existing color names
CARD    = UI_CARD
TEXT    = UI_TEXT
SUBTEXT = UI_MUTE
GREEN   = UI_GREEN
BLUE    = UI_CYAN
PURPLE  = UI_PURPLE
RED     = UI_RED
ORANGE  = UI_ORANGE
Window.clearcolor = get_color_from_hex(UI_BLACK)


def _hex_rgba(hex_color, alpha=1.0):
    rgba = list(get_color_from_hex(hex_color))
    if len(rgba) == 3:
        rgba.append(alpha)
    else:
        rgba[3] = alpha
    return tuple(rgba)


def _mix_hex(a, b, w=0.5):
    ar, ag, ab, _ = _hex_rgba(a)
    br, bg, bb, _ = _hex_rgba(b)
    return (ar * (1 - w) + br * w, ag * (1 - w) + bg * w, ab * (1 - w) + bb * w, 1)


def _section_accent(title=''):
    t = str(title or '').lower()
    if 'casino' in t:
        return UI_PURPLE
    if 'synapse' in t or 'project' in t or 'time' in t:
        return UI_TEAL
    if 'website' in t or 'web' in t:
        return UI_CYAN
    if 'backup' in t or 'vault' in t:
        return UI_ORANGE
    if 'release' in t or 'activity' in t or 'customer' in t:
        return UI_CYAN
    if 'exit' in t or 'danger' in t or 'delete' in t:
        return UI_RED
    if 'licens' in t or 'authority' in t or 'revocation' in t:
        return UI_GREEN
    return UI_GREEN


def _button_fill_for(color_hex):
    c = str(color_hex or UI_GREEN).lower().strip()
    teal_set  = {'#00c8b4', UI_GREEN.lower(), UI_TEAL.lower()}
    red_set   = {'#f43f5e', UI_RED.lower()}
    slate_set = {'#1e3a50', UI_CYAN.lower(), UI_PURPLE.lower(), UI_ORANGE.lower()}
    if c in teal_set:   return '#0a1f1d'
    if c in red_set:    return '#1c0f12'
    if c in slate_set:  return '#0a1520'
    return '#0a1f1d'


def _button_border_for(color_hex):
    c = str(color_hex or UI_GREEN).lower().strip()
    teal_set  = {'#00c8b4', UI_GREEN.lower(), UI_TEAL.lower()}
    red_set   = {'#f43f5e', UI_RED.lower()}
    slate_set = {'#1e3a50', UI_CYAN.lower(), UI_PURPLE.lower(), UI_ORANGE.lower()}
    if c in teal_set:   return '#7ef1e6'
    if c in red_set:    return '#ff7f8e'
    if c in slate_set:  return '#2a5070'
    return '#7ef1e6'


def _soft_text(label, size='12sp', color=UI_MUTE, bold=False, height=dp(20), halign='center'):
    lbl = Label(text=label, color=get_color_from_hex(color), bold=bold, font_size=size, size_hint_y=None, height=height, halign=halign, valign='middle')
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    return lbl


class AccentDot(Widget):
    def __init__(self, color_hex=UI_GREEN, size_px=dp(11), **kwargs):
        kwargs.setdefault('size_hint', (None, None))
        kwargs.setdefault('size', (size_px, size_px))
        super().__init__(**kwargs)
        self._color_hex = color_hex
        with self.canvas.before:
            self._dot_color = _UIColor(*_hex_rgba(color_hex, 1))
            self._dot = _UIEllipse(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)
        self._upd()
    def _upd(self, *_):
        self._dot.pos = self.pos
        self._dot.size = self.size
        self._dot_color.rgba = _hex_rgba(self._color_hex, 1)


class RoundedButton(Button):
    def __init__(self, bg_hex=UI_GREEN, text_color=None, radius=18, border_hex=None, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_down', '')
        kwargs.setdefault('background_color', (0, 0, 0, 0))
        kwargs.setdefault('color', get_color_from_hex(UI_TEXT))
        kwargs.setdefault('font_size', '14sp')
        kwargs.setdefault('bold', True)
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(48))
        kwargs.setdefault('halign', 'center')
        kwargs.setdefault('valign', 'middle')
        super().__init__(**kwargs)
        self._accent_hex = str(bg_hex or UI_GREEN)
        self._fill_hex = _button_fill_for(self._accent_hex)
        self._border_hex = border_hex or _button_border_for(self._accent_hex)
        self._radius = dp(radius)
        self._inset = dp(2)
        if text_color is not None:
            self.color = text_color
        self.bind(size=lambda inst, val: setattr(inst, 'text_size', (max(0, val[0] - dp(8)), max(0, val[1] - dp(4)))))
        with self.canvas.before:
            self._shadow_color = _UIColor(*_hex_rgba('#000000', 0.30))
            self._shadow = _UIRoundedRectangle(pos=(self.x, self.y - dp(2)), size=self.size, radius=[self._radius])
            self._border_color = _UIColor(*_hex_rgba(self._border_hex, 0.95))
            self._border = _UIRoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])
            self._fill_color = _UIColor(*_hex_rgba(self._fill_hex, 1))
            self._fill = _UIRoundedRectangle(pos=self.pos, size=self.size, radius=[max(dp(6), self._radius - self._inset)])
        self.bind(pos=self._update_bg, size=self._update_bg, state=self._update_bg, disabled=self._update_bg)
        self._update_bg()

    def _update_bg(self, *_):
        pressed = self.state == 'down'
        border = _button_border_for(self._accent_hex)
        fill = _button_fill_for(self._accent_hex)
        if pressed:
            fill_rgba = _mix_hex(fill, self._accent_hex, 0.25)
            border_rgba = _hex_rgba(border, 1.0)
        else:
            fill_rgba = _hex_rgba(fill, 1.0)
            border_rgba = _hex_rgba(border, 0.96)
        self._shadow.pos = (self.x, self.y - dp(2))
        self._shadow.size = self.size
        self._border.pos = self.pos
        self._border.size = self.size
        self._fill.pos = (self.x + self._inset, self.y + self._inset)
        self._fill.size = (max(0, self.width - self._inset * 2), max(0, self.height - self._inset * 2))
        self._shadow_color.rgba = _hex_rgba('#000000', 0.34 if not self.disabled else 0.14)
        self._border_color.rgba = border_rgba if not self.disabled else _hex_rgba(UI_LINE, 0.6)
        self._fill_color.rgba = fill_rgba if not self.disabled else _hex_rgba(UI_SOFT, 0.85)
        self.opacity = 0.96 if pressed else 1.0


class SectionCard(BoxLayout):
    def __init__(self, title, subtitle='', accent=None, **kwargs):
        kwargs.setdefault('orientation', 'vertical')
        kwargs.setdefault('spacing', dp(10))
        kwargs.setdefault('padding', [dp(14), dp(14), dp(14), dp(14)])
        kwargs.setdefault('size_hint_y', None)
        super().__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self._accent = accent or _section_accent(title)
        with self.canvas.before:
            self._shadow_color = _UIColor(*_hex_rgba('#000000', 0.34))
            self._shadow = _UIRoundedRectangle(pos=(self.x, self.y - dp(2)), size=self.size, radius=[dp(24)])
            self._bg_color = _UIColor(*_hex_rgba(UI_CARD, 1))
            self._bg = _UIRoundedRectangle(pos=self.pos, size=self.size, radius=[dp(24)])
            self._bar_color = _UIColor(*_hex_rgba(self._accent, 0.95))
            self._bar = _UIRoundedRectangle(pos=self.pos, size=(self.width, dp(4)), radius=[dp(24), dp(24), dp(10), dp(10)])
            self._line_color = _UIColor(*_hex_rgba(UI_LINE, 0.9))
            self._line = _UILine(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(24)), width=1.1)
        self.bind(pos=self._update_bg, size=self._update_bg)
        self._update_bg()

        head = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        head.bind(minimum_height=head.setter('height'))
        title_lbl = Label(text=title, color=get_color_from_hex(UI_TEXT), bold=True, font_size='20sp', size_hint_y=None, height=dp(30), halign='center', valign='middle')
        title_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        head.add_widget(title_lbl)
        if subtitle:
            sub_lbl = Label(text=subtitle, color=get_color_from_hex(UI_MUTE), font_size='12sp', size_hint_y=None, halign='center', valign='middle')
            sub_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
            sub_lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(dp(18), val[1])))
            head.add_widget(sub_lbl)
        self.add_widget(head)

    def _update_bg(self, *_):
        self._shadow.pos = (self.x, self.y - dp(2))
        self._shadow.size = self.size
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bar.pos = self.pos
        self._bar.size = (self.width, dp(4))
        self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(24))


def make_label(text, color=UI_TEXT, bold=False, height=dp(24)):
    lbl = Label(text=text, color=get_color_from_hex(color), bold=bold, size_hint_y=None, height=height, halign='center', valign='middle')
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
    lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', max(height, val[1] + dp(4))))
    return lbl


def _style_input_bg(widget, fill='#0c1118', border='#243141', radius=18):
    with widget.canvas.before:
        widget._ui_shadow_c = _UIColor(*_hex_rgba('#000000', 0.25))
        widget._ui_shadow = _UIRoundedRectangle(pos=(widget.x, widget.y - dp(1)), size=widget.size, radius=[dp(radius)])
        widget._ui_border_c = _UIColor(*_hex_rgba(border, 0.95))
        widget._ui_border = _UIRoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])
        widget._ui_fill_c = _UIColor(*_hex_rgba(fill, 1))
        widget._ui_fill = _UIRoundedRectangle(pos=widget.pos, size=widget.size, radius=[max(dp(6), dp(radius) - dp(2))])
        widget._ui_reset = _UIColor(1, 1, 1, 1)
    def _upd(*_):
        widget._ui_shadow.pos = (widget.x, widget.y - dp(1))
        widget._ui_shadow.size = widget.size
        widget._ui_border.pos = widget.pos
        widget._ui_border.size = widget.size
        widget._ui_fill.pos = (widget.x + dp(2), widget.y + dp(2))
        widget._ui_fill.size = (max(0, widget.width - dp(4)), max(0, widget.height - dp(4)))
        widget._ui_reset.rgba = (1, 1, 1, 1)
    widget.bind(pos=_upd, size=_upd)
    _upd()

def make_input(hint="", multiline=False, readonly=False, password=False):
    ti = TextInput(
        hint_text=hint,
        multiline=multiline,
        readonly=readonly,
        password=password,
        size_hint_y=None,
        height=dp(48) if not multiline else dp(110),
        background_normal='',
        background_active='',
        background_color=(0.08, 0.08, 0.08, 1),
        foreground_color=(1, 1, 1, 1),
        hint_text_color=(0.7, 0.7, 0.7, 1),
        cursor_color=(1, 1, 1, 1),
        cursor_width='3sp',
        padding=[dp(12), dp(14), dp(12), dp(12)],
    )
    return ti



def make_button(text, color=UI_GREEN):
    return RoundedButton(text=text, size_hint_y=None, height=dp(48), bg_hex=color, text_color=get_color_from_hex(UI_TEXT), radius=18)


def make_nav_button(text):
    return RoundedButton(text=text, size_hint=(1, None), height=dp(42), bg_hex=UI_CYAN, text_color=get_color_from_hex(UI_TEXT), radius=18)


def build_top_title(text, size='30sp'):
    box = BoxLayout(orientation='vertical', spacing=dp(4), size_hint_y=None)
    box.bind(minimum_height=box.setter('height'))
    pill = BoxLayout(size_hint_y=None, height=dp(18), spacing=dp(6))
    pill.add_widget(Widget())
    pill.add_widget(AccentDot(UI_GREEN, dp(8)))
    pill.add_widget(_soft_text('SH VERTEX INTERNAL CONSOLE', size='10sp', color=UI_GREEN, bold=True, height=dp(18), halign='center'))
    pill.add_widget(Widget())
    box.add_widget(pill)
    lbl = Label(text=text, color=get_color_from_hex(UI_TEXT), bold=True, font_size=size, size_hint_y=None, height=dp(48), halign='center', valign='middle')
    lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    box.add_widget(lbl)
    sub = _soft_text('Enterprise licensing, websites, operations, backups, and company control tools.', size='13sp', color=UI_MUTE, height=dp(22), halign='center')
    box.add_widget(sub)
    box._title_label = lbl
    return box


def _apply_admin_title_animation(widget):
    target = getattr(widget, '_title_label', widget)
    if not Animation:
        return
    try:
        Animation.cancel_all(target)
        target.opacity = 1.0
        anim = Animation(opacity=0.82, duration=1.6, t='in_out_sine') + Animation(opacity=1.0, duration=1.6, t='in_out_sine')
        anim.repeat = True
        anim.start(target)
    except Exception:
        pass


def build_screen_header(title, subtitle='', back_target='home', extra=None):
    box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
    box.bind(minimum_height=box.setter('height'))
    head = SectionCard(title, subtitle or 'Command surface', accent=_section_accent(title))
    row = GridLayout(cols=2 if extra else 1, spacing=dp(8), size_hint_y=None, height=dp(42))
    if back_target:
        back_btn = make_button('Back', UI_CYAN)
        back_btn.bind(on_release=lambda *_: setattr(App.get_running_app().root, 'current', back_target))
        row.add_widget(back_btn)
    if extra:
        holder = GridLayout(cols=len(extra), spacing=dp(8), size_hint_y=None, height=dp(42))
        for label, target in extra:
            btn = make_button(label, UI_CYAN)
            btn.bind(on_release=lambda *_ , t=target: setattr(App.get_running_app().root, 'current', t) if isinstance(t, str) else t())
            holder.add_widget(btn)
        if back_target:
            row.add_widget(holder)
        else:
            box.add_widget(holder)
    head.add_widget(row)
    box.add_widget(head)
    return box


def build_stat_chip(value, label, accent=UI_GREEN):
    card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(72), padding=[dp(10), dp(10), dp(10), dp(8)], spacing=dp(2))
    with card.canvas.before:
        card._shadow_c = _UIColor(*_hex_rgba('#000000', 0.22))
        card._shadow = _UIRoundedRectangle(pos=(card.x, card.y - dp(1)), size=card.size, radius=[dp(18)])
        card._bg_c = _UIColor(*_hex_rgba(UI_CARD_2, 1))
        card._bg = _UIRoundedRectangle(pos=card.pos, size=card.size, radius=[dp(18)])
        card._bar_c = _UIColor(*_hex_rgba(_button_border_for(accent), 0.95))
        card._bar = _UIRoundedRectangle(pos=card.pos, size=(card.width, dp(3)), radius=[dp(18)])
    def _upd(*_):
        card._shadow.pos = (card.x, card.y - dp(1))
        card._shadow.size = card.size
        card._bg.pos = card.pos
        card._bg.size = card.size
        card._bar.pos = card.pos
        card._bar.size = (card.width, dp(3))
    card.bind(pos=_upd, size=_upd)
    _upd()
    v = Label(text=str(value), color=get_color_from_hex(UI_TEXT), bold=True, font_size='18sp', size_hint_y=None, height=dp(28), halign='center', valign='middle')
    v.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    l = Label(text=str(label).upper(), color=get_color_from_hex(UI_MUTE), font_size='10sp', size_hint_y=None, height=dp(18), halign='left', valign='middle', bold=True)
    l.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
    card.add_widget(v)
    card.add_widget(l)
    return card


def info_popup(title, message):
    content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
    card = SectionCard(title, 'System message', accent=_section_accent(title))
    lbl = make_label(message, color=UI_TEXT, height=dp(80))
    card.add_widget(lbl)
    btn = make_button('OK', UI_GREEN)
    card.add_widget(btn)
    content.add_widget(card)
    popup = Popup(title='', content=content, size_hint=(0.9, 0.55), separator_height=0, background_color=(0, 0, 0, 0))
    btn.bind(on_release=popup.dismiss)
    popup.open()


def _confirm_action_popup(title, message, confirm_text, confirm_color, on_confirm):
    content = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(10))
    card = SectionCard(title, 'Confirm this action', accent=confirm_color)
    card.add_widget(make_label(message, color=UI_TEXT, height=dp(88)))
    row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    cancel_btn = make_button('Cancel', UI_CYAN)
    ok_btn = make_button(confirm_text, confirm_color)
    row.add_widget(cancel_btn)
    row.add_widget(ok_btn)
    card.add_widget(row)
    content.add_widget(card)
    popup = Popup(title='', content=content, size_hint=(0.9, 0.50), separator_height=0, background_color=(0, 0, 0, 0))
    cancel_btn.bind(on_release=popup.dismiss)
    def _do(*_):
        popup.dismiss()
        on_confirm()
    ok_btn.bind(on_release=_do)
    popup.open()


def _animate_children(container, step=0.035):
    if not Animation or not container:
        return
    try:
        children = list(reversed(container.children))
    except Exception:
        return
    for i, child in enumerate(children):
        try:
            Animation.cancel_all(child)
            child.opacity = 0.0
            Animation(opacity=1.0, duration=0.24, t='out_quad').start(child)
        except Exception:
            pass


def _build_home_utility_card():
    app = App.get_running_app()
    muted = bool(getattr(app, '_bg_music_muted', False)) if app else False
    volume = float(getattr(app, '_bg_music_volume', ADMIN_BG_MUSIC_DEFAULT_VOLUME) or ADMIN_BG_MUSIC_DEFAULT_VOLUME) if app else ADMIN_BG_MUSIC_DEFAULT_VOLUME
    volume_pct = int(round(volume * 100))
    card = SectionCard('UTILITY STRIP', 'Fast system controls for music, sound checks, backup, and exit.', accent=UI_ORANGE)
    card.add_widget(make_label(f'Background music: {"Muted" if muted else "Playing"}  •  Volume: {volume_pct}%', color=UI_MUTE, height=dp(22)))
    grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
    grid.bind(minimum_height=grid.setter('height'))
    actions = [
        ('Mute Music' if not muted else 'Unmute Music', lambda: app.toggle_background_music_mute() if app else None, UI_PURPLE if not muted else UI_ORANGE),
        ('Restart Music', lambda: app.start_background_music() if app and not getattr(app, '_bg_music_muted', False) else None, UI_CYAN),
        ('Volume -', lambda: app.change_background_music_volume(-0.10) if app else None, UI_CYAN),
        ('Volume +', lambda: app.change_background_music_volume(0.10) if app else None, UI_GREEN),
        ('Test Startup Sound', lambda: app.test_startup_sound() if app else None, UI_GREEN),
        ('Test Logoff Sound', lambda: app.test_logoff_sound() if app else None, UI_PURPLE),
    ]
    for label, fn, color in actions:
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , f=fn: f())
        grid.add_widget(btn)
    card.add_widget(grid)
    return card


def _build_product_dashboard_body(self, product_rows, collapsed):
    body = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
    body.bind(minimum_height=body.setter('height'))
    if collapsed:
        compact = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
        compact.add_widget(build_stat_chip(sum(int(x[0].get('active', 0)) for x in product_rows), 'Active', UI_GREEN))
        compact.add_widget(build_stat_chip(sum(int(x[0].get('licenses', 0)) for x in product_rows), 'Total', UI_CYAN))
        compact.add_widget(build_stat_chip(sum(int(x[0].get('revoked', 0)) for x in product_rows), 'Revoked', UI_RED))
        body.add_widget(compact)
        syn, ctp, bgt = [x[0] for x in product_rows]
        compact_line = make_label(
            f"Synapse {syn.get('active', 0)}/{syn.get('licenses', 0)}  •  CTP {ctp.get('active', 0)}/{ctp.get('licenses', 0)}  •  Budget {bgt.get('active', 0)}/{bgt.get('licenses', 0)}",
            color=SUBTEXT,
            height=dp(28),
        )
        body.add_widget(compact_line)
    else:
        for summary, accent, screen_name in product_rows:
            card = SectionCard(summary['product'], f"Authority: {'Loaded' if summary['authority_loaded'] else 'Missing'}  •  Fingerprint: {summary['fingerprint']}", accent=accent)
            stats = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(72))
            stats.add_widget(build_stat_chip(summary['active'], 'Active', accent))
            stats.add_widget(build_stat_chip(summary['revoked'], 'Revoked', UI_RED))
            stats.add_widget(build_stat_chip(summary['licenses'], 'Total', UI_CYAN))
            stats.add_widget(build_stat_chip(summary['last_backup'], 'Last Backup', UI_CYAN))
            card.add_widget(stats)
            open_btn = make_button(f'Open {summary["product"]}', accent)
            open_btn.bind(on_release=lambda *_ , s=screen_name: setattr(self.manager, 'current', s))
            card.add_widget(open_btn)
            body.add_widget(card)
    return body


def _render_product_dashboard_state(self, animate=False):
    if not hasattr(self, '_product_dash_body_host'):
        return
    syn = product_summary('Synapse')
    ctp = product_summary('Casino Tools Pro')
    bgt = product_summary('SHV Budget')
    product_rows = [
        (syn, UI_GREEN, 'synapse_manager'),
        (ctp, UI_PURPLE, 'casino_manager'),
        (bgt, BLUE, 'budget_manager'),
    ]
    collapsed = bool(getattr(self, '_product_dashboard_collapsed', False))
    if hasattr(self, '_product_dash_toggle_lbl'):
        self._product_dash_toggle_lbl.text = 'Expand to show all product lanes and quick open buttons.' if collapsed else 'Collapse product cards to save main-screen space.'
    if hasattr(self, '_product_dash_toggle_btn'):
        btn = self._product_dash_toggle_btn
        btn.text = 'Expand' if collapsed else 'Collapse'
        try:
            btn._bg_hex = UI_GREEN if collapsed else UI_ORANGE
            btn._border_hex = btn._derive_neon_border(btn._bg_hex)
            btn.color = (0, 0, 0, 1) if btn._bg_hex == GREEN else (1, 1, 1, 1)
            btn._update_bg()
        except Exception:
            pass
    new_body = _build_product_dashboard_body(self, product_rows, collapsed)
    host = self._product_dash_body_host
    old_body = getattr(self, '_product_dash_current_body', None)
    if old_body is None or not animate:
        host.clear_widgets()
        host.add_widget(new_body)
        self._product_dash_current_body = new_body
        return
    if getattr(self, '_product_dash_animating', False):
        return
    self._product_dash_animating = True
    def _swap(*_):
        host.clear_widgets()
        new_body.opacity = 0.0
        host.add_widget(new_body)
        self._product_dash_current_body = new_body
        anim_in = Animation(opacity=1.0, duration=0.18, t='out_quad')
        anim_in.bind(on_complete=lambda *_: setattr(self, '_product_dash_animating', False))
        anim_in.start(new_body)
    anim_out = Animation(opacity=0.0, duration=0.12, t='out_quad')
    anim_out.bind(on_complete=_swap)
    anim_out.start(old_body)


def _premium_admin_home_refresh_ui(self, *_):
    if not hasattr(self, 'root_box'):
        return
    self.root_box.clear_widgets()
    title_box = build_top_title('SH VERTEX ADMIN PANEL', '30sp')
    self.root_box.add_widget(title_box)
    _apply_admin_title_animation(title_box)

    syn = product_summary('Synapse')
    ctp = product_summary('Casino Tools Pro')
    bgt = product_summary('SHV Budget')
    try:
        _sites_data = [normalize_website_entry(x) for x in load_websites_db()]
    except Exception:
        _sites_data = []
    total_pages = sum(len(s.get('pages', [])) for s in _sites_data)

    hero = SectionCard('CONTROL DASHBOARD', 'Private enterprise command center for product licensing, websites, operations, backups, and company control tools.', accent=UI_GREEN)
    hero_stats = GridLayout(cols=4, spacing=dp(8), size_hint_y=None, height=dp(72))
    hero_stats.add_widget(build_stat_chip(int(syn.get('active', 0)) + int(ctp.get('active', 0)) + int(bgt.get('active', 0)), 'Live Licenses', UI_GREEN))
    hero_stats.add_widget(build_stat_chip(len(_sites_data), 'Sites', UI_CYAN))
    hero_stats.add_widget(build_stat_chip(3, 'Products', UI_TEAL))
    hero_stats.add_widget(build_stat_chip(int(syn.get('revoked', 0)) + int(ctp.get('revoked', 0)) + int(bgt.get('revoked', 0)), 'Revoked', UI_RED))
    hero.add_widget(hero_stats)
    hero_actions = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
    hero_actions.bind(minimum_height=hero_actions.setter('height'))
    for label, fn, color in [
        ('Open Licensing', lambda: setattr(self.manager, 'current', 'licensing'), UI_GREEN),
        ('Open Websites', lambda: setattr(self.manager, 'current', 'websites'), UI_CYAN),
        ('Open Backup Vault', lambda: setattr(self.manager, 'current', 'backup_vault'), UI_ORANGE),
        ('Open Customers', lambda: setattr(self.manager, 'current', 'customers'), UI_TEAL),
    ]:
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , f=fn: f())
        hero_actions.add_widget(btn)
    hero.add_widget(hero_actions)
    self.root_box.add_widget(hero)

    if not hasattr(self, '_product_dashboard_collapsed'):
        self._product_dashboard_collapsed = False

    dash = SectionCard('PRODUCT DASHBOARD', 'Clear separation between product lanes with their own authority health, status, and latest backup.', accent=UI_GREEN)
    self._product_dash_card = dash

    toggle_row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    toggle_lbl = make_label('', color=SUBTEXT, height=dp(46))
    toggle_lbl.size_hint_x = 1
    toggle_btn = make_button('Collapse', UI_ORANGE)
    toggle_btn.size_hint_x = None
    toggle_btn.width = dp(120)
    def _toggle_dashboard(*_):
        if getattr(self, '_product_dash_animating', False):
            return
        self._product_dashboard_collapsed = not bool(getattr(self, '_product_dashboard_collapsed', False))
        _render_product_dashboard_state(self, animate=True)
    toggle_btn.bind(on_release=_toggle_dashboard)
    toggle_row.add_widget(toggle_lbl)
    toggle_row.add_widget(toggle_btn)
    dash.add_widget(toggle_row)
    self._product_dash_toggle_lbl = toggle_lbl
    self._product_dash_toggle_btn = toggle_btn

    body_host = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(0))
    body_host.bind(minimum_height=body_host.setter('height'))
    self._product_dash_body_host = body_host
    self._product_dash_current_body = None
    self._product_dash_animating = False
    dash.add_widget(body_host)
    _render_product_dashboard_state(self, animate=False)
    self.root_box.add_widget(dash)

    quick = SectionCard('QUICK ACTIONS', 'Fast daily operations arranged with better grouping and less visual clutter.', accent=UI_CYAN)
    quick_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
    quick_grid.bind(minimum_height=quick_grid.setter('height'))
    grid_actions = [
        ('Synapse Generate', lambda: App.get_running_app().open_product_manager('synapse_manager', 'generate'), UI_GREEN),
        ('CTP Generate', lambda: App.get_running_app().open_product_manager('casino_manager', 'generate'), UI_PURPLE),
        ('Budget Generate', lambda: App.get_running_app().open_product_manager('budget_manager', 'generate'), BLUE),
        ('Customers', lambda: setattr(self.manager, 'current', 'customers'), UI_CYAN),
        ('Activity Log', lambda: setattr(self.manager, 'current', 'activity'), UI_CYAN),
        ('Releases', lambda: setattr(self.manager, 'current', 'releases'), UI_ORANGE),
        ('Company Modules', lambda: setattr(self.manager, 'current', 'company_modules'), UI_PURPLE),
    ]
    for label, fn, color in grid_actions:
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , f=fn: f())
        quick_grid.add_widget(btn)
    quick.add_widget(quick_grid)
    backup_btn = make_button('App Data Backup', UI_CYAN)
    backup_btn.height = dp(52)
    backup_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'app_data_backup'))
    quick.add_widget(backup_btn)
    self.root_box.add_widget(quick)

    modules = SectionCard('COMPANY MODULES', 'Every module now follows the same glass-neon admin language with tighter spacing and clearer grouping.', accent=UI_PURPLE)
    mod_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
    mod_grid.bind(minimum_height=mod_grid.setter('height'))
    rows = [
        ('Licensing', lambda: setattr(self.manager, 'current', 'licensing'), UI_GREEN),
        ('Backup Vault', lambda: setattr(self.manager, 'current', 'backup_vault'), UI_ORANGE),
        ('Authority Status', lambda: setattr(self.manager, 'current', 'authority_status'), UI_PURPLE),
        ('Customers', lambda: setattr(self.manager, 'current', 'customers'), UI_CYAN),
        ('Releases', lambda: setattr(self.manager, 'current', 'releases'), UI_ORANGE),
        ('Documents', lambda: setattr(self.manager, 'current', 'docs'), UI_PURPLE),
        ('Notes', lambda: show_placeholder('Notes'), UI_CYAN),
        ('Internal Tools', lambda: show_placeholder('Internal Tools'), UI_PURPLE),
    ]
    for label, fn, color in rows:
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , f=fn: f())
        mod_grid.add_widget(btn)
    modules.add_widget(mod_grid)
    self.root_box.add_widget(modules)

    websites_card = SectionCard('WEBSITES', 'Company sites, page registries, and HTML content tracking in a cleaner command layout.', accent=UI_CYAN)
    ws_stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
    ws_stats.add_widget(build_stat_chip(len(_sites_data), 'Sites', UI_CYAN))
    ws_stats.add_widget(build_stat_chip(total_pages, 'Pages', UI_TEAL))
    ws_latest = _sites_data[0].get('updated_at', '--') if _sites_data else '--'
    ws_stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
    ws_stats.add_widget(build_stat_chip(len(_sites_data), 'Sites', UI_CYAN))
    ws_stats.add_widget(build_stat_chip(total_pages, 'Pages', UI_TEAL))
    ws_latest = _sites_data[0].get('updated_at', '--') if _sites_data else '--'
    ws_stats.add_widget(build_stat_chip(_ws_latest[-5:] if (_ws_latest := ws_latest) != '--' else '--', 'Updated', UI_CYAN))
    websites_card.add_widget(ws_stats)
    ws_btn = make_button('Open Websites', UI_CYAN)
    ws_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'websites'))
    websites_card.add_widget(ws_btn)
    self.root_box.add_widget(websites_card)

    self.root_box.add_widget(_build_home_utility_card())

    exit_card = SectionCard('EXIT', 'Close the admin app safely when you are done.', accent=UI_RED)
    exit_btn = make_button('Exit', UI_RED)
    def _confirm_exit(*_):
        app = App.get_running_app()
        on_confirm = getattr(app, 'play_exit_sound_then_stop', app.stop) if app else (lambda: None)
        _confirm_action_popup('Exit App', 'Close SH Vertex Admin Panel?', 'Exit', UI_RED, on_confirm)
    exit_btn.bind(on_release=_confirm_exit)
    exit_card.add_widget(exit_btn)
    self.root_box.add_widget(exit_card)
    _animate_children(self.root_box)


def _premium_licensing_build_ui(self, *_):
    self.clear_widgets()
    root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(14)], spacing=dp(10))
    root.add_widget(build_screen_header('Licensing', 'Company-wide product licensing, authority control, revocations, and vault operations.', 'home'))
    hero = SectionCard('LICENSING COMMAND', 'Choose a lane below. Each keeps its own product separation while sharing the same polished admin shell.', accent=UI_GREEN)
    grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
    grid.bind(minimum_height=grid.setter('height'))
    sections = [
        ('Apps', 'apps', UI_GREEN),
        ('Backup Vault', 'backup_vault', UI_ORANGE),
        ('Authority Status', 'authority_status', UI_PURPLE),
        ('Activity Log', 'activity', UI_CYAN),
    ]
    for label, target, color in sections:
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , t=target: setattr(self.manager, 'current', t))
        grid.add_widget(btn)
    hero.add_widget(grid)
    root.add_widget(hero)
    root.add_widget(Widget())
    self.add_widget(root)


def _premium_company_modules_build_ui(self, *_):
    self.clear_widgets()
    root = BoxLayout(orientation='vertical', padding=[dp(10), dp(12), dp(10), dp(12)], spacing=dp(10))
    root.add_widget(build_screen_header('Company Modules', 'Live internal modules and future expansion lanes inside the same command language.', 'home'))
    card = SectionCard('LIVE INTERNAL MODULES', 'Safe icon-like accent dots are used here instead of external icon fonts, so nothing turns into missing glyph boxes.', accent=UI_PURPLE)
    rows = [
        ('Websites', lambda: setattr(self.manager, 'current', 'websites'), UI_CYAN),
        ('Documents', lambda: setattr(self.manager, 'current', 'docs'), UI_PURPLE),
        ('Customers', lambda: setattr(self.manager, 'current', 'customers'), UI_CYAN),
        ('Releases', lambda: setattr(self.manager, 'current', 'releases'), UI_ORANGE),
        ('Sales', lambda: show_placeholder('Sales'), UI_PURPLE),
        ('Notes', lambda: show_placeholder('Notes'), UI_CYAN),
        ('Internal Tools', lambda: show_placeholder('Internal Tools'), UI_PURPLE),
        ('Operations', lambda: show_placeholder('Operations'), UI_ORANGE),
    ]
    grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
    grid.bind(minimum_height=grid.setter('height'))
    for label, fn, color in rows:
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , f=fn: f())
        grid.add_widget(btn)
    card.add_widget(grid)
    root.add_widget(card)
    root.add_widget(Widget())
    self.add_widget(root)


# Rebind shared UI helpers to the premium versions.
_CTP_NS['RoundedButton'] = RoundedButton
_CTP_NS['make_button'] = make_button
_CTP_NS['make_nav_button'] = make_nav_button
RoundedButton = RoundedButton
SectionCard = SectionCard
AdminHomeScreen.refresh_ui = _premium_admin_home_refresh_ui
AdminHomeScreen._premium_refresh_ui = _premium_admin_home_refresh_ui
AdminHomeScreen._premium_admin_home_refresh_ui = _premium_admin_home_refresh_ui
LicensingHubScreen.build_ui = _premium_licensing_build_ui
LicensingHubScreen._premium_build_ui = _premium_licensing_build_ui
LicensingHubScreen._premium_licensing_build_ui = _premium_licensing_build_ui
CompanyModulesScreen.build_ui = _premium_company_modules_build_ui
CompanyModulesScreen._premium_build_ui = _premium_company_modules_build_ui
CompanyModulesScreen._premium_company_modules_build_ui = _premium_company_modules_build_ui


# ---- licensing cloud backup patch ----

def _cloud_backup_default_cfg(product_name):
    safe_product = str(product_name or '').strip() or 'Synapse'
    return {
        'owner': 'therealwolfman97',
        'repo': 'SH-VERTEX-ADMIN-PANEL',
        'branch': 'main',
        'folder': f'Auth Backups/{safe_product}',
        'token': '',
    }


def _load_cloud_backup_cfg(path, default_cfg):
    data = load_json(path, {})
    merged = dict(default_cfg or {})
    if isinstance(data, dict):
        for key in ('owner', 'repo', 'branch', 'folder', 'token'):
            value = str(data.get(key, '')).strip()
            if value:
                merged[key] = value
    return merged


def _save_cloud_backup_cfg(path, cfg):
    clean = {}
    for key in ('owner', 'repo', 'branch', 'folder', 'token'):
        clean[key] = str(cfg.get(key, '')).strip()
    save_json(path, clean)


def _timestamped_cloud_filename(filename):
    stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    base, ext = os.path.splitext(str(filename or '').strip() or 'backup.bin')
    return f'{base}_{stamp}{ext}'


def _upload_cloud_backup_blob(blob_text, cfg, filename, message):
    owner = str(cfg.get('owner', '')).strip()
    repo = str(cfg.get('repo', '')).strip()
    branch = str(cfg.get('branch', 'main')).strip() or 'main'
    folder = str(cfg.get('folder', '')).strip().strip('/')
    token = str(cfg.get('token', '')).strip()
    if not all([owner, repo, branch, folder, token]):
        raise ValueError('Owner, repo, branch, folder, and token are required.')
    path = f'{folder}/{filename}'
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    body = {
        'message': message,
        'content': base64.b64encode(blob_text.encode('utf-8')).decode('ascii'),
        'branch': branch,
    }
    resp = requests.put(api_url, headers=headers, json=body, timeout=30)
    if resp.status_code not in (200, 201):
        raise RuntimeError(f'GitHub upload failed: {resp.status_code} {resp.text[:220]}')
    return path


def _list_cloud_backup_items(cfg):
    owner = str(cfg.get('owner', '')).strip()
    repo = str(cfg.get('repo', '')).strip()
    branch = str(cfg.get('branch', 'main')).strip() or 'main'
    folder = str(cfg.get('folder', '')).strip().strip('/')
    token = str(cfg.get('token', '')).strip()
    if not all([owner, repo, branch, folder, token]):
        return []
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{folder}?ref={branch}'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    try:
        resp = requests.get(api_url, headers=headers, timeout=20)
        if resp.status_code == 200:
            items = resp.json()
            if isinstance(items, list):
                files = [x for x in items if isinstance(x, dict) and x.get('type') == 'file']
                files.sort(key=lambda x: x.get('name', ''), reverse=True)
                return files
    except Exception:
        pass
    return []


def _download_cloud_backup_blob(cfg, item):
    owner = str(cfg.get('owner', '')).strip()
    repo = str(cfg.get('repo', '')).strip()
    token = str(cfg.get('token', '')).strip()
    if not all([owner, repo, token]):
        raise ValueError('Owner, repo, and token are required.')
    api_url = item.get('url') or ''
    if not api_url:
        path = str(item.get('path', '')).strip().lstrip('/')
        if not path:
            raise ValueError('Remote file item is missing its path.')
        api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    resp = requests.get(api_url, headers=headers, timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f'GitHub download failed: {resp.status_code} {resp.text[:220]}')
    data = resp.json()
    content_b64 = str(data.get('content', '')).replace('\n', '')
    if not content_b64:
        raise RuntimeError('Cloud backup file content was empty.')
    return base64.b64decode(content_b64.encode('ascii')).decode('utf-8')


def _cloud_manager_collect_cfg(self):
    return {
        'owner': self._cloud_owner_input.text.strip(),
        'repo': self._cloud_repo_input.text.strip(),
        'branch': self._cloud_branch_input.text.strip() or 'main',
        'folder': self._cloud_folder_input.text.strip().strip('/') or self._cloud_default_cfg.get('folder', ''),
        'token': self._cloud_token_input.text.strip(),
    }


def _cloud_manager_save_settings(self):
    cfg = self._cloud_collect_cfg()
    _save_cloud_backup_cfg(self._cloud_cfg_path, cfg)
    self._cloud_cfg = cfg
    info_popup('Saved', f'{self._cloud_product} cloud backup settings saved.')


def _cloud_manager_upload_all(self):
    password = self.backup_password_input.text.strip() if hasattr(self, 'backup_password_input') else ''
    if not password:
        info_popup('Password required', 'Enter the backup password above before uploading cloud backups.')
        return
    cfg = self._cloud_collect_cfg()
    if not cfg.get('token'):
        info_popup('Token required', 'Enter your GitHub token before uploading cloud backups.')
        return
    try:
        authority_blob = self._cloud_build_authority_blob(password)
        license_blob = self._cloud_build_license_blob(password)
        full_blob = self._cloud_build_full_blob(password)
        uploaded = []
        for filename, blob, label in (
            (self._cloud_authority_file, authority_blob, 'authority backup'),
            (self._cloud_license_file, license_blob, 'license-list backup'),
            (self._cloud_full_file, full_blob, 'full backup'),
        ):
            stamped_name = _timestamped_cloud_filename(filename)
            path = _upload_cloud_backup_blob(blob, cfg, stamped_name, f'{self._cloud_product} cloud backup {label}')
            uploaded.append(path)
        _save_cloud_backup_cfg(self._cloud_cfg_path, cfg)
        self._cloud_cfg = cfg
        info_popup('Cloud backup complete', '\n'.join(['Uploaded:'] + uploaded))
        self._cloud_list_remote()
    except Exception as e:
        info_popup('Cloud backup failed', str(e))


def _cloud_manager_list_remote(self):
    if not hasattr(self, '_cloud_files_box'):
        return
    self._cloud_files_box.clear_widgets()
    cfg = self._cloud_collect_cfg()
    if not cfg.get('token'):
        info_popup('Token required', 'Enter your GitHub token before listing remote backups.')
        return
    items = _list_cloud_backup_items(cfg)
    if not items:
        self._cloud_files_box.add_widget(make_label('No remote backup files found yet.', color=SUBTEXT, height=dp(24)))
        return
    for item in items:
        name = str(item.get('name', '')).strip()
        lower = name.lower()
        if not (lower.endswith('.ctp') or lower.endswith('.ctlist') or lower.endswith('.ctfull')):
            continue
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        btn = make_button(name, UI_CYAN if 'UI_CYAN' in globals() else BLUE)
        btn.text_size = (btn.width - dp(12), btn.height)
        btn.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - dp(12), val[1])))
        btn.bind(on_release=lambda *_ , it=item: self._cloud_restore_item(it))
        row.add_widget(btn)
        self._cloud_files_box.add_widget(row)


def _cloud_manager_restore_item(self, item):
    password = self.backup_password_input.text.strip() if hasattr(self, 'backup_password_input') else ''
    if not password:
        info_popup('Password required', 'Enter the backup password above before restoring a cloud backup.')
        return
    try:
        cfg = self._cloud_collect_cfg()
        blob_text = _download_cloud_backup_blob(cfg, item)
        bundle = self._cloud_parse_blob(blob_text, password)
        bundle_type = str(bundle.get('bundle_type', '')).strip()
        if bundle_type == 'authority_only':
            if hasattr(self, 'import_backup_input'):
                self.import_backup_input.text = blob_text
            self._finish_authority_import(bundle)
            kind = 'authority backup'
        elif bundle_type == 'license_list_only':
            if hasattr(self, 'import_license_backup_input'):
                self.import_license_backup_input.text = blob_text
            self._finish_license_list_import(bundle)
            kind = 'license-list backup'
        elif bundle_type == 'full_backup':
            if hasattr(self, 'import_full_backup_input'):
                self.import_full_backup_input.text = blob_text
            self._finish_full_backup_import(bundle)
            kind = 'full backup'
        else:
            raise ValueError(f'Unsupported backup type: {bundle_type}')
        info_popup('Cloud restore complete', f'Restored {kind} for {self._cloud_product} from\n{item.get("name", "remote file")}')
    except Exception as e:
        info_popup('Cloud restore failed', str(e))


def _build_cloud_backup_card(self):
    card = SectionCard('Cloud Backup', f'Upload encrypted authority, license-list, and full backups to GitHub under {self._cloud_default_cfg.get("folder", "Auth Backups")}.', accent=UI_CYAN if 'UI_CYAN' in globals() else None)
    card.add_widget(make_label('Uses the same backup password above. Keeps your current manual backup options unchanged.', color=SUBTEXT, height=dp(34)))

    self._cloud_owner_input = make_input('GitHub owner / username')
    self._cloud_repo_input = make_input('Repository name')
    self._cloud_branch_input = make_input('Branch')
    self._cloud_folder_input = make_input('Folder path inside repo')
    self._cloud_token_input = make_input('GitHub token with contents:write access')

    self._cloud_owner_input.text = self._cloud_cfg.get('owner', self._cloud_default_cfg.get('owner', ''))
    self._cloud_repo_input.text = self._cloud_cfg.get('repo', self._cloud_default_cfg.get('repo', ''))
    self._cloud_branch_input.text = self._cloud_cfg.get('branch', self._cloud_default_cfg.get('branch', 'main'))
    self._cloud_folder_input.text = self._cloud_cfg.get('folder', self._cloud_default_cfg.get('folder', ''))
    self._cloud_token_input.text = self._cloud_cfg.get('token', self._cloud_default_cfg.get('token', ''))

    for title, widget in (
        ('Owner', self._cloud_owner_input),
        ('Repo', self._cloud_repo_input),
        ('Branch', self._cloud_branch_input),
        ('Folder', self._cloud_folder_input),
        ('Token', self._cloud_token_input),
    ):
        card.add_widget(make_label(title))
        card.add_widget(widget)
        if widget is self._cloud_token_input:
            paste_token_btn = make_button('Paste Token', UI_CYAN)
            paste_token_btn.height = dp(40)
            paste_token_btn.bind(on_release=lambda *_: paste_clipboard_into(self._cloud_token_input))
            card.add_widget(paste_token_btn)

    row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    save_btn = make_button('Save Cloud Settings', UI_CYAN)
    upload_btn = make_button('Upload All 3 Backups', GREEN)
    row1.add_widget(save_btn)
    row1.add_widget(upload_btn)
    save_btn.bind(on_release=lambda *_: self._cloud_save_settings())
    upload_btn.bind(on_release=lambda *_: self._cloud_upload_all())
    card.add_widget(row1)

    row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
    list_btn = make_button('List Remote Files', UI_CYAN)
    row2.add_widget(list_btn)
    list_btn.bind(on_release=lambda *_: self._cloud_list_remote())
    card.add_widget(row2)

    self._cloud_files_box = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None)
    self._cloud_files_box.bind(minimum_height=self._cloud_files_box.setter('height'))
    card.add_widget(self._cloud_files_box)
    return card


def _patch_manager_cloud_backup(cls, product_name, config_name, file_path_fn, ns):
    original_build_authority_view = cls.build_authority_view

    def wrapped_build_authority_view(self, *args, **kwargs):
        self._cloud_product = product_name
        self._cloud_default_cfg = _cloud_backup_default_cfg(product_name)
        self._cloud_cfg_path = file_path_fn(config_name)
        self._cloud_cfg = _load_cloud_backup_cfg(self._cloud_cfg_path, self._cloud_default_cfg)
        self._cloud_authority_file = ns['AUTHORITY_BACKUP_FILE']
        self._cloud_license_file = ns['LICENSE_LIST_BACKUP_FILE']
        self._cloud_full_file = ns['FULL_BACKUP_FILE']
        self._cloud_build_authority_blob = lambda password: ns['build_authority_backup_blob'](password)
        self._cloud_build_license_blob = lambda password: ns['build_license_list_backup_blob'](password, self.store.records)
        self._cloud_build_full_blob = lambda password: ns['build_full_backup_blob'](password, self.store.records)
        self._cloud_parse_blob = ns['parse_secure_backup_blob']
        view = original_build_authority_view(self, *args, **kwargs)
        try:
            box = view.children[0] if getattr(view, 'children', None) else None
            if box is not None:
                box.add_widget(_build_cloud_backup_card(self))
        except Exception:
            pass
        return view

    cls._cloud_collect_cfg = _cloud_manager_collect_cfg
    cls._cloud_save_settings = _cloud_manager_save_settings
    cls._cloud_upload_all = _cloud_manager_upload_all
    cls._cloud_list_remote = _cloud_manager_list_remote
    cls._cloud_restore_item = _cloud_manager_restore_item
    cls.build_authority_view = wrapped_build_authority_view


_patch_manager_cloud_backup(
    LicenseManagerScreen,
    'Synapse',
    'synapse_cloud_backup_config.json',
    file_path,
    {
        'AUTHORITY_BACKUP_FILE': AUTHORITY_BACKUP_FILE,
        'LICENSE_LIST_BACKUP_FILE': LICENSE_LIST_BACKUP_FILE,
        'FULL_BACKUP_FILE': FULL_BACKUP_FILE,
        'build_authority_backup_blob': build_authority_backup_blob,
        'build_license_list_backup_blob': build_license_list_backup_blob,
        'build_full_backup_blob': build_full_backup_blob,
        'parse_secure_backup_blob': parse_secure_backup_blob,
    },
)

_patch_manager_cloud_backup(
    CasinoToolsLicenseManagerScreen,
    'Casino Tools Pro',
    'casino_cloud_backup_config.json',
    _CTP_NS['file_path'],
    {
        'AUTHORITY_BACKUP_FILE': _CTP_NS['AUTHORITY_BACKUP_FILE'],
        'LICENSE_LIST_BACKUP_FILE': _CTP_NS['LICENSE_LIST_BACKUP_FILE'],
        'FULL_BACKUP_FILE': _CTP_NS['FULL_BACKUP_FILE'],
        'build_authority_backup_blob': _CTP_NS['build_authority_backup_blob'],
        'build_license_list_backup_blob': _CTP_NS['build_license_list_backup_blob'],
        'build_full_backup_blob': _CTP_NS['build_full_backup_blob'],
        'parse_secure_backup_blob': _CTP_NS['parse_secure_backup_blob'],
    },
)


# --- Embedded SHV Budget Licensing Module ---
_BUDGET_MODULE_SOURCE = 'import base64\nimport csv\nimport json\nimport os\nimport secrets\nimport textwrap\nimport zlib\nimport hashlib\nimport hmac\nimport uuid\nfrom datetime import datetime, timedelta, timezone\ntry:\n    from zoneinfo import ZoneInfo, available_timezones\nexcept Exception:\n    ZoneInfo = None\n    def available_timezones():\n        return set()\n\nimport requests\nimport rsa\nfrom kivy.app import App\nfrom kivy.clock import Clock\nfrom kivy.core.clipboard import Clipboard\nfrom kivy.core.audio import SoundLoader\nfrom kivy.core.window import Window\nfrom kivy.metrics import dp\nfrom kivy.utils import get_color_from_hex\nfrom kivy.uix.boxlayout import BoxLayout\nfrom kivy.uix.button import Button\nfrom kivy.uix.gridlayout import GridLayout\nfrom kivy.uix.label import Label\nfrom kivy.uix.popup import Popup\nfrom kivy.uix.scrollview import ScrollView\nfrom kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager\nfrom kivy.uix.spinner import Spinner\nfrom kivy.uix.textinput import TextInput\nfrom kivy.uix.widget import Widget\nfrom kivy.graphics import Color, RoundedRectangle\n\nBG = "#000000"\nCARD = "#0b0b0b"\nTEXT = "#b1bad3"\nSUBTEXT = "#8f9bb3"\nGREEN = "#00e701"\nRED = "#ff4e4e"\nBLUE = "#3498db"\nPURPLE = "#9b59b6"\nORANGE = "#e67e22"\nWindow.clearcolor = get_color_from_hex(BG)\n\nPRIVATE_KEY_FILE = "shv_admin_private.pem"\nPUBLIC_KEY_FILE = "shv_admin_public.pem"\nLICENSE_DB_FILE = "budget_licenses_db.json"\nREVOKED_EXPORT_FILE = "budget_revoked_licenses.json"\nAUTHORITY_BACKUP_FILE = "budget_authority_backup.ctp"\nLICENSE_LIST_BACKUP_FILE = "budget_license_list_backup.ctlist"\nFULL_BACKUP_FILE = "budget_full_backup.ctfull"\nGITHUB_CONFIG_FILE = "budget_github_upload_config.json"\nBACKUP_BUNDLE_APP = "shv_budget"\n\nDEFAULT_GITHUB_UPLOAD = {\n    "owner": "therealwolfman97",\n    "repo": "SH-VERTEX-ADMIN-PANEL",\n    "branch": "main",\n    "path": "LICENSING/APPS/REVOCATIONS/budget-revo.json",\n    "token": "",\n}\n\nDEFAULT_AUTHORITY_PRIVATE_PEM = r\'\'\'-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAyzFeVLwRolUJ8h3EFlqbDBEHCLmqS8AGGZQHmUKRe+UOUPS2\nKPuKY1Z6FzC+agFVXZC1L01b/FbbsjUptqb6o2TYjKG9uOF0SflyhaXLcNq+Jn+d\nJf26ZBTQ8k7fX+YB60FFOQjC1F5/YKztvjwGy/Ze0513+sNU3PfJeh1DZPIXRmyA\nRv7ncMGUmUiocl7b6NpBGQeIzDnuWaewn8UYWskWDWCKiy6mXQZK/EYu17FP55Yb\nhFFxCNQ8KTRBX2bq9NRny/LRZP3BThB8FkCMBX2/gYGYAwtGTLTRPRt3QUgbBkkX\nBt4rnOW9IPGPuy9+77HtNaw3Gge9WmCA12luMwIDAQABAoIBAAZF/iFkARaS+F1w\nswb02y6fMMMBmhMAP1ZdoXJttLiV7nNsN431kWTWkBE609YwBMCAlEEWnicHUEpY\nC9naalVn6qurRR4Tj+STMaItgT948XMwCdw/av7McCF0plh7bUaKW4z5Ct+sEm2C\nSU2c5G5tqw9uucj7OOaHNY6lbD90j+HpYuJsyy5nzj7fw/BxItnvyGaa5/xVsfD1\nuynQUw1zoFNfqRFq+pw/+G+Mel6yChqJsrOJkjzU7LYU+kTgkfsl8XLnkCd61D/L\nSEeJRL2hEtFjHa6T2U98qTX3qT/zGV26HFy2pnvInIvBeEVdgpTNS3BVxDk4Qyum\nCyxGLXECgYEA9o6lWTmH3zxKKVPm22GhKKa5IZIK2KQoRWOH+AeTloS5rlTuBq4m\nYtnVXQhAfP8VKZoXSQFPRMOIfXERaBv3KSeJi0PlyQR/7SCC5bZXE76i1N41yLXw\nKDNuHE1EN3GHB/l2j/g8Gca/J0Yb5zj/eC56VZVZn4eRJDv+FXX0G+sCgYEA0vmP\nOzfqQ/KaGrF0K4YqxhNDHUBgIj8vwxfruy63J3qTkg3TGE/OFh0RHJLDycl6Ha1L\nwQWxtaU6V9UmBJOrnml6W3mtP/bZg5T6nOAbvTE+Z9wCuSX+qjCCQoi+UpxrQQyi\nsRv3eIp62z4Mo+yRWiRzGh1stgO2feck5yCcTNkCgYA737ohp8nqGS79SEW4osXL\nJGmy0E9X+s1YxGnhfp2FoOeigTdoYeQqfzHELNvUPvG5r5TWAr5oOX+szsdmW9wy\nn0pUioGDxlb2k72V4SjWP6Y1QV0YR65xZMPplY3qVORwuFDld2fI7q2+8NSX2wyW\n99p3bBRenEJP5U23knRcTwKBgQCLTMwNxbWgd6bYySJzOnsznbRKtB7FfgMDReAY\nD5hPMNgPL6GaA9eHMloCC8XKjoVa4vmJ0UCtNxN2uv4HN5mxVuO7UnPaMBsejleL\nDU5DdShHWzVRGo0zwiO/2poP4cfPg5BIcLbNmGHWMPoXojO22SpGq/cDlx//sYbk\nNNv+wQKBgQCAcaoq42pIrgoz5v6qp2j2Uj8lJ6BploR7LLkljV5BqLoust2LyzPM\nSW71usiyz3AnfBkTnitmcUVRcpxOXFB/rgLt/aUiEsPnQv88IJPXtuZ+f9JXUXcD\nZCseJ8FWpWy/vW8ffnQV9A38HtgX8lnSUvE90Gkp6Zas1SxN67FFHQ==\n-----END RSA PRIVATE KEY-----\'\'\'\nDEFAULT_AUTHORITY_PUBLIC_PEM = r\'\'\'-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAyzFeVLwRolUJ8h3EFlqbDBEHCLmqS8AGGZQHmUKRe+UOUPS2KPuK\nY1Z6FzC+agFVXZC1L01b/FbbsjUptqb6o2TYjKG9uOF0SflyhaXLcNq+Jn+dJf26\nZBTQ8k7fX+YB60FFOQjC1F5/YKztvjwGy/Ze0513+sNU3PfJeh1DZPIXRmyARv7n\ncMGUmUiocl7b6NpBGQeIzDnuWaewn8UYWskWDWCKiy6mXQZK/EYu17FP55YbhFFx\nCNQ8KTRBX2bq9NRny/LRZP3BThB8FkCMBX2/gYGYAwtGTLTRPRt3QUgbBkkXBt4r\nnOW9IPGPuy9+77HtNaw3Gge9WmCA12luMwIDAQAB\n-----END RSA PUBLIC KEY-----\'\'\'\n\ndef ensure_default_authority_files():\n    priv_path = file_path(PRIVATE_KEY_FILE)\n    pub_path = file_path(PUBLIC_KEY_FILE)\n    if not os.path.exists(priv_path):\n        with open(priv_path, \'wb\') as f:\n            f.write(DEFAULT_AUTHORITY_PRIVATE_PEM.encode(\'utf-8\'))\n    if not os.path.exists(pub_path):\n        with open(pub_path, \'wb\') as f:\n            f.write(DEFAULT_AUTHORITY_PUBLIC_PEM.encode(\'utf-8\'))\n\n\ndef utc_now_iso():\n    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"\n\n\ndef app_data_dir():\n    app = App.get_running_app()\n    if app and getattr(app, "user_data_dir", None):\n        path = app.user_data_dir\n    else:\n        path = os.path.join(os.path.expanduser("~"), ".sh_vertex_admin_panel")\n    os.makedirs(path, exist_ok=True)\n    return path\n\n\ndef file_path(name):\n    return os.path.join(app_data_dir(), name)\n\n\ndef downloads_base_dir():\n    candidates = [\n        "/storage/emulated/0/Download",\n        "/sdcard/Download",\n        os.path.join(os.path.expanduser("~"), "Download"),\n    ]\n    for path in candidates:\n        try:\n            os.makedirs(path, exist_ok=True)\n            return path\n        except Exception:\n            continue\n    fallback = app_data_dir()\n    os.makedirs(fallback, exist_ok=True)\n    return fallback\n\n\ndef admin_export_dir(*parts):\n    path = os.path.join(downloads_base_dir(), "SH Vertex Admin Panel", "Licensing", "SHV Budget", *parts)\n    os.makedirs(path, exist_ok=True)\n    return path\n\n\n\ndef _timestamped_export_path(directory, filename):\n    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")\n    base, ext = os.path.splitext(filename)\n    return os.path.join(directory, f"{base}_{stamp}{ext}")\n\n\ndef list_backup_files(directory, suffixes):\n    candidates = []\n    suffixes = tuple(str(s).lower() for s in (suffixes or []))\n    try:\n        for name in os.listdir(directory):\n            lower = name.lower()\n            if suffixes and not lower.endswith(suffixes):\n                continue\n            path = os.path.join(directory, name)\n            if os.path.isfile(path):\n                candidates.append(path)\n    except Exception:\n        return []\n    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)\n    return candidates\n\n\ndef authority_backup_dir():\n    return admin_export_dir("Authority Backups")\n\n\ndef authority_backup_export_path():\n    return _timestamped_export_path(authority_backup_dir(), AUTHORITY_BACKUP_FILE)\n\n\ndef list_authority_backup_files():\n    return list_backup_files(authority_backup_dir(), [".ctp", ".shva", ".ctfull"])\n\n\ndef license_list_backup_dir():\n    return admin_export_dir("License List Backups")\n\n\ndef license_list_backup_export_path():\n    return _timestamped_export_path(license_list_backup_dir(), LICENSE_LIST_BACKUP_FILE)\n\n\ndef list_license_list_backup_files():\n    return list_backup_files(license_list_backup_dir(), [".ctlist", ".json", ".txt", ".ctfull"])\n\n\ndef full_backup_dir():\n    return admin_export_dir("Full Backups")\n\n\ndef full_backup_export_path():\n    return _timestamped_export_path(full_backup_dir(), FULL_BACKUP_FILE)\n\n\ndef list_full_backup_files():\n    return list_backup_files(full_backup_dir(), [".ctfull", ".ctp", ".shva", ".ctlist"])\n\n\ndef revocation_backup_dir():\n    return admin_export_dir("Revocation Jsons")\n\n\ndef revocation_export_path():\n    return _timestamped_export_path(revocation_backup_dir(), REVOKED_EXPORT_FILE)\n\n\ndef list_revocation_backup_files():\n    return list_backup_files(revocation_backup_dir(), [".json", ".txt"])\n\n\ndef license_export_dir():\n    return admin_export_dir("License Exports")\n\n\ndef license_export_path():\n    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")\n    return os.path.join(license_export_dir(), f"licenses_export_{stamp}.csv")\n\n\ndef github_config_path():\n    return file_path(GITHUB_CONFIG_FILE)\n\n\ndef load_github_upload_config():\n    data = load_json(github_config_path(), {})\n    merged = dict(DEFAULT_GITHUB_UPLOAD)\n    if isinstance(data, dict):\n        for key in ("owner", "repo", "branch", "path"):\n            value = str(data.get(key, "")).strip()\n            if value:\n                merged[key] = value\n    return merged\n\n\ndef save_github_upload_config(data):\n    clean = {}\n    for key in ("owner", "repo", "branch", "path"):\n        clean[key] = str(data.get(key, DEFAULT_GITHUB_UPLOAD.get(key, ""))).strip()\n    save_json(github_config_path(), clean)\n\n\ndef build_github_raw_url(owner, repo, branch, path):\n    owner = str(owner).strip().strip("/")\n    repo = str(repo).strip().strip("/")\n    branch = str(branch).strip().strip("/") or "main"\n    path = str(path).strip().lstrip("/")\n    if not owner or not repo or not path:\n        return ""\n    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"\n\n\ndef load_json(path, default):\n    try:\n        with open(path, "r", encoding="utf-8") as f:\n            return json.load(f)\n    except Exception:\n        return default\n\n\ndef save_json(path, data):\n    os.makedirs(os.path.dirname(path), exist_ok=True)\n    with open(path, "w", encoding="utf-8") as f:\n        json.dump(data, f, indent=2, ensure_ascii=False)\n\n\ndef canonical_json(data):\n    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")\n\n\ndef info_popup(title, message):\n    content = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))\n    lbl = Label(\n        text=message,\n        color=get_color_from_hex(TEXT),\n        halign="left",\n        valign="top",\n        text_size=(dp(300), None),\n        size_hint_y=None,\n    )\n    lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", max(val[1], dp(80))))\n    btn = RoundedButton(\n        text="OK",\n        size_hint_y=None,\n        height=dp(46),\n        bg_hex=GREEN,\n    )\n    content.add_widget(lbl)\n    content.add_widget(btn)\n    popup = Popup(\n        title=title,\n        content=content,\n        size_hint=(0.9, 0.6),\n        separator_color=get_color_from_hex(GREEN),\n        background_color=get_color_from_hex(CARD),\n    )\n    btn.bind(on_release=popup.dismiss)\n    popup.open()\n\n\ndef copy_to_clipboard(label, value):\n    Clipboard.copy(value or "")\n    info_popup("Copied", f"{label} copied to clipboard.")\n\n\ndef paste_clipboard_into(widget):\n    try:\n        widget.text = Clipboard.paste() or ""\n    except Exception as e:\n        info_popup("Paste failed", str(e))\n\n\ndef paste_clipboard_into(widget):\n    try:\n        widget.text = Clipboard.paste() or ""\n    except Exception as e:\n        info_popup("Paste failed", str(e))\n\n\n\ndef _rewrite_default_authority_files():\n    priv_path = file_path(PRIVATE_KEY_FILE)\n    pub_path = file_path(PUBLIC_KEY_FILE)\n    os.makedirs(os.path.dirname(priv_path), exist_ok=True)\n    with open(priv_path, \'wb\') as f:\n        f.write(DEFAULT_AUTHORITY_PRIVATE_PEM.encode(\'utf-8\'))\n    with open(pub_path, \'wb\') as f:\n        f.write(DEFAULT_AUTHORITY_PUBLIC_PEM.encode(\'utf-8\'))\n\n\ndef _stash_corrupt_authority_file(path):\n    try:\n        if os.path.exists(path):\n            stamp = datetime.utcnow().strftime(\'%Y%m%d_%H%M%S\')\n            os.replace(path, path + f\'.corrupt_{stamp}\')\n    except Exception:\n        pass\n\n\ndef load_existing_keypair():\n    ensure_default_authority_files()\n    priv_path = file_path(PRIVATE_KEY_FILE)\n    pub_path = file_path(PUBLIC_KEY_FILE)\n    if not (os.path.exists(priv_path) and os.path.exists(pub_path)):\n        return None, None\n\n    try:\n        with open(priv_path, \'rb\') as f:\n            private_key = rsa.PrivateKey.load_pkcs1(f.read())\n        with open(pub_path, \'rb\') as f:\n            public_key = rsa.PublicKey.load_pkcs1(f.read())\n        return public_key, private_key\n    except Exception:\n        _stash_corrupt_authority_file(priv_path)\n        _stash_corrupt_authority_file(pub_path)\n        try:\n            _rewrite_default_authority_files()\n            with open(priv_path, \'rb\') as f:\n                private_key = rsa.PrivateKey.load_pkcs1(f.read())\n            with open(pub_path, \'rb\') as f:\n                public_key = rsa.PublicKey.load_pkcs1(f.read())\n            return public_key, private_key\n        except Exception:\n            return None, None\n\n\ndef initialize_authority_keypair():\n    ensure_default_authority_files()\n    return load_existing_keypair()\n\n\ndef _pbkdf(password: str, salt: bytes) -> bytes:\n    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=32)\n\n\ndef _xor_stream(key: bytes, data: bytes) -> bytes:\n    out = bytearray()\n    counter = 0\n    while len(out) < len(data):\n        block = hashlib.sha256(key + counter.to_bytes(4, "big")).digest()\n        take = min(len(block), len(data) - len(out))\n        chunk = data[len(out):len(out)+take]\n        out.extend(bytes(a ^ b for a, b in zip(chunk, block[:take])))\n        counter += 1\n    return bytes(out)\n\n\n\ndef build_secure_backup_blob(password: str, bundle_type: str, payload: dict):\n    if not password:\n        raise ValueError("Backup password is required.")\n    raw_payload = {\n        "schema": 2,\n        "app": BACKUP_BUNDLE_APP,\n        "bundle_type": bundle_type,\n        "exported_at": utc_now_iso(),\n        "payload": payload,\n    }\n    raw = canonical_json(raw_payload)\n    salt = os.urandom(16)\n    enc_key = _pbkdf(password, salt)\n    ciphertext = _xor_stream(enc_key, raw)\n    mac = hmac.new(enc_key, salt + ciphertext, hashlib.sha256).digest()\n    bundle = {\n        "schema": 2,\n        "app": BACKUP_BUNDLE_APP,\n        "bundle_type": bundle_type,\n        "salt": base64.urlsafe_b64encode(salt).decode("ascii"),\n        "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),\n        "mac": base64.urlsafe_b64encode(mac).decode("ascii"),\n    }\n    return json.dumps(bundle, indent=2)\n\n\ndef parse_secure_backup_blob(blob_text: str, password: str):\n    if not blob_text.strip():\n        raise ValueError("Backup text is empty.")\n    if not password:\n        raise ValueError("Backup password is required.")\n    bundle = json.loads(blob_text)\n    salt = base64.urlsafe_b64decode(bundle["salt"].encode("ascii"))\n    ciphertext = base64.urlsafe_b64decode(bundle["ciphertext"].encode("ascii"))\n    mac = base64.urlsafe_b64decode(bundle["mac"].encode("ascii"))\n    enc_key = _pbkdf(password, salt)\n    expected = hmac.new(enc_key, salt + ciphertext, hashlib.sha256).digest()\n    if not hmac.compare_digest(mac, expected):\n        raise ValueError("Backup password is incorrect or backup is corrupted.")\n    raw = _xor_stream(enc_key, ciphertext)\n    data = json.loads(raw.decode("utf-8"))\n    if isinstance(data, dict) and "payload" in data and "bundle_type" in data:\n        return data\n    legacy_payload = {}\n    if "private_key_pem" in data:\n        legacy_payload["private_key_pem"] = data.get("private_key_pem", "")\n    if "public_key_pem" in data:\n        legacy_payload["public_key_pem"] = data.get("public_key_pem", "")\n    if "licenses" in data:\n        legacy_payload["licenses"] = data.get("licenses", [])\n    if "revoked_bundle" in data:\n        legacy_payload["revoked_bundle"] = data.get("revoked_bundle", {})\n    return {\n        "schema": data.get("schema", 1),\n        "app": data.get("app", BACKUP_BUNDLE_APP),\n        "bundle_type": "legacy_full_backup",\n        "exported_at": data.get("exported_at", ""),\n        "payload": legacy_payload,\n    }\n\n\ndef build_authority_backup_blob(password: str):\n    public_key, private_key = load_existing_keypair()\n    if not public_key or not private_key:\n        raise ValueError("No authority loaded. Initialize or import authority first.")\n    payload = {\n        "private_key_pem": private_key.save_pkcs1("PEM").decode("utf-8"),\n        "public_key_pem": public_key.save_pkcs1("PEM").decode("utf-8"),\n    }\n    return build_secure_backup_blob(password, "authority_only", payload)\n\n\ndef build_license_list_backup_blob(password: str, records):\n    payload = {\n        "licenses": records,\n    }\n    return build_secure_backup_blob(password, "license_list_only", payload)\n\n\ndef build_full_backup_blob(password: str, records):\n    public_key, private_key = load_existing_keypair()\n    if not public_key or not private_key:\n        raise ValueError("No authority loaded. Initialize or import authority first.")\n    revoked_bundle = build_revocation_bundle(records, private_key)\n    payload = {\n        "private_key_pem": private_key.save_pkcs1("PEM").decode("utf-8"),\n        "public_key_pem": public_key.save_pkcs1("PEM").decode("utf-8"),\n        "licenses": records,\n        "revoked_bundle": revoked_bundle,\n    }\n    return build_secure_backup_blob(password, "full_backup", payload)\n\n\ndef sign_payload(private_key, payload_dict):\n    sig = rsa.sign(canonical_json(payload_dict), private_key, "SHA-256")\n    return base64.urlsafe_b64encode(sig).decode("ascii")\n\n\ndef verify_signature(public_key, payload_dict, sig_b64):\n    try:\n        sig = base64.urlsafe_b64decode(sig_b64.encode("ascii"))\n        rsa.verify(canonical_json(payload_dict), sig, public_key)\n        return True\n    except Exception:\n        return False\n\n\ndef encode_activation_code(payload_dict, signature_b64):\n    blob = {"p": payload_dict, "s": signature_b64}\n    raw = canonical_json(blob)\n    compressed = zlib.compress(raw, level=9)\n    token = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")\n    chunks = textwrap.wrap(token, 24)\n    return "BGT6A-" + ".".join(chunks)\n\n\ndef decode_activation_code(code):\n    cleaned = code.strip().replace("\\n", "").replace(" ", "")\n    if cleaned.startswith("BGT6A-") or cleaned.startswith("CTP6A-"):\n        cleaned = cleaned[6:]\n    cleaned = cleaned.replace(".", "")\n    cleaned += "=" * ((4 - len(cleaned) % 4) % 4)\n    raw = base64.urlsafe_b64decode(cleaned.encode("ascii"))\n    data = json.loads(zlib.decompress(raw).decode("utf-8"))\n    return data["p"], data["s"]\n\n\ndef build_revocation_bundle(records, private_key):\n    revoked_ids = sorted([r["license_id"] for r in records if r.get("status") == "revoked"])\n    payload = {\n        "app": "synapse_by_shv",\n        "version": 1,\n        "updated_at": utc_now_iso(),\n        "revoked_ids": revoked_ids,\n    }\n    signature = sign_payload(private_key, payload)\n    return {"payload": payload, "signature": signature}\n\n\nclass LicenseStore:\n    def __init__(self):\n        self.path = file_path(LICENSE_DB_FILE)\n        self.records = load_json(self.path, [])\n\n    def save(self):\n        save_json(self.path, self.records)\n\n    def add(self, record):\n        self.records.insert(0, record)\n        self.save()\n\n    def update(self, license_id, updater):\n        for rec in self.records:\n            if rec["license_id"] == license_id:\n                updater(rec)\n                self.save()\n                return True\n        return False\n\n    def delete(self, license_id):\n        before = len(self.records)\n        self.records = [rec for rec in self.records if rec.get("license_id") != license_id]\n        changed = len(self.records) != before\n        if changed:\n            self.save()\n        return changed\n\n    def delete_many(self, license_ids):\n        wanted = {str(x) for x in (license_ids or []) if str(x)}\n        if not wanted:\n            return 0\n        before = len(self.records)\n        self.records = [rec for rec in self.records if rec.get("license_id") not in wanted]\n        removed = before - len(self.records)\n        if removed:\n            self.save()\n        return removed\n\n    def find(self, license_id):\n        for rec in self.records:\n            if rec["license_id"] == license_id:\n                return rec\n        return None\n\n\n\nclass RoundedButton(Button):\n    def __init__(self, bg_hex=GREEN, text_color=None, radius=16, border_hex=None, **kwargs):\n        kwargs.setdefault("background_normal", "")\n        kwargs.setdefault("background_down", "")\n        kwargs.setdefault("background_color", (0, 0, 0, 0))\n        super().__init__(**kwargs)\n        self._bg_hex = bg_hex\n        self._radius = dp(radius)\n        self._border_hex = border_hex or self._derive_neon_border(bg_hex)\n        self._inset = dp(2)\n        if text_color is None:\n            text_color = (0, 0, 0, 1) if bg_hex == GREEN else (1, 1, 1, 1)\n        self.color = text_color\n        self.bold = True\n        with self.canvas.before:\n            Color(rgba=get_color_from_hex(self._border_hex))\n            self._border_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])\n            Color(rgba=get_color_from_hex(bg_hex))\n            self._rounded_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[max(dp(4), self._radius - self._inset)])\n        self.bind(pos=self._update_bg, size=self._update_bg)\n\n    def _derive_neon_border(self, bg_hex):\n        color = str(bg_hex or \'\').lower()\n        if color == str(RED).lower():\n            return \'#ff8f8f\'\n        if color == str(BLUE).lower():\n            return \'#6ed1ff\'\n        if color == str(PURPLE).lower():\n            return \'#d39cff\'\n        if color == str(ORANGE).lower():\n            return \'#ffbf73\'\n        if color == str(GREEN).lower():\n            return \'#8cff7c\'\n        return \'#52ffd9\'\n\n    def _update_bg(self, *_):\n        self._border_bg.pos = self.pos\n        self._border_bg.size = self.size\n        self._border_bg.radius = [self._radius]\n        self._rounded_bg.pos = (self.x + self._inset, self.y + self._inset)\n        self._rounded_bg.size = (max(0, self.width - self._inset * 2), max(0, self.height - self._inset * 2))\n        self._rounded_bg.radius = [max(dp(4), self._radius - self._inset)]\n\n\nclass SectionCard(BoxLayout):\n    def __init__(self, title, subtitle="", **kwargs):\n        super().__init__(orientation="vertical", spacing=dp(8), padding=dp(12), size_hint_y=None, **kwargs)\n        self.bind(minimum_height=self.setter("height"))\n        from kivy.graphics import Color, RoundedRectangle\n        with self.canvas.before:\n            Color(rgba=get_color_from_hex(CARD))\n            self._bg = RoundedRectangle(radius=[18], pos=self.pos, size=self.size)\n        self.bind(pos=self._update_bg, size=self._update_bg)\n\n        title_lbl = Label(\n            text=title,\n            bold=True,\n            color=get_color_from_hex(TEXT),\n            font_size=\'20sp\',\n            size_hint_y=None,\n            height=dp(30),\n            halign="center",\n            valign="middle",\n            text_size=(dp(320), None),\n        )\n        self.add_widget(title_lbl)\n\n        if subtitle:\n            subtitle_lbl = Label(\n                text=subtitle,\n                color=get_color_from_hex(SUBTEXT),\n                size_hint_y=None,\n                halign="left",\n                valign="middle",\n                text_size=(dp(320), None),\n            )\n            subtitle_lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(18), val[1])))\n            self.add_widget(subtitle_lbl)\n\n    def _update_bg(self, *_):\n        self._bg.pos = self.pos\n        self._bg.size = self.size\n\n\ndef make_label(text, color=TEXT, bold=False, height=dp(24)):\n    return Label(\n        text=text,\n        color=get_color_from_hex(color),\n        bold=bold,\n        size_hint_y=None,\n        height=height,\n        halign="left",\n        valign="middle",\n        text_size=(dp(320), None),\n    )\n\n\ndef make_input(hint="", multiline=False, readonly=False, password=False):\n    return TextInput(\n        hint_text=hint,\n        multiline=multiline,\n        readonly=readonly,\n        password=password,\n        size_hint_y=None,\n        height=dp(46) if not multiline else dp(100),\n        background_color=get_color_from_hex("#111111"),\n        foreground_color=get_color_from_hex(TEXT),\n        cursor_color=(1, 0, 0, 1),\n        cursor_width=\'2sp\',\n        selection_color=(0.22, 0.68, 0.95, 0.35),\n        hint_text_color=get_color_from_hex(SUBTEXT),\n        padding=[dp(10), dp(12), dp(10), dp(12)],\n    )\n\n\ndef make_button(text, color=GREEN):\n    return RoundedButton(\n        text=text,\n        size_hint_y=None,\n        height=dp(46),\n        bg_hex=color,\n        text_color=(0, 0, 0, 1) if color == GREEN else (1, 1, 1, 1),\n    )\n\n\ndef make_nav_button(text):\n    btn = RoundedButton(\n        text=text,\n        size_hint=(1, None),\n        height=dp(42),\n        bg_hex="#182432",\n        text_color=get_color_from_hex(TEXT),\n    )\n    return btn\n\n\nclass LicenseManagerScreen(Screen):\n    def __init__(self, **kwargs):\n        super().__init__(**kwargs)\n        self.store = LicenseStore()\n        self.public_key = None\n        self.private_key = None\n        self._load_error = ""\n        try:\n            self.public_key, self.private_key = load_existing_keypair()\n        except Exception as e:\n            self._load_error = str(e)\n        self.github_config = load_github_upload_config()\n        self._last_license_id = ""\n        self.add_widget(BoxLayout())\n        Clock.schedule_once(self.safe_build_ui, 0)\n\n    def safe_build_ui(self, *_):\n        try:\n            self.build_ui()\n        except Exception as e:\n            self.show_build_error(e)\n\n    def show_build_error(self, error):\n        self.clear_widgets()\n        root = BoxLayout(orientation=\'vertical\', padding=dp(10), spacing=dp(10))\n        card = SectionCard(\'SHV Budget Licensing Error\', \'The APK prevented this module from loading normally. Use Retry after the patch or backup/import authority again if old key files were corrupted.\')\n        err_text = str(error or self._load_error or \'Unknown error\')\n        card.add_widget(make_label(\'Details: \' + err_text[:500], color=RED, height=dp(72)))\n        if self._load_error:\n            card.add_widget(make_label(\'Authority load note: \' + self._load_error[:500], color=ORANGE, height=dp(72)))\n        retry_btn = make_button(\'Retry Loading\', GREEN)\n        retry_btn.bind(on_release=lambda *_: self.safe_build_ui())\n        card.add_widget(retry_btn)\n        root.add_widget(card)\n        self.add_widget(root)\n\n    def build_ui(self, *_):\n        self.clear_widgets()\n        root = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))\n\n        top_bar = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))\n        title_lbl = Label(\n            text="SHV Budget Licensing Interface",\n            color=get_color_from_hex(TEXT),\n            bold=True,\n            halign="left",\n            valign="middle",\n            font_size=\'18sp\',\n        )\n        title_lbl.bind(size=lambda inst, val: setattr(inst, "text_size", val))\n        top_bar.add_widget(title_lbl)\n        exit_btn = make_button("EXIT", RED)\n        exit_btn.size_hint_x = None\n        exit_btn.width = dp(100)\n        exit_btn.bind(on_release=lambda *_: App.get_running_app().stop())\n        top_bar.add_widget(exit_btn)\n        root.add_widget(top_bar)\n\n        nav_grid = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(92))\n        self.tab_buttons = {}\n        self.tab_titles = {\n            "dashboard": "Dashboard",\n            "authority": "Authority",\n            "generate": "Generate",\n            "licenses": "Licenses",\n            "revocations": "Revocations",\n        }\n        for key in ("dashboard", "authority", "generate", "licenses", "revocations"):\n            btn = make_nav_button(self.tab_titles[key])\n            btn.bind(on_release=lambda *_ , tab_key=key: self.switch_tab(tab_key))\n            self.tab_buttons[key] = btn\n            nav_grid.add_widget(btn)\n        root.add_widget(nav_grid)\n\n        self.content_host = BoxLayout()\n        root.add_widget(self.content_host)\n        self.add_widget(root)\n\n        self.tab_views = {\n            "dashboard": self.build_dashboard_view(),\n            "authority": self.build_authority_view(),\n            "generate": self.build_generate_view(),\n            "licenses": self.build_licenses_view(),\n            "revocations": self.build_revocation_view(),\n        }\n\n        self.switch_tab("dashboard")\n        self.update_authority_status()\n        self.refresh_dashboard()\n        self.refresh_license_list()\n        self.refresh_revocation_box()\n\n    def switch_tab(self, key):\n        if not hasattr(self, "content_host"):\n            return\n        self.content_host.clear_widgets()\n        view = self.tab_views.get(key)\n        if view is not None:\n            self.content_host.add_widget(view)\n\n        active_bg = get_color_from_hex(GREEN)\n        inactive_bg = get_color_from_hex("#141a22")\n        active_text = (0, 0, 0, 1)\n        inactive_text = get_color_from_hex(TEXT)\n        for btn_key, btn in self.tab_buttons.items():\n            if btn_key == key:\n                btn.background_color = active_bg\n                btn.color = active_text\n            else:\n                btn.background_color = inactive_bg\n                btn.color = inactive_text\n\n    def switch_license_subtab(self, key):\n        if not hasattr(self, \'license_subtab_host\'):\n            return\n        self.license_subtab_host.clear_widgets()\n        if key == \'tools\':\n            self.license_subtab_host.add_widget(self.license_tools_view)\n        else:\n            self.license_subtab_host.add_widget(self.license_list_view)\n        active_bg = get_color_from_hex(GREEN)\n        inactive_bg = get_color_from_hex("#141a22")\n        active_text = (0, 0, 0, 1)\n        inactive_text = get_color_from_hex(TEXT)\n        for btn_key, btn in getattr(self, \'license_subtab_buttons\', {}).items():\n            if btn_key == key:\n                btn.background_color = active_bg\n                btn.color = active_text\n            else:\n                btn.background_color = inactive_bg\n                btn.color = inactive_text\n\n    def build_dashboard_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        self.dashboard_box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        self.dashboard_box.bind(minimum_height=self.dashboard_box.setter("height"))\n        scroll.add_widget(self.dashboard_box)\n        return scroll\n\n\n    def build_authority_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        box.bind(minimum_height=box.setter("height"))\n\n        card = SectionCard("Authority only backup", "Share the same signing authority across apps without replacing this app\'s local license list.")\n        self.auth_status_label = make_label("", color=SUBTEXT, height=dp(44))\n        card.add_widget(self.auth_status_label)\n\n        card.add_widget(make_label("Backup Password"))\n        self.backup_password_input = make_input("Enter backup password")\n        card.add_widget(self.backup_password_input)\n\n        row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        init_btn = make_button("Initialize Authority", UI_CYAN)\n        copy_pub_btn = make_button("Copy Public Key PEM", UI_CYAN)\n        row1.add_widget(init_btn)\n        row1.add_widget(copy_pub_btn)\n        init_btn.bind(on_release=lambda *_: self.initialize_authority())\n        copy_pub_btn.bind(on_release=lambda *_: self.copy_public_key())\n        card.add_widget(row1)\n\n        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_backup_btn = make_button("Generate Authority Backup", GREEN)\n        copy_backup_btn = make_button("Copy Authority Backup", UI_CYAN)\n        row2.add_widget(gen_backup_btn)\n        row2.add_widget(copy_backup_btn)\n        gen_backup_btn.bind(on_release=lambda *_: self.generate_authority_backup())\n        copy_backup_btn.bind(on_release=lambda *_: copy_to_clipboard("Authority backup", getattr(self, "backup_output", make_input()).text if hasattr(self, "backup_output") else ""))\n        card.add_widget(row2)\n\n        self.backup_output = make_input("Generated encrypted authority-only backup will appear here", multiline=True, readonly=True)\n        self.backup_output.height = dp(220)\n        card.add_widget(self.backup_output)\n\n        row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_backup_btn = make_button("Save Authority File", UI_CYAN)\n        import_backup_btn = make_button("Import Authority", GREEN)\n        row3.add_widget(save_backup_btn)\n        row3.add_widget(import_backup_btn)\n        save_backup_btn.bind(on_release=lambda *_: self.save_authority_backup())\n        import_backup_btn.bind(on_release=lambda *_: self.import_authority_backup())\n        card.add_widget(row3)\n\n        card.add_widget(make_label("Paste Authority Backup To Import"))\n        self.import_backup_input = make_input("Paste encrypted authority backup here", multiline=True)\n        self.import_backup_input.height = dp(180)\n        card.add_widget(self.import_backup_input)\n\n        row4 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        paste_btn = make_button("Paste", UI_CYAN)\n        import_file_btn = make_button("Import Auth File", UI_CYAN)\n        paste_btn.bind(on_release=lambda *_: self.paste_backup_from_clipboard())\n        import_file_btn.bind(on_release=lambda *_: self.open_auth_file_picker())\n        row4.add_widget(paste_btn)\n        row4.add_widget(import_file_btn)\n        card.add_widget(row4)\n        box.add_widget(card)\n\n        full_card = SectionCard("Full backup", "Back up authority + this app\'s local license list + a revocation snapshot in one encrypted file.")\n        full_card.add_widget(make_label("Uses the same backup password above.", color=SUBTEXT, height=dp(28)))\n\n        full_row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_full_btn = make_button("Generate Full Backup", GREEN)\n        copy_full_btn = make_button("Copy Full Backup", UI_CYAN)\n        gen_full_btn.bind(on_release=lambda *_: self.generate_full_backup())\n        copy_full_btn.bind(on_release=lambda *_: copy_to_clipboard("Full backup", getattr(self, "full_backup_output", make_input()).text if hasattr(self, "full_backup_output") else ""))\n        full_row1.add_widget(gen_full_btn)\n        full_row1.add_widget(copy_full_btn)\n        full_card.add_widget(full_row1)\n\n        self.full_backup_output = make_input("Generated encrypted full backup will appear here", multiline=True, readonly=True)\n        self.full_backup_output.height = dp(220)\n        full_card.add_widget(self.full_backup_output)\n\n        full_row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_full_btn = make_button("Save Full Backup", UI_CYAN)\n        import_full_btn = make_button("Import Full Backup", GREEN)\n        save_full_btn.bind(on_release=lambda *_: self.save_full_backup())\n        import_full_btn.bind(on_release=lambda *_: self.import_full_backup())\n        full_row2.add_widget(save_full_btn)\n        full_row2.add_widget(import_full_btn)\n        full_card.add_widget(full_row2)\n\n        full_card.add_widget(make_label("Paste Full Backup To Import"))\n        self.import_full_backup_input = make_input("Paste encrypted full backup here", multiline=True)\n        self.import_full_backup_input.height = dp(180)\n        full_card.add_widget(self.import_full_backup_input)\n\n        full_row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        paste_full_btn = make_button("Paste", UI_CYAN)\n        import_full_file_btn = make_button("Import Full File", UI_CYAN)\n        paste_full_btn.bind(on_release=lambda *_: self.paste_full_backup_from_clipboard())\n        import_full_file_btn.bind(on_release=lambda *_: self.open_full_backup_file_picker())\n        full_row3.add_widget(paste_full_btn)\n        full_row3.add_widget(import_full_file_btn)\n        full_card.add_widget(full_row3)\n        box.add_widget(full_card)\n\n        scroll.add_widget(box)\n        return scroll\n\n    def build_generate_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        box.bind(minimum_height=box.setter("height"))\n\n        card = SectionCard("Generate activation code", "Create device-bound Pro licenses for SHV Budget")\n        self.device_input = make_input("Device Code (ex: BGT-DEV-1234ABCD5678)")\n        self.tier_spinner = Spinner(text="pro", values=("pro",), size_hint_y=None, height=dp(46))\n        self.source_spinner = Spinner(text="crypto", values=("crypto", "bank", "promo", "partner", "personal", "test"), size_hint_y=None, height=dp(46))\n        self.customer_name_input = make_input("Customer name")\n        self.customer_email_input = make_input("Customer email (optional)")\n        self.label_input = make_input("Internal label / tag (optional)")\n        self.note_input = make_input("Notes (optional)", multiline=True)\n        self.expiry_input = make_input("Expiry date YYYY-MM-DD (optional)")\n\n        for title, widget in [\n            ("Device Code", self.device_input),\n            ("Tier", self.tier_spinner),\n            ("Payment Method", self.source_spinner),\n            ("Customer Name", self.customer_name_input),\n            ("Customer Email", self.customer_email_input),\n            ("Label", self.label_input),\n            ("Note", self.note_input),\n            ("Expiry", self.expiry_input),\n        ]:\n            card.add_widget(make_label(title))\n            card.add_widget(widget)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_btn = make_button("Generate License")\n        clear_btn = make_button("Clear", UI_CYAN)\n        gen_btn.bind(on_release=lambda *_: self.generate_license())\n        clear_btn.bind(on_release=lambda *_: self.clear_generate_form())\n        row.add_widget(gen_btn)\n        row.add_widget(clear_btn)\n        card.add_widget(row)\n\n        self.generated_code_input = make_input("Generated activation code will appear here", multiline=True, readonly=True)\n        self.generated_code_input.height = dp(160)\n        card.add_widget(make_label("Activation Code"))\n        card.add_widget(self.generated_code_input)\n\n        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        copy_btn = make_button("Copy Code", UI_CYAN)\n        copy_id_btn = make_button("Copy License ID", UI_CYAN)\n        copy_btn.bind(on_release=lambda *_: copy_to_clipboard("Activation code", self.generated_code_input.text))\n        copy_id_btn.bind(on_release=lambda *_: copy_to_clipboard("License ID", self._last_license_id))\n        row2.add_widget(copy_btn)\n        row2.add_widget(copy_id_btn)\n        card.add_widget(row2)\n\n        box.add_widget(card)\n        scroll.add_widget(box)\n        return scroll\n\n\n    def build_licenses_view(self):\n        root = BoxLayout(orientation=\'vertical\', spacing=dp(8), padding=[0, dp(4), 0, dp(4)])\n\n        tab_row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(46))\n        self.license_subtab_buttons = {}\n        for key, title in (("tools", "Tools"), ("list", "License List")):\n            btn = make_nav_button(title)\n            btn.bind(on_release=lambda *_ , tab_key=key: self.switch_license_subtab(tab_key))\n            self.license_subtab_buttons[key] = btn\n            tab_row.add_widget(btn)\n        root.add_widget(tab_row)\n\n        self.license_subtab_host = BoxLayout()\n        root.add_widget(self.license_subtab_host)\n\n        tools_scroll = ScrollView(do_scroll_x=False, scroll_type=[\'bars\', \'content\'], bar_width=dp(6))\n        tools_outer = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])\n        tools_outer.bind(minimum_height=tools_outer.setter(\'height\'))\n\n        backup_card = SectionCard("License list backup", "Back up or restore only this app\'s local license list. Shared authority stays untouched.")\n        backup_row1 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        gen_backup_btn = make_button("Generate License Backup", GREEN)\n        copy_backup_btn = make_button("Copy License Backup", UI_CYAN)\n        gen_backup_btn.bind(on_release=lambda *_: self.generate_license_list_backup())\n        copy_backup_btn.bind(on_release=lambda *_: copy_to_clipboard("License list backup", getattr(self, "license_backup_output", make_input()).text if hasattr(self, "license_backup_output") else ""))\n        backup_row1.add_widget(gen_backup_btn)\n        backup_row1.add_widget(copy_backup_btn)\n        backup_card.add_widget(backup_row1)\n\n        self.license_backup_output = make_input("Generated encrypted license-list backup will appear here", multiline=True, readonly=True)\n        self.license_backup_output.height = dp(160)\n        backup_card.add_widget(self.license_backup_output)\n\n        backup_row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_backup_btn = make_button("Save License Backup", UI_CYAN)\n        import_backup_btn = make_button("Import License Backup", GREEN)\n        save_backup_btn.bind(on_release=lambda *_: self.save_license_list_backup())\n        import_backup_btn.bind(on_release=lambda *_: self.import_license_list_backup())\n        backup_row2.add_widget(save_backup_btn)\n        backup_row2.add_widget(import_backup_btn)\n        backup_card.add_widget(backup_row2)\n\n        backup_card.add_widget(make_label("Paste License Backup To Import"))\n        self.import_license_backup_input = make_input("Paste encrypted license-list backup here", multiline=True)\n        self.import_license_backup_input.height = dp(140)\n        backup_card.add_widget(self.import_license_backup_input)\n\n        backup_row3 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        paste_btn = make_button("Paste", UI_CYAN)\n        import_file_btn = make_button("Import Backup File", UI_CYAN)\n        paste_btn.bind(on_release=lambda *_: self.paste_license_backup_from_clipboard())\n        import_file_btn.bind(on_release=lambda *_: self.open_license_backup_file_picker())\n        backup_row3.add_widget(paste_btn)\n        backup_row3.add_widget(import_file_btn)\n        backup_card.add_widget(backup_row3)\n        tools_outer.add_widget(backup_card)\n        tools_scroll.add_widget(tools_outer)\n        self.license_tools_view = tools_scroll\n\n        search_card = SectionCard("License search", "Search, filter, export, or delete test keys")\n        self.search_input = make_input("Search by ID / customer / email / device / label / payment")\n        self.search_input.height = dp(42)\n        self.search_input.bind(text=lambda *_: self.refresh_license_list())\n        search_card.add_widget(self.search_input)\n\n        filters = GridLayout(cols=4, spacing=dp(6), size_hint_y=None, height=dp(42))\n        self.license_status_spinner = Spinner(text="all", values=("all", "active", "revoked"), size_hint_y=None, height=dp(42))\n        self.license_tier_spinner = Spinner(text="all", values=("all", "demo", "pro"), size_hint_y=None, height=dp(42))\n        self.license_source_spinner = Spinner(text="all", values=("all", "crypto", "bank", "promo", "partner", "personal", "test"), size_hint_y=None, height=dp(42))\n        self.license_sort_spinner = Spinner(text="newest", values=("newest", "oldest", "tier", "status"), size_hint_y=None, height=dp(42))\n        self.license_status_spinner.bind(text=lambda *_: self.refresh_license_list())\n        self.license_tier_spinner.bind(text=lambda *_: self.refresh_license_list())\n        self.license_source_spinner.bind(text=lambda *_: self.refresh_license_list())\n        self.license_sort_spinner.bind(text=lambda *_: self.refresh_license_list())\n        filters.add_widget(self.license_status_spinner)\n        filters.add_widget(self.license_tier_spinner)\n        filters.add_widget(self.license_source_spinner)\n        filters.add_widget(self.license_sort_spinner)\n        search_card.add_widget(filters)\n\n        actions = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(44))\n        export_btn = make_button("Export Visible CSV", UI_CYAN)\n        delete_filtered_btn = make_button("Delete Visible", RED)\n        export_btn.bind(on_release=lambda *_: self.export_visible_licenses_csv())\n        delete_filtered_btn.bind(on_release=lambda *_: self.confirm_delete_visible_licenses())\n        actions.add_widget(export_btn)\n        actions.add_widget(delete_filtered_btn)\n        search_card.add_widget(actions)\n        search_card.add_widget(make_label("Tip: set Source = test before using Delete Visible.", color=SUBTEXT, height=dp(24)))\n\n        list_scroll = ScrollView(do_scroll_x=False, scroll_type=[\'bars\', \'content\'], bar_width=dp(6))\n        list_outer = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])\n        list_outer.bind(minimum_height=list_outer.setter(\'height\'))\n        list_outer.add_widget(search_card)\n        results_card = SectionCard("License list", "Tap Details to inspect, copy, revoke, or restore.")\n        self.license_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=[0, 0, 0, dp(8)])\n        self.license_box.bind(minimum_height=self.license_box.setter("height"))\n        results_card.add_widget(self.license_box)\n        list_outer.add_widget(results_card)\n        list_scroll.add_widget(list_outer)\n        self.license_list_view = list_scroll\n\n        self.switch_license_subtab(\'list\')\n        return root\n\n    def build_revocation_view(self):\n        scroll = ScrollView(do_scroll_x=False)\n        box = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(8), 0, dp(8)])\n        box.bind(minimum_height=box.setter("height"))\n\n        card = SectionCard("Revocation export", "Generate, save, copy, or manually import the signed revoked list for the customer app.")\n        export_btn = make_button("Generate Signed Revocation File")\n        export_btn.bind(on_release=lambda *_: self.refresh_revocation_box())\n        card.add_widget(export_btn)\n\n        self.revocation_output = make_input("", multiline=True, readonly=True)\n        self.revocation_output.height = dp(220)\n        card.add_widget(self.revocation_output)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_btn = make_button("Save synapse_revoked_licenses.json", UI_CYAN)\n        copy_btn = make_button("Copy JSON", UI_CYAN)\n        save_btn.bind(on_release=lambda *_: self.save_revocation_bundle())\n        copy_btn.bind(on_release=lambda *_: copy_to_clipboard("Revocation JSON", self.revocation_output.text))\n        row.add_widget(save_btn)\n        row.add_widget(copy_btn)\n        card.add_widget(row)\n\n        pub_btn = make_button("Copy Public Key PEM", UI_CYAN)\n        pub_btn.bind(on_release=lambda *_: self.copy_public_key())\n        card.add_widget(pub_btn)\n\n        card.add_widget(make_label("Paste Revocation JSON To Import"))\n        self.import_revocation_input = make_input("Paste signed revocation JSON here", multiline=True)\n        self.import_revocation_input.height = dp(180)\n        card.add_widget(self.import_revocation_input)\n\n        row_import = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(46))\n        paste_btn = make_button("Paste", UI_CYAN)\n        import_btn = make_button("Import JSON", GREEN)\n        import_file_btn = make_button("Import File", UI_CYAN)\n        paste_btn.bind(on_release=lambda *_: self.paste_revocation_from_clipboard())\n        import_btn.bind(on_release=lambda *_: self.import_revocation_bundle())\n        import_file_btn.bind(on_release=lambda *_: self.open_revocation_file_picker())\n        row_import.add_widget(paste_btn)\n        row_import.add_widget(import_btn)\n        row_import.add_widget(import_file_btn)\n        card.add_widget(row_import)\n        box.add_widget(card)\n\n        gh = SectionCard("GitHub upload", "Store the revocation JSON online so customer apps can read the fixed raw URL")\n        self.github_owner_input = make_input("GitHub owner / username")\n        self.github_repo_input = make_input("Repository name")\n        self.github_branch_input = make_input("Branch", readonly=False)\n        self.github_path_input = make_input("Path inside repo (ex: synapse_revoked_licenses.json)")\n        self.github_token_input = make_input("GitHub token with contents:write access")\n        self.github_raw_url_input = make_input("Raw URL", readonly=True)\n\n        self.github_owner_input.text = self.github_config.get(\'owner\', \'\')\n        self.github_repo_input.text = self.github_config.get(\'repo\', \'\')\n        self.github_branch_input.text = self.github_config.get(\'branch\', \'main\') or \'main\'\n        self.github_path_input.text = self.github_config.get(\'path\', REVOKED_EXPORT_FILE) or REVOKED_EXPORT_FILE\n        self.github_token_input.text = self.github_config.get(\'token\', \'\')\n\n        for title, widget in [\n            ("Owner", self.github_owner_input),\n            ("Repo", self.github_repo_input),\n            ("Branch", self.github_branch_input),\n            ("Path", self.github_path_input),\n            ("Token", self.github_token_input),\n            ("Raw URL", self.github_raw_url_input),\n        ]:\n            gh.add_widget(make_label(title))\n            gh.add_widget(widget)\n            if widget is self.github_token_input:\n                paste_token_btn = make_button("Paste Token", UI_CYAN)\n                paste_token_btn.height = dp(40)\n                paste_token_btn.bind(on_release=lambda *_: paste_clipboard_into(self.github_token_input))\n                gh.add_widget(paste_token_btn)\n            if widget is self.github_token_input:\n                paste_token_btn = make_button("Paste Token", UI_CYAN)\n                paste_token_btn.height = dp(40)\n                paste_token_btn.bind(on_release=lambda *_: paste_clipboard_into(self.github_token_input))\n                gh.add_widget(paste_token_btn)\n\n        for widget in (self.github_owner_input, self.github_repo_input, self.github_branch_input, self.github_path_input):\n            widget.bind(text=self.update_github_raw_url)\n        self.update_github_raw_url()\n\n        row2 = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        save_cfg_btn = make_button("Save Upload Settings", UI_CYAN)\n        upload_btn = make_button("Upload Revocation JSON", GREEN)\n        save_cfg_btn.bind(on_release=lambda *_: self.save_github_settings())\n        upload_btn.bind(on_release=lambda *_: self.upload_revocation_to_github())\n        row2.add_widget(save_cfg_btn)\n        row2.add_widget(upload_btn)\n        gh.add_widget(row2)\n        box.add_widget(gh)\n\n        scroll.add_widget(box)\n        return scroll\n\n    def update_authority_status(self):\n        if hasattr(self, "auth_status_label"):\n            if self.public_key and self.private_key:\n                self.auth_status_label.text = f"Authority loaded. Public key fingerprint: {hashlib.sha256(self.public_key.save_pkcs1(\'PEM\')).hexdigest()[:16].upper()}"\n                self.auth_status_label.color = get_color_from_hex(GREEN)\n            else:\n                self.auth_status_label.text = "No authority loaded. Import your backup or initialize authority."\n                self.auth_status_label.color = get_color_from_hex(RED)\n\n    def require_authority(self):\n        if self.public_key and self.private_key:\n            return True\n        info_popup("Authority required", "No signing authority is loaded. Import your authority backup or initialize authority first.")\n        return False\n\n    def initialize_authority(self):\n        if self.public_key and self.private_key:\n            info_popup("Authority exists", "This device already has an authority loaded.")\n            return\n        try:\n            self.public_key, self.private_key = initialize_authority_keypair()\n            self.update_authority_status()\n            self.refresh_dashboard()\n            info_popup("Authority initialized", "A new signing authority was created on this device. Back it up immediately.")\n        except Exception as e:\n            info_popup("Initialize failed", str(e))\n\n\n    def copy_public_key(self):\n        if not self.require_authority():\n            return\n        copy_to_clipboard("Public key PEM", self.public_key.save_pkcs1("PEM").decode("utf-8"))\n\n    def _refresh_everything(self):\n        self.refresh_dashboard()\n        self.refresh_license_list()\n        self.refresh_revocation_box()\n\n    def _write_authority_payload(self, payload):\n        private_pem = str(payload.get("private_key_pem", "")).strip()\n        public_pem = str(payload.get("public_key_pem", "")).strip()\n        if not private_pem or not public_pem:\n            raise ValueError("Backup does not contain a valid authority keypair.")\n        with open(file_path(PRIVATE_KEY_FILE), "wb") as f:\n            f.write(private_pem.encode("utf-8"))\n        with open(file_path(PUBLIC_KEY_FILE), "wb") as f:\n            f.write(public_pem.encode("utf-8"))\n        self.public_key, self.private_key = load_existing_keypair()\n        self.update_authority_status()\n\n    def _write_license_payload(self, payload):\n        records = payload.get("licenses", [])\n        if not isinstance(records, list):\n            raise ValueError("Backup does not contain a valid license list.")\n        save_json(file_path(LICENSE_DB_FILE), records)\n        self.store = LicenseStore()\n\n    def _apply_revocation_bundle_to_store(self, bundle):\n        if not isinstance(bundle, dict):\n            raise ValueError("Revocation JSON is invalid.")\n        payload = bundle.get("payload") if isinstance(bundle.get("payload"), dict) else bundle\n        revoked_ids = payload.get("revoked_ids", []) if isinstance(payload, dict) else []\n        revoked_ids = {str(x).strip() for x in revoked_ids if str(x).strip()}\n        changed = False\n        if revoked_ids:\n            for rec in self.store.records:\n                lid = str(rec.get("license_id", "")).strip()\n                if lid in revoked_ids and rec.get("status") != "revoked":\n                    rec["status"] = "revoked"\n                    rec["revoked_at"] = utc_now_iso()\n                    changed = True\n            if changed:\n                self.store.save()\n        save_json(file_path(REVOKED_EXPORT_FILE), bundle)\n        return len(revoked_ids), changed\n\n    def _finish_authority_import(self, bundle):\n        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}\n        self._write_authority_payload(payload)\n        self._refresh_everything()\n\n    def _finish_license_list_import(self, bundle):\n        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}\n        self._write_license_payload(payload)\n        self._refresh_everything()\n\n    def _finish_full_backup_import(self, bundle):\n        payload = bundle.get("payload", {}) if isinstance(bundle, dict) else {}\n        self._write_authority_payload(payload)\n        self._write_license_payload(payload)\n        revoked_bundle = payload.get("revoked_bundle", {})\n        if revoked_bundle:\n            self._apply_revocation_bundle_to_store(revoked_bundle)\n        self._refresh_everything()\n\n    def _paste_into_widget(self, widget, empty_message="There is no backup content in the clipboard."):\n        try:\n            pasted = Clipboard.paste() or ""\n            if not pasted.strip():\n                info_popup("Clipboard empty", empty_message)\n                return\n            widget.text = pasted\n        except Exception as e:\n            info_popup("Paste failed", str(e))\n\n    def _open_backup_file_picker(self, title_text, folder, backup_files, on_select):\n        if not backup_files:\n            info_popup("No backup file found", f"No backup file was found in:\\n{folder}")\n            return\n\n        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))\n        title = Label(\n            text=f"Select backup file from:\\n{folder}",\n            color=get_color_from_hex(TEXT),\n            halign="left",\n            valign="middle",\n            text_size=(dp(300), None),\n            size_hint_y=None,\n        )\n        title.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(48), val[1] + dp(8))))\n        content.add_widget(title)\n\n        scroll = ScrollView(do_scroll_x=False, size_hint=(1, 1))\n        file_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)\n        file_box.bind(minimum_height=file_box.setter("height"))\n\n        popup = Popup(\n            title=title_text,\n            content=content,\n            size_hint=(0.92, 0.8),\n            separator_color=get_color_from_hex(GREEN),\n            background_color=get_color_from_hex(CARD),\n        )\n\n        for path in backup_files:\n            name = os.path.basename(path)\n            try:\n                stamp = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")\n            except Exception:\n                stamp = "Unknown time"\n            btn = RoundedButton(\n                text=f"{name}\\n{stamp}",\n                size_hint_y=None,\n                height=dp(68),\n                halign="left",\n                valign="middle",\n                text_size=(dp(260), None),\n                bg_hex="#182432",\n                text_color=get_color_from_hex(TEXT),\n            )\n            btn.bind(on_release=lambda *_ , selected_path=path, pop=popup: on_select(selected_path, pop))\n            file_box.add_widget(btn)\n\n        scroll.add_widget(file_box)\n        content.add_widget(scroll)\n\n        close_btn = make_button("Close", RED)\n        close_btn.bind(on_release=popup.dismiss)\n        content.add_widget(close_btn)\n        popup.open()\n\n    def generate_authority_backup(self):\n        if not self.require_authority():\n            return\n        try:\n            blob = build_authority_backup_blob(self.backup_password_input.text.strip())\n            self.backup_output.text = blob\n            info_popup("Backup generated", "Encrypted authority-only backup generated successfully.")\n        except Exception as e:\n            info_popup("Backup failed", str(e))\n\n    def save_authority_backup(self):\n        text = self.backup_output.text.strip() if hasattr(self, "backup_output") else ""\n        if not text:\n            info_popup("Nothing to save", "Generate an authority backup first.")\n            return\n        path = authority_backup_export_path()\n        with open(path, "w", encoding="utf-8") as f:\n            f.write(text)\n        info_popup("Saved", f"Authority backup saved to:\\n{path}")\n\n    def import_authority_backup(self):\n        try:\n            blob_text = self.import_backup_input.text.strip()\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_authority_import(bundle)\n            info_popup("Import successful", "Authority backup imported successfully. Local license list was not changed.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_backup_from_clipboard(self):\n        self._paste_into_widget(self.import_backup_input)\n\n    def open_auth_file_picker(self):\n        self._open_backup_file_picker("Import Auth File", authority_backup_dir(), list_authority_backup_files(), self.import_authority_from_file)\n\n    def import_authority_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_backup_input"):\n                self.import_backup_input.text = blob_text\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_authority_import(bundle)\n            if popup is not None:\n                popup.dismiss()\n            info_popup("Import successful", f"Authority file imported successfully from:\\n{backup_path}\\n\\nLocal license list was not changed.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def generate_license_list_backup(self):\n        try:\n            blob = build_license_list_backup_blob(self.backup_password_input.text.strip(), self.store.records)\n            self.license_backup_output.text = blob\n            info_popup("Backup generated", "Encrypted license-list backup generated successfully.")\n        except Exception as e:\n            info_popup("Backup failed", str(e))\n\n    def save_license_list_backup(self):\n        text = self.license_backup_output.text.strip() if hasattr(self, "license_backup_output") else ""\n        if not text:\n            info_popup("Nothing to save", "Generate a license-list backup first.")\n            return\n        path = license_list_backup_export_path()\n        with open(path, "w", encoding="utf-8") as f:\n            f.write(text)\n        info_popup("Saved", f"License-list backup saved to:\\n{path}")\n\n    def import_license_list_backup(self):\n        try:\n            blob_text = self.import_license_backup_input.text.strip()\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_license_list_import(bundle)\n            info_popup("Import successful", "License-list backup imported successfully. Authority keys were not changed.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_license_backup_from_clipboard(self):\n        self._paste_into_widget(self.import_license_backup_input)\n\n    def open_license_backup_file_picker(self):\n        self._open_backup_file_picker("Import License Backup", license_list_backup_dir(), list_license_list_backup_files(), self.import_license_backup_from_file)\n\n    def import_license_backup_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_license_backup_input"):\n                self.import_license_backup_input.text = blob_text\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_license_list_import(bundle)\n            if popup is not None:\n                popup.dismiss()\n            info_popup("Import successful", f"License-list backup imported successfully from:\\n{backup_path}")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def generate_full_backup(self):\n        if not self.require_authority():\n            return\n        try:\n            blob = build_full_backup_blob(self.backup_password_input.text.strip(), self.store.records)\n            self.full_backup_output.text = blob\n            info_popup("Backup generated", "Encrypted full backup generated successfully.")\n        except Exception as e:\n            info_popup("Backup failed", str(e))\n\n    def save_full_backup(self):\n        text = self.full_backup_output.text.strip() if hasattr(self, "full_backup_output") else ""\n        if not text:\n            info_popup("Nothing to save", "Generate a full backup first.")\n            return\n        path = full_backup_export_path()\n        with open(path, "w", encoding="utf-8") as f:\n            f.write(text)\n        info_popup("Saved", f"Full backup saved to:\\n{path}")\n\n    def import_full_backup(self):\n        try:\n            blob_text = self.import_full_backup_input.text.strip()\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_full_backup_import(bundle)\n            info_popup("Import successful", "Full backup imported successfully.")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_full_backup_from_clipboard(self):\n        self._paste_into_widget(self.import_full_backup_input)\n\n    def open_full_backup_file_picker(self):\n        self._open_backup_file_picker("Import Full Backup", full_backup_dir(), list_full_backup_files(), self.import_full_backup_from_file)\n\n    def import_full_backup_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_full_backup_input"):\n                self.import_full_backup_input.text = blob_text\n            bundle = parse_secure_backup_blob(blob_text, self.backup_password_input.text.strip())\n            self._finish_full_backup_import(bundle)\n            if popup is not None:\n                popup.dismiss()\n            info_popup("Import successful", f"Full backup imported successfully from:\\n{backup_path}")\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def paste_revocation_from_clipboard(self):\n        self._paste_into_widget(self.import_revocation_input, "There is no revocation JSON in the clipboard.")\n\n    def open_revocation_file_picker(self):\n        self._open_backup_file_picker("Import Revocation JSON", revocation_backup_dir(), list_revocation_backup_files(), self.import_revocation_from_file)\n\n    def import_revocation_from_file(self, backup_path, popup=None):\n        try:\n            with open(backup_path, "r", encoding="utf-8") as f:\n                blob_text = f.read().strip()\n            if hasattr(self, "import_revocation_input"):\n                self.import_revocation_input.text = blob_text\n            self._finish_revocation_import(blob_text)\n            if popup is not None:\n                popup.dismiss()\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def _finish_revocation_import(self, blob_text):\n        bundle = json.loads(blob_text)\n        revoked_count, matched_updates = self._apply_revocation_bundle_to_store(bundle)\n        self._refresh_everything()\n        info_popup("Revocation import complete", f"Imported revocation JSON with {revoked_count} revoked ID(s). Matching local licenses updated: {\'yes\' if matched_updates else \'no\'}.")\n\n    def import_revocation_bundle(self):\n        try:\n            blob_text = self.import_revocation_input.text.strip()\n            self._finish_revocation_import(blob_text)\n        except Exception as e:\n            info_popup("Import failed", str(e))\n\n    def get_compact_device_label(self, device_code):\n            device_code = str(device_code or \'\').strip()\n            if not device_code:\n                return \'No device\'\n            return device_code[-8:] if len(device_code) > 8 else device_code\n\n    def get_compact_issued_label(self, issued_at):\n            txt = str(issued_at or \'\').strip()\n            if not txt:\n                return \'No issue date\'\n            return txt.replace(\'T\', \' \')[:16].replace(\'Z\', \'\')\n\n    def show_license_details(self, rec):\n            details = [\n                f"License ID: {rec.get(\'license_id\', \'\')}",\n                f"Tier: {str(rec.get(\'tier\', \'\')).upper()}",\n                f"Status: {str(rec.get(\'status\', \'active\')).upper()}",\n                f"Payment: {rec.get(\'payment_method\', rec.get(\'source\', \'\'))}",\n                f"Customer: {rec.get(\'customer_name\', \'\') or \'-\'}",\n                f"Email: {rec.get(\'customer_email\', \'\') or \'-\'}",\n                f"Device Code: {rec.get(\'device_code\', \'\') or \'Not bound\'}",\n                f"Issued: {rec.get(\'issued_at\', \'\')}",\n            ]\n            if rec.get(\'expiry\'):\n                details.append(f"Expiry: {rec.get(\'expiry\')}")\n            if rec.get(\'label\'):\n                details.append(f"Label: {rec.get(\'label\')}")\n            if rec.get(\'customer_note\'):\n                details.append(f"Note: {rec.get(\'customer_note\')}")\n\n            content = BoxLayout(orientation=\'vertical\', padding=dp(12), spacing=dp(10))\n            body = Label(\n                text=\'\\n\'.join(details),\n                color=get_color_from_hex(TEXT),\n                halign=\'left\',\n                valign=\'top\',\n                text_size=(dp(300), None),\n                size_hint_y=None,\n            )\n            body.bind(texture_size=lambda inst, val: setattr(inst, \'height\', max(dp(120), val[1])))\n            content.add_widget(body)\n\n            row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n            copy_id_btn = make_button(\'Copy ID\', UI_CYAN)\n            copy_code_btn = make_button(\'Copy Code\', UI_CYAN)\n            delete_btn = make_button(\'Delete\', RED)\n            row.add_widget(copy_id_btn)\n            row.add_widget(copy_code_btn)\n            row.add_widget(delete_btn)\n            content.add_widget(row)\n\n            close_btn = make_button(\'Close\', UI_CYAN)\n            content.add_widget(close_btn)\n\n            popup = Popup(\n                title=\'License Details\',\n                content=content,\n                size_hint=(0.92, 0.68),\n                separator_color=get_color_from_hex(GREEN),\n                background_color=get_color_from_hex(CARD),\n            )\n            copy_id_btn.bind(on_release=lambda *_: copy_to_clipboard(\'License ID\', rec.get(\'license_id\', \'\')))\n            copy_code_btn.bind(on_release=lambda *_: copy_to_clipboard(\'Activation code\', rec.get(\'activation_code\', \'\')))\n            delete_btn.bind(on_release=lambda *_: self.confirm_delete_license(rec.get(\'license_id\', \'\'), popup))\n            close_btn.bind(on_release=popup.dismiss)\n            popup.open()\n\n    def collect_github_settings(self):\n            return {\n                \'owner\': self.github_owner_input.text.strip(),\n                \'repo\': self.github_repo_input.text.strip(),\n                \'branch\': self.github_branch_input.text.strip() or \'main\',\n                \'path\': self.github_path_input.text.strip().lstrip(\'/\'),\n                \'token\': self.github_token_input.text.strip(),\n            }\n\n    def update_github_raw_url(self, *_):\n            if not hasattr(self, \'github_raw_url_input\'):\n                return\n            cfg = self.collect_github_settings() if hasattr(self, \'github_owner_input\') else dict(self.github_config)\n            self.github_raw_url_input.text = build_github_raw_url(cfg.get(\'owner\', \'\'), cfg.get(\'repo\', \'\'), cfg.get(\'branch\', \'main\'), cfg.get(\'path\', REVOKED_EXPORT_FILE))\n\n    def save_github_settings(self):\n            cfg = self.collect_github_settings()\n            save_github_upload_config(cfg)\n            self.github_config = load_github_upload_config()\n            self.update_github_raw_url()\n            info_popup(\'Saved\', \'GitHub upload settings saved on this admin device.\')\n\n    def upload_revocation_to_github(self):\n            if not self.require_authority():\n                return\n            cfg = self.collect_github_settings()\n            missing = [name for name, value in [(\'owner\', cfg[\'owner\']), (\'repo\', cfg[\'repo\']), (\'branch\', cfg[\'branch\']), (\'path\', cfg[\'path\']), (\'token\', cfg[\'token\'])] if not value]\n            if missing:\n                info_popup(\'Missing fields\', f"Fill these GitHub fields first: {\', \'.join(missing)}")\n                return\n\n            bundle = build_revocation_bundle(self.store.records, self.private_key)\n            payload_text = json.dumps(bundle, indent=2)\n            api_url = f"https://api.github.com/repos/{cfg[\'owner\']}/{cfg[\'repo\']}/contents/{cfg[\'path\']}"\n            headers = {\n                \'Accept\': \'application/vnd.github+json\',\n                \'Authorization\': f"Bearer {cfg[\'token\']}",\n                \'X-GitHub-Api-Version\': \'2022-11-28\',\n            }\n            body = {\n                \'message\': f"Update revoked licenses at {utc_now_iso()}",\n                \'content\': base64.b64encode(payload_text.encode(\'utf-8\')).decode(\'ascii\'),\n                \'branch\': cfg[\'branch\'],\n            }\n            try:\n                existing = requests.get(api_url, headers=headers, timeout=20)\n                if existing.status_code == 200:\n                    existing_data = existing.json()\n                    if existing_data.get(\'sha\'):\n                        body[\'sha\'] = existing_data[\'sha\']\n                elif existing.status_code not in (404,):\n                    raise RuntimeError(f"GitHub lookup failed: {existing.status_code} {existing.text[:180]}")\n\n                resp = requests.put(api_url, headers=headers, json=body, timeout=25)\n                if resp.status_code not in (200, 201):\n                    raise RuntimeError(f"GitHub upload failed: {resp.status_code} {resp.text[:220]}")\n\n                save_github_upload_config(cfg)\n                self.github_config = load_github_upload_config()\n                self.refresh_revocation_box()\n                self.update_github_raw_url()\n                info_popup(\'Uploaded\', f"Revocation file uploaded successfully to:\\n{self.github_raw_url_input.text}")\n            except Exception as e:\n                info_popup(\'Upload failed\', str(e))\n\n    def build_and_store_license(self, tier, source, device_code, customer_name=\'\', customer_email=\'\', label=\'\', note=\'\', expiry=\'\'):\n            if tier != \'pro\':\n                raise ValueError(\'Only Pro licenses are supported for SHV Budget.\')\n            if source not in (\'crypto\', \'bank\', \'promo\', \'partner\', \'personal\', \'test\'):\n                raise ValueError(\'Choose one of the payment/source types.\')\n            if not device_code:\n                raise ValueError("Enter the customer\'s Device Code from the app.")\n\n            license_id = \'BGT-\' + secrets.token_hex(4).upper()\n            payload = {\n                \'app\': \'shv_budget\',\n                \'schema\': 1,\n                \'license_id\': license_id,\n                \'tier\': tier,\n                \'payment_method\': source,\n                \'source\': source,\n                \'device_code\': device_code,\n                \'customer_name\': customer_name,\n                \'customer_email\': customer_email,\n                \'label\': label,\n                \'issued_at\': utc_now_iso(),\n            }\n            if note:\n                payload[\'note\'] = note\n            if expiry:\n                payload[\'expires_at\'] = expiry\n\n            signature = sign_payload(self.private_key, payload)\n            activation_code = encode_activation_code(payload, signature)\n            record = {\n                \'license_id\': license_id,\n                \'tier\': tier,\n                \'source\': source,\n                \'payment_method\': source,\n                \'customer_name\': customer_name,\n                \'customer_email\': customer_email,\n                \'device_code\': device_code,\n                \'label\': label,\n                \'customer_note\': note,\n                \'expiry\': expiry,\n                \'expires_at\': expiry,\n                \'issued_at\': payload[\'issued_at\'],\n                \'status\': \'active\',\n                \'activation_code\': activation_code,\n                \'license_bundle\': {\'payload\': payload, \'signature\': signature},\n                \'signature_valid\': verify_signature(self.public_key, payload, signature),\n            }\n            self.store.add(record)\n            self._last_license_id = license_id\n            self.generated_code_input.text = activation_code\n            self.refresh_dashboard()\n            self.refresh_license_list()\n            self.refresh_revocation_box()\n            return record\n\n\n    def generate_test_license(self):\n            if not self.require_authority():\n                return\n            try:\n                device_code = self.device_input.text.strip().upper()\n                if not device_code:\n                    raise ValueError("Enter the customer\'s Device Code before generating a test license.")\n                expiry = self.expiry_input.text.strip() or (datetime.utcnow() + timedelta(days=7)).strftime(\'%Y-%m-%d\')\n                label = self.label_input.text.strip() or \'Internal Test\'\n                note = self.note_input.text.strip() or \'Admin-generated test key\'\n                self.build_and_store_license(\'pro\', \'test\', device_code, customer_name=self.customer_name_input.text.strip() or \'Internal Test\', customer_email=self.customer_email_input.text.strip(), label=label, note=note, expiry=expiry)\n                info_popup(\'Test license generated\', \'7-day style test Pro license created successfully. Change the expiry field first if you want a different end date.\')\n            except Exception as e:\n                info_popup(\'Test license failed\', str(e))\n\n    def refresh_dashboard(self):\n        if not hasattr(self, "dashboard_box"):\n            return\n        self.dashboard_box.clear_widgets()\n        records = self.store.records\n        total = len(records)\n        active = len([r for r in records if r.get("status") == "active"])\n        revoked = len([r for r in records if r.get("status") == "revoked"])\n        demo = len([r for r in records if r.get("tier") == "demo"])\n        pro = len([r for r in records if r.get("tier") == "pro"])\n\n\n        authority_card = SectionCard("Authority status")\n        if self.public_key and self.private_key:\n            authority_card.add_widget(make_label("Authority loaded", GREEN))\n            authority_card.add_widget(make_label(f"Data folder: {app_data_dir()}", height=dp(38)))\n        else:\n            authority_card.add_widget(make_label("No authority loaded. Import your backup or initialize authority.", RED, height=dp(38)))\n            if getattr(self, \'_load_error\', \'\'):\n                authority_card.add_widget(make_label(f"Recovered from authority load issue: {self._load_error[:120]}", ORANGE, height=dp(38)))\n        self.dashboard_box.add_widget(authority_card)\n\n        stats = SectionCard("License totals")\n        for t in [\n            f"Total licenses: {total}",\n            f"Active: {active}",\n            f"Revoked: {revoked}",\n            f"Demo: {demo}",\n            f"Pro: {pro}",\n        ]:\n            stats.add_widget(make_label(t, GREEN if "Active" in t else (RED if "Revoked" in t else TEXT)))\n        self.dashboard_box.add_widget(stats)\n\n        latest = SectionCard("Latest issued")\n        if records:\n            for rec in records[:8]:\n                latest.add_widget(make_label(\n                    f"{rec[\'license_id\']}  |  {rec[\'tier\']}  |  {rec.get(\'customer_name\',\'-\')}  |  {rec.get(\'status\',\'active\')}",\n                    height=dp(22),\n                ))\n        else:\n            latest.add_widget(make_label("No licenses yet."))\n        self.dashboard_box.add_widget(latest)\n\n    def get_filtered_license_records(self):\n        query = (self.search_input.text or "").strip().lower() if hasattr(self, "search_input") else ""\n        status_filter = getattr(getattr(self, \'license_status_spinner\', None), \'text\', \'all\').strip().lower()\n        tier_filter = getattr(getattr(self, \'license_tier_spinner\', None), \'text\', \'all\').strip().lower()\n        source_filter = getattr(getattr(self, \'license_source_spinner\', None), \'text\', \'all\').strip().lower()\n        sort_mode = getattr(getattr(self, \'license_sort_spinner\', None), \'text\', \'newest\').strip().lower()\n\n        visible = []\n        for rec in self.store.records:\n            hay = " ".join([\n                rec.get("license_id", ""),\n                rec.get("device_code", ""),\n                rec.get("tier", ""),\n                rec.get("source", ""),\n                rec.get("label", ""),\n                rec.get("customer_note", ""),\n                rec.get("status", ""),\n            ]).lower()\n            if query and query not in hay:\n                continue\n            if status_filter != \'all\' and str(rec.get(\'status\', \'active\')).lower() != status_filter:\n                continue\n            if tier_filter != \'all\' and str(rec.get(\'tier\', \'\')).lower() != tier_filter:\n                continue\n            if source_filter != \'all\' and str(rec.get(\'source\', \'\')).lower() != source_filter:\n                continue\n            visible.append(rec)\n\n        if sort_mode == \'oldest\':\n            visible.sort(key=lambda r: str(r.get(\'issued_at\', \'\')))\n        elif sort_mode == \'tier\':\n            visible.sort(key=lambda r: (str(r.get(\'tier\', \'\')), str(r.get(\'issued_at\', \'\'))), reverse=False)\n            visible.reverse()\n        elif sort_mode == \'status\':\n            visible.sort(key=lambda r: (str(r.get(\'status\', \'active\')), str(r.get(\'issued_at\', \'\'))), reverse=False)\n            visible.reverse()\n        else:\n            visible.sort(key=lambda r: str(r.get(\'issued_at\', \'\')), reverse=True)\n        return visible\n\n    def export_visible_licenses_csv(self):\n        records = self.get_filtered_license_records()\n        if not records:\n            info_popup("Nothing to export", "There are no visible licenses to export with the current filters.")\n            return\n        export_path = license_export_path()\n        fieldnames = [\n            "license_id",\n            "tier",\n            "status",\n            "source",\n            "payment_method",\n            "customer_name",\n            "customer_email",\n            "device_code",\n            "label",\n            "customer_note",\n            "issued_at",\n            "expiry",\n            "expires_at",\n            "revoked_at",\n            "signature_valid",\n        ]\n        with open(export_path, "w", encoding="utf-8", newline="") as f:\n            writer = csv.DictWriter(f, fieldnames=fieldnames)\n            writer.writeheader()\n            for rec in records:\n                row = {name: rec.get(name, "") for name in fieldnames}\n                writer.writerow(row)\n        info_popup("Exported", f"Visible licenses exported successfully to:\\n{export_path}")\n\n    def confirm_delete_license(self, license_id, parent_popup=None):\n        rec = self.store.find(license_id)\n        if not rec:\n            info_popup("Not found", "That license could not be found anymore.")\n            return\n\n        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))\n        message = Label(\n            text=f"Delete this license permanently?\\n\\n{license_id}\\n{str(rec.get(\'tier\', \'\')).upper()} • {str(rec.get(\'status\', \'active\')).upper()}\\n\\nUse delete mainly for test keys and clutter. Revoked licenses removed from the database will also disappear from future revocation exports.",\n            color=get_color_from_hex(TEXT),\n            halign="left",\n            valign="top",\n            text_size=(dp(300), None),\n            size_hint_y=None,\n        )\n        message.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(140), val[1])))\n        content.add_widget(message)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        cancel_btn = make_button("Cancel", UI_CYAN)\n        delete_btn = make_button("Delete", RED)\n        row.add_widget(cancel_btn)\n        row.add_widget(delete_btn)\n        content.add_widget(row)\n\n        popup = Popup(\n            title="Delete License",\n            content=content,\n            size_hint=(0.92, 0.62),\n            separator_color=get_color_from_hex(RED),\n            background_color=get_color_from_hex(CARD),\n        )\n\n        cancel_btn.bind(on_release=popup.dismiss)\n\n        def do_delete(*_):\n            removed = self.store.delete(license_id)\n            popup.dismiss()\n            if parent_popup is not None:\n                parent_popup.dismiss()\n            if removed:\n                self.refresh_dashboard()\n                self.refresh_license_list()\n                self.refresh_revocation_box()\n                info_popup("Deleted", f"{license_id} was deleted from the license database.")\n            else:\n                info_popup("Not found", "That license could not be found anymore.")\n\n        delete_btn.bind(on_release=do_delete)\n        popup.open()\n\n    def confirm_delete_visible_licenses(self):\n        records = self.get_filtered_license_records()\n        if not records:\n            info_popup("Nothing to delete", "There are no visible licenses to delete with the current filters.")\n            return\n\n        count = len(records)\n        ids = [rec.get("license_id", "") for rec in records if rec.get("license_id")]\n\n        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))\n        message = Label(\n            text=f"Delete all {count} currently visible licenses?\\n\\nThis is best used after narrowing the list to test keys with search and filters. Any revoked licenses deleted here will also disappear from future revocation exports.",\n            color=get_color_from_hex(TEXT),\n            halign="left",\n            valign="top",\n            text_size=(dp(300), None),\n            size_hint_y=None,\n        )\n        message.bind(texture_size=lambda inst, val: setattr(inst, "height", max(dp(130), val[1])))\n        content.add_widget(message)\n\n        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))\n        cancel_btn = make_button("Cancel", UI_CYAN)\n        delete_btn = make_button("Delete Visible", RED)\n        row.add_widget(cancel_btn)\n        row.add_widget(delete_btn)\n        content.add_widget(row)\n\n        popup = Popup(\n            title="Delete Visible Licenses",\n            content=content,\n            size_hint=(0.92, 0.58),\n            separator_color=get_color_from_hex(RED),\n            background_color=get_color_from_hex(CARD),\n        )\n\n        cancel_btn.bind(on_release=popup.dismiss)\n\n        def do_delete(*_):\n            removed = self.store.delete_many(ids)\n            popup.dismiss()\n            self.refresh_dashboard()\n            self.refresh_license_list()\n            self.refresh_revocation_box()\n            info_popup("Deleted", f"Deleted {removed} visible license(s).")\n\n        delete_btn.bind(on_release=do_delete)\n        popup.open()\n\n    def refresh_license_list(self):\n        if not hasattr(self, "license_box"):\n            return\n\n        self.license_box.clear_widgets()\n        visible = self.get_filtered_license_records()\n\n        if not visible:\n            self.license_box.add_widget(make_label("No matching licenses found."))\n            return\n\n        for rec in visible:\n            status = str(rec.get(\'status\', \'active\')).upper()\n            source = str(rec.get(\'source\', \'\')).upper()\n            device_short = self.get_compact_device_label(rec.get(\'device_code\', \'\'))\n            issued_short = self.get_compact_issued_label(rec.get(\'issued_at\', \'\'))\n            subtitle = f"{source}  •  {status}"\n            if rec.get(\'label\'):\n                subtitle += f"  •  {rec.get(\'label\')}"\n\n            card = SectionCard(f"{rec[\'license_id\']}  •  {rec[\'tier\'].upper()}", subtitle)\n            card.add_widget(make_label(f"Device suffix: {device_short}  •  Issued: {issued_short}", height=dp(22)))\n            if rec.get(\'expiry\'):\n                card.add_widget(make_label(f"Expiry: {rec.get(\'expiry\')}", height=dp(22)))\n\n            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))\n            details_btn = make_button("Details", UI_CYAN)\n            id_btn = make_button("Copy ID", UI_CYAN)\n            revoke_btn = make_button("Revoke" if rec.get("status") != "revoked" else "Restore", RED if rec.get("status") != "revoked" else PURPLE)\n\n            details_btn.bind(on_release=lambda *_ , record=rec: self.show_license_details(record))\n            id_btn.bind(on_release=lambda *_ , lid=rec["license_id"]: copy_to_clipboard("License ID", lid))\n            revoke_btn.bind(on_release=lambda *_ , lid=rec["license_id"], status=rec.get("status"): self.toggle_revoke(lid, status))\n\n            row.add_widget(details_btn)\n            row.add_widget(id_btn)\n            row.add_widget(revoke_btn)\n            card.add_widget(row)\n            self.license_box.add_widget(card)\n\n    def refresh_revocation_box(self):\n        if not hasattr(self, "revocation_output"):\n            return\n        if not self.private_key:\n            self.revocation_output.text = ""\n            return\n        bundle = build_revocation_bundle(self.store.records, self.private_key)\n        self.revocation_output.text = json.dumps(bundle, indent=2)\n\n    def clear_generate_form(self):\n        self.device_input.text = ""\n        self.tier_spinner.text = "pro"\n        self.source_spinner.text = "crypto"\n        self.customer_name_input.text = ""\n        self.customer_email_input.text = ""\n        self.label_input.text = ""\n        self.note_input.text = ""\n        self.expiry_input.text = ""\n        self.generated_code_input.text = ""\n        self._last_license_id = ""\n\n    def generate_license(self):\n        if not self.require_authority():\n            return\n        try:\n            tier = self.tier_spinner.text.strip()\n            source = self.source_spinner.text.strip()\n            device_code = self.device_input.text.strip().upper()\n            label = self.label_input.text.strip()\n            note = self.note_input.text.strip()\n            expiry = self.expiry_input.text.strip()\n            self.build_and_store_license(tier, source, device_code, customer_name=self.customer_name_input.text.strip(), customer_email=self.customer_email_input.text.strip(), label=label, note=note, expiry=expiry)\n            info_popup("License generated", f"{tier.upper()} license created successfully.")\n        except Exception as e:\n            info_popup("License failed", str(e))\n\n    def toggle_revoke(self, license_id, status):\n        target = "revoked" if status != "revoked" else "active"\n        self.store.update(\n            license_id,\n            lambda rec: rec.update({"status": target, "revoked_at": utc_now_iso() if target == "revoked" else ""}),\n        )\n        self.refresh_dashboard()\n        self.refresh_license_list()\n        self.refresh_revocation_box()\n        info_popup("License updated", f"{license_id} is now {target.upper()}.")\n\n    def save_revocation_bundle(self):\n        if not self.require_authority():\n            return\n        bundle = build_revocation_bundle(self.store.records, self.private_key)\n        path = revocation_export_path()\n        save_json(path, bundle)\n        save_json(file_path(REVOKED_EXPORT_FILE), bundle)\n        self.refresh_revocation_box()\n        info_popup("Saved", f"Revocation file saved to:\\n{path}")\n\n\n'
_BUDGET_NS = {'__name__': '_shv_budget_module'}
exec(_BUDGET_MODULE_SOURCE, _BUDGET_NS)
_BUDGET_NS.update({
    'UI_CYAN': BLUE,
    'UI_GREEN': GREEN,
    'UI_PURPLE': PURPLE,
    'UI_ORANGE': ORANGE,
    'UI_RED': RED,
    'UI_TEAL': BLUE,
    'UI_BLUE': BLUE,
    'UI_TEXT': TEXT,
    'UI_SUBTEXT': SUBTEXT,
    'UI_BG': BG,
    'UI_CARD': CARD,
})
_BUDGET_NS['RoundedButton'] = RoundedButton
_BUDGET_NS['make_button'] = make_button
_BUDGET_NS['make_nav_button'] = make_nav_button
BudgetLicenseManagerScreen = _BUDGET_NS['LicenseManagerScreen']
try:
    BudgetLicenseManagerScreen.__name__ = 'BudgetLicenseManagerScreen'
    BudgetLicenseManagerScreen.__qualname__ = 'BudgetLicenseManagerScreen'
except Exception:
    pass

BUDGET_REVOCATION_RAW_URL = "https://raw.githubusercontent.com/therealwolfman97/SH-VERTEX-ADMIN-PANEL/main/LICENSING/APPS/REVOCATIONS/budget-revo.json"

def budget_license_records():
    return _safe_records(admin_data_path(_BUDGET_NS.get('LICENSE_DB_FILE', 'budget_licenses_db.json')))

class BudgetManagerShellScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.build_ui, 0)

    def build_ui(self, *_):
        self.clear_widgets()
        self.manager_widget = None
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        nav = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(8))
        back_btn = make_button('Back to Apps', UI_CYAN)
        home_btn = make_button('Admin Home', UI_CYAN)
        vault_btn = make_button('Vault', UI_CYAN)
        back_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'apps'))
        home_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'home'))
        vault_btn.bind(on_release=lambda *_: setattr(self.manager, 'current', 'backup_vault'))
        nav.add_widget(back_btn)
        nav.add_widget(home_btn)
        nav.add_widget(vault_btn)
        root.add_widget(nav)
        placeholder = SectionCard('SHV Budget Licensing', 'Loading is deferred until you actually open this screen, which is safer for the packaged APK startup path.')
        placeholder.add_widget(make_label('Open this screen to load the full SHV Budget licensing interface.', color=SUBTEXT, height=dp(28)))
        self._body_host = BoxLayout()
        self._body_host.add_widget(placeholder)
        root.add_widget(self._body_host)
        self.add_widget(root)

    def on_pre_enter(self, *_):
        if getattr(self, 'manager_widget', None) is None:
            if hasattr(self, '_body_host'):
                self._body_host.clear_widgets()
                loading = SectionCard('SHV Budget Licensing', 'Loading the interface...')
                loading.add_widget(make_label('Please wait while the licensing tools initialize.', color=SUBTEXT, height=dp(28)))
                self._body_host.add_widget(loading)

            def _load_widget(*__):
                try:
                    self.manager_widget = BudgetLicenseManagerScreen()
                    if hasattr(self, '_body_host'):
                        self._body_host.clear_widgets()
                        self._body_host.add_widget(self.manager_widget)
                except Exception as e:
                    if hasattr(self, '_body_host'):
                        self._body_host.clear_widgets()
                        failed = SectionCard('SHV Budget Licensing Error', 'The APK hit an initialization error while opening this module.')
                        failed.add_widget(make_label(str(e), color=RED, height=dp(72)))
                        retry_btn = make_button('Retry', GREEN)
                        retry_btn.bind(on_release=lambda *_: self.on_pre_enter())
                        failed.add_widget(retry_btn)
                        self._body_host.add_widget(failed)

            Clock.schedule_once(_load_widget, 0)

_original_product_backup_categories = product_backup_categories
def product_backup_categories(product):
    if product == 'SHV Budget':
        return [
            ('Authority Backups', _BUDGET_NS['authority_backup_dir']()),
            ('Full Backups', _BUDGET_NS['full_backup_dir']()),
            ('License-List Backups', _BUDGET_NS['license_list_backup_dir']()),
            ('Revocation Jsons', _BUDGET_NS['revocation_backup_dir']()),
        ]
    return _original_product_backup_categories(product)

_original_product_summary = product_summary
def product_summary(product):
    if product == 'SHV Budget':
        records = budget_license_records()
        pub_path = admin_data_path(_BUDGET_NS.get('PUBLIC_KEY_FILE', 'budget_public.pem'))
        authority_loaded = os.path.exists(pub_path)
        backup_dirs = [_BUDGET_NS['authority_backup_dir'](), _BUDGET_NS['full_backup_dir'](), _BUDGET_NS['license_list_backup_dir'](), _BUDGET_NS['revocation_backup_dir']()]
        active = len([r for r in records if str(r.get('status', 'active')).lower() == 'active'])
        revoked = len([r for r in records if str(r.get('status', '')).lower() == 'revoked'])
        latest_paths = []
        for d in backup_dirs:
            try:
                latest_paths.extend([os.path.join(d, n) for n in os.listdir(d)])
            except Exception:
                pass
        latest = latest_file_from(latest_paths)
        return {
            'product': product,
            'active': active,
            'revoked': revoked,
            'licenses': len(records),
            'authority_loaded': authority_loaded,
            'fingerprint': authority_fingerprint(pub_path),
            'last_backup': file_stamp(latest) if latest else 'Never',
        }
    return _original_product_summary(product)

_original_aggregated_customer_rows = aggregated_customer_rows
def aggregated_customer_rows():
    rows = _original_aggregated_customer_rows()
    overrides = load_customer_overrides()
    for rec in budget_license_records():
        lid = str(rec.get('license_id', '')).strip()
        if not lid:
            continue
        ov = overrides.get(lid, {}) if isinstance(overrides, dict) else {}
        name = str(ov.get('name') or rec.get('customer_name') or rec.get('label') or 'Unnamed Customer').strip()
        contact = str(ov.get('contact') or rec.get('customer_email') or '').strip()
        note = str(ov.get('note') or rec.get('note') or rec.get('customer_note') or '').strip()
        rows.append({
            'license_id': lid,
            'product': 'SHV Budget',
            'tier': str(rec.get('tier', '')).upper(),
            'status': str(rec.get('status', 'active')).upper(),
            'payment': str(rec.get('source', '')).strip(),
            'issued_at': str(rec.get('issued_at', '') or rec.get('created_at', '')).strip(),
            'name': name,
            'contact': contact,
            'note': note,
            'device_code': str(rec.get('device_code', '')).strip(),
        })
    rows.sort(key=lambda r: r.get('issued_at', ''), reverse=True)
    return rows

def _patched_apps_refresh_ui(self, *_):
    self.root_box.clear_widgets()
    self.root_box.add_widget(build_screen_header('Apps', 'Each product keeps its own authority, license list, and revocation lane.', 'licensing', [('Home', 'home')]))
    items = (
        (product_summary('Synapse'), 'synapse_manager', GREEN),
        (product_summary('Casino Tools Pro'), 'casino_manager', PURPLE),
        (product_summary('SHV Budget'), 'budget_manager', BLUE),
    )
    for summary, screen_name, color in items:
        card = SectionCard(summary['product'], f"Authority {'Loaded' if summary['authority_loaded'] else 'Missing'}  •  Fingerprint {summary['fingerprint']}")
        stats = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, height=dp(72))
        stats.add_widget(build_stat_chip(summary['active'], 'Active', color))
        stats.add_widget(build_stat_chip(summary['revoked'], 'Revoked', RED))
        stats.add_widget(build_stat_chip(summary['last_backup'], 'Last Backup', UI_CYAN))
        card.add_widget(stats)
        open_btn = make_button(f"Open {summary['product']}", color)
        open_btn.bind(on_release=lambda *_ , s=screen_name: setattr(self.manager, 'current', s))
        card.add_widget(open_btn)
        self.root_box.add_widget(card)
LicensingAppsScreen.refresh_ui = _patched_apps_refresh_ui
LicensingAppsScreen._patched_apps_refresh_ui = _patched_apps_refresh_ui

def _patched_backup_vault_refresh_ui(self, *_):
    self.root_box.clear_widgets()
    self.root_box.add_widget(build_screen_header('Backup Vault', 'Central vault for authority backups, full backups, license-list backups, and revocation exports.', 'home', [('Licensing', 'licensing')]))
    top = SectionCard('Vault Actions', 'Open product managers to create new backups, then return here to review the latest saved files.')
    for label, screen_name, color in (
        ('Open Synapse Vault', 'synapse_manager', GREEN),
        ('Open Casino Tools Vault', 'casino_manager', PURPLE),
        ('Open SHV Budget Vault', 'budget_manager', BLUE),
    ):
        btn = make_button(label, color)
        btn.bind(on_release=lambda *_ , s=screen_name: setattr(self.manager, 'current', s))
        top.add_widget(btn)
    self.root_box.add_widget(top)
    for product, color in (('Synapse', GREEN), ('Casino Tools Pro', PURPLE), ('SHV Budget', BLUE)):
        pcard = SectionCard(product, 'Latest files across all backup categories for this product.')
        for label, directory in product_backup_categories(product):
            files = []
            try:
                files = [os.path.join(directory, n) for n in os.listdir(directory) if os.path.isfile(os.path.join(directory, n))]
            except Exception:
                files = []
            latest = latest_file_from(files)
            sub = SectionCard(label, f"Count: {len(files)}")
            if latest:
                sub.add_widget(make_label(f"Latest: {os.path.basename(latest)}", height=dp(22)))
                sub.add_widget(make_label(f"Saved: {file_stamp(latest)}  •  Size: {file_size_text(latest)}", color=SUBTEXT, height=dp(22)))
                copy_btn = make_button('Copy Latest Path', color)
                copy_btn.bind(on_release=lambda *_ , p=latest: copy_to_clipboard('Latest backup path', p))
                sub.add_widget(copy_btn)
            else:
                sub.add_widget(make_label('No files yet.', color=SUBTEXT, height=dp(22)))
            pcard.add_widget(sub)
        self.root_box.add_widget(pcard)
BackupVaultScreen.refresh_ui = _patched_backup_vault_refresh_ui
BackupVaultScreen._patched_backup_vault_refresh_ui = _patched_backup_vault_refresh_ui

def _patched_authority_status_refresh_ui(self, *_):
    self.root_box.clear_widgets()
    self.root_box.add_widget(build_screen_header('Authority Status', 'See the active public-key fingerprints and the latest authority backups before you issue licenses.', 'home'))
    syn_pub = file_path(PUBLIC_KEY_FILE)
    ctp_pub = admin_data_path(_CTP_NS.get('PUBLIC_KEY_FILE', 'license_public.pem'))
    bgt_pub = admin_data_path(_BUDGET_NS.get('PUBLIC_KEY_FILE', 'budget_public.pem'))
    items = [
        ('Synapse', syn_pub, authority_backup_dir(), GREEN, 'synapse_manager'),
        ('Casino Tools Pro', ctp_pub, _CTP_NS['authority_backup_dir'](), PURPLE, 'casino_manager'),
        ('SHV Budget', bgt_pub, _BUDGET_NS['authority_backup_dir'](), BLUE, 'budget_manager'),
    ]
    for product, pub_path, backup_dir, color, screen_name in items:
        latest = latest_file_from([os.path.join(backup_dir, n) for n in os.listdir(backup_dir)] if os.path.exists(backup_dir) else [])
        card = SectionCard(product, f"Fingerprint: {authority_fingerprint(pub_path)}")
        card.add_widget(make_label(f"Authority Loaded: {'Yes' if os.path.exists(pub_path) else 'No'}", height=dp(22)))
        card.add_widget(make_label(f"Latest Authority Backup: {file_stamp(latest) if latest else 'Never'}", color=SUBTEXT, height=dp(22)))
        btn = make_button(f"Open {product}", color)
        btn.bind(on_release=lambda *_ , s=screen_name: setattr(self.manager, 'current', s))
        card.add_widget(btn)
        self.root_box.add_widget(card)
AuthorityStatusScreen.refresh_ui = _patched_authority_status_refresh_ui
AuthorityStatusScreen._patched_authority_status_refresh_ui = _patched_authority_status_refresh_ui

try:
    _patch_manager_logging(BudgetLicenseManagerScreen, 'SHV Budget')
except Exception:
    pass

_bgt_confirm_remove, _bgt_perform_remove = _make_local_authority_remove_methods(
    'SHV Budget',
    admin_data_path,
    _BUDGET_NS['PRIVATE_KEY_FILE'],
    _BUDGET_NS['PUBLIC_KEY_FILE'],
)
BudgetLicenseManagerScreen.confirm_remove_local_authority = _bgt_confirm_remove
BudgetLicenseManagerScreen.perform_remove_local_authority = _bgt_perform_remove
_patch_authority_view_with_remove_button(BudgetLicenseManagerScreen, make_button)

_patch_manager_cloud_backup(
    BudgetLicenseManagerScreen,
    'SHV Budget',
    'budget_cloud_backup_config.json',
    admin_data_path,
    {
        'AUTHORITY_BACKUP_FILE': _BUDGET_NS['AUTHORITY_BACKUP_FILE'],
        'LICENSE_LIST_BACKUP_FILE': _BUDGET_NS['LICENSE_LIST_BACKUP_FILE'],
        'FULL_BACKUP_FILE': _BUDGET_NS['FULL_BACKUP_FILE'],
        'build_authority_backup_blob': _BUDGET_NS['build_authority_backup_blob'],
        'build_license_list_backup_blob': _BUDGET_NS['build_license_list_backup_blob'],
        'build_full_backup_blob': _BUDGET_NS['build_full_backup_blob'],
        'parse_secure_backup_blob': _BUDGET_NS['parse_secure_backup_blob'],
    },
)

_original_admin_build = SHVertexAdminPanelApp.build
def _patched_admin_build(self):
    sm = _original_admin_build(self)
    try:
        sm.get_screen('budget_manager')
    except Exception:
        sm.add_widget(BudgetManagerShellScreen(name='budget_manager'))
    return sm
SHVertexAdminPanelApp.build = _patched_admin_build



# ---- Budget fresh-authority override ----
# Budget should use its own separate PEM filenames and start with no preloaded default authority.
_BUDGET_NS['PRIVATE_KEY_FILE'] = 'budget_private.pem'
_BUDGET_NS['PUBLIC_KEY_FILE'] = 'budget_public.pem'

def _budget_fresh_load_existing_keypair():
    priv_path = _BUDGET_NS['file_path'](_BUDGET_NS['PRIVATE_KEY_FILE'])
    pub_path = _BUDGET_NS['file_path'](_BUDGET_NS['PUBLIC_KEY_FILE'])
    if os.path.exists(priv_path) and os.path.exists(pub_path):
        with open(priv_path, 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
        with open(pub_path, 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
        return public_key, private_key
    return None, None


def _budget_fresh_initialize_authority_keypair():
    priv_path = _BUDGET_NS['file_path'](_BUDGET_NS['PRIVATE_KEY_FILE'])
    pub_path = _BUDGET_NS['file_path'](_BUDGET_NS['PUBLIC_KEY_FILE'])
    if os.path.exists(priv_path) or os.path.exists(pub_path):
        raise RuntimeError('Budget authority already exists on this device.')
    public_key, private_key = rsa.newkeys(2048)
    with open(priv_path, 'wb') as f:
        f.write(private_key.save_pkcs1('PEM'))
    with open(pub_path, 'wb') as f:
        f.write(public_key.save_pkcs1('PEM'))
    return public_key, private_key


def _budget_no_default_authority_files():
    return

_BUDGET_NS['load_existing_keypair'] = _budget_fresh_load_existing_keypair
_BUDGET_NS['initialize_authority_keypair'] = _budget_fresh_initialize_authority_keypair
_BUDGET_NS['ensure_default_authority_files'] = _budget_no_default_authority_files

# ═══════════════════════════════════════════════════════════════════════════════
# PERMANENT BOTTOM NAV BAR — injected at the very end after all patches
# Two rows, 4 buttons each. Teal active, slate idle. Rounded edges.
# ALL logic untouched — layout wrappers only.
# ═══════════════════════════════════════════════════════════════════════════════

NAV_BG         = '#03080c'
NAV_ACTIVE_BG  = '#00c8b4'
NAV_ACTIVE_TXT = '#b8860b'
NAV_IDLE_BG    = '#0d1e2b'
NAV_IDLE_TXT   = '#5a8aaa'
NAV_RADIUS     = 12

_NAV_ITEMS = [
    ('HOME',      'home'),
    ('LICNSING', 'licensing'),
    ('VAULT',     'backup_vault'),
    ('ACT',  'activity'),
    ('CUS', 'customers'),
    ('RELEASES',  'releases'),
    ('WEBSITES',  'websites'),
    ('MODULES',   'company_modules'),
]

def _make_bottom_nav(screen_instance, active_name=''):
    from kivy.graphics import Color as _C, RoundedRectangle as _R

    outer = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(106))

    sep = Widget(size_hint_y=None, height=dp(1))
    with sep.canvas:
        _C(rgba=get_color_from_hex('#0f2030'))
        _sr = _R(pos=sep.pos, size=sep.size, radius=[0])
    sep.bind(pos=lambda *_: setattr(_sr, 'pos', sep.pos),
             size=lambda *_: setattr(_sr, 'size', sep.size))

    bg = Widget(size_hint_y=None, height=dp(105))
    with bg.canvas.before:
        _C(rgba=get_color_from_hex(NAV_BG))
        _bgr = _R(pos=bg.pos, size=bg.size, radius=[0])
    bg.bind(pos=lambda *_: setattr(_bgr, 'pos', bg.pos),
            size=lambda *_: setattr(_bgr, 'size', bg.size))

    rows = BoxLayout(
        orientation='vertical', size_hint_y=None, height=dp(105),
        padding=[dp(5), dp(5), dp(5), dp(5)], spacing=dp(4),
    )
    row1 = GridLayout(cols=4, spacing=dp(4), size_hint_y=None, height=dp(44))
    row2 = GridLayout(cols=4, spacing=dp(4), size_hint_y=None, height=dp(44))

    def _nav(t):
        try:
            screen_instance.manager.current = t
        except Exception:
            pass

    for i, (lbl, tgt) in enumerate(_NAV_ITEMS):
        active = (tgt == active_name)
        btn = RoundedButton(
            text=lbl,
            bg_hex=NAV_ACTIVE_BG if active else NAV_IDLE_BG,
            text_color=get_color_from_hex(NAV_ACTIVE_TXT if active else NAV_IDLE_TXT),
            radius=NAV_RADIUS,
            size_hint=(1, 1),
            font_size='16sp',
            bold=True,
        )
        btn.bind(on_release=lambda *_, t=tgt: _nav(t))
        (row1 if i < 4 else row2).add_widget(btn)

    rows.add_widget(row1)
    rows.add_widget(row2)

    # Stack: bg behind rows using FloatLayout trick
    fl = FloatLayout(size_hint_y=None, height=dp(105))
    bg.size_hint = (1, 1)
    bg.size = (100, dp(105))
    bg.pos_hint = {'x': 0, 'y': 0}
    rows.size_hint = (1, 1)
    rows.pos_hint = {'x': 0, 'y': 0}
    fl.add_widget(bg)
    fl.add_widget(rows)

    outer.add_widget(sep)
    outer.add_widget(fl)
    return outer


def _inject_nav(screen_cls, active_name):
    """
    Wrap build_ui to append a permanent bottom nav bar.
    For screens that use build_ui + refresh_ui pattern:
      - build_ui sets up the scroll/root_box structure ONCE
      - refresh_ui only repopulates root_box content
    We wrap build_ui so the nav bar is added once at build time,
    and the scroll area sits inside a wrapper that already has the nav.
    """
    if getattr(screen_cls, '_nav_bar_injected', False):
        return

    _orig_build = screen_cls.build_ui

    def _nav_build_ui(self, *a, **kw):
        # Run the original build — it calls self.add_widget(...)
        _orig_build(self, *a, **kw)
        if not self.children:
            return
        # Collect everything the original added
        children = list(reversed(self.children))
        self.clear_widgets()
        # Outer wrapper: scrollable content takes all space, nav fixed at bottom
        outer = BoxLayout(orientation='vertical')
        for child in children:
            outer.add_widget(child)
        outer.add_widget(_make_bottom_nav(self, active_name))
        self.add_widget(outer)

    _nav_build_ui.__name__ = 'build_ui'
    _nav_build_ui.__qualname__ = screen_cls.__name__ + '.build_ui'
    screen_cls.build_ui = _nav_build_ui
    screen_cls._nav_build_ui = _nav_build_ui
    screen_cls._nav_bar_injected = True


# Inject nav into every main screen
for _cls, _name in [
    (AdminHomeScreen,                  'home'),
    (LicensingHubScreen,               'licensing'),
    (LicensingAppsScreen,              'apps'),
    (BackupVaultScreen,                'backup_vault'),
    (AuthorityStatusScreen,            'authority_status'),
    (CustomersScreen,                  'customers'),
    (ActivityLogScreen,                'activity'),
    (ReleaseTrackerScreen,             'releases'),
    (DocumentationScreen,              'docs'),
    (CompanyModulesScreen,             'company_modules'),
    (AppDataBackupScreen,              'app_data_backup'),
    (WebsitesScreen,                   'websites'),
    (SynapseManagerShellScreen,        'synapse_manager'),
    (CasinoManagerShellScreen,         'casino_manager'),
    (BudgetManagerShellScreen,         'budget_manager'),
]:
    _inject_nav(_cls, _name)


# ── AdminHomeScreen special handling ─────────────────────────────────────────
# AdminHomeScreen.build_ui creates self.scroll + self.root_box then calls
# self.refresh_ui() which populates root_box. The Clock-scheduled refresh_ui
# calls are safe because they only touch root_box.clear_widgets() / add_widget,
# never self.clear_widgets(). So the wrapper+nav structure survives refreshes.
# No extra patching needed — the _inject_nav wrapper above handles it correctly.

# ── Also import FloatLayout at top level (used above) ────────────────────────
from kivy.uix.floatlayout import FloatLayout

if __name__ == '__main__':
    SHVertexAdminPanelApp().run()
