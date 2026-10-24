AudioTranscriptor: Wichtige Hinweise vor der Nutzung
====================================================

Lizenz: Apache License 2.0 + Commons Clause License Condition v1.0:
Quelltext verfügbar (source-available), NICHT Open Source und nicht einfach
Apache-2.0. LICENSE.txt enthält die Commons Clause und den vollständigen,
unveränderten Apache-Text. LICENSE-SUPPLEMENT.md ist eine erläuternde
Anleitung, keine zusätzlichen oder vorrangigen Bedingungen. Urheber:
Antonio Aversa / aversa.design. Behalten Sie die von der Lizenz geforderten
Urhebernennungen und Hinweise bei; siehe NOTICE.

Die persönliche und die interne berufliche Nutzung, auch für bezahlte Arbeiten
mit der App, ist im Rahmen der Lizenz erlaubt, ohne automatische Lizenzgebühr.
Die Lizenz gewährt nicht das Recht zum "Sell": Dritten gegen Entgelt oder eine
andere Gegenleistung ein Produkt oder eine Dienstleistung bereitzustellen,
deren Wert vollständig oder im Wesentlichen aus den Funktionen der Software
stammt. Dazu gehören Entgelte für Hosting sowie für Beratung/Support im
Zusammenhang mit der Software, stets nach demselben Kriterium des
wesentlichen Werts. Für solche Angebote ist eine gesonderte Erlaubnis der
jeweiligen Rechteinhaber erforderlich: Kontakt über https://aversa.design.
Das ist kein generelles Verbot jeder kommerziellen Integration:
Integrationen mit Mehrwert können zulässig sein. Änderung und Weitergabe
unterliegen weiterhin den Lizenzbedingungen und sind nicht grundsätzlich
verboten.
Komponenten von Drittanbietern behalten ihre eigenen Lizenzen. Diese
Zusammenfassung ist weder Rechtsberatung noch eine Konformitätsbescheinigung.

IHRE DATEIEN BLEIBEN AUF DIESEM COMPUTER
- Audio und Video werden nie ins Internet hochgeladen: Die Transkription
  läuft lokal mit Whisper.
- Bei der ersten Nutzung eines Modells wird das Modell von Hugging Face
  heruntergeladen (etwa 0,5 GB für "small"); von Ihren Dateien wird nichts
  gesendet.
- Die Übersetzung ist die einzige Funktion, die den Computer verlässt: Wenn
  Sie auf "Ins Englische übersetzen" klicken, wird der Text der Transkription
  mit Ihrem Schlüssel an die OpenAI-API gesendet. Wenn Sie das nicht möchten,
  nutzen Sie die Übersetzung nicht.
- Keine Telemetrie, kein Konto, keine Nutzungsstatistiken.

DATEN AUF DER FESTPLATTE
- Einstellungen und OpenAI-Schlüssel:
  %LOCALAPPDATA%\AudioTranscriptor\settings.json
- Heruntergeladene Modelle: %USERPROFILE%\.cache\huggingface\hub
- Exporte: der Ordner, den Sie auswählen.
Um alles zu entfernen: App deinstallieren und die beiden Ordner oben löschen.

VERANTWORTUNG
Die automatische Transkription kann Wörter, Namen und Zahlen falsch erkennen:
Prüfen Sie das Ergebnis immer, bevor Sie es verwenden. Wenn Sie ein Gespräch
aufzeichnen, sind Sie für die Einwilligung der beteiligten Personen und für
die Verarbeitung der Daten verantwortlich.

Keine Sicherheitsgarantie: Das Programm ist weder zertifiziert noch geprüft,
und es wird nicht garantiert, dass es frei von Fehlern oder Schwachstellen
ist. Der OpenAI-Schlüssel wird im Klartext in der Einstellungsdatei
gespeichert. Der Schutz von Computer und Konto (Updates, Virenschutz,
physischer Zugang) liegt bei Ihnen.

Keine Pflicht zu Support oder Updates: Das Projekt ist kostenlos und kein
Dienst. Es besteht keine Pflicht, zu antworten, Fehler zu beheben, das
Programm zu aktualisieren oder mit künftigen Versionen von Windows, macOS
oder von Bibliotheken kompatibel zu halten. Meldungen sind willkommen, aber
ohne garantierte Fristen.

Nutzung auf eigenes Risiko, soweit gesetzlich zulässig: Das Programm wird
"wie besehen" bereitgestellt und ist weder für Anwendungen mit hohem Risiko
(medizinisch, rechtlich, sicherheitsrelevant) noch als Ersatz für eine
fachliche Prüfung gedacht. Die Sicherung von Transkripten und Exporten liegt
bei Ihnen. Wenn ein Dritter wegen Ihrer Nutzung des Programms Ansprüche
erhebt, zum Beispiel wegen einer Aufnahme ohne Einwilligung, haften Sie dafür
und stellen den Autor frei. Zwingende gesetzliche Rechte und die Haftung für
Vorsatz oder grobe Fahrlässigkeit bleiben unberührt. Vollständiger Text in
TERMS.md.

Vollständige Dokumente im Anwendungsordner:
  LICENSE.txt            Apache 2.0 + Commons Clause v1.0 (Volltexte)
  LICENSE-SUPPLEMENT.md  erläuternde Anleitung zur Lizenz
  NOTICE                 wie der Autor zu nennen ist
  PRIVACY.md             welche Daten den Computer wann verlassen
  TERMS.md               Haftungsausschluss und Nutzungsbedingungen
  THIRD_PARTY_NOTICES.md Lizenzen der Drittanbieter-Komponenten (Qt, Whisper...)
  licenses\              Volltexte von LGPL-3.0, GPL-3.0, Apache-2.0

Projekt: https://aversa.design
