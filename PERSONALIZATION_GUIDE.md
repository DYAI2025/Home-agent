# Personalisierungsanleitung - Dein eigener AI Agent

Diese Anleitung zeigt dir, wie du den Voice AI Agent mit deiner eigenen Stimme und deinem eigenen Avatar personalisieren kannst.

## Übersicht

Das System unterstützt jetzt vollständige Personalisierung:
- ✅ **Eigene Stimme**: Voice Cloning mit ElevenLabs oder Coqui TTS
- ✅ **Eigener Avatar**: Personalisierter Ready Player Me Avatar
- ✅ **Eigene Persönlichkeit**: Anpassbare Sprachstile und Begrüßungen
- ✅ **Mehrsprachig**: Unterstützung für verschiedene Sprachen

## Schnellstart

### 1. Benutzerprofil erstellen

Erstelle eine `user_profile.json` Datei im Projektverzeichnis:

```bash
cp user_profile.example.json user_profile.json
```

### 2. Profil anpassen

Öffne `user_profile.json` und passe die Einstellungen an:

```json
{
  "user_id": "mein_name",
  "display_name": "Max Mustermann",
  "preferred_language": "de",
  "agent_personality": "friendly",
  "use_voice_cloning": true,

  "voice": {
    "voice_provider": "elevenlabs",
    "voice_id": "DEINE_VOICE_ID"
  },

  "avatar": {
    "avatar_url": "https://models.readyplayer.me/DEINE_AVATAR_ID.glb"
  }
}
```

## Voice Cloning einrichten

### Option A: ElevenLabs (Professionell, Cloud-basiert)

**Vorteile:**
- Sehr hohe Stimmqualität
- Schnelle Verarbeitung
- Multi-linguales Voice Cloning

**Kosten:** Ab $5/Monat (Starter Plan)

#### Schritt-für-Schritt:

