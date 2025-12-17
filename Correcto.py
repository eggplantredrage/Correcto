#!/usr/bin/env python3
"""
Correcto — Professional Writing Assistant for Linux
Copyleft 2025 Kevin A. Leblanc — GNU GPL v2
"""

import sys
import os
import json
import re
from pathlib import Path

# Qt imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout,
    QWidget, QLabel, QHBoxLayout, QTabWidget, QLineEdit, QListWidget,
    QMessageBox, QCheckBox, QComboBox, QStatusBar, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QClipboard

# Global module placeholders
language_tool = None
textstat = None
mlconjug = None
wordnet = None
wn = None

# === FULL FRENCH LEXICON (100+ words) ===
FRENCH_LEXICON = {
    "être": {"pos": "verbe", "def": "avoir une existence", "ex": "Je suis heureux."},
    "avoir": {"pos": "verbe", "def": "posséder", "ex": "J'ai un livre."},
    "faire": {"pos": "verbe", "def": "accomplir une action", "ex": "Fais attention !"},
    "dire": {"pos": "verbe", "def": "exprimer par la parole", "ex": "Il dit la vérité."},
    "aller": {"pos": "verbe", "def": "se déplacer", "ex": "Je vais à l'école."},
    "voir": {"pos": "verbe", "def": "percevoir avec les yeux", "ex": "Je vois un chat."},
    "prendre": {"pos": "verbe", "def": "saisir", "ex": "Prends ton sac."},
    "pouvoir": {"pos": "verbe", "def": "avoir la capacité", "ex": "Je peux aider."},
    "devoir": {"pos": "verbe", "def": "être obligé", "ex": "Je dois partir."},
    "vouloir": {"pos": "verbe", "def": "avoir envie", "ex": "Je veux réussir."},
    "savoir": {"pos": "verbe", "def": "connaître une information", "ex": "Je sais la réponse."},
    "connaître": {"pos": "verbe", "def": "avoir de l'expérience", "ex": "Je connais Paris."},
    "mettre": {"pos": "verbe", "def": "placer", "ex": "Mets le livre sur la table."},
    "donner": {"pos": "verbe", "def": "offrir", "ex": "Il donne un cadeau."},
    "trouver": {"pos": "verbe", "def": "localiser", "ex": "J'ai trouvé les clés."},
    "demander": {"pos": "verbe", "def": "poser une question", "ex": "Je demande de l'aide."},
    "parler": {"pos": "verbe", "def": "s'exprimer oralement", "ex": "Je parle français."},
    "comprendre": {"pos": "verbe", "def": "saisir le sens", "ex": "Je comprends la leçon."},
    "apprendre": {"pos": "verbe", "def": "acquérir des connaissances", "ex": "J'apprends le français."},
    "travailler": {"pos": "verbe", "def": "exercer une activité professionnelle", "ex": "Je travaille dans un bureau."},
    "habiter": {"pos": "verbe", "def": "vivre dans un lieu", "ex": "J'habite à Paris."},
    "aimer": {"pos": "verbe", "def": "avoir de l'affection", "ex": "J'aime la musique."},
    "penser": {"pos": "verbe", "def": "avoir une opinion", "ex": "Je pense que c'est vrai."},
    "sentir": {"pos": "verbe", "def": "percevoir une odeur ou une émotion", "ex": "Je sens une fleur."},
    "rester": {"pos": "verbe", "def": "demeurer", "ex": "Reste ici !"},
    "tenir": {"pos": "verbe", "def": "maintenir en place", "ex": "Tiens ce sac."},
    "venir": {"pos": "verbe", "def": "se déplacer vers ici", "ex": "Viens avec moi."},
    "arriver": {"pos": "verbe", "def": "atteindre un lieu", "ex": "Il arrive bientôt."},
    "partir": {"pos": "verbe", "def": "quitter un lieu", "ex": "Je pars maintenant."},
    "rentrer": {"pos": "verbe", "def": "retourner chez soi", "ex": "Je rentre à la maison."},
    "sortir": {"pos": "verbe", "def": "aller dehors", "ex": "Nous sortons ce soir."},
    "entrer": {"pos": "verbe", "def": "aller à l'intérieur", "ex": "Entrez, s'il vous plaît."},
    "monter": {"pos": "verbe", "def": "aller vers le haut", "ex": "Monte l'escalier."},
    "descendre": {"pos": "verbe", "def": "aller vers le bas", "ex": "Descends de là !"},
    "passer": {"pos": "verbe", "def": "aller d'un côté à l'autre", "ex": "Passe-moi le sel."},
    "finir": {"pos": "verbe", "def": "terminer", "ex": "Finis ton devoir."},
    "commencer": {"pos": "verbe", "def": "initier une action", "ex": "Commence maintenant."},
    "continuer": {"pos": "verbe", "def": "ne pas s'arrêter", "ex": "Continue à marcher."},
    "changer": {"pos": "verbe", "def": "devenir différent", "ex": "Tout peut changer."},
    "essayer": {"pos": "verbe", "def": "faire une tentative", "ex": "Essaye encore."},
    "réussir": {"pos": "verbe", "def": "atteindre le succès", "ex": "Il réussit son examen."},
    "échouer": {"pos": "verbe", "def": "ne pas réussir", "ex": "Ne pas échouer."},
    "gagner": {"pos": "verbe", "def": "obtenir une victoire", "ex": "Nous gagnons le match."},
    "perdre": {"pos": "verbe", "def": "ne plus avoir", "ex": "J'ai perdu mes clés."},
    "ouvrir": {"pos": "verbe", "def": "rendre accessible", "ex": "Ouvre la porte."},
    "fermer": {"pos": "verbe", "def": "rendre inaccessible", "ex": "Ferme la fenêtre."},
    "lire": {"pos": "verbe", "def": "déchiffrer du texte", "ex": "Je lis un roman."},
    "écrire": {"pos": "verbe", "def": "tracer des signes", "ex": "J'écris une lettre."},
    "écouter": {"pos": "verbe", "def": "prêter attention", "ex": "Écoute la musique."},
    "regarder": {"pos": "verbe", "def": "observer avec les yeux", "ex": "Regarde ce film."},
    "manger": {"pos": "verbe", "def": "consommer de la nourriture", "ex": "Je mange une pomme."},
    "boire": {"pos": "verbe", "def": "consommer un liquide", "ex": "Bois de l'eau."},
    "dormir": {"pos": "verbe", "def": "reposer son corps", "ex": "Je dors huit heures."},
    "vivre": {"pos": "verbe", "def": "être en vie", "ex": "Je vis en France."},
    "mourir": {"pos": "verbe", "def": "cesser de vivre", "ex": "Les feuilles meurent en hiver."},
    "homme": {"pos": "nom", "def": "être humain masculin", "ex": "Cet homme est gentil."},
    "femme": {"pos": "nom", "def": "être humain féminin", "ex": "Cette femme est intelligente."},
    "enfant": {"pos": "nom", "def": "jeune être humain", "ex": "L'enfant joue."},
    "ami": {"pos": "nom", "def": "personne chère", "ex": "Mon ami m'aide."},
    "maison": {"pos": "nom", "def": "bâtiment d'habitation", "ex": "La maison est grande."},
    "voiture": {"pos": "nom", "def": "véhicule à moteur", "ex": "La voiture est rouge."},
    "ville": {"pos": "nom", "def": "grand ensemble urbain", "ex": "Paris est une grande ville."},
    "pays": {"pos": "nom", "def": "nation", "ex": "La France est un beau pays."},
    "monde": {"pos": "nom", "def": "planète Terre", "ex": "Le monde est vaste."},
    "jour": {"pos": "nom", "def": "période de lumière", "ex": "Bon jour !"},
    "nuit": {"pos": "nom", "def": "période d'obscurité", "ex": "La nuit est calme."},
    "temps": {"pos": "nom", "def": "durée ou météo", "ex": "Il fait beau temps."},
    "année": {"pos": "nom", "def": "période de 365 jours", "ex": "Cette année est spéciale."},
    "mois": {"pos": "nom", "def": "période d'environ 30 jours", "ex": "Janvier est un mois froid."},
    "semaine": {"pos": "nom", "def": "période de 7 jours", "ex": "Une semaine de vacances."},
    "heure": {"pos": "nom", "def": "période de 60 minutes", "ex": "Il est trois heures."},
    "minute": {"pos": "nom", "def": "période de 60 secondes", "ex": "Attends une minute."},
    "seconde": {"pos": "nom", "def": "unité de temps", "ex": "Une seconde suffit."},
    "eau": {"pos": "nom", "def": "liquide transparent", "ex": "Je bois de l'eau."},
    "feu": {"pos": "nom", "def": "combustion", "ex": "Le feu brûle."},
    "air": {"pos": "nom", "def": "mélange gazeux", "ex": "L'air est pur."},
    "terre": {"pos": "nom", "def": "sol ou planète", "ex": "La Terre est bleue."},
    "ciel": {"pos": "nom", "def": "espace au-dessus de la terre", "ex": "Le ciel est bleu."},
    "mer": {"pos": "nom", "def": "grande étendue d'eau salée", "ex": "La mer est calme."},
    "fleur": {"pos": "nom", "def": "organe reproducteur des plantes", "ex": "Cette fleur est belle."},
    "arbre": {"pos": "nom", "def": "plante ligneuse", "ex": "L'arbre donne de l'ombre."},
    "chat": {"pos": "nom", "def": "animal domestique", "ex": "Le chat dort."},
    "chien": {"pos": "nom", "def": "animal domestique fidèle", "ex": "Le chien aboie."},
    "oiseau": {"pos": "nom", "def": "animal volant", "ex": "L'oiseau chante."},
    "poisson": {"pos": "nom", "def": "animal aquatique", "ex": "Le poisson nage."},
    "livre": {"pos": "nom", "def": "ouvrage imprimé", "ex": "Je lis un livre."},
    "lettre": {"pos": "nom", "def": "caractère ou message écrit", "ex": "Écris une lettre."},
    "mot": {"pos": "nom", "def": "unité de langage", "ex": "Ce mot est difficile."},
    "phrase": {"pos": "nom", "def": "groupe de mots", "ex": "Cette phrase est longue."},
    "langue": {"pos": "nom", "def": "système de communication", "ex": "Le français est ma langue."},
    "voix": {"pos": "nom", "def": "son produit par la parole", "ex": "Sa voix est douce."},
    "main": {"pos": "nom", "def": "partie du corps", "ex": "Donne-moi la main."},
    "pied": {"pos": "nom", "def": "extrémité de la jambe", "ex": "J'ai mal au pied."},
    "tête": {"pos": "nom", "def": "partie supérieure du corps", "ex": "Ma tête tourne."},
    "cœur": {"pos": "nom", "def": "organe ou symbole d'amour", "ex": "Mon cœur bat vite."},
    "bouche": {"pos": "nom", "def": "organe de la parole et de la nourriture", "ex": "Ferme la bouche."},
    "yeux": {"pos": "nom", "def": "organes de la vue", "ex": "Mes yeux sont fatigués."},
    "nez": {"pos": "nom", "def": "organe de l'odorat", "ex": "Mon nez coule."},
    "oreilles": {"pos": "nom", "def": "organes de l'ouïe", "ex": "Mes oreilles sifflent."},
    "peau": {"pos": "nom", "def": "enveloppe du corps", "ex": "Ma peau est sèche."},
    "cheveux": {"pos": "nom", "def": "filaments sur la tête", "ex": "Mes cheveux sont longs."},
    "grand": {"pos": "adjectif", "def": "de grande taille", "ex": "Un grand arbre."},
    "petit": {"pos": "adjectif", "def": "de petite taille", "ex": "Un petit chien."},
    "beau": {"pos": "adjectif", "def": "agréable à voir", "ex": "Une belle fleur."},
    "bon": {"pos": "adjectif", "def": "de bonne qualité", "ex": "Un bon repas."},
    "mauvais": {"pos": "adjectif", "def": "de mauvaise qualité", "ex": "Un mauvais film."},
    "vieux": {"pos": "adjectif", "def": "ancien", "ex": "Un vieux livre."},
    "nouveau": {"pos": "adjectif", "def": "récent", "ex": "Une nouvelle voiture."},
    "jeune": {"pos": "adjectif", "def": "pas vieux", "ex": "Un jeune homme."},
    "fort": {"pos": "adjectif", "def": "ayant de la force", "ex": "Il est très fort."},
    "faible": {"pos": "adjectif", "def": "manquant de force", "ex": "Je me sens faible."},
    "rapide": {"pos": "adjectif", "def": "allant vite", "ex": "Une voiture rapide."},
    "lent": {"pos": "adjectif", "def": "allant lentement", "ex": "Un escargot est lent."},
    "chaud": {"pos": "adjectif", "def": "ayant une température élevée", "ex": "L'eau est chaude."},
    "froid": {"pos": "adjectif", "def": "ayant une température basse", "ex": "L'hiver est froid."},
    "clair": {"pos": "adjectif", "def": "bien éclairé", "ex": "Le ciel est clair."},
    "sombre": {"pos": "adjectif", "def": "mal éclairé", "ex": "La pièce est sombre."},
    "plein": {"pos": "adjectif", "def": "rempli", "ex": "Le verre est plein."},
    "vide": {"pos": "adjectif", "def": "pas rempli", "ex": "La bouteille est vide."},
    "propre": {"pos": "adjectif", "def": "sans saleté", "ex": "Les vêtements sont propres."},
    "sale": {"pos": "adjectif", "def": "avec de la saleté", "ex": "Les chaussures sont sales."},
    "facile": {"pos": "adjectif", "def": "sans difficulté", "ex": "C'est une question facile."},
    "difficile": {"pos": "adjectif", "def": "avec difficulté", "ex": "C'est un exercice difficile."},
    "important": {"pos": "adjectif", "def": "ayant de l'importance", "ex": "C'est très important."},
    "utile": {"pos": "adjectif", "def": "qui sert à quelque chose", "ex": "Ce conseil est utile."},
    "inutile": {"pos": "adjectif", "def": "qui ne sert à rien", "ex": "C'est une remarque inutile."},
    "possible": {"pos": "adjectif", "def": "qui peut exister", "ex": "Tout est possible."},
    "impossible": {"pos": "adjectif", "def": "qui ne peut pas exister", "ex": "C'est impossible !"},
    "vrai": {"pos": "adjectif", "def": "conforme à la réalité", "ex": "C'est la vérité."},
    "faux": {"pos": "adjectif", "def": "non conforme à la réalité", "ex": "C'est un faux document."},
    "libre": {"pos": "adjectif", "def": "non prisonnier", "ex": "Je suis libre."},
    "occupé": {"pos": "adjectif", "def": "non disponible", "ex": "Je suis occupé."},
    "content": {"pos": "adjectif", "def": "heureux", "ex": "Je suis content."},
    "triste": {"pos": "adjectif", "def": "malheureux", "ex": "Il est triste."},
    "heureux": {"pos": "adjectif", "def": "joyeux", "ex": "Elle est heureuse."},
    "malheureux": {"pos": "adjectif", "def": "pas heureux", "ex": "Il est malheureux."},
    "calme": {"pos": "adjectif", "def": "paisible", "ex": "Sois calme."},
    "agité": {"pos": "adjectif", "def": "pas calme", "ex": "L'enfant est agité."},
    "gentil": {"pos": "adjectif", "def": "aimable", "ex": "Il est gentil."},
    "méchant": {"pos": "adjectif", "def": "cruel", "ex": "Il est méchant."},
    "intelligent": {"pos": "adjectif", "def": "ayant de l'intelligence", "ex": "Elle est intelligente."},
    "bête": {"pos": "adjectif", "def": "pas intelligent", "ex": "C'est une bête question."},
    "riche": {"pos": "adjectif", "def": "ayant beaucoup d'argent", "ex": "Il est riche."},
    "pauvre": {"pos": "adjectif", "def": "n'ayant pas d'argent", "ex": "Le pays est pauvre."},
    "cher": {"pos": "adjectif", "def": "coûteux", "ex": "Cette montre est chère."},
    "bon marché": {"pos": "adjectif", "def": "peu coûteux", "ex": "C'est bon marché."},
    "proche": {"pos": "adjectif", "def": "pas loin", "ex": "La gare est proche."},
    "loin": {"pos": "adjectif", "def": "à grande distance", "ex": "L'école est loin."},
    "haut": {"pos": "adjectif", "def": "de grande altitude", "ex": "La montagne est haute."},
    "bas": {"pos": "adjectif", "def": "de faible altitude", "ex": "Le ciel est bas."},
    "long": {"pos": "adjectif", "def": "de grande longueur", "ex": "Une longue route."},
    "court": {"pos": "adjectif", "def": "de faible longueur", "ex": "Une courte réponse."},
    "large": {"pos": "adjectif", "def": "de grande largeur", "ex": "Une large rue."},
    "étroit": {"pos": "adjectif", "def": "de faible largeur", "ex": "Un étroit passage."},
    "épais": {"pos": "adjectif", "def": "de grande épaisseur", "ex": "Un épais livre."},
    "mince": {"pos": "adjectif", "def": "de faible épaisseur", "ex": "Une mince feuille."},
    "lourd": {"pos": "adjectif", "def": "de grand poids", "ex": "Ce sac est lourd."},
    "léger": {"pos": "adjectif", "def": "de faible poids", "ex": "Une plume est légère."},
    "dur": {"pos": "adjectif", "def": "solide", "ex": "Le bois est dur."},
    "mou": {"pos": "adjectif", "def": "pas solide", "ex": "Le pain est mou."},
    "doux": {"pos": "adjectif", "def": "agréable au toucher", "ex": "Le tissu est doux."},
    "rude": {"pos": "adjectif", "def": "désagréable au toucher", "ex": "Le tissu est rude."}
}

