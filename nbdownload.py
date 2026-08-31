import argparse
import io
import socket
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image


class Book:
    def __init__(self, book_id, cookie=None, referer=None):
        self.id = str(book_id)
        self.cookie = cookie
        self.referer = referer or "https://www.nb.no/"
        self.failed_pages = []

        self.url_template = (
            "https://www.nb.no/services/image/resolver?"
            "url_ver=geneza&"
            "urn=URN:NBN:no-nb_digibok_{book_id}_{page}&"
            "maxLevel=5&"
            "level=5&"
            "col={col}&"
            "row={row}&"
            "resX=9999&"
            "resY=9999&"
            "tileWidth=1024&"
            "tileHeight=1024&"
            "pg_id={page_nr}"
        )

        self.output_dir = Path(f"{self.id}_pages")
        self.output_dir.mkdir(exist_ok=True)

    @staticmethod
    def page_name(page_nr):
        if isinstance(page_nr, int):
            return str(page_nr).zfill(4)
        return str(page_nr)

    def request_tile(self, page, page_nr, col, row):
        url = self.url_template.format(
            book_id=self.id,
            page=page,
            page_nr=page_nr,
            col=col,
            row=row,
        )

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": self.referer,
            "Accept": "image/*,*/*;q=0.8",
        }

        if self.cookie:
            headers["Cookie"] = self.cookie

        for attempt in range(1, 6):
            try:
                request = urllib.request.Request(url, headers=headers)

                with urllib.request.urlopen(request, timeout=30) as response:
                    data = response.read()

                image = Image.open(io.BytesIO(data))
                image.load()
                return image.convert("RGB")

            except urllib.error.HTTPError as error:
                # NB also uses these responses when a requested tile/page
                # is outside the available image grid.
                if error.code in (400, 403, 404):
                    return None

                print(
                    f"  HTTP {error.code} on tile {col},{row} "
                    f"- attempt {attempt}/5"
                )

            except (
                ConnectionResetError,
                TimeoutError,
                urllib.error.URLError,
                socket.timeout,
                ssl.SSLError,
            ) as error:
                print(
                    f"  connection error on tile {col},{row} "
                    f"- attempt {attempt}/5: {error}"
                )

            if attempt < 5:
                time.sleep(3)

        return False

    def load_existing_page(self, page):
        path = self.output_dir / f"{page}.jpg"

        if not path.exists():
            return None

        try:
            image = Image.open(path)
            image.load()
            print(f"[EXISTS] {page}")
            return image.convert("RGB")
        except Exception:
            print(f"[BAD FILE] {page}, downloading again")
            return None

    def mark_failed(self, page, reason=None):
        if page not in self.failed_pages:
            self.failed_pages.append(page)

        if reason:
            print(f"[FAILED] {page}: {reason}")
        else:
            print(f"[FAILED] {page}")

    def download_page(self, page_nr):
        page = self.page_name(page_nr)

        existing = self.load_existing_page(page)
        if existing is not None:
            return existing

        print(f"\nReading page {page}...")
        tiles = {}

        # Detect columns from the first row.
        col = 0
        while True:
            image = self.request_tile(page, page_nr, col, 0)

            if image is False:
                self.mark_failed(page, f"tile {col},0 failed after retries")
                return None

            if image is None:
                break

            tiles[(col, 0)] = image
            print(f"  column {col} found ({image.width}x{image.height})")
            col += 1
            time.sleep(0.25)

        cols = col
        if cols == 0:
            print(f"[skip] {page}: no tiles")
            return None

        # Detect rows from the first column.
        row = 1
        while True:
            image = self.request_tile(page, page_nr, 0, row)

            if image is False:
                self.mark_failed(page, f"tile 0,{row} failed after retries")
                return None

            if image is None:
                break

            tiles[(0, row)] = image
            print(f"  row {row} found ({image.width}x{image.height})")
            row += 1
            time.sleep(0.25)

        rows = row
        print(f"  grid: {cols} x {rows}")

        # Download all remaining tiles.
        for row in range(rows):
            for col in range(cols):
                if (col, row) in tiles:
                    continue

                image = self.request_tile(page, page_nr, col, row)

                if image is False:
                    self.mark_failed(page, f"tile {col},{row} failed after retries")
                    return None

                if image is None:
                    self.mark_failed(page, f"missing tile {col},{row}")
                    return None

                tiles[(col, row)] = image
                time.sleep(0.25)

        widths = [tiles[(col, 0)].width for col in range(cols)]
        heights = [tiles[(0, row)].height for row in range(rows)]
        total_width = sum(widths)
        total_height = sum(heights)

        full_page = Image.new("RGB", (total_width, total_height), "white")

        y = 0
        for row in range(rows):
            x = 0
            for col in range(cols):
                image = tiles[(col, row)]
                full_page.paste(image, (x, y))
                x += image.width
            y += tiles[(0, row)].height

        output_path = self.output_dir / f"{page}.jpg"
        full_page.save(output_path, "JPEG", quality=92)

        print(f"[OK] {page}: {total_width}x{total_height}")
        return full_page

    def download_book(self, start, end, include_cover=True):
        requested_pages = []

        if include_cover:
            requested_pages.append("C1")

        requested_pages.extend(range(start, end + 1))

        if include_cover:
            requested_pages.append("C3")

        # Download missing pages. Existing JPEGs are reused automatically.
        for page_nr in requested_pages:
            self.download_page(page_nr)

        # Build the PDF from every successfully saved requested page.
        pdf_images = []

        for page_nr in requested_pages:
            page = self.page_name(page_nr)
            path = self.output_dir / f"{page}.jpg"

            if not path.exists():
                continue

            try:
                image = Image.open(path)
                image.load()
                pdf_images.append(image.convert("RGB"))
            except Exception:
                print(f"[BAD FILE] {page}")

        if not pdf_images:
            print("\nNo pages available for PDF.")
            return

        pdf_path = Path(f"{self.id}.pdf")
        pdf_images[0].save(
            pdf_path,
            "PDF",
            save_all=True,
            append_images=pdf_images[1:],
            resolution=150,
        )

        print()
        print(f"PDF saved: {pdf_path.resolve()}")
        print(f"Pages included: {len(pdf_images)}")

        if self.failed_pages:
            print()
            print("Pages that failed:")
            print(", ".join(self.failed_pages))
            print("Run the same command again to retry only missing pages.")


def main():
    parser = argparse.ArgumentParser(
        description="Download NB.no page tiles and combine them into a PDF."
    )
    parser.add_argument("book_id", help="NB digibok ID")
    parser.add_argument("--start", type=int, default=1, help="First numbered page")
    parser.add_argument("--end", type=int, required=True, help="Last numbered page to try")
    parser.add_argument("--cookie-file", help="Plain-text file containing the Cookie header value")
    parser.add_argument("--referer", help="URL of the book's nb.no item page")
    parser.add_argument("--no-cover", action="store_true", help="Do not request C1/C3 covers")
    args = parser.parse_args()

    cookie = None
    if args.cookie_file:
        cookie = Path(args.cookie_file).expanduser().read_text().strip()

    book = Book(args.book_id, cookie=cookie, referer=args.referer)
    book.download_book(
        args.start,
        args.end,
        include_cover=not args.no_cover,
    )


if __name__ == "__main__":
    main()
