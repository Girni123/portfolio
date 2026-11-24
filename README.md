# portfolio.girnstein.studio

Davids Portfolio als statische Website, gebaut aus einfachen Textdateien. Nachbau des früheren Framer-Portfolios (girnstein-david.framer.website).

## So funktioniert's

- Jedes Projekt ist **eine Datei** in `content/work/<slug>.md`. Oben stehen die Eckdaten (Frontmatter), darunter der Text.
- `build.py` macht daraus die fertige Website in `_site/` (reines Python, nichts zu installieren).
- Bei jedem Push auf `main` baut GitHub Actions die Seite automatisch und veröffentlicht sie. Du kannst Dateien also auch direkt auf github.com bearbeiten.

Lokale Vorschau:

```bash
python3 build.py --serve
```

Dann http://localhost:8000 öffnen.

## Ein Projekt ändern (meist eine Zeile)

```yaml
---
title: "Crosswired Bootshaus"
year: 2025
category: creative          # creative oder tech  -> Filter auf /work/
focus: "Projektmanagement"  # Untertitel-Label, z. B. Development, Design, Produktion & Film
highlight: true             # grünes "Highlight"-Badge auf der Karte
featured: true              # erscheint auf der Startseite unter "Selected Projects"
order: 40                   # Reihenfolge, kleiner = weiter oben
visible: true               # false = Seite wird nicht gebaut (ausgeblendet)
portfolio: main             # welchem Portfolio der Eintrag gehört, mehrere: [main, tech]
tags: ["Projekt Lead", "68 Leuten zu Koordinieren"]
summary: "Kurzer Teaser unter dem Titel"
cover: cover.jpg            # Bild in assets/work/<slug>/
cover_alt: "Bildbeschreibung"
link: "Crosswired Website | https://..."   # optionaler Button im Header
---
```

- **Ausblenden:** `visible: false`
- **Kategorie wechseln:** `category: tech`
- **Reihenfolge:** `order:` anpassen
- **Anderem Portfolio zuordnen:** `portfolio: [main, kreativ]`. Welches Portfolio gebaut wird, steht in `content/site.md` (`portfolio: main`). Ein zweites Portfolio ist später dieselbe Codebasis mit anderem Wert dort.

## Textformat

Normales Markdown (`**fett**`, `_kursiv_`, `[Link](url)`, `## Überschrift`, Listen) plus ein paar Bausteine:

| Zeile | Ergebnis |
| --- | --- |
| `::label Gamification` | kleines Label mit grünem Punkt |
| `> Großer Text` | großer Einleitungstext |
| `::button [Text](https://...)` | Button |
| `::youtube VIDEO-ID` | YouTube-Video, lädt erst nach Klick (Datenschutz). Vorschaubild in `assets/video/<ID>.jpg` |
| Bilder direkt untereinander | werden als Galerie nebeneinander gezeigt |
| `::section Titel \| 01` | Abschnittsüberschrift mit Nummer |
| `::projects featured` | Projektkarten (`all`, `featured`, `highlight`, `tech`, `creative`) |
| `::contact` | Kontakt-Block |
| `::: name` … `:::` | Container mit CSS-Klasse `name` (für Layouts wie `split`, `timeline`, `stats`) |

## Ordner

```
content/site.md        globale Einstellungen (Domain, E-Mail, Social Links)
content/pages/         Startseite, About, Volunteering, Kontakt, Impressum, Work-Übersicht
content/work/          17 Projekte
content/blog/          Blogposts (aktuell 3 Platzhalter aus dem Framer-Template, ausgeblendet)
assets/                Bilder, Schriften, CSS, JS
templates/gs-network.html   Footer-Leiste "Mehr von David Girnstein" (gleich auf allen girnstein.studio-Seiten)
docs/screenshots/      Screenshots Desktop und Mobil
```

## SEO

Canonical-URL, Open Graph und Twitter Cards mit absoluten URLs, JSON-LD (Person `https://cv.girnstein.studio/#person`, `CreativeWork` pro Projekt, `BlogPosting` pro Blogpost, Breadcrumbs), `robots.txt` und `sitemap.xml` werden von `build.py` erzeugt. Das Impressum steht auf `noindex`.
