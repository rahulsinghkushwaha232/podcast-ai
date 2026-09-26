import logging
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
RESULT_CACHE = {}
CACHE_TTL_SECONDS = 600
POPULAR_QUERIES = (
    "tech",
    "comedy",
    "news",
    "true crime",
    "business",
    "health",
    "education",
)
CACHE_EXECUTOR = ThreadPoolExecutor(max_workers=4)
REFRESHING_QUERIES = set()
INSTANT_RESULTS = {
    "podcast": [
        {
            "id": "instant-podcast-1",
            "title": "PodcastAI Picks",
            "description": "PodcastAI Picks by PodcastAI",
            "publisher": "PodcastAI",
            "episodes": 0,
            "image_url": "",
            "topics": ["Podcast"],
            "external_url": "https://podcasts.apple.com/",
        }
    ],
    "tech": [
        {
            "id": "instant-tech-1",
            "title": "Hard Fork",
            "description": "Hard Fork by The New York Times",
            "publisher": "The New York Times",
            "episodes": 100,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/9c/4f/0e/9c4f0e0b-6b11-4d9f-98c2-0d2f7a4e5fcb/mza_13516432599882622535.jpg/600x600bb.jpg",
            "topics": ["Technology"],
            "external_url": "https://podcasts.apple.com/us/podcast/hard-fork/id1528594034",
        },
        {
            "id": "instant-tech-2",
            "title": "The Vergecast",
            "description": "The Vergecast by The Verge",
            "publisher": "The Verge",
            "episodes": 500,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/21/8e/8f/218e8f4b-a4f7-32c2-8b0a-2a7d4f1d0a4e/mza_11524812913990541053.jpg/600x600bb.jpg",
            "topics": ["Technology"],
            "external_url": "https://podcasts.apple.com/us/podcast/the-vergecast/id430333725",
        },
    ],
    "comedy": [
        {
            "id": "instant-comedy-1",
            "title": "SmartLess",
            "description": "SmartLess by Jason Bateman, Sean Hayes, Will Arnett",
            "publisher": "SmartLess",
            "episodes": 250,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/2b/4e/cb/2b4ecb7a-6ef3-9a72-9b1b-70d7d6d9d1e4/mza_15509385225969447656.jpg/600x600bb.jpg",
            "topics": ["Comedy"],
            "external_url": "https://podcasts.apple.com/us/podcast/smartless/id1521578868",
        }
    ],
    "news": [
        {
            "id": "instant-news-1",
            "title": "The Daily",
            "description": "The Daily by The New York Times",
            "publisher": "The New York Times",
            "episodes": 2000,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/6e/4f/4d/6e4f4db6-8c1c-9ab5-c78d-13e83c9e1bc8/mza_16712821197810084163.jpg/600x600bb.jpg",
            "topics": ["News"],
            "external_url": "https://podcasts.apple.com/us/podcast/the-daily/id1200361736",
        }
    ],
    "business": [
        {
            "id": "instant-business-1",
            "title": "The Diary Of A CEO",
            "description": "The Diary Of A CEO by Steven Bartlett",
            "publisher": "Steven Bartlett",
            "episodes": 400,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/0c/25/2f/0c252f21-29ab-fb1e-8cc9-5b2b7ec5f2b6/mza_11811791588790595339.jpg/600x600bb.jpg",
            "topics": ["Business"],
            "external_url": "https://podcasts.apple.com/us/podcast/the-diary-of-a-ceo-with-steven-bartlett/id1291423644",
        }
    ],
    "health": [
        {
            "id": "instant-health-1",
            "title": "Huberman Lab",
            "description": "Huberman Lab by Andrew Huberman",
            "publisher": "Andrew Huberman",
            "episodes": 200,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/7d/2e/0b/7d2e0b3f-2a4b-5f8b-9d7a-4e1f0b8c2d6a/mza_10500000000000000000.jpg/600x600bb.jpg",
            "topics": ["Health"],
            "external_url": "https://podcasts.apple.com/us/podcast/huberman-lab/id1545953110",
        }
    ],
    "education": [
        {
            "id": "instant-education-1",
            "title": "Stuff You Should Know",
            "description": "Stuff You Should Know by iHeartPodcasts",
            "publisher": "iHeartPodcasts",
            "episodes": 1000,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/4e/4f/7e/4e4f7e0c-5b2a-8d1f-9c7e-3a6b2d5f0e8a/mza_10000000000000000000.jpg/600x600bb.jpg",
            "topics": ["Education"],
            "external_url": "https://podcasts.apple.com/us/podcast/stuff-you-should-know/id278981407",
        }
    ],
    "true crime": [
        {
            "id": "instant-true-crime-1",
            "title": "Crime Junkie",
            "description": "Crime Junkie by audiochuck",
            "publisher": "audiochuck",
            "episodes": 400,
            "image_url": "https://is1-ssl.mzstatic.com/image/thumb/Podcasts126/v4/2a/8f/1b/2a8f1b7c-6d3e-9a4b-8c2f-5e1d0b7a3f6c/mza_10000000000000000001.jpg/600x600bb.jpg",
            "topics": ["True Crime"],
            "external_url": "https://podcasts.apple.com/us/podcast/crime-junkie/id1322200189",
        }
    ],
}


