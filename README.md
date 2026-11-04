# Weltkarten

Interaktive Karten, erzeugt mit Python/folium, veröffentlicht über GitHub Pages (Jekyll, eigenes Layout ohne externes Theme).

## Neue Karte
1. `weltkarte_lebenserwartung.py` kopieren, oben `SLUG`, `TITLE`, `DESCRIPTION`, `CSV_FILE` anpassen
2. `python <skript>.py` ausführen: schreibt `maps/<slug>.html` und legt `_posts/<datum>-<slug>.md` an
3. `git add . && git commit -m "Neue Karte" && git push`

Die neueste Karte steht groß oben auf der Startseite, ältere als Kacheln darunter (Reihenfolge nach Datum im Post-Dateinamen).

## Struktur
- `_layouts/` Seitenvorlagen, `assets/css/style.css` Design (Hell/Dunkel automatisch)
- `_posts/` ein Post pro Karte, `maps/` die Karten-HTML-Dateien
