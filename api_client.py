import argparse
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def api_call(method):

    bodies = {
        "POST": {
            "name": "demo",
            "status": "new",
            "note": "temporary"
        },
        "PUT": {
            "name": "demo",
            "status": "replaced"
        },
        "PATCH": {
            "status": "ready"
        }
    }

    body = bodies.get(method)

    url = "http://127.0.0.1:8765" + (
        "/items" if method == "POST" else "/items/1"
    )

    request = Request(
        url,
        data=json.dumps(body).encode() if body else None,
        method=method,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urlopen(request, timeout=5) as response:
            code = response.status
            text = response.read().decode()

    except HTTPError as error:
        code = error.code
        text = error.read().decode()

    print(f"{method} {url} -> {code} {text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "method",
        choices=["GET", "POST", "PUT", "PATCH", "DELETE"]
    )

    args = parser.parse_args()

    api_call(args.method)
