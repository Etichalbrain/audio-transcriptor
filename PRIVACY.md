# Privacy and data handling

AudioTranscriptor is a local desktop application. It has no account system, no
telemetry, no analytics, no crash reporting and no automatic update check. The
author of the app does not receive your audio, your transcripts or any usage
data.

Everything below describes what the application does with your files, based on
the code in this repository.

## At a glance

| Data | Where it goes | When |
| --- | --- | --- |
| Audio and video files | Stay on your computer | Always |
| Italian transcript and edits | Stay on your computer | Always |
| Transcript text for translation | Sent to the OpenAI API | Only when you click **Translate to English** |
| Whisper model | Downloaded from Hugging Face | First transcription with a given model |
| Settings and OpenAI API key | Local settings file on your computer | When you save Settings |
| Exported TXT / SRT / DOCX | The folder you choose | When you export |
| Usage statistics, telemetry | Not collected | Never |

## Transcription stays local

Audio and video are decoded and transcribed on your machine by
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) with the CTranslate2
engine. No audio ever leaves the computer.

The first transcription with a model downloads that model from the Hugging Face
CDN (roughly 0.5 GB for `small`, 1.5 GB for `medium`, 3 GB for `large-v3`). That
request carries the model name and your IP address to Hugging Face; it does not
carry your media. The model is cached on disk and reused offline afterwards.

## Translation is the only upload

Translation is optional. When you press **Translate to English**, the text of the
transcript segments (in batches of 20) is sent to the OpenAI API together with a
translation instruction, using the API key you configured. Audio is never
uploaded. OpenAI processes that text under its own terms and privacy policy:

- <https://openai.com/policies/privacy-policy>
- <https://openai.com/policies/terms-of-use>

If you cannot upload transcript content, do not use the translation feature; the
rest of the app works entirely offline.

## Your OpenAI API key

- The key is stored in the local settings file described below, in plain text
  JSON, because the app has no keychain integration.
- The file is created with owner-only permissions (`0600`) where the operating
  system supports it.
- The key is shown masked in the Settings dialog and is only sent to
  `api.openai.com`.
- Anyone with access to your user account can read the file. If you share the
  computer, remove the key in Settings when you are done, and revoke it at
  <https://platform.openai.com/api-keys> if you suspect it was exposed.

## Where data is stored

Settings (including the API key):

- Windows: `%LOCALAPPDATA%\AudioTranscriptor\settings.json`
- macOS: `~/Library/Application Support/AudioTranscriptor/settings.json`
- Linux: `~/.config/AudioTranscriptor/settings.json`

Whisper model cache:

- Windows: `%USERPROFILE%\.cache\huggingface\hub`
- macOS and Linux: `~/.cache/huggingface/hub`

Exports are written only to the folder selected in Settings or through the
export dialog.

## Deleting your data

1. Remove the key in Settings (or delete the settings file listed above).
2. Delete the exports you created.
3. Delete the model cache folder if you want to reclaim the disk space.
4. Uninstall the application (`Settings → Apps` on Windows, or drag the app to the
   Trash on macOS), then delete the settings folder listed above.

There is no server-side copy of your data to delete, because none is ever
created.

## Your responsibilities

Transcription and translation process other people's voices. Depending on where
you live, recording and processing a conversation may require the consent of the
people involved (in Italy, for example, the GDPR and the rules on recording
conversations). You are the data controller for the files you process; the
author of the application is not a processor and never receives them.

Do not use the app to process material you are not allowed to process.

## Contact

For privacy questions, use the contact options on <https://aversa.design>.
Do not post recordings, transcripts, API keys or personal information in public
issues. The author cannot delete files stored on your device or content sent
directly by you to OpenAI; manage those copies locally or with that provider.
