# Terms of use and disclaimer

AudioTranscriptor is provided under the **Apache License 2.0 + Commons Clause
License Condition v1.0**, not vanilla Apache-2.0. It is **source-available, not
open source**. [LICENSE](LICENSE) contains the Commons Clause condition and the
full, unmodified Apache License 2.0 text. [LICENSE-SUPPLEMENT.md](LICENSE-SUPPLEMENT.md)
is an explanatory licensing guide, not additional or prevailing license terms.
These notes explain use and responsibility in plain language; where they and
the combined license disagree, the combined license prevails.

Personal and professional internal use, including paid work using the app, is
allowed subject to the license, without an automatic royalty. The license does
not grant the right to “Sell”: providing third parties, for a fee or other
consideration, a product or service whose value derives entirely or substantially
from the software's functionality. This definition includes fees for hosting and
consulting/support services related to the software, subject to that same
substantial-value test. Such an offering requires separate permission from the
relevant rights holder(s); contact <https://aversa.design> to discuss it. This is
not a blanket ban on commercial integrations: value-added integrations may be
permitted if they do not meet that definition. Modification and redistribution
are subject to the combined license's conditions, not automatically forbidden.

Project credits: **Antonio Aversa / aversa.design**. Third-party components keep
their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). This
summary does not establish ownership of third-party rights or certify legal
compliance.

The transcripts and translations are generated automatically by artificial-
intelligence models. Treat them as draft output and verify them before use.

## No warranty

The application is provided **"as is"**, without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability, fitness
for a particular purpose, accuracy and non-infringement.

Automatic speech recognition and machine translation are probabilistic. The
transcript can contain wrong words, wrong names, wrong numbers and missing
segments, and the translation can change the meaning of a sentence. You must
review the output before using it.

## No guarantee of security

The software is not certified, audited or hardened. The author does not warrant
that it is free of defects, vulnerabilities or errors, that it resists a
determined attacker, or that it protects data on a computer that is already
compromised. What the code does today is described in [SECURITY.md](SECURITY.md):
that is a description of behaviour, not a security guarantee.

You are responsible for the environment it runs in: operating-system updates,
malware protection, disk encryption, physical access and who can use your user
account. The OpenAI API key is stored in plain text in the settings file (see
[PRIVACY.md](PRIVACY.md)); anyone with access to your account can read it.

Vulnerability reports are welcome and handled on a best-effort basis. There is no
bug bounty and no commitment to fix a reported issue within a given time.

## No support, maintenance or updates

This is a free project, not a service. The author has no obligation to provide
support, assistance, training, configuration, bug fixes, updates, new features,
or compatibility with future versions of Windows, macOS, Python or third-party
libraries. Requests may be left unanswered, and the project may be changed or
discontinued at any time without notice.

The issue tracker is the only channel and it is best-effort: no service level, no
guaranteed response time, no guaranteed fix. Anyone who needs guaranteed support,
maintenance or continuity must not rely on this software.

## Limitation of liability

The software is provided free of charge; no fee is paid for it and no service is
sold with it.

To the maximum extent permitted by law, the author is not liable for any claim,
damage, loss of data, loss of profit, loss of opportunity, business
interruption, professional consequence or other liability arising from the use
of, or inability to use, this software.

This does not exclude or limit liability that cannot be excluded or limited by
applicable law. See "Limits that cannot be excluded" below.

## Correct use

Intended use: producing a first-draft transcript of audio and video that you are
entitled to process, which you then review, correct and export.

The software is not intended for, and must not be relied on for, high-risk or
regulated uses where an error can cause harm or a legal consequence: medical,
legal, safety-critical, financial or employment decisions, surveillance,
biometric identification, or use of the output as evidence without checking it
against the recording. It is a transcription aid, not a certified transcript,
not a professional service and not a substitute for expert review.

## What you are responsible for

- **Consent to record and process.** Recording a conversation and processing
  someone's voice may require their consent and a lawful basis (GDPR, Italian
  rules on recordings). That responsibility is yours.
- **The content you process.** Do not use the app on material you have no right
  to process.
- **Verification.** Do not rely on the transcript alone for legal, medical,
  journalistic, HR or financial decisions. Check it against the recording.
- **Backups and data loss.** Transcripts, edits, settings and exports are stored
  only on your computer. Keep your own copies: the author cannot recover them,
  restore a deleted export or repair a damaged settings file.
- **Build provenance.** If you receive the app from someone else, verify where it
  came from and, where published, its SHA-256 checksum; the author is not
  responsible for modified builds distributed by third parties.
- **Your OpenAI account.** Translation uses your own API key and is billed to your
  account by OpenAI. The author has no access to that account and no control over
  its costs, availability or data handling.
- **Keeping the attribution.** Preserve required license and attribution notices,
  including the Commons Clause notice and [NOTICE](NOTICE), when redistributing
  copies or modifications; comply with Apache's modification-notice requirements.

## Indemnity

To the extent permitted by law, you agree to hold the author harmless from
claims, complaints or proceedings brought by third parties arising from your use
of the software, in particular from recording or processing conversations
without the required consent, or in breach of data-protection law.

## Limits that cannot be excluded

Nothing in these notes excludes or limits liability for wilful misconduct or
gross negligence (dolo o colpa grave, art. 1229 of the Italian Civil Code), for
death or personal injury caused by negligence, or any right granted to you by
mandatory law, including consumer rights.

If any provision of these notes is held invalid or unenforceable, the remaining
provisions stay in force.

## No legal advice

Nothing in this repository or in the application is legal advice. If you plan to
redistribute the app commercially, review the third-party licenses in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) with your own counsel.

## Third-party services

The app talks to Hugging Face (model download) and, if you enable translation,
the OpenAI API. Those services are governed by their own terms and privacy
policies, not by this document, and the author does not control their
availability, pricing or behaviour.

## Changes

These notes and the application may change in future releases. The version you
installed is the one these notes describe.

## Governing law

These notes are governed by the laws of Italy, without prejudice to the mandatory
protections granted to consumers by the law of their country of residence.

## Contact

Use the contact options on <https://aversa.design>. Do not include recordings,
transcripts, API keys or personal information in public reports.
