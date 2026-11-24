---
title: "Office Shrimp | Mac App"
year: 2025
category: tech
focus: "Development"
highlight: false
featured: true
order: 50
visible: true
portfolio: main
tags: ["App Development", "MacOS"]
summary: ""
cover: cover.jpg
cover_alt: "App-Icon von Office Shrimp: ein orangefarbener Shrimp"
link: "Office Shrimp | Waitlist | https://office-shrimp.girnstein.studio"
framer_url: https://girnstein-david.framer.website/work/office-shrimp
---

::label The Mission

### Schluss mit dem krummen Rücken – ein Gesundheits-Assistent, der tatsächlich Spaß macht.

Office Shrimp ist eine native macOS-App, die in der **Menüleiste** lebt und dem Nutzer spielerisch zu einer besseren Körperhaltung verhilft.

Das Ziel war es, ein Tool zu schaffen, das nicht wie ein medizinischer Wecker nervt, sondern durch Charme und Witz motiviert. Die App trackt Haltung, Trinkpausen und Bildschirmzeit im Hintergrund und meldet sich nur dann, wenn es wirklich nötig ist. So wird Gesundheit nahtlos in den Workflow integriert, ohne die Produktivität zu stören.

Dadurch ist der kleine Shrimp entstanden, ein kleines süßes Tier, und wer kann diesen großen Augen schon widerstehen?

![Meet Shrimp – Your little Mac Companion, Illustration des Shrimps](01.jpg)

::label Gamification

## Vom "Junior Krill" zum CEO – Motivation durch spielerischen Fortschritt.

Das Alleinstellungsmerkmal von Office Shrimp ist der Verzicht auf den klassischen "Zeigefinger".

Stattdessen setzt die App auf ein RPG-ähnliches Level-System: Nutzer sammeln XP (Erfahrungspunkte) für gute Haltung und Pausen, um ihren Charakter visuell weiterzuentwickeln.

Kombiniert mit einem hochwertigen "Deep Sea"-Interface im Dark Mode und smarten Features wie dem "Oase-Modus" zur Entspannung, schafft die App eine emotionale Bindung, die langfristig zu gesünderen Gewohnheiten am Schreibtisch führt.

Durch die XP kann dein kleiner Shrimp auf der Karriereleiter weiter nach oben Kletter und wenn du dich immer an den Shrimp hältst kann er sogar zu CEO heranwachsen.

![Office-Shrimp-Fenster mit Fortschrittsringen für Haltung, Weitsicht, Trinken und Blinzeln](02.jpg)
![Einstellungen von Office Shrimp auf dem macOS-Desktop](03.jpg)

::label Tech Stack

## Native Performance und modernes State-Management mit 100% SwiftUI.

Technisch basiert die App auf dem modernen MenuBarExtra API von macOS, um sich ressourcenschonend in das System einzufügen. Eine besondere Herausforderung lag im komplexen State-Management: Ein zentraler TimerService (injiziert via Dependency Injection) dient als "Single Source of Truth", damit die UI-Ringe auch nach dem Schließen des Fensters frame-genau und synchron bleiben. Für das Interface kamen benutzerdefinierte Canvas-Zeichnungen und mathematisch berechnete Vektoren zum Einsatz, um das responsive "C-Shape"-Design der Fortschrittsbalken zu realisieren.
