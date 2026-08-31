# NB.no Downloader – Authenticated-Access Book PDF Downloader

**Updated and tested against NB.no in August 2026.**

Small Python downloader for **NB.no / Nasjonalbiblioteket** books available through an authenticated browser session but awkward to save as a complete local PDF.

Improved fork of [akselsd/NB.no-Downloader](https://github.com/akselsd/NB.no-Downloader). This fork keeps the original tile-based image method and adds the session handling and reliability needed for the authenticated NB.no case I wanted to solve.

## What it does

- Uses an existing logged-in NB.no session from a cookie file
- Keeps the tile-based downloader instead of relying on `/full/` image requests
- Reconstructs high-resolution book pages from NB image tiles
- Downloads scanned pages and combines them into a PDF
- Retries temporary connection resets and network errors
- Resume support: already downloaded pages are reused with `[EXISTS]`
- Continues past failed pages and reports them at the end
- Works with modern Python 3 on macOS and Windows

This is intentionally a small, focused fork rather than a general-purpose NB.no media downloader.

## Setup on macOS

```bash
brew install python
/opt/homebrew/bin/python3 -m venv nbvenv
source nbvenv/bin/activate
pip install -r requirements.txt
```

## Setup on Windows

Install Python 3 from python.org and make sure Python is added to PATH during installation.

Then open PowerShell or Command Prompt in the folder containing `nbdownload.py`:

```powershell
py -m venv nbvenv
nbvenv\Scripts\activate
pip install -r requirements.txt
```

If `py` is not available, use `python` instead:

```powershell
python -m venv nbvenv
```

## Find the NB.no Book ID

Open the book on nb.no while logged in, then open Developer Tools → Network and find a `default.jpg` request.

Example:

```text
URN:NBN:no-nb_digibok_2020050448518_0153
```

The NB.no Book ID is:

```text
2020050448518
```

## Use your logged-in session

Find a working `default.jpg` request in Developer Tools and copy the value of the `Cookie` request header.

Create a plain-text file called `nb_cookie.txt` in the same folder as the script and paste only the cookie value, without `Cookie:`.

Do not share this file. It contains your active NB session.

## Download the book

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

On Windows PowerShell, the same command can be written on one line:

```powershell
python nbdownload.py 2020050448518 --start 1 --end 250 --cookie-file nb_cookie.txt --referer "https://www.nb.no/items/97425fae2080c80dcf13a989f44ecd1d"
```

Downloaded pages are saved in `BOOK_ID_pages/` and the final PDF is saved as `BOOK_ID.pdf`.

If the script stops, run the same command again. Existing pages are reused and shown as `[EXISTS]`.

Network failures are retried up to 5 times. Pages that still fail are skipped and reported at the end.

**Note:** creating a PDF with the same Book ID overwrites an existing `BOOK_ID.pdf`. Keep a backup if you are running a smaller test after downloading a full book.

Use only on material you are authorized to access and download, and respect applicable copyright law and NB.no usage terms.
