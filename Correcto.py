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

# === MINIMAL FRENCH LEXICON ===
FRENCH_LEXICON = {
    "être": {"pos": "verbe", "def": "avoir une existence", "ex": "Je suis heureux."},
    "avoir": {"pos": "verbe", "def": "posséder", "ex": "J'ai un livre."},
    "maison": {"pos": "nom", "def": "bâtiment", "ex": "La maison est bleue."}
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
def init_nltk():
    global wordnet, wn
    if wordnet is None:
        try:
            import nltk
            from nltk.corpus import wordnet as wn_mod
            try:
                wn_mod.synsets("test")
            except LookupError:
                nltk.download('wordnet', quiet=True)
            wordnet = wn_mod
            wn = wn_mod
        except ImportError:
            pass

def lookup_english(word):
    init_nltk()
    if wn is None:
        return {"error": "nltk"}
    synsets = wn.synsets(word)
    if not synsets:
        return {"def": "Not found", "ex": ""}
    return {"def": synsets[0].definition(), "ex": synsets[0].examples()[0] if synsets[0].examples() else ""}

def lookup_french(word):
    entry = FRENCH_LEXICON.get(word.lower())
    if entry:
        return {"def": entry["def"], "ex": entry["ex"]}
    return {"def": "Non trouvé", "ex": ""}

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

# === ANALYSIS THREAD (SIMPLIFIED & ROBUST) ===
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

            # Collect grammar issues with full context
            grammar_issues = []
            for m in matches:
                grammar_issues.append({
                    'message': getattr(m, 'message', 'Unknown issue'),
                    'context': getattr(m, 'context', '—'),
                    'suggestions': getattr(m, 'replacements', [])
                })

            # Style issues
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

        # Grammar issues
        for issue in data.get("grammar_issues", []):
            suggestions = ', '.join(issue['suggestions'][:3]) if issue['suggestions'] else "—"
            block = f"[{self.tr['grammar']}] {issue['message']}\n" \
                    f"{self.tr['context']}: “{issue['context']}”\n" \
                    f"{self.tr['suggestions']}: {suggestions}"
            report_lines.append(block)

        # Style issues
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
        """Show About dialog with your copyright."""
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
            if "error" in info:
                self.dict_results.addItem(self.tr["install_nltk"])
            else:
                self.dict_results.addItem(f"{self.tr['def']}: {info['def']}")
                if info["ex"]:
                    self.dict_results.addItem(f"{self.tr['example']}: {info['ex']}")
        else:
            info = lookup_french(word)
            self.dict_results.addItem(f"{self.tr['def']}: {info['def']}")
            if info["ex"]:
                self.dict_results.addItem(f"{self.tr['example']}: {info['ex']}")

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
