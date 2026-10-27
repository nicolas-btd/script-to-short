# script-to-short

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange.svg)](https://aistudio.google.com/)
[![FFmpeg](https://img.shields.io/badge/Render-FFmpeg-green.svg)](https://ffmpeg.org/)
[![Playwright](https://img.shields.io/badge/Automation-Playwright-red.svg)](https://playwright.dev/)

> **Automated vertical video generator (9:16) for TikTok, YouTube Shorts, and Instagram Reels from a simple text file (`script.txt`).**
> 
> *Générateur automatique de vidéos courtes verticales (9:16) pour TikTok, YouTube Shorts et Instagram Reels à partir d'un simple fichier texte.*

---

> [!TIP]
> ### 🤖 Guide pour ChatGPT, Claude & assistants IA (et utilisateurs débutants)
> Si vous utilisez une IA pour vous guider ou si vous débutez complètement en informatique :
> - **Tout est expliqué pas à pas ci-dessous**, du téléchargement jusqu'à la vidéo finale.
> - Vous pouvez copier-coller ce README directement dans ChatGPT et lui demander :  
>   *« Guide-moi pas à pas pour installer script-to-short et créer ma première vidéo sur [Windows / Mac / Linux]. »*  
> - L'IA disposera de 100% du contexte technique, des commandes exactes et de la résolution des erreurs.

---

## Sommaire / Table of Contents

- [1. En bref : Qu'est-ce que fait ce projet ?](#1-en-bref--quest-ce-que-fait-ce-projet-)
- [2. Guide d'installation complet (Pas-à-pas pour débutants)](#2-guide-dinstallation-complet-pas-à-pas-pour-débutants)
  - [Étape 1 : Télécharger le projet](#étape-1--télécharger-le-projet)
  - [Étape 2 : Installer Python (Attention au piège Windows !)](#étape-2--installer-python-attention-au-piège-windows-)
  - [Étape 3 : Installer FFmpeg](#étape-3--installer-ffmpeg)
  - [Étape 4 : Obtenir sa clé API Google Gemini gratuite](#étape-4--obtenir-sa-clé-api-google-gemini-gratuite)
  - [Étape 5 : Configurer le fichier .env](#étape-5--configurer-le-fichier-env)
  - [Étape 6 : Installer les dépendances du projet](#étape-6--installer-les-dépendances-du-projet)
- [3. Créer sa première vidéo en 3 étapes](#3-créer-sa-première-vidéo-en-3-étapes)
  - [Étape 1 : Écrire votre script](#étape-1--écrire-votre-script)
  - [Étape 2 : Lancer Chrome sur Google Flow](#étape-2--lancer-chrome-sur-google-flow)
  - [Étape 3 : Lancer la génération](#étape-3--lancer-la-génération)
  - [Étape 4 : Choisir les images sur la page web](#étape-4--choisir-les-images-sur-la-page-web)
- [4. Fonctionnement de l'Interface Web de Sélection](#4-fonctionnement-de-linterface-web-de-sélection)
  - [Détection automatique du nombre d'images (x1, x2, x3, x4)](#détection-automatique-du-nombre-dimages-x1-x2-x3-x4)
  - [Raccourcis clavier & interaction](#raccourcis-clavier--interaction)
  - [Régénération ciblée (Touche X)](#régénération-ciblée-touche-x)
- [5. Architecture et Pipeline Technique](#5-architecture-et-pipeline-technique)
- [6. Les Deux Modes de Fonctionnement](#6-les-deux-modes-de-fonctionnement)
  - [Mode 1 : Automatique (Script + Style avec Gemini)](#mode-1--automatique-script--style-avec-gemini)
  - [Mode 2 : Manuel (Prompts & Timeline sur-mesure, zéro appel LLM)](#mode-2--manuel-prompts--timeline-sur-mesure-zéro-appel-llm)
- [7. Dictionnaire de tous les fichiers d'un projet vidéo](#7-dictionnaire-de-tous-les-fichiers-dun-projet-vidéo)
- [8. Personnalisation & Configuration](#8-personnalisation--configuration)
  - [Priorité des réglages](#priorité-des-réglages)
  - [Fichier config.json complet](#fichier-configjson-complet)
  - [Styles visuels & Direction artistique (style.txt)](#styles-visuels--direction-artistique-styletxt)
  - [Personnalisation des sous-titres](#personnalisation-des-sous-titres)
  - [Effets de caméra & Zooms Ken Burns](#effets-de-caméra--zooms-ken-burns)
  - [Bruitages sonores (SFX)](#bruitages-sonores-sfx)
  - [Voix IA Gemini & Direction d'acteur](#voix-ia-gemini--direction-dacteur)
  - [Utiliser sa propre voix ou un audio externe](#utiliser-sa-propre-voix-ou-un-audio-externe)
  - [Profils de chaîne multi-comptes (accounts/)](#profils-de-chaîne-multi-comptes-accounts)
- [9. Recettes & Styles Prêts à l'Emploi](#9-recettes--styles-prêts-à-lemploi)
- [10. Référence Complète des Commandes CLI](#10-référence-complète-des-commandes-cli)
- [11. FAQ & Résolution des Problèmes (Dépannage)](#11-faq--résolution-des-problèmes-dépannage)
- [12. Structure du Dépôt](#12-structure-du-dépôt)
- [13. Licence](#13-licence)
- [14. Avertissement & Usage Légal (Disclaimer)](#14-avertissement--usage-légal-disclaimer)

---

## 1. En bref : Qu'est-ce que fait ce projet ?

Créer des vidéos courtes percutantes pour TikTok ou YouTube demande habituellement des heures de travail sur plusieurs logiciels :
1. Enregistrer une voix off et la nettoyer.
2. Découper manuellement le texte toutes les 1 à 2 secondes pour garder l'attention du spectateur.
3. Rédiger des prompts et générer des dizaines d'images cohérentes.
4. Synchroniser les sous-titres mot par mot avec un surlignage dynamique en couleur.
5. Ajouter des animations de zoom (effet Ken Burns), des secousses d'impact et des bruitages (whoosh, pop).
6. Monter et exporter la vidéo finale au format vertical 9:16 (1080x1920) à 60 images par seconde.

**`script-to-short` automatise 100% de cette chaîne de production.**  
Vous écrivez simplement votre texte dans un fichier `script.txt`, et le programme s'occupe de tout le reste.

---

## 2. Guide d'installation complet (Pas-à-pas pour débutants)

Aucune connaissance préalable en programmation n'est requise. Suivez simplement ces 6 étapes.

### Étape 1 : Télécharger le projet

Deux méthodes simples :
- **Option A (Sans Git)** : Cliquez sur le bouton vert **`<> Code`** en haut de la page GitHub, puis sur **`Download ZIP`**. Décompressez ensuite le dossier ZIP sur votre ordinateur (par exemple dans vos *Documents*).
- **Option B (Avec Git)** : Ouvrez votre terminal et tapez :
  ```bash
  git clone https://github.com/votre-nom/script-to-short.git
  cd script-to-short
  ```

---

### Étape 2 : Installer Python (Attention au piège Windows !)

Ce projet nécessite **Python 3.10 ou une version supérieure**.

- **Sur Windows :**
  1. Téléchargez Python sur le site officiel : [python.org/downloads](https://www.python.org/downloads/)
  2. Lancez l'installateur.
  3. > [!CRITICAL]
     > **PIÈGE IMPORTANT :** Cochez impérativement la case **`Add python.exe to PATH`** tout en bas de la première fenêtre d'installation avant de cliquer sur *Install Now*. Si vous ne cochez pas cette case, votre terminal ne reconnaîtra pas la commande `python`.
- **Sur macOS :**
  Ouvrez l'application *Terminal* et tapez (avec [Homebrew](https://brew.sh/)) :
  ```bash
  brew install python
  ```
- **Sur Linux (Ubuntu/Debian) :**
  ```bash
  sudo apt update && sudo apt install -y python3 python3-pip python3-venv
  ```

---

### Étape 3 : Installer FFmpeg

FFmpeg est le moteur qui mixe le son, anime les images et encode la vidéo finale.

- **Sur Windows :**
  Ouvrez *PowerShell* ou l'*Invite de commandes* et tapez :
  ```powershell
  winget install Gyan.FFmpeg
  ```
  *(Redémarrez votre terminal après l'installation pour que FFmpeg soit pris en compte).*
- **Sur macOS :**
  ```bash
  brew install ffmpeg
  ```
- **Sur Linux (Ubuntu/Debian) :**
  ```bash
  sudo apt install -y ffmpeg
  ```

*Vérification : tapez `ffmpeg -version` dans votre terminal. Si un texte décrivant la version s'affiche, c'est réussi !*

---

### Étape 4 : Obtenir sa clé API Google Gemini gratuite

La clé API Gemini permet de générer la voix off ultra-réaliste et de découper le script en scènes. C'est **100% gratuit** :

1. Rendez-vous sur **[Google AI Studio](https://aistudio.google.com/)**.
2. Connectez-vous avec n'importe quel compte Google.
3. Cliquez sur le bouton bleu **`Get API key`** (dans la colonne de gauche).
4. Cliquez sur **`Create API key`**, puis copiez la clé générée (elle commence généralement par `AIzaSy...`).

---

### Étape 5 : Configurer le fichier .env

Dans le dossier du projet :
1. Trouvez le fichier nommé `.env.example`.
2. Dupliquez-le ou renommez-le en **`.env`** (avec un point devant, sans `.example`).
3. Ouvrez-le avec n'importe quel éditeur de texte (Bloc-notes, VS Code, TextEdit).
4. Remplacez le texte factice par votre vraie clé Gemini :
   ```env
   GEMINI_API_KEY="AIzaSyVotreCleSecreteIci"
   ```
5. Enregistrez le fichier.

---

### Étape 6 : Installer les dépendances du projet

Ouvrez un terminal dans le dossier du projet :

1. **Créer et activer un environnement virtuel (recommandé) :**
   - **Sur macOS / Linux :**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - **Sur Windows :**
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
2. **Installer les modules Python :**
   ```bash
   pip install -r requirements.txt
   ```
3. **Installer les navigateurs pour l'automatisation :**
   ```bash
   playwright install chromium
   ```

Tout est installé ! Vous êtes prêt à créer votre première vidéo.

---

## 3. Créer sa première vidéo en 3 étapes

### Étape 1 : Écrire votre script

Créez un nouveau dossier pour votre vidéo dans `videos/` (par exemple `videos/ma_video/`).  
À l'intérieur, créez un fichier texte simple nommé **`script.txt`** et collez-y votre texte :

```text
Saviez-vous que votre cerveau consomme 20% de toute votre énergie quotidienne ? 
Pourtant, il ne représente que 2% de votre poids total. 
Quand vous réfléchissez intensément, il brûle du glucose à toute vitesse. 
Alors la prochaine fois que vous êtes fatigué après avoir étudié, c'est totalement normal !
```

*(Optionnel)* Vous pouvez ajouter un fichier **`style.txt`** dans le même dossier pour définir le style graphique que vous souhaitez (ex: *« Clean 2D stickman cartoon, minimalist, solid colors »* ou *« Dark cinematic historical painting, dramatic lighting »*).

---

### Étape 2 : Lancer Chrome sur Google Flow

Google Flow (`flow.google.com`) est l'outil de génération d'images de Google. Pour éviter tout problème de mot de passe ou de blocage, le projet pilote votre propre session Google Chrome :

- **Sur macOS / Linux :**
  ```bash
  ./flow/start_chrome.sh
  ```
- **Sur Windows :**
  Double-cliquez sur `flow\start_chrome.bat` ou lancez :
  ```cmd
  flow\start_chrome.bat
  ```

Une fenêtre Google Chrome s'ouvre.  
👉 **Dans cette fenêtre Chrome :**
1. Allez sur **[flow.google.com](https://flow.google.com/)**.
2. Connectez-vous avec votre compte Google.
3. Ouvrez le projet dans lequel vous souhaitez générer les images (ou créez-en un nouveau).
4. **Laissez cette fenêtre Chrome ouverte en arrière-plan.**

---

### Étape 3 : Lancer la génération

Dans votre terminal (toujours dans le dossier `script-to-short`) :

```bash
python main.py videos/ma_video
```

Le programme va automatiquement :
1. 🎙️ Générer la voix off avec Gemini TTS au format audio broadcast (-14 LUFS).
2. ⏱️ Synchroniser chaque mot avec Whisper pour les sous-titres.
3. 🎬 Découper le script en scènes rapides de 1 à 2 secondes et rédiger les prompts d'images adaptés.
4. 🎨 Envoyer les prompts à Google Flow via Chrome et télécharger toutes les variantes générées.
5. 🌐 Ouvrir automatiquement votre navigateur sur l'interface de sélection : `http://localhost:8765/`.

---

### Étape 4 : Choisir les images sur la page web

Une interface web élégante s'ouvre sur `http://localhost:8765/` :

1. Pour chaque plan, vous voyez le texte prononcé et les variantes d'images proposées côte à côte.
2. **Appuyez sur `1`, `2`, `3` ou `4` sur votre clavier** (ou cliquez sur l'image) pour sélectionner celle que vous préférez.
3. Si aucune image ne vous plaît pour un plan, appuyez sur la touche **`X`** (le plan passe en rouge « À refaire »).
4. Tout en haut, cliquez sur le bouton vert **`✅ Valider et lancer le montage`**.
5. Une barre de progression violette affiche en direct le calage et le rendu de la vidéo finale.
6. Dès que c'est terminé, cliquez sur **`▶️ Ouvrir la vidéo finale`** : votre vidéo **`video_finale.mp4`** s'ouvre, prête à être partagée !

---

## 4. Fonctionnement de l'Interface Web de Sélection

L'interface web (`flow/choisir_web.py`) a été spécialement conçue pour être ultra-rapide et intuitive.

### Détection automatique du nombre d'images (x1, x2, x3, x4)

Google Flow permet de générer 1, 2, 3 ou 4 variantes par prompt (via le bouton de réglages `🍌 Nano Banana ... crop_9_16 x4`).
- **Détection automatique dans Flow** : Le moteur lit directement le réglage actif sur la page de Flow (`x1`, `x2`, `x3` ou `x4`).
- **Affichage sur-mesure sur la page web** : La page web s'adapte dynamiquement pour chaque plan. Si un plan a 4 variantes, 4 colonnes s'affichent. S'il en a 2 ou 3, elle affiche exactement le bon nombre.

### Raccourcis clavier & interaction

Vous pouvez faire tout le tri sans toucher à la souris :
- Touches **`1`**, **`2`**, **`3`**, **`4`** (pavé numérique ou chiffres standard) : sélectionne la variante et fait défiler automatiquement jusqu'au plan suivant.
- Touches AZERTY **`&`**, **`é`**, **`"`**, **`'`** : fonctionnent également de la même manière.
- Touche **`X`** : bascule le plan en mode « À refaire ».
- Clic direct sur n'importe quelle vignette.

### Régénération ciblée (Touche X)

Si vous marquez un ou plusieurs plans avec la touche `X` et que vous cliquez sur *Valider* :
1. Le système ne relance que les scènes marquées `X`.
2. Il vous génère de nouvelles propositions sans toucher aux scènes que vous aviez déjà validées.

---

## 5. Architecture et Pipeline Technique

Le pipeline complet fonctionne comme une suite d'ateliers automatisés :

```text
[ script.txt ] (Texte de votre narration)
      │
      ▼
1. core/voice.py ──────────► Gemini TTS ──────────► [ voix.mp3 ] (-14 LUFS)
      │
      ▼
2. core/transcribe.py ─────► Faster-Whisper ──────► [ whisper_words.json ] (Timestamps mot à mot)
      │
      ▼
3. core/scene_planner.py ──► Gemini 2.5 Flash ────► [ timeline_raw.json ] (Découpage des scènes)
      │                                             [ prompts.json ]      (Prompts visuels 9:16)
      ▼
4. flow/flow_fast.py ──────► Google Flow (CDP) ───► [ images_candidates/ ] (1 à 4 variantes par plan)
      │
      ▼
5. flow/choisir_web.py ────► Interface Web ───────► [ 01.jpg, 02.jpg... ] (Images retenues)
      │
      ▼
6. core/renderer.py ───────► Pillow + FFmpeg ─────► [ video_finale.mp4 ] (Vidéo 60 fps avec zooms,
                                                                          sous-titres & bruitages)
```

---

## 6. Les Deux Modes de Fonctionnement

### Mode 1 : Automatique (Script + Style avec Gemini)

C'est le mode par défaut pour aller vite.
- **Entrées requises :** Uniquement `videos/<mon_projet>/script.txt` (et optionnellement `style.txt`).
- **Rôle de l'IA :** Gemini 2.5 Flash analyse le texte, le découpe en segments dynamiques de 1 à 2 secondes, rédige les descriptions visuelles adaptées à votre style artistique, place les effets de zoom, les secousses d'impact (`shake`), les mots-clés en majuscules et les bruitages sonores (`sfx`).
- **Commande :**
  ```bash
  python main.py videos/mon_projet
  ```

### Mode 2 : Manuel (Prompts & Timeline sur-mesure, zéro appel LLM)

Idéal si vous avez préparé vos propres prompts avec ChatGPT, Claude, DeepSeek ou à la main.
- **Entrées reconnues :**
  - `prompts.jsonl` ou `prompts.json` : la liste exacte de vos prompts d'images avec leurs références de personnages.
  - `timeline_raw.json` ou `scenes.json` : les repères de synchronisation audio-texte (`anchor`), mots-clés et bruitages.
- **Comportement :** Dès que ces fichiers sont présents, le découpage par Gemini est automatiquement sauté.
- **Commande :**
  ```bash
  python main.py videos/mon_projet --mode manual
  ```

---

## 7. Dictionnaire de tous les fichiers d'un projet vidéo

Lors de la production d'une vidéo dans `videos/mon_projet/`, voici à quoi sert chaque fichier :

| Fichier | Obligatoire ? | Rôle et description |
| :--- | :---: | :--- |
| `script.txt` | **Oui** (en mode auto) | Le texte brut de la narration que la voix IA va lire. |
| `style.txt` | Non | Description du style artistique souhaité (ex: cartoon 2D, rendu 3D, peinture à l'huile). |
| `account.txt` | Non | Nom du profil de chaîne à utiliser (`cartoon`, `documentary`, `medical`, `horror`). |
| `cover.txt` | Non | Idée de titre et de miniature générée pour les réseaux sociaux. |
| `desc.txt` | Non | Description et hashtags générés pour TikTok / YouTube Shorts / Instagram. |
| `voix.mp3` | Auto-généré | Fichier audio de la voix off, normalisé au standard -14 LUFS. |
| `whisper_words.json` | Auto-généré | Empreinte temporelle précise de chaque mot prononcé (pour les sous-titres). |
| `timeline_raw.json` | Auto-généré | Découpage des plans avec mots de calage (`anchor`), bruitages (`sfx`) et secousses (`fx`). |
| `prompts.json` | Auto-généré | Liste complète des prompts envoyés à Google Flow. |
| `prompts.txt` | Auto-généré | Feuille de prompts lisible par un humain (pratique pour copier-coller ailleurs). |
| `images_candidates/` | Auto-généré | Dossier contenant toutes les variantes d'images téléchargées depuis Flow (`1_1.jpg`, `1_2.jpg`, etc.). |
| `choix_images.json` | Auto-généré | Fichier de sauvegarde de vos choix sur la page web. |
| `01.jpg`, `02.jpg`... | Auto-généré | Les images finales retenues, renommées dans l'ordre chronologique de la vidéo. |
| `timeline_finale.csv` | Auto-généré | Tableau final des durées exactes de chaque plan en secondes. |
| `video_finale.mp4` | **RÉSULTAT** | **Votre vidéo finale complète à 60 fps**, avec sous-titres animés, zooms et audio mixé ! |

---

## 8. Personnalisation & Configuration

### Priorité des réglages

Les paramètres de style, sous-titres, voix et zoom sont résolus selon cet ordre de priorité (le niveau supérieur écrase le niveau inférieur) :

1. **Options de la ligne de commande** (`--sub-size 80`, `--voice-name Charon`, etc.)
2. **Configuration du projet** (`videos/<projet>/config.json`)
3. **Profil de compte** (`accounts/<profil>/config.json`)
4. **Valeurs par défaut du moteur**

---

### Fichier config.json complet

Vous pouvez placer un fichier `config.json` dans votre dossier vidéo pour personnaliser le rendu :

```json
{
  "name": "mon_style",
  "subtitles": {
    "enabled": true,
    "font": "Arial Rounded Bold",
    "size": 70,
    "position": "bottom",
    "y_percent": 0.70,
    "alignment": "center",
    "active_color": [255, 212, 59],
    "inactive_color": [255, 255, 255],
    "stroke_color": [0, 0, 0],
    "stroke_width": 6,
    "uppercase": true,
    "max_words": 3,
    "max_width": 880
  },
  "visual_fx": {
    "zoom_enabled": true,
    "zoom_intensity": 0.08,
    "zoom_mode": "alternate",
    "shake_enabled": true,
    "shake_intensity": 10.0
  },
  "editing": {
    "min_scene_dur": 1.0,
    "max_scene_dur": 2.2,
    "keyword_font_size": 150,
    "show_keywords": true,
    "sfx_pack": "cartoon"
  },
  "voice": {
    "name": "Puck",
    "style": "A dynamic, engaging narrator voice for short-form video. Lively rhythm and crisp pronunciation."
  }
}
```

---

### Styles visuels & Direction artistique (`style.txt`)

Pour garantir que tous les plans d'une vidéo aient le même univers graphique, écrivez votre style dans `videos/<mon_projet>/style.txt` ou passez-le avec `--style`.

Exemples de styles testés et approuvés :

#### 1. Cartoon Stickman 2D (Idéal pour vidéos explicatives virales)
```text
Clean digital cartoon illustration in a simple stickman style. The stickman has a large perfectly round white head with a thick black outline, expressive eyes (white circles with black pupils), thin curved eyebrows and a small simple mouth. His body, arms and legs are very thin black lines, with no hands or feet drawn. Flat color background filling the whole frame, no paper texture. Objects have flat colors with thick black outlines and no shading. Vertical 9:16 format. Absolutely no text or writing anywhere in the image.
```

#### 2. Documentaire Historique & Cinématique
```text
Vivid cinematic digital illustration, rich atmospheric chiaroscuro lighting, detailed historical storytelling scene, dramatic depth of field, vertical 9:16 format. Absolutely no text, words, or writing anywhere in the image.
```

#### 3. Rendu 3D Médical & Scientifique
```text
Stylized 3D animation render, clean medical and biology explainer aesthetic, smooth matte materials, simple organic shapes, soft global illumination, vertical 9:16 composition. Absolutely no text or writing anywhere in the image.
```

#### 4. Anime / Manga Cyberpunk
```text
Modern cyberpunk anime digital illustration, vibrant neon lighting, high contrast, wet reflective pavement, detailed character design, Studio Trigger inspired dynamic framing, vertical 9:16 portrait composition. Absolutely no text or writing anywhere in the image.
```

---

### Personnalisation des sous-titres

Les sous-titres sont affichés mot par mot en synchronisation parfaite avec la voix :

- **Changer la position verticale :**
  - En bas (recommandé pour TikTok, au-dessus de la légende) : `--sub-pos bottom` ou `--sub-y 0.68`
  - Au milieu (style documentaire) : `--sub-pos center` ou `--sub-y 0.50`
  - En haut : `--sub-pos top` ou `--sub-y 0.22`
- **Changer la couleur du mot prononcé (effet karaoké) :**
  - Jaune éclatant : `--sub-accent "#FFE600"`
  - Vert fluo : `--sub-accent "#00FF66"`
  - Cyan électrique : `--sub-accent "#00E5FF"`
  - Désactiver le surlignage (texte blanc uniforme) : `--sub-accent none`
- **Changer la taille :** `--sub-size 65` (discret) à `--sub-size 90` (très gros, style viral)
- **Désactiver complètement les sous-titres :** `--no-subtitles`

---

### Effets de caméra & Zooms Ken Burns

Pour rendre les images vivantes et dynamiques, la caméra bouge en continu :

- **`--zoom-mode alternate` (Par défaut) :** Alterne à chaque plan. Le plan 1 zoome lentement vers l'avant, le plan 2 dézoome lentement vers l'arrière, le plan 3 zoome vers l'avant. Très fluide et captivant.
- **`--zoom-mode in` :** Tous les plans zooment vers l'avant.
- **`--zoom-mode out` :** Tous les plans commencent avec un plan plus serré et s'élargissent.
- **`--no-zoom` :** Images complètement statiques.
- **`--zoom-intensity 0.12` :** Augmente l'amplitude du zoom (par défaut : `0.08`).
- **`--no-shake` :** Désactive les secousses de caméra sur les moments de surprise ou d'impact.

---

### Bruitages sonores (SFX)

Des effets sonores courts et discrets sont insérés automatiquement au moment des transitions ou des révélations pour booster le dynamisme :
- `whoosh` : transition rapide d'air.
- `pop` : apparition d'un mot ou d'un objet.
- `tic` : bruitage d'horloge ou de compte à rebours.
- `rire`, `boing`, `alarme`...
Les sons se trouvent dans `assets/sfx/`. Vous pouvez ajouter vos propres fichiers `.wav` ou `.mp3` dans ce dossier.

---

### Voix IA Gemini & Direction d'acteur

Le modèle Gemini TTS propose 5 timbres vocaux de base :

| Voix | Registre | Style vocal | Idéal pour |
| :--- | :--- | :--- | :--- |
| **Puck** | Homme (Ténor) | Énergique, moderne, punchy, diction nette | Cartoons, explications rapides, TikTok |
| **Charon** | Homme (Basse) | Profond, grave, solennel, captivant | Documentaires, histoire, mystère, horreur |
| **Kore** | Femme (Alto) | Chaleureuse, posée, bienveillante, claire | Santé, sciences, vulgarisation, récits |
| **Fenrir** | Homme (Baryton)| Intense, rauque, autoritaire, puissant | Action, fitness, bandes-annonces |
| **Aoede** | Femme (Soprano)| Douce, fluide, mélodieuse, sophistiquée | Culture, littérature, lifestyle |

Vous pouvez choisir la voix avec :
```bash
python main.py videos/mon_projet --voice-name Charon
```

---

### Utiliser sa propre voix ou un audio externe

Si vous enregistrez votre propre voix au micro ou si vous utilisez un autre outil (ElevenLabs, etc.) :
1. Déposez simplement votre fichier audio dans le dossier de la vidéo sous le nom **`voix.mp3`** (ou `.wav`).
2. Lancez le programme :
   ```bash
   python main.py videos/mon_projet --skip-voice
   ```
3. Faster-Whisper détectera automatiquement votre fichier, extraira chaque mot à la milliseconde près et calera la vidéo dessus !

---

### Profils de chaîne multi-comptes (`accounts/`)

Si vous gérez plusieurs comptes TikTok ou YouTube avec des identités visuelles différentes, regroupez vos réglages dans `accounts/<nom_du_compte>/` :

- `accounts/cartoon/` : style stickman, voix Puck, sous-titres jaunes.
- `accounts/documentary/` : style réaliste, voix Charon, zoom lent, sous-titres blancs.
- `accounts/medical/` : style 3D épuré, voix Kore, accent turquoise.

Pour appliquer un profil à votre vidéo :
```bash
python main.py videos/mon_projet --account cartoon
```

---

## 9. Recettes & Styles Prêts à l'Emploi

#### Style Alex Hormozi (Gros sous-titres jaunes dynamiques)
```bash
python main.py videos/mon_projet \
  --sub-pos bottom \
  --sub-size 90 \
  --sub-accent "#FFE600" \
  --sub-color "#FFFFFF" \
  --zoom-intensity 0.10
```

#### Style Documentaire Minimaliste (Sous-titres blancs sobres)
```bash
python main.py videos/mon_projet \
  --voice-name Charon \
  --sub-pos center \
  --sub-accent none \
  --sub-color "#FFFFFF" \
  --zoom-mode in \
  --zoom-intensity 0.04
```

#### Style Scientifique & Médical
```bash
python main.py videos/mon_projet \
  --voice-name Kore \
  --sub-pos center \
  --sub-accent "#00FFC2" \
  --sub-size 75 \
  --zoom-mode in
```

#### Re-générer seulement la vidéo avec de nouveaux sous-titres (sans refaire les images)
```bash
python main.py videos/mon_projet \
  --render-only \
  --sub-accent "#FF3366" \
  --sub-y 0.65
```

---

## 10. Référence Complète des Commandes CLI

```text
usage: main.py [-h] [--mode {auto,manual}] [--account ACCOUNT] [--skip-voice]
               [--skip-flow] [--render-only] [--web-only] [--fps FPS]
               [--sub-pos {top,center,bottom}] [--sub-y SUB_Y]
               [--sub-size SUB_SIZE] [--sub-color SUB_COLOR]
               [--sub-accent SUB_ACCENT] [--sub-align {center,left,right}]
               [--no-subtitles] [--no-zoom] [--zoom-intensity ZOOM_INTENSITY]
               [--zoom-mode {alternate,in,out,none}] [--no-shake]
               [--no-keywords] [--voice-name VOICE_NAME]
               [--voice-style VOICE_STYLE] [--style STYLE]
               video_dir
```

| Option | Valeurs possibles | Description |
| :--- | :--- | :--- |
| `video_dir` | Chemin de dossier | **(Requis)** Dossier contenant `script.txt` (ex: `videos/projet1`). |
| `--mode` | `auto`, `manual` | Mode automatique (Gemini découpe) ou manuel (fichiers JSON pré-fournis). |
| `--account` | Nom de dossier dans `accounts/` | Applique les styles d'une chaîne spécifique (`cartoon`, `documentary`, etc.). |
| `--style` | Texte entre guillemets | Définit la consigne de style artistique pour les images. |
| `--voice-name` | `Puck`, `Charon`, `Kore`, `Fenrir`, `Aoede` | Choix du timbre de la voix IA. |
| `--voice-style`| Texte descriptif | Direction d'acteur pour la voix (intonation, rythme, émotion). |
| `--skip-voice` | Drapeau (sans valeur) | Ignore la synthèse vocale si `voix.mp3` existe déjà. |
| `--skip-flow`  | Drapeau (sans valeur) | Ignore la génération d'images Flow (utilise les images déjà présentes). |
| `--render-only`| Drapeau (sans valeur) | Reconstruit directement la vidéo finale sans rien regénérer d'autre. |
| `--web-only`   | Drapeau (sans valeur) | Lance uniquement la page web de sélection d'images `http://localhost:8765/`. |
| `--fps`        | `30`, `60` | Fréquence d'images de la vidéo (par défaut : 30 fps, 60 fps recommandé pour une fluidité maximale). |
| `--sub-pos`    | `top`, `center`, `bottom` | Position prédéfinie des sous-titres à l'écran. |
| `--sub-y`      | Nombre entre `0.0` et `1.0` | Position verticale sur-mesure (`0.68` = idéal pour TikTok). |
| `--sub-size`   | Nombre (ex: `70`) | Taille de la police des sous-titres. |
| `--sub-accent` | Code hex ou `none` | Couleur du mot prononcé (ex: `"#FFE600"` pour jaune, `none` pour monochrome). |
| `--sub-color`  | Code hex | Couleur des autres mots du sous-titre (ex: `"#FFFFFF"`). |
| `--no-subtitles`| Drapeau | Supprime totalement les sous-titres de la vidéo. |
| `--zoom-mode`  | `alternate`, `in`, `out`, `none` | Type d'animation de caméra Ken Burns. |
| `--zoom-intensity` | Nombre (ex: `0.08`) | Amplitude du zoom de caméra. |
| `--no-zoom`    | Drapeau | Désactive tout mouvement de caméra (images statiques). |
| `--no-shake`   | Drapeau | Désactive les secousses de caméra. |
| `--no-keywords`| Drapeau | Désactive les bandeaux de mots-clés en majuscules en haut de l'écran. |

---

## 11. FAQ & Résolution des Problèmes (Dépannage)

#### Q1 : Le terminal affiche `'ffmpeg' is not recognized` ou `ffmpeg: command not found`
> **Cause :** FFmpeg n'est pas installé ou n'a pas été ajouté à la variable d'environnement PATH.  
> **Solution :**  
> - Sur Windows : Ouvrez un terminal administrateur et tapez `winget install Gyan.FFmpeg`, puis fermez et rouvrez votre terminal.  
> - Sur Mac : Tapez `brew install ffmpeg`.  
> - Vérifiez en tapant `ffmpeg -version`.

#### Q2 : Le terminal affiche `GEMINI_API_KEY environment variable is not defined`
> **Cause :** Le fichier `.env` est manquant ou ne contient pas votre clé.  
> **Solution :** Dupliquez le fichier `.env.example`, renommez la copie en `.env`, et écrivez dedans : `GEMINI_API_KEY="votre_cle"`.

#### Q3 : Le terminal affiche `Cannot connect to host 127.0.0.1:9222` ou erreur CDP
> **Cause :** Google Chrome n'a pas été lancé avec le port de débogage 9222.  
> **Solution :** Lancez `./flow/start_chrome.sh` (Mac/Linux) ou `flow\start_chrome.bat` (Windows). Ne fermez pas la fenêtre Chrome qui s'ouvre.

#### Q4 : Google Flow affiche un Captcha ou demande de confirmer une action
> **Cause :** Google vérifie périodiquement que vous êtes bien un humain.  
> **Solution :** Cliquez simplement sur la fenêtre Chrome ouverte, résolvez le Captcha manuellement à la souris, puis relancez votre commande dans le terminal.

#### Q5 : Comment changer la police d'écriture des sous-titres ?
> **Solution :** Déposez votre fichier de police (ex: `MaPolice.ttf` ou `.otf`) dans le dossier `assets/fonts/` (ou `accounts/<compte>/fonts/`), puis indiquez `"font": "MaPolice.ttf"` dans votre `config.json`.

#### Q6 : Les images générées ne correspondent pas à mon projet
> **Cause :** Soit la description dans `style.txt` est trop vague, soit le projet sélectionné dans Google Flow n'est pas le bon.  
> **Solution :** Dans la fenêtre Chrome ouverte sur Flow, assurez-vous d'être dans le bon projet. Précisez bien votre style artistique dans `style.txt`.

#### Q7 : Comment exporter en 60 images par seconde (60 fps) ?
> **Solution :** Ajoutez simplement `--fps 60` à votre commande :
> ```bash
> python main.py videos/mon_projet --fps 60
> ```

---

## 12. Structure du Dépôt

```text
script-to-short/
├── .env.example              # Modèle de configuration avec explications
├── .gitignore                # Fichiers ignorés par Git (clés privées, caches)
├── LICENSE                   # Licence MIT
├── README.md                 # Cette documentation complète
├── requirements.txt          # Liste des bibliothèques Python nécessaires
├── main.py                   # Point d'entrée principal en ligne de commande
│
├── core/                     # Moteur de production
│   ├── voice.py              # Synthèse vocale Gemini TTS + normalisation -14 LUFS
│   ├── transcribe.py         # Découpage mot par mot avec Faster-Whisper
│   ├── scene_planner.py      # Découpage dynamique des scènes et prompts IA
│   ├── timeline.py           # Calage précis de la timeline et sous-titres
│   ├── renderer.py           # Moteur de rendu vidéo 60 fps (Pillow + FFmpeg)
│   ├── account_manager.py    # Gestionnaire des profils de compte et des polices
│   └── utils.py              # Outils utilitaires
│
├── flow/                     # Automatisation de Google Flow
│   ├── flow_auto.py          # Pilote Playwright pour Google Flow
│   ├── flow_fast.py          # Gestionnaire de file d'attente et téléchargement des images
│   ├── choisir_web.py        # Interface web de sélection (port 8765)
│   ├── build_prompts.py      # Formateur de prompts visuels 9:16
│   ├── start_chrome.sh       # Lanceur Chrome débogage (macOS / Linux)
│   └── start_chrome.bat      # Lanceur Chrome débogage (Windows)
│
├── accounts/                 # Profils de chaînes pré-configurés
│   ├── _template/            # Modèle pour créer une nouvelle chaîne
│   ├── cartoon/              # Profil stickman / cartoon
│   ├── documentary/          # Profil histoire / documentaire
│   ├── medical/              # Profil vulgarisation médicale & biologique
│   └── horror/               # Profil horreur / énigmes
│
├── assets/
│   ├── fonts/                # Polices de sous-titres
│   └── sfx/                  # Bruitages sonores (whoosh, pop, tic, rire...)
│
└── videos/
    └── demo/                 # Projet de démonstration prêt à tester
```

---

## 13. Licence

Ce projet est distribué sous licence libre **MIT**. Vous êtes libre de l'utiliser, le modifier et l'adapter pour vos projets personnels ou commerciaux. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 14. Avertissement & Usage Légal (Disclaimer)

> [!NOTE]
> ### ⚖️ Usage légal & éthique
> Ce projet est développé à des fins d'expérimentation personnelle, d'apprentissage et de recherche technique (Proof of Concept). 
> L'automatisation du navigateur s'appuie sur la session locale de l'utilisateur via le protocole Chrome DevTools (CDP) afin de pallier l'absence d'une API publique REST pour Google Labs.
> Les utilisateurs sont tenus de respecter les Conditions d'Utilisation des plateformes tierces. L'intégration d'API officielles (telles que Vertex AI / Imagen 3) reste la voie privilégiée dès leur mise à disposition grand public.