# === TRANSLATIONS ===
TRANSLATIONS = {
    "en": {
        "app_title": "Correcto — Professional Writing Assistant",
        "lang_label_ui": "UI Language:",
        "lang_label_text": "Text Language:",
        "switch_text_lang": "Switch Text Language",
        "style_mode": "Writing Mode:",
        "analyze": "Analyze Text",
        "stats": "Show Statistics",
        "export": "Export Report",
        "corrections": "Corrections",
        "dictionary": "Dictionary",
        "conjugation": "Conjugation",
        "document": "Document:",
        "empty_doc": "📝 Empty document.",
        "analyzing": "🔍 Analyzing...",
        "no_issues": "✅ No issues detected.",
        "grammar": "Grammar",
        "style": "Style",
        "context": "Context",
        "suggestions": "Suggestions",
        "def": "Definition",
        "example": "Example",
        "error": "Error",
        "stats_title": "Document Statistics",
        "words": "Words",
        "sentences": "Sentences",
        "flesch": "Flesch Reading Ease",
        "passive": "Passive Voice",
        "repetition": "Repetitions",
        "long_sent": "Long Sentences",
        "style_checks": "Style Checks:",
        "conj_verb": "Conjugate verb",
        "lookup_word": "Look up word",
        "install_nltk": "⚠️ Install NLTK for English dictionary",
        "not_found": "Not found",
        "install_deps": "Install dependencies:\npip install --user {}",
        "academic": "Academic",
        "professional": "Professional",
        "neutral": "Neutral",
        "about": "About Correcto"
    },
    "fr": {
        "app_title": "Correcto — Assistant de rédaction professionnel",
        "lang_label_ui": "Langue de l'interface :",
        "lang_label_text": "Langue du texte :",
        "switch_text_lang": "Changer la langue du texte",
        "style_mode": "Mode de rédaction :",
        "analyze": "Analyser le texte",
        "stats": "Afficher les statistiques",
        "export": "Exporter le rapport",
        "corrections": "Corrections",
        "dictionary": "Dictionnaire",
        "conjugation": "Conjugaison",
        "document": "Document :",
        "empty_doc": "📝 Document vide.",
        "analyzing": "🔍 Analyse en cours...",
        "no_issues": "✅ Aucun problème détecté.",
        "grammar": "Grammaire",
        "style": "Style",
        "context": "Contexte",
        "suggestions": "Suggestions",
        "def": "Définition",
        "example": "Exemple",
        "error": "Erreur",
        "stats_title": "Statistiques du document",
        "words": "Mots",
        "sentences": "Phrases",
        "flesch": "Lisibilité Flesch",
        "passive": "Voix passive",
        "repetition": "Répétitions",
        "long_sent": "Phrases longues",
        "style_checks": "Vérifications de style :",
        "conj_verb": "Conjuguer un verbe",
        "lookup_word": "Rechercher un mot",
        "install_nltk": "⚠️ Installez NLTK pour le dictionnaire anglais",
        "not_found": "Non trouvé",
        "install_deps": "Installez les dépendances :\npip install --user {}",
        "academic": "Universitaire",
        "professional": "Professionnel",
        "neutral": "Neutre",
        "about": "À propos de Correcto"
    }
}

