import requests
import urllib3

# Disabilita i warning per certificati SSL non validi
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =============================================================================
# CONFIGURAZIONE
# =============================================================================

TARGET_URL = "http://192.168.4.100/dvwa/login.php"   # IP di Metasploitable 2
PATH       = "/"                           # Percorso da testare
TIMEOUT    = 5                             # Secondi prima di rinunciare


# Credenziali per Basic Auth ("None" se non serve)
AUTH = None        # oppure: AUTH = ("username", "password")


# =============================================================================
# COLORI per il terminale (ANSI)
# =============================================================================

VERDE   = "\033[92m"
ROSSO   = "\033[91m"
GIALLO  = "\033[93m"
CIANO   = "\033[96m"
GRIGIO  = "\033[90m"
BOLD    = "\033[1m"
RESET   = "\033[0m"


def colora_status(codice):
    """Restituisce il codice HTTP colorato in base al suo significato."""
    if isinstance(codice, int):
        if 200 <= codice < 300:
            return f"{VERDE}{BOLD}{codice}{RESET}"    # Successo
        elif 300 <= codice < 400:
            return f"{GIALLO}{codice}{RESET}"         # Redirect
        elif 400 <= codice < 500:
            return f"{GIALLO}{BOLD}{codice}{RESET}"   # Errore client
        else:
            return f"{ROSSO}{BOLD}{codice}{RESET}"    # Errore server
    return f"{GRIGIO}{codice}{RESET}"


# =============================================================================
# FUNZIONE PRINCIPALE — invia una singola richiesta HTTP
# =============================================================================

def invia_richiesta(metodo, url, auth, timeout):
    """
    Invia una richiesta HTTP specifica e restituiusce i dettagli della risposta.

    Parametri:
        metodo  — stringa con il verbo HTTP (GET, POST, ecc.)
        url     — URL completo del target
        auth    — tupla (utente, password) o None
        timeout — secondi di attesa massima

    Ritorna:
        dizionario con: metodo, url, status, tempo_ms, errore
    """

    risultato = {
        "metodo":          metodo,
        "url":             url,
        "status":          None,
        "tempo_ms":        None,
        "errore":          None,
    }

    try:
        inizio = __import__("time").time()
        risposta = requests.request(metodo, url)
        fine = __import__("time").time()

        risultato["status"]           = risposta.status_code
        risultato["tempo_ms"]         = round((fine - inizio) * 1000, 1)

    except requests.exceptions.ConnectionError:
        risultato["errore"] = "Connessione rifiutata o host non raggiungibile"
    except requests.exceptions.Timeout:
        risultato["errore"] = f"Timeout dopo {timeout}s"
    except requests.exceptions.RequestException as e:
        risultato["errore"] = str(e)

    return risultato


# =============================================================================
# STAMPA DEI RISULTATI
# =============================================================================

def stampa_risultato(r):
    """Stampa a schermo il risultato di una singola richiesta in modo leggibile."""

    print(f"\n{'─' * 60}")
    print(f"  {CIANO}{BOLD}Metodo  :{RESET} {BOLD}{r['metodo']}{RESET}")
    print(f"  {CIANO}{BOLD}URL     :{RESET} {r['url']}")

    if r["errore"]:
        print(f"  {ROSSO}{BOLD}ERRORE  :{RESET} {r['errore']}")
        return

    print(f"  {CIANO}{BOLD}Status  :{RESET} {colora_status(r['status'])}")
    print(f"  {CIANO}{BOLD}Tempo   :{RESET} {r['tempo_ms']} ms")

# =============================================================================
# RIEPILOGO FINALE
# =============================================================================

def stampa_riepilogo(risultati):
    """Stampa una tabella riassuntiva di tutti i risultati."""

    print(f"\n\n{'═' * 60}")
    print(f"{BOLD}  RIEPILOGO{RESET}")
    print(f"{'═' * 60}")
    print(f"  {'METODO':<12} {'STATUS':<20} {'TEMPO':<10} {'NOTE'}")
    print(f"  {'─'*12} {'─'*20} {'─'*10} {'─'*20}")

    metodi_rischiosi = {"PUT", "DELETE", "TRACE", "PATCH"}

    for r in risultati:
        if r["errore"]:
            status_str = f"{ROSSO}ERRORE{RESET}"
            tempo_str  = "—"
            nota       = r["errore"][:30]
        else:
            status_str = colora_status(r["status"])
            tempo_str  = f"{r['tempo_ms']} ms"

            # Nota: metodo abilitato o bloccato?
            if r["status"] == 405:
                nota = f"{ROSSO}Non abilitato{RESET}"
            elif r["status"] == 501:
                nota = f"{GRIGIO}Non implementato{RESET}"
            elif r["status"] in (401, 403):
                nota = f"{GIALLO}Richiede auth{RESET}"
            elif 200 <= r["status"] < 300:
                if r["metodo"] in metodi_rischiosi:
                    nota = f"{ROSSO}⚠ ABILITATO — RISCHIOSO{RESET}"
                else:
                    nota = f"{VERDE}Abilitato{RESET}"
            else:
                nota = ""

        metodo_fmt = r["metodo"]
        print(f"  {metodo_fmt:<12} {status_str:<20} {tempo_str:<10} {nota}")

    print()

# =============================================================================
# MENU INTERATTIVO
# =============================================================================

def chiedi_configurazione():
    """Chiede all'utente l'URL e i metodi da testare (se in modalità interattiva)."""
    print(f"{CIANO}Configurazione rapida (premi INVIO per usare i valori predefiniti){RESET}\n")

    url_input = input(f"  URL target [{TARGET_URL}{PATH}]: ").strip().lower()
    url = url_input if url_input else TARGET_URL + PATH

    print(f"\n  Metodi disponibili: {', '.join(ALL_METHODS)}")
    metodi_input = input("  Metodi da testare [tutti]: ").strip()
    if metodi_input:
        metodi = [m.strip().upper() for m in metodi_input.split(",")]
    else:
        metodi = list(ALL_METHODS)

    return url, metodi


# =============================================================================
# ELENCO METODI
# =============================================================================

ALL_METHODS = [
    "GET",      # Legge una risorsa
    "POST",     # Crea una nuova risorsa
    "PUT",      # Sostituisce una risorsa esistente
    "DELETE",   # Elimina una risorsa
    "PATCH",    # Modifica parzialmente una risorsa
    "HEAD",     # Come GET ma senza body
    "OPTIONS",  # Chiede quali metodi sono supportati
    "TRACE",    # Echo della richiesta
]


# =============================================================================
# MAIN
# =============================================================================

def main():
    while True:
        print(f"""
    {CIANO}{BOLD}HTTP TESTER{RESET}
    """)

        # Chiedi configurazione all'utente
        url, metodi = chiedi_configurazione()

        print(f"\n{BOLD}  Avvio test su: {CIANO}{url}{RESET}")
        print(f"  Metodi: {', '.join(metodi)}")
        print(f"  Timeout: {TIMEOUT}s\n")

        risultati = []

        # ── Invia una richiesta per ogni metodo ───────────────────────────────────
        for metodo in metodi:
            print(f"  {GRIGIO}→ Invio {metodo}...{RESET}", end="", flush=True)
            r = invia_richiesta(metodo, url, AUTH, TIMEOUT)
            risultati.append(r)
            stampa_risultato(r)

        # ── Riepilogo ─────────────────────────────────────────────────────────────
        stampa_riepilogo(risultati)
 
if __name__ == "__main__":
    main()