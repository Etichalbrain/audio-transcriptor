AudioTranscriptor: what to know before using it
===============================================

License: Apache License 2.0 + Commons Clause License Condition v1.0:
source-available code, NOT open source and not plain Apache-2.0.
LICENSE.txt contains the Commons Clause and the full, unaltered Apache text.
LICENSE-SUPPLEMENT.md is an explanatory guide, not additional or overriding
conditions. Credits: Antonio Aversa / aversa.design. Keep the attributions
and notices required by the license; see NOTICE.

Personal use and internal professional use, including paid work done with the
app, is permitted within the license, with no automatic royalty.
The license does not grant the right to "Sell": providing to third parties,
for a fee or other consideration, a product or service whose value derives
entirely or substantially from the software's functionality. This includes
fees for hosting and for consulting/support services related to the software,
always subject to the same substantial-value test. Such offerings require
separate permission from the relevant rights holders: contact
https://aversa.design.
This is not a general ban on every commercial integration: integrations that
add value may be allowed. Modification and redistribution remain subject to
the terms of the license; they are not prohibited outright.
Third-party components keep their own licenses. This summary is not legal
advice nor a certification of compliance.

YOUR FILES STAY ON THIS COMPUTER
- Audio and video are never uploaded to the internet: transcription runs
  locally with Whisper.
- The first use of a model downloads the model from Hugging Face (about
  0.5 GB for "small"); nothing from your files is sent.
- Translation is the only feature that leaves the computer: when you press
  "Translate to English", the transcript text is sent to the OpenAI API with
  your key. If you do not want that, do not use translation.
- No telemetry, no account, no usage statistics.

DATA ON DISK
- Settings and OpenAI key: %LOCALAPPDATA%\AudioTranscriptor\settings.json
- Downloaded models: %USERPROFILE%\.cache\huggingface\hub
- Exports: the folder you choose.
To remove everything: uninstall the app and delete the two folders above.

RESPONSIBILITY
Automatic transcription can get words, names and numbers wrong: always check
the result before using it. If you record a conversation, you are responsible
for the consent of the people involved and for the handling of the data.

No guarantee of security: the program is not certified or verified and is not
guaranteed to be free of defects or vulnerabilities. The OpenAI key is saved
in plain text in the settings file. Protecting the computer and the account
(updates, antivirus, physical access) is up to you.

No obligation of support or updates: the project is free and is not a
service. There is no obligation to reply, fix errors, update the program or
keep it compatible with future versions of Windows, macOS or libraries.
Reports are welcome, but with no guaranteed timeframe.

Use at your own risk, within the limits of the law: the program is provided
"as is" and is not intended for high-risk uses (medical, legal, safety) nor
to replace professional verification. Keeping backups of transcripts and
exports is up to you. If a third party makes a claim over how you used the
program, for example for a recording made without consent, you are
responsible for it and you hold the author harmless. Mandatory statutory
rights and liability for wilful misconduct or gross negligence remain
unaffected. Full text in TERMS.md.

Complete documents in the application folder:
  LICENSE.txt            Apache 2.0 + Commons Clause v1.0 (full texts)
  LICENSE-SUPPLEMENT.md  explanatory guide to the license
  NOTICE                 how to credit the author
  PRIVACY.md             what data leaves the computer and when
  TERMS.md               disclaimer of liability and terms of use
  THIRD_PARTY_NOTICES.md licenses of third-party components (Qt, Whisper...)
  licenses\              full texts of LGPL-3.0, GPL-3.0, Apache-2.0

Project: https://aversa.design