# === STYLE CHECKERS ===
def detect_passive_voice_en(text):
    patterns = [r'\b(am|are|is|was|were|been|being)\s+\w+ed\b']
    matches = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append(("Passive voice", match.group()))
    return matches

def detect_passive_voice_fr(text):
    etre_forms = r'\b(suis|es|est|sommes|êtes|sont)\b'
    pattern = rf'({etre_forms})\s+\w+[é]\b'
    matches = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
        matches.append(("Voix passive", match.group()))
    return matches

def detect_repetitions(text, window=10):
    words = re.findall(r'\b\w+\b', text.lower())
    repeated = []
    for i in range(len(words)):
        for j in range(i+1, min(i+window+1, len(words))):
            if words[i] == words[j] and len(words[i]) > 3:
                repeated.append((f"Repetition of '{words[i]}'", words[i]))
    return repeated

def pragmatic_prism_en(text):
    issues = []
    hedges = r"\b(maybe|perhaps|sort of|kind of|somewhat|quite|very|really)\b"
    for match in re.finditer(hedges, text, re.IGNORECASE):
        issues.append(("Avoid hedging for clarity", match.group()))
    return issues

def apply_style_mode(text, mode, lang):
    issues = []
    if lang == "en-US":
        if mode == "academic" and re.search(r"\b(can't|don't|won't|it's)\b", text, re.IGNORECASE):
            issues.append(("Avoid contractions in academic writing", "contraction"))
        elif mode == "professional" and re.search(r"\butilize\b", text, re.IGNORECASE):
            issues.append(("Prefer 'use' over 'utilize'", "utilize"))
    return issues

