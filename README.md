# NB.no-Downloader

Improved fork of [akselsd/NB.no-Downloader](https://github.com/akselsd/NB.no-Downloader).

This version keeps the original tile-based download method, but adds authenticated sessions, macOS/Python 3 support, automatic retries, resume support and more reliable PDF creation.

## Setup on macOS

```bash
brew install python
/opt/homebrew/bin/python3 -m venv nbvenv
source nbvenv/bin/activate
pip install -r requirements.txt
```

## Find the Book ID

Open the book on nb.no, then open Developer Tools → Network and find a `default.jpg` request.

Example:

```text
URN:NBN:no-nb_digibok_2020050448518_0153
```

The Book ID is:

```text
2020050448518
```

## Cookie for logged-in books

If the book requires login, find a working `default.jpg` request in Developer Tools and copy the value of the `Cookie` request header.

Create a plain-text file:

```bash
nano nb_cookie.txt
```

Paste only the cookie value, without `Cookie:`.

Do not share this file. It contains your active NB session.

## Run

```bash
python nbdownload.py BOOK_ID \
  --start 1 \
  --end LAST_PAGE \
  --cookie-file nb_cookie.txt \
  --referer 'BOOK_NB_URL'
```

Example:

```bash
python nbdownload.py 2020050448518 \
  --start 1 \
  --end 250 \
  --cookie-file nb_cookie.txt \
  --referer 'https://www.nb.no/items/97425fae2080c80dcf13a989f44ecd1d'
```

Downloaded pages are saved in `BOOK_ID_pages/` and the final PDF is saved as `BOOK_ID.pdf`.

If the script stops, run the same command again. Existing pages are reused and shown as `[EXISTS]`.

Network failures are retried up to 5 times. Pages that still fail are skipped and reported at the end.

Use only on material you have the right to access and download.
