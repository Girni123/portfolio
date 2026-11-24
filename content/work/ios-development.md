---
title: "IOS Development (Case & MONO)"
year: 2026
category: tech
focus: "Development"
highlight: false
featured: true
order: 30
visible: true
portfolio: main
tags: ["Swift", "IOS Development"]
summary: "Native iOS-Entwicklung: Fokus auf Funktionalität und User Experience."
cover: cover.jpg
cover_alt: "App-Icons von MONO und Case, iOS Development"
framer_url: https://girnstein-david.framer.website/work/ios-development
---

::label Intro

### Native iOS-Entwicklung mit Fokus auf Funktionalität und User Experience.

Ich entwickle native iOS-Apps mit Swift und SwiftUI. Mein Ansatz: Konkrete Alltagsprobleme durch reduzierte Interfaces und solide Software-Architektur lösen. Statt Feature-Creep liegt mein Fokus darauf, native Apple-Frameworks effizient zu nutzen, um stabile und intuitive Anwendungen zu schaffen. _Besonderheit:_ Durch den gezielten Einsatz von AI-Assisted Coding (GPT/Claude) verkürze ich die Time-to-Market drastisch – von der ersten Produktidee zum funktionalen Prototypen in nur einem Tag.

![Screens der iOS-Apps MONO und Case im Überblick](01.jpg)

::label Case

## Case – Visuelle Portionierung von Bildschirmzeit.

**Funktionsbeschreibung:**

**Das Produkt:** MONO ist eine minimalistische Aufgaben-App, die das klassische To-Do-Listen-Konzept aufbricht.

Keine unendlichen Backlogs – die App zwingt den Nutzer, sich auf die _eine_ wichtigste Aufgabe des Tages zu fokussieren.

Diese wird via Widgets prominent auf dem Home- und Lockscreen platziert. Ein integriertes Streak-System visualisiert die Konsistenz und Gamification-Elemente belohnen den täglichen Erfolg.

**Technische Umsetzung:**

**WidgetKit:** Entwicklung von interaktiven Widgets für den Home- und Lockscreen, die Aufgaben direkt als erledigt markieren können, ohne die Haupt-App zu öffnen.

**App Groups:** Einrichtung eines geteilten Daten-Containers, damit die Haupt-App und die Widget-Extensions (die als separate Prozesse laufen) auf denselben Datenbestand (UserDefaults/Core Data) zugreifen können.

**State Management:** Synchronisation des Status zwischen Widget und App. Wenn eine Aufgabe im Widget abgehakt wird, muss mittels WidgetCenter ein Reload getriggert werden, um die Streak in der Haupt-App sofort zu aktualisieren.

**Swift Concurrency:** Nutzung moderner Concurrency-Features für reibungslose Hintergrundaktualisierungen.

![MONO-App: Streak-Kalender und die wichtigste Aufgabe des Tages als Widget](02.jpg)
![Case-App: eine Dose als Zeitkontingent für die Bildschirmzeit](03.jpg)

::label MONO

## Mono – Priorisierung durch radikalen Singular-Fokus.  Weg von 20 ToDo's - Fokus auf die wichtigste Aufgabe des Tages

**Funktionsbeschreibung:**

**Das Produkt:** Case ist eine "Digital Wellbeing"-App, die einen greifbaren Ansatz zur Begrenzung der Handynutzung verfolgt.

Statt abstrakter Zeitlimits nutzt die App die Metapher einer physischen Dose ("Container"). Nutzer legen ein Zeitkontingent für bestimmte Apps fest, das visuell als Objekt in diese Dose gelegt wird.

Ist das Kontingent aufgebraucht, wird der Zugriff gesperrt. Das Ziel: Bewusster Medienkonsum ("Portion Control") statt unsichtbarem Tracking.

**Technische Umsetzung:**

**FamilyControls Framework:** Implementierung der notwendigen Autorisierung, um Zugriff auf die Bildschirmzeit-Einstellungen des Nutzers zu erhalten, ohne die Privatsphäre zu verletzen.

**DeviceActivity API:** Lokale Überwachung der Nutzungsdauer ausgewählter Apps im Hintergrund.

**ManagedSettings (ShieldAction):** Technische Umsetzung der App-Sperre durch ein Overlay (Shield), das sich über die blockierte App legt, sobald das Zeitbudget (Event-Threshold) erreicht ist.

**UI & Haptik:** Nutzung von SwiftUI und Core Haptics, um durch Parallax-Effekte und Vibrations-Feedback die Interaktion mit der "Dose" realistisch zu simulieren, ohne eine aufwendige 3D-Engine zu benötigen.