# === DICTIONARY HELPERS ===
def lookup_english(word):
    """Get definition and example from WordNet (NLTK)."""
    try:
        import nltk
        from nltk.corpus import wordnet as wn
        # Ensure WordNet is downloaded
        try:
            wn.synsets("test")
        except LookupError:
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
        
        synsets = wn.synsets(word)
        if not synsets:
            return {"def": "Word not found in English dictionary.", "pos": "", "ex": ""}
        
        # Use first synset
        syn = synsets[0]
        pos_map = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 'r': 'adverb'}
        pos = pos_map.get(syn.pos(), syn.pos())
        definition = syn.definition()
        examples = syn.examples()
        example = examples[0] if examples else ""
        return {"def": definition, "pos": pos, "ex": example}
    except Exception as e:
        return {"def": f"English dictionary error: {str(e)}", "pos": "", "ex": ""}

def lookup_french(word):
    """Lookup in embedded French lexicon."""
    word = word.lower()
    entry = FRENCH_LEXICON.get(word)
    if entry:
        return {"def": entry["def"], "pos": entry["pos"], "ex": entry["ex"]}
    return {"def": "Mot non trouvé dans le dictionnaire français.", "pos": "", "ex": ""}

# === CONFIGURATION ===
CONFIG_DIR = Path.home() / ".config" / "correcto"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"

