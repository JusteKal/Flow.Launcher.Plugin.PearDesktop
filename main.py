# -*- coding: utf-8 -*-
"""Flow Launcher plugin : contrôle Pear Desktop from this plugin « API Server ».
No external dependance."""
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

APP_ID = "flowlauncher"
ICON = "Images\\app.png"


# ---------------------------------------------------------------- config
def settings_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~/.config")
    d = os.path.join(base, "FlowLauncher", "Settings", "Plugins", "PearDesktop")
    try:
        os.makedirs(d, exist_ok=True)
        return d
    except OSError:
        return os.path.dirname(os.path.abspath(__file__))


TOKEN_FILE = os.path.join(settings_dir(), "token.txt")


def load_token():
    try:
        with open(TOKEN_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def save_token(token):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(token)


class Pear:
    def __init__(self, settings):
        s = settings or {}
        self.base = "http://%s:%s" % (s.get("host") or "127.0.0.1", s.get("port") or "26538")
        self.token = load_token()

    def _raw(self, method, path, body=None, auth=True, timeout=3):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        if auth and self.token:
            req.add_header("Authorization", "Bearer " + self.token)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8", "replace")
            return json.loads(raw) if raw.strip() else {}

    def authenticate(self):
        # Pear affiche une pop-up « autoriser » : on attend la réponse de l'utilisateur
        res = self._raw("POST", "/auth/" + APP_ID, auth=False, timeout=60)
        self.token = res.get("accessToken", "")
        if not self.token:
            raise RuntimeError("Aucun token reçu")
        save_token(self.token)

    def call(self, method, path, body=None, timeout=3):
        if not self.token:
            self.authenticate()
        try:
            return self._raw(method, path, body, timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                self.authenticate()
                return self._raw(method, path, body, timeout=timeout)
            raise



# ---------------------------------------------------------------- pochette
COVER_DIR = os.path.join(settings_dir(), "covers")


def get_cover(url):
    """Télécharge la pochette (cache local) et renvoie son chemin, sinon l'icône par défaut."""
    if not url or not url.startswith("http"):
        return ICON
    # miniature 60x60 par défaut -> version plus grande
    url = re.sub(r"=w\d+-h\d+.*$", "=w256-h256-l90-rj", url)
    try:
        os.makedirs(COVER_DIR, exist_ok=True)
        path = os.path.join(COVER_DIR, hashlib.sha1(url.encode()).hexdigest() + ".jpg")
        if not os.path.exists(path):
            with urllib.request.urlopen(url, timeout=3) as r, open(path, "wb") as f:
                f.write(r.read())
            # on ne garde que les 30 pochettes les plus récentes
            files = sorted((os.path.join(COVER_DIR, n) for n in os.listdir(COVER_DIR)),
                           key=os.path.getmtime, reverse=True)
            for old in files[30:]:
                try:
                    os.remove(old)
                except OSError:
                    pass
        return path
    except Exception:  # noqa: BLE001
        return ICON


# ---------------------------------------------------------------- commandes
# (mots-clés, titre, sous-titre, méthode, chemin, corps)
COMMANDS = [
    ("play pause toggle", "Lecture / Pause", "Basculer la lecture", "POST", "/api/v1/toggle-play", None),
    ("play lecture", "Lecture", "Reprendre la lecture", "POST", "/api/v1/play", None),
    ("pause", "Pause", "Mettre en pause", "POST", "/api/v1/pause", None),
    ("next suivant skip", "Piste suivante", "Passer à la piste suivante", "POST", "/api/v1/next", None),
    ("previous precedent prev back", "Piste précédente", "Revenir à la piste précédente", "POST", "/api/v1/previous", None),
    ("like aimer", "J'aime", "Aimer / retirer le j'aime", "POST", "/api/v1/like", None),
    ("dislike", "Je n'aime pas", "Marquer comme non apprécié", "POST", "/api/v1/dislike", None),
    ("shuffle aleatoire", "Aléatoire", "Activer/désactiver la lecture aléatoire", "POST", "/api/v1/shuffle", None),
    ("repeat repetition boucle", "Répéter", "Changer le mode de répétition", "POST", "/api/v1/switch-repeat", {"iteration": 1}),
    ("mute muet", "Muet", "Activer/désactiver le son", "POST", "/api/v1/toggle-mute", None),
    ("fullscreen plein ecran", "Plein écran", "Basculer le plein écran", "POST", "/api/v1/fullscreen", None),
    ("forward avance +10", "Avancer de 10 s", "Avance rapide", "POST", "/api/v1/go-forward", {"seconds": 10}),
    ("rewind recule -10", "Reculer de 10 s", "Retour rapide", "POST", "/api/v1/go-back", {"seconds": 10}),
]


def action(title, sub, method, path, body=None, **extra):
    r = {
        "Title": title,
        "SubTitle": sub,
        "IcoPath": ICON,
        "JsonRPCAction": {"method": "run", "parameters": [method, path, json.dumps(body)]},
    }
    r.update(extra)
    return r


def fmt_time(sec):
    sec = int(sec or 0)
    return "%d:%02d" % (sec // 60, sec % 60)


def parse_time(txt):
    try:
        if ":" in txt:
            m, s = txt.split(":", 1)
            return int(m) * 60 + int(s)
        return int(txt)
    except ValueError:
        return None


def now_playing(pear):
    song = pear.call("GET", "/api/v1/song")
    if not song or not song.get("title"):
        return None
    paused = song.get("isPaused", False)
    state = "⏸" if paused else "▶"
    dur = song.get("songDuration")
    elapsed = song.get("elapsedSeconds")
    pos = " · %s / %s" % (fmt_time(elapsed), fmt_time(dur)) if dur else ""
    return action(
        "%s %s" % (state, song.get("title")),
        "%s%s — Entrée : lecture/pause" % (song.get("artist", ""), pos),
        "POST", "/api/v1/toggle-play",
        IcoPath=get_cover(song.get("imageSrc")),
    )



# ---------------------------------------------------------------- recherche
def _find_items(node, out):
    if isinstance(node, dict):
        r = node.get("musicResponsiveListItemRenderer")
        if isinstance(r, dict):
            out.append(r)
            return
        for v in node.values():
            _find_items(v, out)
    elif isinstance(node, list):
        for v in node:
            _find_items(v, out)


def _find_key(node, key):
    if isinstance(node, dict):
        if isinstance(node.get(key), str):
            return node[key]
        for v in node.values():
            r = _find_key(v, key)
            if r:
                return r
    elif isinstance(node, list):
        for v in node:
            r = _find_key(v, key)
            if r:
                return r
    return None


def _col_text(col):
    try:
        runs = col["musicResponsiveListItemFlexColumnRenderer"]["text"]["runs"]
        return "".join(r.get("text", "") for r in runs)
    except (KeyError, TypeError):
        return ""


def _generic(node, out):
    """Repli : tout dict possédant videoId + title (chaînes)."""
    if isinstance(node, dict):
        if isinstance(node.get("videoId"), str) and isinstance(node.get("title"), str):
            out.append({"id": node["videoId"], "title": node["title"],
                        "sub": str(node.get("artist") or node.get("author") or "")})
        for v in node.values():
            _generic(v, out)
    elif isinstance(node, list):
        for v in node:
            _generic(v, out)


def parse_search(data):
    items, res, seen = [], [], set()
    _find_items(data, items)
    for it in items:
        vid = (it.get("playlistItemData") or {}).get("videoId") or _find_key(it, "videoId")
        cols = it.get("flexColumns") or []
        title = _col_text(cols[0]) if cols else ""
        sub = _col_text(cols[1]) if len(cols) > 1 else ""
        if vid and title and vid not in seen:
            seen.add(vid)
            res.append({"id": vid, "title": title, "sub": sub})
    if not res:
        fallback = []
        _generic(data, fallback)
        for r in fallback:
            if r["id"] not in seen:
                seen.add(r["id"])
                res.append(r)
    return res[:10]


def search_results(pear, text):
    data = pear.call("POST", "/api/v1/search", {"query": text}, timeout=10)
    out = []
    for r in parse_search(data):
        out.append({
            "Title": r["title"],
            "SubTitle": (r["sub"] + " — " if r["sub"] else "") + "Entrée : lire · Maj+Entrée : file d'attente",
            "IcoPath": ICON,
            "JsonRPCAction": {"method": "play_now", "parameters": [r["id"]]},
            "ContextData": [r["id"], r["title"]],
        })
    return out


# ---------------------------------------------------------------- requête
def query(q, settings):
    pear = Pear(settings)
    q = (q or "").strip()
    results = []

    if q.lower() == "auth":
        return [action("Autoriser Flow Launcher dans Pear Desktop",
                       "Une pop-up s'ouvre dans Pear : cliquez sur « Autoriser »",
                       "AUTH", "")]

    words0 = q.split(None, 1)
    if words0 and words0[0].lower() in ("search", "s", "find", "rechercher"):
        text = words0[1].strip() if len(words0) > 1 else ""
        if len(text) < 2:
            return [{"Title": "Rechercher un morceau",
                     "SubTitle": "Ex. : pear search daft punk around the world", "IcoPath": ICON}]
        try:
            res = search_results(pear, text)
        except urllib.error.HTTPError:
            return [action("Autorisation requise", "Entrée : demander l'accès à Pear Desktop", "AUTH", "")]
        except Exception as e:  # noqa: BLE001
            return [{"Title": "Recherche impossible", "SubTitle": str(e), "IcoPath": ICON}]
        return res or [{"Title": "Aucun résultat pour « %s »" % text, "SubTitle": "", "IcoPath": ICON}]

    try:
        np = now_playing(pear)
    except urllib.error.HTTPError:
        return [action("Autorisation requise", "Entrée : demander l'accès à Pear Desktop", "AUTH", "")]
    except Exception:
        return [{
            "Title": "Pear Desktop est injoignable",
            "SubTitle": "Lancez Pear et activez Plugins > API Server (port %s)" % (settings or {}).get("port", "26538"),
            "IcoPath": ICON,
        }]
    if np:
        results.append(np)

    words = q.lower().split()
    # pear vol 40
    if words and words[0] in ("vol", "volume", "v"):
        if len(words) > 1 and words[1].isdigit():
            v = max(0, min(100, int(words[1])))
            results.insert(0, action("Volume : %d %%" % v, "Régler le volume", "POST", "/api/v1/volume", {"volume": v}))
        else:
            try:
                cur = pear.call("GET", "/api/v1/volume").get("state", "?")
            except Exception:
                cur = "?"
            results.insert(0, {"Title": "Volume actuel : %s %%" % cur,
                               "SubTitle": "Tapez « pear vol 40 » pour le changer", "IcoPath": ICON})
        return results

    # pear seek 1:30
    if words and words[0] in ("seek", "goto"):
        t = parse_time(words[1]) if len(words) > 1 else None
        if t is not None:
            results.insert(0, action("Aller à %s" % fmt_time(t), "Positionner la lecture", "POST", "/api/v1/seek-to", {"seconds": t}))
        else:
            results.insert(0, {"Title": "Seek", "SubTitle": "Ex. : pear seek 1:30", "IcoPath": ICON})
        return results

    for keys, title, sub, method, path, body in COMMANDS:
        if not words or all(any(k.startswith(w) for k in keys.split()) for w in words):
            results.append(action(title, sub, method, path, body))
    return results


# ---------------------------------------------------------------- action
def run(method, path, body, settings):
    pear = Pear(settings)
    try:
        if method == "AUTH":
            pear.authenticate()
            msg("Pear Desktop", "Autorisation accordée ✔")
            return
        pear.call(method, path, json.loads(body) if body and body != "null" else None)
    except Exception as e:  # noqa: BLE001
        msg("Pear Desktop", "Erreur : %s" % e)


def play_now(video_id, settings):
    pear = Pear(settings)
    try:
        pear.call("POST", "/api/v1/queue", {"videoId": video_id, "insertPosition": "INSERT_AFTER_CURRENT_VIDEO"})
        time.sleep(0.8)
        pear.call("POST", "/api/v1/next")
    except Exception as e:  # noqa: BLE001
        msg("Pear Desktop", "Erreur : %s" % e)


def enqueue(video_id, position, settings):
    try:
        Pear(settings).call("POST", "/api/v1/queue", {"videoId": video_id, "insertPosition": position})
        msg("Pear Desktop", "Ajouté à la file d'attente")
    except Exception as e:  # noqa: BLE001
        msg("Pear Desktop", "Erreur : %s" % e)


def context_menu(data):
    if not data or len(data) < 2:
        return []
    vid, title = data[0], data[1]
    return [
        {"Title": "Lire ensuite", "SubTitle": title, "IcoPath": ICON,
         "JsonRPCAction": {"method": "enqueue", "parameters": [vid, "INSERT_AFTER_CURRENT_VIDEO"]}},
        {"Title": "Ajouter en fin de file", "SubTitle": title, "IcoPath": ICON,
         "JsonRPCAction": {"method": "enqueue", "parameters": [vid, "INSERT_AT_END"]}},
    ]


def msg(title, sub):
    print(json.dumps({"method": "Flow.Launcher.ShowMsg", "parameters": [title, sub, ICON]}))


def main():
    req = json.loads(sys.argv[1])
    method = req.get("method")
    params = req.get("parameters", [])
    settings = req.get("settings", {})
    if method == "query":
        print(json.dumps({"result": query(params[0] if params else "", settings)}))
    elif method == "run":
        run(params[0], params[1], params[2], settings)
    elif method == "play_now":
        play_now(params[0], settings)
    elif method == "enqueue":
        enqueue(params[0], params[1], settings)
    elif method == "context_menu":
        print(json.dumps({"result": context_menu(params[0] if params else None)}))


if __name__ == "__main__":
    main()