1. **Konto erstellen**
   - Gehe zu [elevenlabs.io](https://elevenlabs.io)
   - Erstelle ein kostenloses Konto (11,000 Zeichen/Monat)

2. **Stimme klonen**
   - Navigiere zu "VoiceLab" → "Add Voice" → "Instant Voice Cloning"
   - Lade 1-3 Audio-Samples deiner Stimme hoch (min. 1 Minute Gesamtlänge)
   - Tipps für beste Qualität:
     - Ruhige Umgebung
     - Klare Aussprache
     - Verschiedene Satztypen (Fragen, Aussagen)
     - Keine Hintergrundgeräusche

3. **Voice ID kopieren**
   - Klicke auf deine geklonte Stimme
   - Kopiere die Voice ID (z.B. "21m00Tcm4TlvDq8ikWAM")

4. **API Key holen**
   - Gehe zu "Profile Settings" → "API Keys"
   - Generiere einen neuen API Key
   - **Wichtig:** Speichere ihn sicher!

5. **Environment Variable setzen**
   ```bash
   # In .env Datei hinzufügen:
   ELEVENLABS_API_KEY=sk_your_api_key_here
   ELEVENLABS_VOICE_ID=your_voice_id_here
   ```

6. **Profil konfigurieren**
   ```json
   {
     "voice": {
       "voice_provider": "elevenlabs",
       "voice_id": "your_voice_id_here",
       "voice_model": "eleven_multilingual_v2",
       "elevenlabs_stability": 0.5,
       "elevenlabs_similarity_boost": 0.75,
       "elevenlabs_style": 0.0,
       "elevenlabs_use_speaker_boost": true
     }
   }
   ```

7. **Optional Features installieren**
   ```bash
   pip install -r requirements-optional.txt
   ```

### Option B: Coqui TTS (Kostenlos, Lokal)

**Vorteile:**
- Komplett kostenlos
- Läuft lokal (keine Cloud)
- Volle Datenkontrolle

**Nachteile:**
- Größerer Download (~2GB)
- Langsamere Verarbeitung
- Etwas geringere Qualität

#### Installation:

```bash
# Coqui TTS installieren
pip install TTS

# Optional: CUDA für GPU-Beschleunigung
pip install TTS[cuda]
```

#### Voice Cloning:

1. **Audio-Sample vorbereiten**
   - Nimm 1-5 Minuten von deiner Stimme auf
   - Format: WAV oder MP3
   - Ruhige Umgebung, klare Aussprache
   - Speichere als `my_voice.wav` im Projektordner

2. **Profil konfigurieren**
   ```json
   {
     "voice": {
       "voice_provider": "coqui",
       "coqui_voice_file": "./my_voice.wav",
       "coqui_language": "de"
     }
   }
   ```

**Hinweis:** Die Coqui-Integration ist derzeit ein Platzhalter. Für volle Funktionalität ist eine erweiterte Implementierung erforderlich.

### Option C: OpenAI TTS (Standard)

Falls du kein Voice Cloning verwenden möchtest:

```json
{
  "voice": {
    "voice_provider": "openai",
    "voice_id": "nova",
    "voice_model": "tts-1"
  }
}
```

Verfügbare OpenAI Stimmen:
- `alloy` - Neutral, ausgewogen
- `echo` - Männlich, klar
- `fable` - Britisch, artikuliert
- `onyx` - Männlich, tief
- `nova` - Weiblich, warm (empfohlen für Deutsch)
- `shimmer` - Weiblich, hell

## Avatar personalisieren

### Ready Player Me Avatar erstellen

1. **Avatar erstellen**
   - Gehe zu [readyplayer.me/avatar](https://readyplayer.me/avatar)
   - Erstelle deinen Avatar:
     - Foto hochladen für automatische Generierung
     - Oder manuell anpassen
   - Wähle Kleidung, Frisur, Accessoires

2. **Avatar URL kopieren**
   - Nach der Erstellung: "View Avatar" → "Download"
   - Kopiere die GLB URL (z.B. `https://models.readyplayer.me/65abc123.glb`)

3. **Im Profil eintragen**
   ```json
   {
     "avatar": {
       "avatar_url": "https://models.readyplayer.me/DEINE_ID.glb",
       "pose": "standing",
       "background": "#1e1e2f",
       "auto_rotate": true
     }
   }
   ```

### Eigene GLB-Datei verwenden

Falls du eine eigene 3D-Modell-Datei hast:

```json
{
  "avatar": {
    "avatar_url": "file:///pfad/zu/deinem/avatar.glb",
    "pose": "standing"
  }
}
```

## Persönlichkeit anpassen

### Agent-Persönlichkeit

Wähle einen Stil für deinen Agenten:

```json
{
  "agent_personality": "friendly"
}
```

Optionen:
- `friendly` - Freundlich und hilfsbereit
- `professional` - Professionell und effizient
- `casual` - Locker und entspannt

### Begrüßung personalisieren

```json
{
  "greeting_message": "Hallo! Ich bin Max, dein persönlicher Assistent. Wie kann ich dir heute helfen?"
}
```

### Sprache einstellen

```json
{
  "preferred_language": "de"
}
```

Unterstützte Sprachen: `de`, `en`, `es`, `fr`, `it`, etc.

## Vollständiges Beispiel

Hier ist ein vollständig konfiguriertes Profil:

```json
{
  "user_id": "max_mueller",
  "display_name": "Max Müller",
  "preferred_language": "de",
  "greeting_message": "Hallo! Ich bin Max, dein KI-Assistent. Lass uns loslegen!",
  "agent_personality": "friendly",
  "use_voice_cloning": true,

  "voice": {
    "voice_provider": "elevenlabs",
    "voice_id": "21m00Tcm4TlvDq8ikWAM",
    "voice_model": "eleven_multilingual_v2",
    "elevenlabs_stability": 0.6,
    "elevenlabs_similarity_boost": 0.8,
    "elevenlabs_style": 0.1,
    "elevenlabs_use_speaker_boost": true,
    "speaking_rate": 1.0,
    "pitch": 1.0,
    "volume": 1.0
  },

  "avatar": {
    "avatar_url": "https://models.readyplayer.me/65f7a8c9b1234567.glb",
    "pose": "standing",
    "background": "#2a1f3d",
    "auto_rotate": true,
    "custom_animations": null
  }
}
```

## System starten

Nachdem du dein Profil konfiguriert hast:

```bash
# 1. Dependencies installieren (falls noch nicht geschehen)
pip install -r requirements-optional.txt

# 2. System starten
./start_all.sh

# Oder einzeln:
npm start                 # Frontend
python main.py dev        # Agent mit deinem Profil
```

Der Agent lädt automatisch dein Profil aus `user_profile.json`.

## Profil zur Laufzeit ändern

Du kannst das Profil auch zur Laufzeit aktualisieren:

```python
from voice_ai_agent.utils.voice_profile_manager import VoiceProfileManager

# Profil laden
manager = VoiceProfileManager()

# Stimme ändern
manager.update_voice_settings(
    voice_provider="elevenlabs",
    voice_id="neue_voice_id"
)

# Avatar ändern
manager.update_avatar_settings(
    avatar_url="https://models.readyplayer.me/neue_id.glb"
)
```

## Troubleshooting

### ElevenLabs funktioniert nicht

**Problem:** "ElevenLabs API key not found"
- **Lösung:** Stelle sicher, dass `ELEVENLABS_API_KEY` in der `.env` Datei gesetzt ist

**Problem:** Voice klingt verzerrt
- **Lösung:** Passe die Einstellungen an:
  ```json
  "elevenlabs_stability": 0.7,
  "elevenlabs_similarity_boost": 0.6
  ```

### Avatar lädt nicht

**Problem:** Avatar wird nicht angezeigt
- **Lösung:**
  - Überprüfe die URL (muss `.glb` enden)
  - Teste die URL im Browser
  - Stelle sicher, dass die URL öffentlich zugänglich ist

### Profil wird nicht geladen

**Problem:** "No user profile found"
- **Lösung:**
  - Stelle sicher, dass `user_profile.json` im Projektroot liegt
  - Überprüfe JSON-Syntax mit `python -m json.tool user_profile.json`

### Performance-Probleme

**Problem:** TTS ist langsam
- **Lösung für ElevenLabs:** Reduziere `similarity_boost` auf 0.5
- **Lösung für Coqui:** Nutze GPU-Beschleunigung oder wechsle zu OpenAI/ElevenLabs

## Best Practices

1. **Voice Samples**:
   - Mindestens 1 Minute klare Aufnahmen
   - Verschiedene Emotionen und Satztypen
   - Ruhige Umgebung ohne Echo

2. **Profil-Backup**:
   ```bash
   cp user_profile.json user_profile.backup.json
   ```

3. **Kosten im Blick behalten**:
   - ElevenLabs: Überwache dein Character-Limit
   - OpenAI TTS: ~$15 per 1M Zeichen

4. **Sicherheit**:
   - API Keys niemals in Git committen
   - Nutze `.env` für Secrets
   - `user_profile.json` kann persönliche Daten enthalten

## Support & Weiterentwicklung

Für Fragen und Issues:
- [GitHub Issues](https://github.com/DYAI2025/Home-agent/issues)
- Dokumentation: `README.md` und `CLAUDE.md`

## Nächste Schritte

Nach der Personalisierung kannst du:
- Weitere Features in `integrated_agent.py` anpassen
- Eigene Sprachkommandos hinzufügen
- Memory-Systeme für deine Präferenzen nutzen
- MongoDB für persistente Speicherung konfigurieren

Viel Erfolg mit deinem personalisierten AI Agenten! 🎉