def get_config():
    default = {
        "ui_language": "en",
        "text_language": "en-US",
        "style_mode": "neutral",
        "check_passive": True,
        "check_repetition": True,
        "check_long_sent": True
    }
    if CONFIG_FILE.exists():
        try:
            saved = json.loads(CONFIG_FILE.read_text())
            for key in default:
                if key not in saved:
                    saved[key] = default[key]
            return saved
        except Exception:
            pass
    return default

def save_config(cfg):
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    except Exception:
        pass

# === ANALYSIS THREAD ===
class AnalyzerThread(QThread):
    result_ready = pyqtSignal(dict)

    def __init__(self, text, lang, config):
        super().__init__()
        self.text = text
        self.lang = lang
        self.config = config

    def run(self):
        global language_tool
        if language_tool is None:
            try:
                import language_tool_python
                language_tool = language_tool_python
            except ImportError:
                self.result_ready.emit({"error": "language-tool-python"})
                return

        try:
            tool = language_tool.LanguageTool(self.lang)
            matches = tool.check(self.text)

            grammar_issues = []
            for m in matches:
                grammar_issues.append({
                    'message': getattr(m, 'message', 'Unknown issue'),
                    'context': getattr(m, 'context', '—'),
                    'suggestions': getattr(m, 'replacements', [])
                })

            style_issues = []
            if self.config["check_passive"]:
                if self.lang == "en-US":
                    style_issues.extend([{"message": msg, "example": ex} for msg, ex in detect_passive_voice_en(self.text)])
                elif self.lang == "fr":
                    style_issues.extend([{"message": msg, "example": ex} for msg, ex in detect_passive_voice_fr(self.text)])
            if self.config["check_repetition"]:
                style_issues.extend([{"message": msg, "example": ex} for msg, ex in detect_repetitions(self.text)])

            if self.lang == "en-US":
                style_issues.extend([{"message": msg, "example": ex} for msg, ex in pragmatic_prism_en(self.text)])

            mode_issues = apply_style_mode(self.text, self.config["style_mode"], self.lang)
            for msg, ex in mode_issues:
                style_issues.append({"message": msg, "example": ex})

            self.result_ready.emit({
                "grammar_issues": grammar_issues,
                "style_issues": style_issues,
                "error": None
            })
        except Exception as e:
            self.result_ready.emit({"error": str(e)})

