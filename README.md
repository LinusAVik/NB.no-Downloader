# NB.no Downloader – Norwegian National Library PDF Downloader

**Updated and tested against NB.no in August 2026.**

Python downloader for books and scanned documents from **NB.no**, the **Nasjonalbiblioteket (National Library of Norway / Norwegian National Library)**. It downloads NB image tiles, reconstructs high-resolution pages, resumes interrupted downloads, and creates a PDF.

Improved fork of [akselsd/NB.no-Downloader](https://github.com/akselsd/NB.no-Downloader). The original script was last updated years ago and did not work out-of-the-box for the logged-in NB.no book I tested in 2026.

This fork keeps the original tile-based image method, but updates the downloader for current NB.no use.

## Features

- NB.no / Nasjonalbiblioteket book downloader written in Python
- Tested successfully on NB.no in August 2026
- Supports logged-in NB sessions using a cookie file and Referer
- Keeps the tile-based downloader instead of relying on `/full/` image requests
- Reconstructs high-resolution book pages from NB image tiles
- Downloads scanned pages and combines them into a PDF
- Retries temporary connection resets and network errors
- Resume support: already downloaded pages are reused with `[EXISTS]`
- Continues past failed pages and reports them at the end
- Works with modern Python 3 on macOS and Windows
- Creates the final PDF directly with Pillow

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

Open the book on nb.no, then open Developer Tools → Network and find a `default.jpg` request.

Example:

```text
URN:NBN:no-nb_digibok_2020050448518_0153
```

The NB.no Book ID is:

```text
2020050448518
```

## Cookie for logged-in NB.no books

If the book requires login, find a working `default.jpg` request in Developer Tools and copy the value of the `Cookie` request header.

Create a plain-text file called `nb_cookie.txt` in the same folder as the script and paste only the cookie value, without `Cookie:`.

Do not share this file. It contains your active NB session.

## Download an NB.no book

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