@app.route("/")
def home():
    return frontend()


@app.route("/app")
def frontend():
    response = send_from_directory(FRONTEND_DIR, "index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/recommend", methods=["POST"])
def recommend():
    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query", "")).strip().lower()

    if not query:
        return jsonify({"error": "Query not provided"}), 400

    try:
        instant = INSTANT_RESULTS.get(query)
        if instant:
            RESULT_CACHE[query] = {"created_at": time.time(), "results": instant}
            if query not in REFRESHING_QUERIES:
                REFRESHING_QUERIES.add(query)
                CACHE_EXECUTOR.submit(refresh_query, query)
            return jsonify(instant)

        cached = RESULT_CACHE.get(query)
        if cached and time.time() - cached["created_at"] < CACHE_TTL_SECONDS:
            return jsonify(cached["results"])

        encoded_query = urllib.parse.quote(query)
        url = f"https://itunes.apple.com/search?term={encoded_query}&media=podcast&limit=10"
        response = requests.get(
            url,
            headers={"User-Agent": "PodcastAI/1.0"},
            timeout=(5, 30),
        )
        response.raise_for_status()
        search_results = response.json().get("results", [])

        recommendations = []
        for item in search_results:
            try:
                genres = item.get("genres") or []
                if isinstance(genres, list) and genres:
                    topics = [genres[0]]
                else:
                    topics = ["Podcast"]

                recommendations.append(
                    {
                        "id": str(item.get("collectionId", "")),
                        "title": item.get("collectionName", ""),
                        "description": (
                            f"{item.get('collectionName', '')} by {item.get('artistName', '')}"
                        ),
                        "publisher": item.get("artistName", ""),
                        "episodes": item.get("trackCount", 0),
                        "image_url": item.get("artworkUrl600") or item.get("artworkUrl100"),
                        "topics": topics,
                        "external_url": item.get("collectionViewUrl", ""),
                    }
                )
            except Exception as exc:
                logging.exception("Failed to parse podcast item: %s", exc)
                continue

        RESULT_CACHE[query] = {
            "created_at": time.time(),
            "results": recommendations,
        }
        return jsonify(recommendations)
    except requests.RequestException as exc:
        logging.exception("iTunes API request failed: %s", exc)
        return jsonify({"error": "Failed to fetch podcast recommendations"}), 500
    except Exception as exc:
        logging.exception("Unexpected error in /recommend: %s", exc)
        return jsonify({"error": "Internal server error"}), 500


def refresh_query(query):
    try:
        encoded_query = urllib.parse.quote(query)
        response = requests.get(
            f"https://itunes.apple.com/search?term={encoded_query}&media=podcast&limit=10",
            headers={"User-Agent": "PodcastAI/1.0"},
            timeout=(3, 8),
        )
        response.raise_for_status()
        items = response.json().get("results", [])
        refreshed = []
        for item in items:
            refreshed.append(
                {
                    "id": str(item.get("collectionId", "")),
                    "title": item.get("collectionName", ""),
                    "description": f"{item.get('collectionName', '')} by {item.get('artistName', '')}",
                    "publisher": item.get("artistName", ""),
                    "episodes": item.get("trackCount", 0),
                    "image_url": item.get("artworkUrl600") or item.get("artworkUrl100"),
                    "topics": [
                        (item.get("genres") or ["Podcast"])[0]
                    ],
                    "external_url": item.get("collectionViewUrl", ""),
                }
            )
        if refreshed:
            RESULT_CACHE[query] = {"created_at": time.time(), "results": refreshed}
    except requests.RequestException:
        logging.warning("Background refresh timed out for %s", query)
    finally:
        REFRESHING_QUERIES.discard(query)


def warm_cache():
    for query in POPULAR_QUERIES:
        try:
            with app.test_request_context(
                "/recommend",
                method="POST",
                json={"query": query},
            ):
                recommend()
            logging.info("Warmed podcast cache for %s", query)
        except Exception:
            logging.exception("Failed to warm podcast cache for %s", query)


if __name__ == "__main__":
    # Keep the standalone process single-instance and stable when launched by
    # VS Code tasks or from a detached terminal.
    app.run(
        debug=False,
        use_reloader=False,
        threaded=True,
        host="localhost",
        port=5000,
    )
