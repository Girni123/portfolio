---
title: "NFC Verification Service"
year: 2026
category: tech
focus: "Development"
highlight: true
featured: true
order: 20
visible: true
portfolio: main
tags: ["Echtheitsverifikation", "Software as a Service"]
summary: ""
cover: cover.jpg
cover_alt: "Person"
framer_url: https://girnstein-david.framer.website/work/nfc-verification-service
---

::label Intro

> Du siehst bei deinen Freunden ein tolles Kleidungsstück. "Hey woher hast du den diese Hose?" - "Ou keine Ahnung glaube von H&M".
> Und wie finde ich jetzt diese eine schwarze H&M Hose, warscheinlich garnicht.

Kleidung ist heute oft ein „stummes“ Produkt – Informationen über Herkunft, Echtheit oder Storytelling gehen nach dem Kauf meist verloren. Basierend auf den Forschungsergebnissen meiner Bachelor-Thesis habe ich ein System entwickelt, das physische Modeartikel durch NFC-Technologie mit ihrem digitalen Zwilling („Digital Twin“) verknüpft.

Das Ziel: Eine absolut hürdenfreie User Experience. Anstatt mühsam QR-Codes zu scannen oder zusätzliche Apps zu installieren, genügt ein einfaches Annähern des Smartphones an ein im Textil integriertes Element. (z.B. unter dem Logo)

Dieser „Tap“ öffnet sofort den Zugang zu der Produktseite, exklusiven Inhalten, Nachhaltigkeitsdaten und digitalen Services der Marke. So wird das Kleidungsstück zum langfristigen Kommunikationskanal zwischen Brand und Community

Außerdem lassen sich Kleidungsstücke so auf ihre Echtheit überprüfen und können so als Fälschungssicher deklariert werden.

![](01.jpg)

::label Kryptografie

## Mit NFC Chips zum kryptografischen Sicherheitslevel

Für die technische Umsetzung setze ich auf den **NXP NTAG 424 DNA**. Im Gegensatz zu Standard-NFC-Chips, die lediglich statische Links speichern, berechnet dieser Chip bei jedem Scanvorgang direkt auf der Hardware eine AES-128-Verschlüsselung.

**Der technische Prozess:** Durch die „Secure Unique NFC Message“ (SUN) generiert der Chip bei jedem Kontakt einen dynamischen, einmaligen Code, der als CMAC (Cipher-based Message Authentication Code) an die URL angehängt wird. Mein Backend-System – basierend auf **AWS Lambda und DynamoDB** – entschlüsselt diesen Wert in Echtzeit und validiert den internen Zählerstand des Chips. Nur bei mathematischer Übereinstimmung wird die Echtheit bestätigt. Dieser Schutz gegen Replay-Attacken verlagert die gesamte Sicherheitskomplexität in die Cloud, während die Interaktion für den Endnutzer maximal simpel bleibt

![](02.jpg)
![](03.jpg)

::label UX

## Tap-to-Verify: UX-Strategie für die Modeindustrie

Die technische Tiefe der kryptografischen Prüfung bleibt für den Nutzer vollständig im Hintergrund. Die Interaktion nutzt die nativen „Background Tag Reading“-Funktionen moderner Betriebssysteme. Nach der Validierung landet der Nutzer auf einer dynamischen Landingpage:

**Echtheits-Garantie:** Bei Erfolg entfaltet sich das Marken-Storytelling mit transparenten Einblicken in Materialien und Produktion.

**Proaktiver Schutz:** Erkennt das System einen Manipulationsversuch (z. B. einen kopierten statischen Link), wird der Nutzer sofort gewarnt.

Diese fälschungssichere Basis ermöglicht zudem die Integration von **Web3-Assets**: Jedem physischen Artikel kann ein individueller NFT zugeordnet werden, der direkt nach der Verifizierung in das Wallet des Käufers übertragen wird. Damit schaffe ich ein neues Level an digitalem Besitz und Vertrauen am Point of Sale.

![](04.jpg)

### Tech-Stack im Überblick

**Hardware:** NXP NTAG 424 DNA (ISO/IEC 14443-4).

**Cloud & Backend:** AWS Lambda, API Gateway, DynamoDB.

**Frontend & Data:** Streamlit (für das Produktions-Dashboard), Python

**Security:** AES-128 Cryptography, SUN (Secure Unique NFC) Authentifizierung
