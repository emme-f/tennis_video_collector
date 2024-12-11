from googleapiclient.discovery import build
import sqlite3
from datetime import datetime
import isodate
import os
from dotenv import load_dotenv

load_dotenv()

# Configurazione API
API_KEY = os.environ.get("API_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


# Funzione per connettersi al database
def connetti_db(nome_db="TennisVideos.db"):
    conn = sqlite3.connect(nome_db)
    return conn


# Funzione per cercare video
def cerca_video(query, max_results=50, published_after=None):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    ricerca = (
        youtube.search()
        .list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            publishedAfter=published_after,  # Filtra per data
        )
        .execute()
    )

    risultati = []
    for item in ricerca.get("items", []):
        video_data = {
            "video_id": item["id"]["videoId"],
            "titolo": item["snippet"]["title"],
            "descrizione": item["snippet"]["description"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
            "data_pubblicazione": item["snippet"]["publishedAt"],
        }
        risultati.append(video_data)
    return risultati


def recupera_dettagli_video(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    dettagli = (
        youtube.videos().list(part="contentDetails,statistics", id=video_id).execute()
    )

    if not dettagli["items"]:
        return None  # Nessun dato trovato

    dettagli_video = dettagli["items"][0]
    content_details = dettagli_video["contentDetails"]
    statistics = dettagli_video.get("statistics", {})

    # Calcolo della durata in secondi
    durata_iso = content_details.get("duration", "PT0S")
    durata_secondi = int(isodate.parse_duration(durata_iso).total_seconds())

    return {
        "durata": durata_secondi,
        "view_count": int(statistics.get("viewCount", 0)),
        "like_count": int(statistics.get("likeCount", 0)),
        "comment_count": int(statistics.get("commentCount", 0)),
    }


# Salva i video nel database
def salva_video(conn, video):
    try:
        with conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO video (video_id, titolo, descrizione, url, thumbnail, data_pubblicazione)
                VALUES (:video_id, :titolo, :descrizione, :url, :thumbnail, :data_pubblicazione)
            """,
                video,
            )
    except Exception as e:
        print(f"Errore nel salvataggio: {e}")


# Salva una scansione
def salva_scansione(conn, tipo):
    with conn:
        conn.execute(
            """
            INSERT INTO scansioni (tipo, data)
            VALUES (?, ?)
        """,
            (tipo, datetime.utcnow()),
        )


# Recupera l'ultima data di scansione
def ultima_data_scansione(conn, tipo):
    cursore = conn.cursor()
    cursore.execute(
        """
        SELECT data FROM scansioni
        WHERE tipo = ?
        ORDER BY data DESC
        LIMIT 1
    """,
        (tipo,),
    )
    risultato = cursore.fetchone()
    return risultato[0] if risultato else None


# Esegui una scansione
def esegui_scansione(query, tipo="full"):
    conn = connetti_db()
    if tipo == "delta":
        published_after = ultima_data_scansione(conn, tipo)
    else:
        published_after = None

    videos = cerca_video(query, published_after=published_after)
    for video in videos:
        salva_video(conn, video)

    # Salva la scansione corrente
    salva_scansione(conn, tipo)
    conn.close()
    print(f"Scansione {tipo} completata con {len(videos)} video raccolti.")


# Esecuzione modalità FULL
esegui_scansione("tennis serve drill", tipo="full")

# Esecuzione modalità DELTA
# esegui_scansione("tennis serve drill", tipo="delta")
