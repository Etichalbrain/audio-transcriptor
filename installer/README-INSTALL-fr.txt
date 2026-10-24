AudioTranscriptor : ce qu'il faut savoir avant de l'utiliser
============================================================

Licence : Apache License 2.0 + Commons Clause License Condition v1.0 :
code disponible (source-available), PAS open source et pas simplement
Apache-2.0. LICENSE.txt contient la Commons Clause et le texte Apache complet
et inchangé. LICENSE-SUPPLEMENT.md est un guide explicatif, pas des
conditions supplémentaires ou prioritaires. Crédits : Antonio Aversa /
aversa.design. Conservez les attributions et les avis exigés par la licence ;
voir NOTICE.

L'usage personnel et l'usage professionnel interne, y compris pour des
travaux rémunérés réalisés avec l'application, sont autorisés dans le respect
de la licence, sans redevance automatique.
La licence n'accorde pas le droit de "Sell" : fournir à des tiers, contre
paiement ou autre contrepartie, un produit ou un service dont la valeur
provient entièrement ou substantiellement des fonctionnalités du logiciel.
Cela comprend les rémunérations pour l'hébergement et pour le conseil ou
l'assistance liés au logiciel, toujours soumises au même critère de la valeur
substantielle. Pour de telles offres, une autorisation distincte des
titulaires de droits concernés est nécessaire : contactez
https://aversa.design.
Ce n'est pas une interdiction générale de toute intégration commerciale : des
intégrations apportant une valeur ajoutée peuvent être autorisées. La
modification et la redistribution restent soumises aux conditions de la
licence, elles ne sont pas interdites de façon absolue.
Les composants tiers conservent leurs propres licences. Ce résumé n'est ni un
conseil juridique ni une certification de conformité.

VOS FICHIERS RESTENT SUR CET ORDINATEUR
- L'audio et la vidéo ne sont jamais envoyés sur internet : la transcription
  se fait en local avec Whisper.
- La première utilisation d'un modèle télécharge le modèle depuis Hugging
  Face (environ 0,5 Go pour "small") ; rien de vos fichiers n'est envoyé.
- La traduction est la seule fonction qui sort de l'ordinateur : lorsque vous
  cliquez sur "Traduire en anglais", le texte de la transcription est envoyé
  à l'API d'OpenAI avec votre clé. Si vous ne le souhaitez pas, n'utilisez
  pas la traduction.
- Aucune télémétrie, aucun compte, aucune statistique d'utilisation.

DONNÉES SUR LE DISQUE
- Réglages et clé OpenAI :
  %LOCALAPPDATA%\AudioTranscriptor\settings.json
- Modèles téléchargés : %USERPROFILE%\.cache\huggingface\hub
- Exportations : le dossier que vous choisissez.
Pour tout supprimer : désinstallez l'application et supprimez les deux
dossiers ci-dessus.

RESPONSABILITÉ
La transcription automatique peut se tromper sur les mots, les noms et les
chiffres : vérifiez toujours le résultat avant de l'utiliser. Si vous
enregistrez une conversation, vous êtes responsable du consentement des
personnes concernées et du traitement des données.

Aucune garantie de sécurité : le programme n'est ni certifié ni vérifié et
rien ne garantit qu'il soit exempt de défauts ou de vulnérabilités. La clé
OpenAI est enregistrée en clair dans le fichier de réglages. Protéger
l'ordinateur et le compte (mises à jour, antivirus, accès physique) vous
incombe.

Aucune obligation d'assistance ou de mises à jour : le projet est gratuit et
n'est pas un service. Il n'y a aucune obligation de répondre, de corriger les
erreurs, de mettre à jour le programme ou de le maintenir compatible avec les
futures versions de Windows, macOS ou des bibliothèques. Les signalements
sont les bienvenus, mais sans délai garanti.

Utilisation à vos risques, dans les limites de la loi : le programme est
fourni "tel quel" et n'est pas destiné à des usages à haut risque (médical,
juridique, sécurité) ni à remplacer une vérification professionnelle.
Conserver des sauvegardes des transcriptions et des exportations vous
incombe. Si un tiers formule des réclamations au sujet de la façon dont vous
avez utilisé le programme, par exemple pour un enregistrement sans
consentement, vous en répondez et vous garantissez l'auteur contre toute
réclamation. Les droits impératifs prévus par la loi et la responsabilité en
cas de dol ou de faute lourde demeurent. Texte complet dans TERMS.md.

Documents complets dans le dossier de l'application :
  LICENSE.txt            Apache 2.0 + Commons Clause v1.0 (textes complets)
  LICENSE-SUPPLEMENT.md  guide explicatif de la licence
  NOTICE                 comment citer l'auteur
  PRIVACY.md             quelles données sortent de l'ordinateur et quand
  TERMS.md               exclusion de responsabilité et conditions d'utilisation
  THIRD_PARTY_NOTICES.md licences des composants tiers (Qt, Whisper...)
  licenses\              textes complets de LGPL-3.0, GPL-3.0, Apache-2.0

Projet : https://aversa.design