# === MAIN WINDOW ===
class CorrectoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.ui_lang = self.config["ui_language"]
        self.text_lang = self.config["text_language"]
        self.style_mode = self.config.get("style_mode", "neutral")
        self.tr = TRANSLATIONS[self.ui_lang]
        self.init_ui()
        self.update_ui()

    def init_ui(self):
        self.central = QWidget()
        self.main_layout = QVBoxLayout()

        ui_lang_layout = QHBoxLayout()
        ui_lang_layout.addWidget(QLabel(self.tr["lang_label_ui"]))
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItems(["English", "Français"])
        self.ui_lang_combo.setCurrentText("English" if self.ui_lang == "en" else "Français")
        self.ui_lang_combo.currentTextChanged.connect(self.change_ui_language)
        ui_lang_layout.addWidget(self.ui_lang_combo)
        ui_lang_layout.addStretch()

        text_lang_layout = QHBoxLayout()
        self.text_lang_label = QLabel()
        self.text_lang_btn = QPushButton()
        self.text_lang_btn.clicked.connect(self.toggle_text_language)
        self.style_mode_label = QLabel(self.tr["style_mode"])
        self.style_mode_combo = QComboBox()
        self.style_mode_combo.addItems([self.tr["neutral"], self.tr["academic"], self.tr["professional"]])
        mode_map = {"neutral": 0, "academic": 1, "professional": 2}
        self.style_mode_combo.setCurrentIndex(mode_map.get(self.style_mode, 0))
        self.style_mode_combo.currentIndexChanged.connect(self.change_style_mode)
        text_lang_layout.addWidget(self.text_lang_label)
        text_lang_layout.addWidget(self.text_lang_btn)
        text_lang_layout.addWidget(self.style_mode_label)
        text_lang_layout.addWidget(self.style_mode_combo)
        text_lang_layout.addStretch()

        self.passive_cb = QCheckBox(self.tr["passive"])
        self.repeat_cb = QCheckBox(self.tr["repetition"])
        self.long_cb = QCheckBox(self.tr["long_sent"])
        self.passive_cb.setChecked(self.config["check_passive"])
        self.repeat_cb.setChecked(self.config["check_repetition"])
        self.long_cb.setChecked(self.config["check_long_sent"])

        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel(self.tr["style_checks"]))
        style_layout.addWidget(self.passive_cb)
        style_layout.addWidget(self.repeat_cb)
        style_layout.addWidget(self.long_cb)
        style_layout.addStretch()

        self.editor = QTextEdit()
        self.editor.setFont(QFont("DejaVu Sans Mono", 11))
        self.editor.setPlaceholderText("Write your text...")

        btn_layout = QHBoxLayout()
        self.analyze_btn = QPushButton(self.tr["analyze"])
        self.analyze_btn.clicked.connect(self.run_analysis)
        self.stats_btn = QPushButton(self.tr["stats"])
        self.stats_btn.clicked.connect(self.show_stats)
        self.export_btn = QPushButton(self.tr["export"])
        self.export_btn.clicked.connect(self.export_report)
        self.about_btn = QPushButton(self.tr["about"])
        self.about_btn.clicked.connect(self.show_about)
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addWidget(self.stats_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.about_btn)

        self.tabs = QTabWidget()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("DejaVu Sans Mono", 10))
        self.tabs.addTab(self.results_text, self.tr["corrections"])

        dict_widget = QWidget()
        dict_layout = QVBoxLayout()
        self.dict_input = QLineEdit()
        self.dict_input.setPlaceholderText(self.tr["lookup_word"])
        self.dict_input.returnPressed.connect(self.lookup_word)
        self.dict_results = QListWidget()
        dict_layout.addWidget(self.dict_input)
        dict_layout.addWidget(self.dict_results)
        dict_widget.setLayout(dict_layout)
        self.tabs.addTab(dict_widget, self.tr["dictionary"])

        conj_widget = QWidget()
        conj_layout = QVBoxLayout()
        self.conj_input = QLineEdit()
        self.conj_input.setPlaceholderText(self.tr["conj_verb"])
        self.conj_input.returnPressed.connect(self.conjugate_verb)
        self.conj_results = QTextEdit()
        self.conj_results.setReadOnly(True)
        conj_layout.addWidget(self.conj_input)
        conj_layout.addWidget(self.conj_results)
        conj_widget.setLayout(conj_layout)
        self.tabs.addTab(conj_widget, self.tr["conjugation"])

        self.main_layout.addLayout(ui_lang_layout)
        self.main_layout.addLayout(text_lang_layout)
        self.main_layout.addLayout(style_layout)
        self.main_layout.addWidget(QLabel(self.tr["document"]))
        self.main_layout.addWidget(self.editor)
        self.main_layout.addLayout(btn_layout)
        self.main_layout.addWidget(self.tabs)

        self.central.setLayout(self.main_layout)
        self.setCentralWidget(self.central)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def update_ui(self):
        self.tr = TRANSLATIONS[self.ui_lang]
        self.setWindowTitle(self.tr["app_title"])
        lang_name = "English" if self.text_lang == "en-US" else "Français"
        self.text_lang_label.setText(f"{self.tr['lang_label_text']} {lang_name}")
        self.text_lang_btn.setText(self.tr["switch_text_lang"])
        self.analyze_btn.setText(self.tr["analyze"])
        self.stats_btn.setText(self.tr["stats"])
        self.export_btn.setText(self.tr["export"])
        self.about_btn.setText(self.tr["about"])
        self.tabs.setTabText(0, self.tr["corrections"])
        self.tabs.setTabText(1, self.tr["dictionary"])
        self.tabs.setTabText(2, self.tr["conjugation"])
        placeholder = "Write your text..." if self.ui_lang == "en" else "Écrivez votre texte..."
        self.editor.setPlaceholderText(placeholder)
        self.passive_cb.setText(self.tr["passive"])
        self.repeat_cb.setText(self.tr["repetition"])
        self.long_cb.setText(self.tr["long_sent"])
        style_label = self.main_layout.itemAt(2).layout().itemAt(0).widget()
        style_label.setText(self.tr["style_checks"])

    def change_ui_language(self, lang_name):
        self.ui_lang = "en" if lang_name == "English" else "fr"
        self.config["ui_language"] = self.ui_lang
        save_config(self.config)
        self.update_ui()

    def toggle_text_language(self):
        self.text_lang = "fr" if self.text_lang == "en-US" else "en-US"
        self.config["text_language"] = self.text_lang
        save_config(self.config)
        self.update_ui()

    def change_style_mode(self, index):
        modes = ["neutral", "academic", "professional"]
        self.style_mode = modes[index]
        self.config["style_mode"] = self.style_mode
        save_config(self.config)

    def run_analysis(self):
        self.config.update({
            "check_passive": self.passive_cb.isChecked(),
            "check_repetition": self.repeat_cb.isChecked(),
            "check_long_sent": self.long_cb.isChecked()
        })
        save_config(self.config)

        text = self.editor.toPlainText()
        if not text.strip():
            self.results_text.setPlainText(self.tr["empty_doc"])
            return

        self.results_text.setPlainText(self.tr["analyzing"])
        self.analyzer = AnalyzerThread(text, self.text_lang, self.config)
        self.analyzer.result_ready.connect(self.display_results)
        self.analyzer.start()

    def display_results(self, data):
        if "error" in data and data["error"]:
            err = data["error"]
            msg = self.tr["install_deps"].format(err) if err == "language-tool-python" else f"{self.tr['error']}: {err}"
            self.results_text.setPlainText(msg)
            return

        report_lines = []

        for issue in data.get("grammar_issues", []):
            suggestions = ', '.join(issue['suggestions'][:3]) if issue['suggestions'] else "—"
            block = f"[{self.tr['grammar']}] {issue['message']}\n" \
                    f"{self.tr['context']}: “{issue['context']}”\n" \
                    f"{self.tr['suggestions']}: {suggestions}"
            report_lines.append(block)

        for issue in data.get("style_issues", []):
            block = f"[{self.tr['style']}] {issue['message']}"
            if issue.get('example'):
                block += f"\nExample: “{issue['example']}”"
            report_lines.append(block)

        if not report_lines:
            self.results_text.setPlainText(self.tr["no_issues"])
        else:
            self.results_text.setPlainText("\n\n".join(report_lines))

    def show_stats(self):
        text = self.editor.toPlainText()
        if not text.strip():
            QMessageBox.information(self, self.tr["stats_title"], self.tr["empty_doc"])
            return

        global textstat
        if textstat is None:
            try:
                import textstat
            except ImportError:
                QMessageBox.warning(self, self.tr["error"], self.tr["install_deps"].format("textstat"))
                return

        words = len(text.split())
        sentences = max(0, len(re.split(r'[.!?]+', text)) - 1)
        try:
            flesch = textstat.flesch_reading_ease(text)
            ease = f"{flesch:.1f}"
        except:
            ease = "N/A"

        stats = (
            f"{self.tr['words']}: {words}\n"
            f"{self.tr['sentences']}: {sentences}\n"
            f"{self.tr['flesch']}: {ease}"
        )
        QMessageBox.information(self, self.tr["stats_title"], stats)

    def export_report(self):
        text = self.editor.toPlainText()
        if not text.strip():
            return

        path, _ = QFileDialog.getSaveFileName(self, self.tr["export_html"], "", "HTML Files (*.html)")
        if not path:
            return

        words = len(text.split())
        sentences = max(0, len(re.split(r'[.!?]+', text)) - 1)
        passive_count = len(re.findall(r'\b(am|are|is|was|were|been|being)\s+\w+ed\b', text, re.IGNORECASE))
        passive_pct = (passive_count / max(words, 1)) * 100

        html = f"""
        <html><head><title>Correcto Report</title></head><body>
        <h1>Correcto Writing Report</h1>
        <p><b>{self.tr['words']}:</b> {words}</p>
        <p><b>{self.tr['sentences']}:</b> {sentences}</p>
        <p><b>Passive Voice %:</b> {passive_pct:.2f}%</p>
        <p><b>Style Mode:</b> {self.style_mode}</p>
        <h2>Text</h2>
        <pre>{text}</pre>
        </body></html>
        """
        Path(path).write_text(html)
        self.statusBar.showMessage(f"Report exported to {path}", 3000)

    def show_about(self):
        logo_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABhGlDQ1BJQ0MgcHJvZmlsZQAAKJF9"
            "kT1Iw0AcxV9TpSIVBzuIOGSoThZERRy1CkWoQqgVWnUwufQLmjQkKS6OgmvBwY/FqoOLs64O"
            "roIg+AHi5uak6CIl/i8ptIjx4Lgf7+497t4BQqPCVDMwAaiaZaTiMTGbWxW7XxFGEOEIRjGl"
            "mJnJSUgBX/F1j4+rOIZ9Ls9xPn9Xz0rOWDAg4HFmmGZcEG8QT1u6wXlf4jCrSgrxGfGYQRck"
            "fuS67PIb56LD+Z0iM5q1JOIgYkhrK5jFqMyqxJPEUUXVKN+Pua5y3uKsVeusfR5+Mb+krrTc"
            "px1JLKKEJEQoqKAKCzbqcaKsJcVCmuMJPf+Ic0myyJVjToU1WXB0g+D84He3+T25mJpKnQSc"
            "t4H2hmPXtwG7C6B95tifO/Z3APqfzV5bSzt6ABY6XddrR0DfM9C/5tibOq65f0D6ed3b2DsA"
            "B4dArGjK1v3+7oHe2rZV3z/31J7P1y0t3ge8JXCeA3cN6LkCJ2fdtXWf0zsHUNtZ3/76eD8A"
            "Z7+UdZkO9AAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyNS0xMi0xN1QxNToyMToxMCswMDowMLTq"
            "q40AAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjUtMTItMTdUMTU6MjE6MTArMDA6MDCRk1aPAAAA"
            "AElFTkSuQmCC"
        )
        about_html = f"""
        <div style="text-align: center; font-family: sans-serif;">
            <img src="image/png;base64,{logo_b64}" width="64" height="64" style="margin-bottom: 12px;">
            <h3>Correcto</h3>
            <p>Professional Writing Assistant for Linux</p>
            <p style="margin-top: 10px; margin-bottom: 10px;">
                Copylefted 2025 Kevin A. Leblanc<br>
                License: GNU GPL v2
            </p>
            <p style="font-size: 90%;">
                <a href="https://www.gnu.org/licenses/old-licenses/gpl-2.0.html" style="text-decoration: none; color: #2980b9;">
                    View GPL v2 License
                </a>
            </p>
        </div>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(self.tr["about"])
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_html)
        msg_box.exec()

    def lookup_word(self):
        word = self.dict_input.text().strip().lower()
        if not word:
            return
        self.dict_results.clear()
        if self.text_lang == "en-US":
            info = lookup_english(word)
            self.dict_results.addItem(f"Word: {word}")
            if info["pos"]:
                self.dict_results.addItem(f"Part of speech: {info['pos']}")
            self.dict_results.addItem(f"Definition: {info['def']}")
            if info["ex"]:
                self.dict_results.addItem(f"Example: {info['ex']}")
        else:
            info = lookup_french(word)
            self.dict_results.addItem(f"Mot : {word}")
            if info["pos"]:
                self.dict_results.addItem(f"Catégorie : {info['pos']}")
            self.dict_results.addItem(f"Définition : {info['def']}")
            if info["ex"]:
                self.dict_results.addItem(f"Exemple : {info['ex']}")

    def conjugate_verb(self):
        verb = self.conj_input.text().strip()
        if not verb:
            return

        global mlconjug
        if mlconjug is None:
            try:
                import mlconjug3
                mlconjug = mlconjug3
            except ImportError:
                self.conj_results.setPlainText(self.tr["install_deps"].format("mlconjug3"))
                return

        lang = "fr" if self.text_lang == "fr" else "en"
        try:
            conjugator = mlconjug.Conjugator(language=lang)
            conj = conjugator.conjugate(verb)
            lang_name = "français" if lang == "fr" else "anglais"
            output = f"Conjugaison de « {verb} » ({lang_name}) :\n\n" if lang == "fr" else f"Conjugation of '{verb}' ({lang_name}):\n\n"
            for i, (tense, forms) in enumerate(conj.iterate()):
                if i >= 3:
                    break
                output += f"{tense}: {forms}\n"
            self.conj_results.setPlainText(output)
        except Exception as e:
            self.conj_results.setPlainText(f"{self.tr['error']}: {e}")

def main():
    app = QApplication(sys.argv)
    font = QFont()
    font.setPointSize(10)
    app.setFont(font)
    window = CorrectoApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
