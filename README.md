# Pear Desktop pour Flow Launcher

Contrôle [Pear Desktop](https://github.com/pear-devs/pear-desktop) depuis [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher).

## Prérequis
1. Pear Desktop : **Plugins > API Server** activé (port par défaut 26538).
2. Flow Launcher avec Python configuré (Paramètres > Python) — aucune librairie à installer.

## Installation
Copiez le dossier `Flow.Launcher.Plugin.PearDesktop` dans
`%APPDATA%\FlowLauncher\Plugins\` puis redémarrez Flow Launcher.

## Première utilisation
Tapez `pear auth` → Entrée, puis cliquez sur **Autoriser** dans la pop-up de Pear.
(Le token est stocké dans `%APPDATA%\FlowLauncher\Settings\Plugins\PearDesktop\token.txt`.)

## Commandes (mot-clé `pear`)
| Saisie | Action |
|---|---|
| `pear` | Morceau en cours (avec sa pochette) + toutes les commandes |
| `pear play` / `pause` / `next` / `prev` | Lecture / pause / suivant / précédent |
| `pear like` / `dislike` | J'aime / je n'aime pas |
| `pear shuffle` / `repeat` / `mute` / `full` | Aléatoire / répétition / muet / plein écran |
| `pear vol 40` | Volume à 40 % |
| `pear seek 1:30` | Aller à 1:30 |
| `pear +10` / `-10` | Avancer / reculer de 10 s |
| `pear search <texte>` (ou `pear s <texte>`) | Recherche de morceaux. Entrée : lire maintenant ; Maj+Entrée : « Lire ensuite » / « Ajouter en fin de file » |

> Astuce : dans Flow Launcher > Plugins > Pear Desktop, réglez un *Search delay* (≈ 400 ms) pour ne pas lancer une recherche à chaque touche.
