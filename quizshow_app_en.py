#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"QuizShow - Version 1.9 - Complete UI redesign"

import sys ,json ,os ,copy ,urllib .request 
from functools import partial 

from PyQt5 .QtWidgets import (
QApplication ,QMainWindow ,QWidget ,QDialog ,QLabel ,QPushButton ,
QLineEdit ,QTextEdit ,QComboBox ,QListWidget ,QVBoxLayout ,QHBoxLayout ,
QGridLayout ,QStackedWidget ,QScrollArea ,QFileDialog ,QMessageBox ,
QDialogButtonBox ,QSplitter ,QFrame ,QSizePolicy ,QCheckBox ,QColorDialog ,
QSlider ,QGroupBox 
)
from PyQt5 .QtCore import Qt ,QObject ,pyqtSignal 
from PyQt5 .QtGui import QPainter ,QPixmap ,QColor ,QPalette ,QBrush ,QLinearGradient ,QFont ,QFontDatabase 

PRESETS_DIR ="presets"
FONTS_DIR ="fonts"
APP_TITLE ="QuizShow"

# ── ШРИФТЫ ───────────────────────────────────────────────
_app_font =["Segoe UI"]# текущий шрифт (mutable global)
_font_map ={}# display_name → реальное Qt-имя семьи

FONT_OPTIONS =[
("Segoe UI",None ,None ),
("Fredoka One","FredokaOne-Regular.ttf",
"https://raw.githubusercontent.com/google/fonts/main/ofl/fredokaone/FredokaOne-Regular.ttf"),
("Roboto","Roboto-Regular.ttf",
"https://raw.githubusercontent.com/google/fonts/main/apache/roboto/static/Roboto-Regular.ttf"),
("Ubuntu","Ubuntu-Regular.ttf",
"https://raw.githubusercontent.com/google/fonts/main/ufl/ubuntu/Ubuntu-Regular.ttf"),
("Nunito","Nunito-Regular.ttf",
"https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/static/Nunito-Regular.ttf"),
("Pacifico","Pacifico-Regular.ttf",
"https://raw.githubusercontent.com/google/fonts/main/ofl/pacifico/Pacifico-Regular.ttf"),
("Comfortaa","Comfortaa-Regular.ttf",
"https://raw.githubusercontent.com/google/fonts/main/ofl/comfortaa/static/Comfortaa-Regular.ttf"),
("Arial",None ,None ),
("Comic Sans MS",None ,None ),
("Courier New",None ,None ),
]


def _try_download_font (filename ,url ):
    "Download the TTF font if it is not already downloaded."
    os .makedirs (FONTS_DIR ,exist_ok =True )
    path =os .path .join (FONTS_DIR ,filename )
    if os .path .exists (path ):
        return path 
    try :
        req =urllib .request .Request (url ,headers ={"User-Agent":"Mozilla/5.0"})
        with urllib .request .urlopen (req ,timeout =8 )as resp :
            data =resp .read ()
        with open (path ,"wb")as f :
            f .write (data )
        return path 
    except Exception :
        return None 


def init_fonts ():
    "Load/download all fonts from FONT_OPTIONS."
    global _font_map 
    for name ,filename ,url in FONT_OPTIONS :
        if filename is None :
            _font_map [name ]=name 
            continue 
        path =os .path .join (FONTS_DIR ,filename )
        if not os .path .exists (path )and url :
            path =_try_download_font (filename ,url )or ""
        if path and os .path .exists (path ):
            fid =QFontDatabase .addApplicationFont (path )
            if fid >=0 :
                fams =QFontDatabase .applicationFontFamilies (fid )
                if fams :
                    _font_map [name ]=fams [0 ]
                    continue 
        _font_map [name ]=name # fallback — системное имя

        # ── ПАЛИТРА ──────────────────────────────────────────────
C ={
"bg0":"#05080F",# самый тёмный фон
"bg1":"#0A0E1A",# фон панелей
"bg2":"#0F1525",# карточки / elevated
"bg3":"#161E32",# hover / selected
"border":"#1C2640",# тихая рамка
"border2":"#2A3A5C",# заметная рамка
"indigo":"#6366F1",# основной акцент
"violet":"#8B5CF6",# вторичный акцент
"cyan":"#22D3EE",# подсветка
"gold":"#EAB308",# золото (номера)
"green":"#22C55E",# успех
"red":"#EF4444",# опасность
"orange":"#F97316",# предупреждение
"text":"#F1F5F9",# основной текст
"subtext":"#94A3B8",# вторичный текст
"muted":"#475569",# приглушённый
}

TYPE_NAMES_HOST ={
1 :"Type 1 — Hidden answers (revealed on click)",
2 :"Type 2 — All answers visible immediately",
3 :"Type 3 — Image + hidden answer",
4 :"Type 4 — Image + all answers visible",
}

# ── СТИЛИ КНОПОК ─────────────────────────────────────────
def style_btn (btn ,color ,text_color ="white",hover_color =None ):
    hc =hover_color or color 
    btn .setStyleSheet (f"""
        QPushButton {{
            background: {color };
            color: {text_color };
            padding: 9px 18px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 13px;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        QPushButton:hover {{
            background: {hc };
            border: 1px solid rgba(255,255,255,0.22);
        }}
        QPushButton:pressed {{
            background: {color };
            opacity: 0.8;
        }}
    """)

def get_global_style (font_family =None ):
    "Return a global stylesheet with the given font."
    ff =font_family or _app_font [0 ]
    return f"""
    QMainWindow, QWidget {{
        background: {C ['bg1']};
        color: {C ['text']};
        font-family: '{ff }', 'Segoe UI', sans-serif;
        font-size: 13px;
    }}
    QLineEdit, QTextEdit {{
        background: {C ['bg2']};
        color: {C ['text']};
        border: 1px solid {C ['border2']};
        border-radius: 8px;
        padding: 8px 12px;
        selection-background-color: {C ['indigo']};
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 1px solid {C ['indigo']};
    }}
    QComboBox {{
        background: {C ['bg2']};
        color: {C ['text']};
        border: 1px solid {C ['border2']};
        border-radius: 8px;
        padding: 6px 12px;
    }}
    QComboBox:focus {{ border: 1px solid {C ['indigo']}; }}
    QComboBox QAbstractItemView {{
        background: {C ['bg2']};
        color: {C ['text']};
        border: 1px solid {C ['border2']};
        selection-background-color: {C ['indigo']};
    }}
    QListWidget {{
        background: {C ['bg2']};
        border: 1px solid {C ['border']};
        border-radius: 12px;
        padding: 4px;
        outline: none;
    }}
    QListWidget::item {{
        padding: 10px 14px;
        border-radius: 8px;
        color: {C ['subtext']};
        margin: 2px 0px;
    }}
    QListWidget::item:selected {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 rgba(99,102,241,0.35), stop:1 rgba(139,92,246,0.25));
        color: {C ['text']};
        border: 1px solid {C ['indigo']};
    }}
    QListWidget::item:hover:!selected {{
        background: {C ['bg3']};
        color: {C ['text']};
    }}
    QGroupBox {{
        border: 1px solid {C ['border2']};
        border-radius: 10px;
        margin-top: 10px;
        padding: 10px 8px 8px 8px;
        color: {C ['subtext']};
        font-size: 12px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {C ['subtext']};
    }}
    QScrollBar:vertical {{
        background: {C ['bg1']};
        width: 6px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {C ['border2']};
        border-radius: 3px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
    QScrollArea {{ border: none; background: transparent; }}
    QSlider::groove:horizontal {{
        background: {C ['border2']};
        height: 4px;
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {C ['indigo']};
        width: 14px; height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 {C ['indigo']}, stop:1 {C ['violet']});
        border-radius: 2px;
    }}
    QCheckBox {{
        spacing: 8px;
        color: {C ['green']};
        font-weight: 700;
    }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border-radius: 4px;
        border: 2px solid {C ['green']};
        background: transparent;
    }}
    QCheckBox::indicator:checked {{
        background: {C ['green']};
    }}
    QSplitter::handle {{ background: {C ['border']}; width: 1px; }}
    QMessageBox {{ background: {C ['bg1']}; }}
    QDialogButtonBox QPushButton {{
        background: {C ['bg3']};
        color: {C ['text']};
        padding: 8px 24px;
        border-radius: 8px;
        border: 1px solid {C ['border2']};
        font-weight: 600;
    }}
    QDialogButtonBox QPushButton:hover {{
        border: 1px solid {C ['indigo']};
        background: rgba(99,102,241,0.2);
    }}
"""

    # ── SEPARATOR LINE ────────────────────────────────────────
def make_separator ():
    line =QFrame ()
    line .setFrameShape (QFrame .HLine )
    line .setStyleSheet (f"color: {C ['border']}; background: {C ['border']}; max-height:1px;")
    return line 

    # ── CARD WIDGET ───────────────────────────────────────────
def card_widget (widget ,radius =12 ):
    widget .setStyleSheet (f"""
        QWidget {{
            background: {C ['bg2']};
            border: 1px solid {C ['border']};
            border-radius: {radius }px;
        }}
    """)
    return widget 

    # ====================== МОДЕЛИ ======================
class AnswerData :
    def __init__ (self ,text ="",media_path ="",media_type ="none",is_correct =False ,media_mode ="inline"):
        self .text =text 
        self .media_path =media_path 
        self .media_type =media_type 
        self .is_correct =is_correct 
        self .media_mode =media_mode 

    def to_dict (self ):
        return {**self .__dict__ }

    @classmethod 
    def from_dict (cls ,d ):
        return cls (
        d .get ("text",""),d .get ("media_path",""),d .get ("media_type","none"),
        d .get ("is_correct",False ),d .get ("media_mode","inline")
        )


class QuestionData :
    def __init__ (self ):
        self .text =""
        self .q_type =1 
        self .answers =[]
        self .image_path =""
        self .text_scale =1.0 
        self .answer_text_scale =1.0 
        self .answer_image_scale =1.0 
        self .q_image_scale =1.0 
        self .explanation_text =""
        self .explanation_text_scale =1.0 
        self .explanation_image_path =""
        self .explanation_image_scale =1.0 

    def to_dict (self ):
        return {
        "text":self .text ,"q_type":self .q_type ,
        "answers":[a .to_dict ()for a in self .answers ],
        "image_path":self .image_path ,
        "text_scale":self .text_scale ,
        "answer_text_scale":self .answer_text_scale ,
        "answer_image_scale":self .answer_image_scale ,
        "q_image_scale":self .q_image_scale ,
        "explanation_text":self .explanation_text ,
        "explanation_text_scale":self .explanation_text_scale ,
        "explanation_image_path":self .explanation_image_path ,
        "explanation_image_scale":self .explanation_image_scale ,
        }

    @classmethod 
    def from_dict (cls ,d ):
        q =cls ()
        q .text =d .get ("text","")
        q .q_type =d .get ("q_type",1 )
        q .answers =[AnswerData .from_dict (a )for a in d .get ("answers",[])]
        q .image_path =d .get ("image_path","")
        q .text_scale =d .get ("text_scale",1.0 )
        q .answer_text_scale =d .get ("answer_text_scale",1.0 )
        q .answer_image_scale =d .get ("answer_image_scale",1.0 )
        q .q_image_scale =d .get ("q_image_scale",1.0 )
        q .explanation_text =d .get ("explanation_text","")
        q .explanation_text_scale =d .get ("explanation_text_scale",1.0 )
        q .explanation_image_path =d .get ("explanation_image_path","")
        q .explanation_image_scale =d .get ("explanation_image_scale",1.0 )
        return q 


class PresetData :
    def __init__ (self ,name ="New preset"):
        self .name =name 
        self .questions =[]
        self .bg_image =""
        self .end_image =""
        self .cell_border_color ="#6366F1"
        self .cell_bg_color ="rgba(10,14,26,210)"

    def to_dict (self ):
        return {
        "name":self .name ,
        "questions":[q .to_dict ()for q in self .questions ],
        "bg_image":self .bg_image ,"end_image":self .end_image ,
        "cell_border_color":self .cell_border_color ,
        "cell_bg_color":self .cell_bg_color ,
        }

    @classmethod 
    def from_dict (cls ,d ):
        p =cls (d .get ("name","Untitled"))
        p .questions =[QuestionData .from_dict (q )for q in d .get ("questions",[])]
        p .bg_image =d .get ("bg_image","")
        p .end_image =d .get ("end_image","")
        p .cell_border_color =d .get ("cell_border_color","#6366F1")
        p .cell_bg_color =d .get ("cell_bg_color","rgba(10,14,26,210)")
        return p 

    def save (self ,directory =PRESETS_DIR ):
        os .makedirs (directory ,exist_ok =True )
        safe ="".join (c for c in self .name if c .isalnum ()or c in " _-").strip ()or "preset"
        path =os .path .join (directory ,f"{safe }.json")
        with open (path ,"w",encoding ="utf-8")as f :
            json .dump (self .to_dict (),f ,ensure_ascii =False ,indent =2 )
        return path 

    @classmethod 
    def load (cls ,path ):
        with open (path ,"r",encoding ="utf-8")as f :
            return cls .from_dict (json .load (f ))


            # ====================== КОНТРОЛЛЕР ======================
class GameController (QObject ):
    question_changed =pyqtSignal (int )
    answer_revealed =pyqtSignal (int )
    answer_hidden =pyqtSignal (int )
    bg_changed =pyqtSignal (str )
    game_ended =pyqtSignal (str )
    correct_only_toggled =pyqtSignal (bool )
    explanation_toggled =pyqtSignal (bool )
    font_scale_changed =pyqtSignal (float )
    image_scale_changed =pyqtSignal (float )
    colors_changed =pyqtSignal ()
    font_family_changed =pyqtSignal (str )

    def __init__ (self ,preset ,initial_font =None ):
        super ().__init__ ()
        self .preset =preset 
        self .current_q_idx =0 
        self .revealed =set ()
        self .show_correct_only =False 
        self .show_explanation =False 
        self .font_scale =1.0 
        self .image_scale =1.0 
        self .font_family =initial_font or _app_font [0 ]

    @property 
    def current_question (self ):
        if 0 <=self .current_q_idx <len (self .preset .questions ):
            return self .preset .questions [self .current_q_idx ]
        return None 

    def question_has_explanation (self ):
        q =self .current_question 
        return bool (q and ((q .explanation_text or '').strip ()or q .explanation_image_path ))

    def can_show_explanation (self ):
        q =self .current_question 
        if not q or not self .question_has_explanation ():
            return False 
        if self .show_correct_only or q .q_type in (2 ,4 ):
            return any (a .is_correct for a in q .answers )
        return any (i in self .revealed for i ,a in enumerate (q .answers )if a .is_correct )

    def refresh_explanation_state (self ):
        if self .show_explanation and not self .can_show_explanation ():
            self .show_explanation =False 
        self .explanation_toggled .emit (self .show_explanation )

    def toggle_explanation (self ):
        if not self .can_show_explanation ():
            self .show_explanation =False 
            self .explanation_toggled .emit (False )
            return 
        self .show_explanation =not self .show_explanation 
        self .explanation_toggled .emit (self .show_explanation )

    def go_to_question (self ,idx ):
        if 0 <=idx <len (self .preset .questions ):
            self .current_q_idx =idx 
            self .revealed .clear ()
            self .show_correct_only =False 
            self .show_explanation =False 
            self .question_changed .emit (idx )
            self .correct_only_toggled .emit (False )
            self .explanation_toggled .emit (False )

    def toggle_answer (self ,idx ):
        if idx in self .revealed :
            self .revealed .discard (idx )
            self .answer_hidden .emit (idx )
        else :
            self .revealed .add (idx )
            self .answer_revealed .emit (idx )
        self .refresh_explanation_state ()

    def toggle_correct_only (self ):
        self .show_correct_only =not self .show_correct_only 
        if self .show_correct_only :
            self .revealed ={i for i ,a in enumerate (self .current_question .answers )if a .is_correct }
        else :
            self .revealed .clear ()
            self .show_explanation =False 
        self .correct_only_toggled .emit (self .show_correct_only )
        self .question_changed .emit (self .current_q_idx )
        self .refresh_explanation_state ()

    def set_background (self ,path ):
        self .preset .bg_image =path 
        self .bg_changed .emit (path )

    def end_game (self ):
        self .show_explanation =False 
        self .explanation_toggled .emit (False )
        self .game_ended .emit (self .preset .end_image )

    def increase_font (self ):
        self .font_scale =min (5.0 ,self .font_scale +0.1 );self .font_scale_changed .emit (self .font_scale )
    def decrease_font (self ):
        self .font_scale =max (0.5 ,self .font_scale -0.1 );self .font_scale_changed .emit (self .font_scale )
    def increase_image (self ):
        self .image_scale =min (3.0 ,self .image_scale +0.1 );self .image_scale_changed .emit (self .image_scale )
    def decrease_image (self ):
        self .image_scale =max (0.5 ,self .image_scale -0.1 );self .image_scale_changed .emit (self .image_scale )

    def set_font_family (self ,family ):
        self .font_family =family 
        _app_font [0 ]=family 
        QApplication .instance ().setFont (QFont (family ))
        self .font_family_changed .emit (family )


        # ====================== ЯЧЕЙКА ОТВЕТА ======================
class AnswerCell (QFrame ):
    def __init__ (self ,number ,answer ,revealed =False ,font_scale =1.0 ,image_scale =1.0 ,
    show_correct_only =False ,border_color =None ,bg_color =None ,parent =None ):
        super ().__init__ (parent )
        self .answer =answer 
        border_color =border_color or C ['indigo']
        bg_color =bg_color or f"rgba(10,14,26,210)"

        self .setMinimumSize (160 ,160 )
        self .setSizePolicy (QSizePolicy .Expanding ,QSizePolicy .Expanding )

        layout =QVBoxLayout (self )
        layout .setContentsMargins (16 ,16 ,16 ,16 )

        self .stack =QStackedWidget ()
        layout .addWidget (self .stack )

        # ── Скрытое ──
        hidden =QWidget ()
        hl =QVBoxLayout (hidden )
        num =QLabel (str (number ))
        num .setAlignment (Qt .AlignCenter )
        num .setStyleSheet (f"""
            color: {C ['gold']};
            font-size: {int (58 *font_scale )}px;
            font-weight: 900;
            background: transparent;
            border: none;
        """)
        hl .addWidget (num )
        self .stack .addWidget (hidden )

        # ── Открытое ──
        shown =QWidget ()
        sl =QVBoxLayout (shown )
        sl .setContentsMargins (4 ,4 ,4 ,4 )
        sl .setSpacing (8 )

        prefix ="✅ The correct answer is: "if show_correct_only and answer .is_correct else ""

        if answer .media_mode =="background"and answer .media_type =="image"and answer .media_path and os .path .exists (answer .media_path ):
            pix =QPixmap (answer .media_path ).scaled (400 ,400 ,Qt .KeepAspectRatioByExpanding ,Qt .SmoothTransformation )
            shown .setAutoFillBackground (True )
            pal =shown .palette ()
            pal .setBrush (QPalette .Window ,QBrush (pix ))
            shown .setPalette (pal )
            txt =QLabel (prefix +answer .text )
            txt .setAlignment (Qt .AlignCenter )
            txt .setWordWrap (True )
            txt .setStyleSheet (f"""
                color: white;
                font-size: {int (24 *font_scale )}px;
                font-weight: 700;
                background: rgba(0,0,0,160);
                padding: 12px 16px;
                border-radius: 12px;
                border: none;
            """)
            sl .addWidget (txt ,alignment =Qt .AlignCenter )
        else :
            txt =QLabel (prefix +answer .text )
            txt .setAlignment (Qt .AlignCenter )
            txt .setWordWrap (True )
            txt .setStyleSheet (f"""
                color: {C ['text']};
                font-size: {int (22 *font_scale )}px;
                font-weight: 700;
                background: transparent;
                border: none;
            """)
            sl .addWidget (txt )

            if answer .media_type =="image"and answer .media_path and os .path .exists (answer .media_path ):
                pix =QPixmap (answer .media_path ).scaled (
                int (260 *image_scale ),int (190 *image_scale ),
                Qt .KeepAspectRatio ,Qt .SmoothTransformation 
                )
                img =QLabel ()
                img .setPixmap (pix )
                img .setAlignment (Qt .AlignCenter )
                sl .addWidget (img )
            elif answer .media_type =="video"and answer .media_path :
                vid =QLabel ("▶  "+os .path .basename (answer .media_path ))
                vid .setAlignment (Qt .AlignCenter )
                vid .setStyleSheet (f"color:{C ['cyan']}; font-size:{int (16 *font_scale )}px; background:transparent; border:none;")
                sl .addWidget (vid )

        self .stack .addWidget (shown )
        self .stack .setCurrentIndex (1 if revealed else 0 )

        glow ="box-shadow"if False else ""
        self .setStyleSheet (f"""
            AnswerCell {{
                background: {bg_color };
                border: 2px solid {border_color };
                border-radius: 18px;
            }}
            AnswerCell:hover {{
                border: 2px solid {C ['violet']};
            }}
        """)


        # ====================== ФОНОВЫЙ ВИДЖЕТ ЗРИТЕЛЬСКОГО ОКНА ==
class _AudBg (QWidget ):
    "Central widget AudienceWindow: draws a scaled background."
    def __init__ (self ):
        super ().__init__ ()
        self ._pix =None 
        self .setAttribute (Qt .WA_OpaquePaintEvent )

    def set_pix (self ,pix ):
        self ._pix =pix 
        self .update ()

    def paintEvent (self ,_ ):
        p =QPainter (self )
        if self ._pix and not self ._pix .isNull ():
            s =self ._pix .scaled (self .size (),Qt .KeepAspectRatioByExpanding ,Qt .SmoothTransformation )
            p .drawPixmap ((self .width ()-s .width ())//2 ,(self .height ()-s .height ())//2 ,s )
        else :
            g =QLinearGradient (0 ,0 ,self .width (),self .height ())
            g .setColorAt (0 ,QColor (5 ,8 ,15 ))
            g .setColorAt (0.5 ,QColor (10 ,14 ,26 ))
            g .setColorAt (1 ,QColor (8 ,5 ,20 ))
            p .fillRect (self .rect (),g )


            # ====================== ЗРИТЕЛЬСКОЕ ОКНО ======================
class AudienceWindow (QMainWindow ):
    def __init__ (self ,controller ):
        super ().__init__ ()
        self .controller =controller 
        self .setWindowTitle ("QuizShow — Audience")
        self .setMinimumSize (1280 ,720 )

        self ._cells =[]
        self ._bg_pix =None 
        self ._end_pix =None 
        self ._game_over =False 

        self ._bg_widget =_AudBg ()
        self .setCentralWidget (self ._bg_widget )
        vl =QVBoxLayout (self ._bg_widget )
        vl .setContentsMargins (50 ,30 ,50 ,30 )
        vl .setSpacing (20 )

        self .q_lbl =QLabel ("")
        self .q_lbl .setAlignment (Qt .AlignCenter )
        self .q_lbl .setWordWrap (True )
        self .q_lbl .setSizePolicy (QSizePolicy .Expanding ,QSizePolicy .Preferred )
        self .q_lbl .setStyleSheet (f"""
            color: {C ['text']};
            font-size: 48px;
            font-weight: 800;
            background: rgba(5,8,15,200);
            border-radius: 18px;
            padding: 22px 32px;
            border: 1px solid {C ['border2']};
        """)
        vl .addWidget (self .q_lbl )

        self .q_img =QLabel ()
        self .q_img .setAlignment (Qt .AlignCenter )
        self .q_img .setSizePolicy (QSizePolicy .Preferred ,QSizePolicy .Preferred )
        self .q_img .setStyleSheet ("background: transparent;")
        self .q_img .hide ()
        vl .addWidget (self .q_img ,alignment =Qt .AlignCenter )

        self .expl_panel =QWidget ()
        self .expl_panel .setStyleSheet (f"""
            QWidget {{
                background: rgba(5,8,15,215);
                border: 1px solid {C ['border2']};
                border-radius: 18px;
            }}
        """)
        expl_l =QVBoxLayout (self .expl_panel )
        expl_l .setContentsMargins (24 ,20 ,24 ,20 )
        expl_l .setSpacing (14 )

        expl_title =QLabel ("Full answer:")
        expl_title .setAlignment (Qt .AlignCenter )
        expl_title .setStyleSheet (f"color:{C ['gold']}; font-size:16px; font-weight:900; background:transparent; border:none;")
        expl_l .addWidget (expl_title )

        self .expl_text_lbl =QLabel ("")
        self .expl_text_lbl .setAlignment (Qt .AlignCenter )
        self .expl_text_lbl .setWordWrap (True )
        self .expl_text_lbl .setStyleSheet (f"""
            color: {C ['text']};
            font-size: 26px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        expl_l .addWidget (self .expl_text_lbl )

        self .expl_img =QLabel ()
        self .expl_img .setAlignment (Qt .AlignCenter )
        self .expl_img .setStyleSheet ("background: transparent;")
        self .expl_img .hide ()
        expl_l .addWidget (self .expl_img ,alignment =Qt .AlignCenter )

        self .expl_panel .hide ()
        vl .addWidget (self .expl_panel )

        self .ans_container =QWidget ()
        self .ans_container .setStyleSheet ("background: transparent;")
        self .ans_container .setSizePolicy (QSizePolicy .Expanding ,QSizePolicy .Expanding )
        self .ans_grid =QGridLayout (self .ans_container )
        self .ans_grid .setSpacing (20 )

        scroll =QScrollArea ()
        scroll .setWidgetResizable (True )
        scroll .setWidget (self .ans_container )
        scroll .setStyleSheet ("QScrollArea{border:none; background:transparent;}")
        scroll .viewport ().setStyleSheet ("background: transparent;")
        scroll .setHorizontalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        vl .addWidget (scroll ,1 )

        controller .question_changed .connect (self ._load_q )
        controller .answer_revealed .connect (self ._reveal )
        controller .answer_hidden .connect (self ._hide )
        controller .bg_changed .connect (self ._set_bg )
        controller .game_ended .connect (self ._end_game )
        controller .correct_only_toggled .connect (self ._load_q )
        controller .explanation_toggled .connect (self ._toggle_explanation )
        controller .font_scale_changed .connect (self ._load_q )
        controller .image_scale_changed .connect (self ._load_q )
        controller .colors_changed .connect (self ._load_q )
        controller .font_family_changed .connect (self ._on_font_changed )

        # Minimal stylesheet: scrollbars only, no opaque QWidget backgrounds
        self .setStyleSheet ("""
            QScrollBar:vertical { background: transparent; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,0.18); border-radius: 3px; min-height: 30px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        if controller .preset .bg_image and os .path .exists (controller .preset .bg_image ):
            self ._set_bg (controller .preset .bg_image )
        if controller .preset .questions :
            self ._load_q (0 )

    def _on_font_changed (self ,family ):
    # Font propagated via QApplication.setFont(); just rebuild cells
        self ._load_q ()

    def _set_bg (self ,path ):
        self ._bg_pix =QPixmap (path )if path and os .path .exists (path )else None 
        if not self ._game_over :
            self ._bg_widget .set_pix (self ._bg_pix )

    def _load_q (self ,_ =None ):
        self ._cells .clear ()
        while self .ans_grid .count ():
            item =self .ans_grid .takeAt (0 )
            if item .widget ():item .widget ().deleteLater ()

        q =self .controller .current_question 
        if not q :return 

        self .q_lbl .setText (q .text )

        if q .q_type in (3 ,4 )and q .image_path and os .path .exists (q .image_path ):
            scale =getattr (q ,'q_image_scale',1.0 )
            pix =QPixmap (q .image_path ).scaled (int (820 *scale ),int (480 *scale ),Qt .KeepAspectRatio ,Qt .SmoothTransformation )
            self .q_img .setPixmap (pix )
            self .q_img .show ()
        else :
            self .q_img .hide ()

        expl_text =(q .explanation_text or '').strip ()
        expl_scale =getattr (q ,'explanation_text_scale',1.0 )
        self .expl_text_lbl .setStyleSheet (f"""
            color: {C ['text']};
            font-size: {int (26 *self .controller .font_scale *expl_scale )}px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        self .expl_text_lbl .setText (expl_text )
        self .expl_text_lbl .setVisible (bool (expl_text ))
        if q .explanation_image_path and os .path .exists (q .explanation_image_path ):
            scale =getattr (q ,'explanation_image_scale',1.0 )
            pix =QPixmap (q .explanation_image_path ).scaled (int (760 *scale ),int (430 *scale ),Qt .KeepAspectRatio ,Qt .SmoothTransformation )
            self .expl_img .setPixmap (pix )
            self .expl_img .show ()
        else :
            self .expl_img .clear ()
            self .expl_img .hide ()
        explanation_visible =self .controller .show_explanation and self .controller .question_has_explanation ()
        self .expl_panel .setVisible (explanation_visible )
        self .ans_container .setVisible (not explanation_visible )

        cols =2 
        for i ,ans in enumerate (q .answers ):
            revealed =(self .controller .show_correct_only and ans .is_correct )or (not self .controller .show_correct_only and (q .q_type in (2 ,4 )or i in self .controller .revealed ))
            cell =AnswerCell (i +1 ,ans ,revealed ,
            self .controller .font_scale *getattr (q ,"answer_text_scale",1.0 ),self .controller .image_scale ,
            self .controller .show_correct_only ,
            self .controller .preset .cell_border_color ,
            self .controller .preset .cell_bg_color )
            r ,c =divmod (i ,cols )
            self .ans_grid .addWidget (cell ,r ,c )
            self ._cells .append (cell )

    def _reveal (self ,idx ):
        if 0 <=idx <len (self ._cells ):
            self ._cells [idx ].stack .setCurrentIndex (1 )

    def _hide (self ,idx ):
        if 0 <=idx <len (self ._cells ):
            self ._cells [idx ].stack .setCurrentIndex (0 )

    def _toggle_explanation (self ,visible ):
        show =visible and self .controller .question_has_explanation ()
        self .expl_panel .setVisible (show )
        self .ans_container .setVisible (not show )

    def _end_game (self ,path ):
        self ._game_over =True 
        self ._end_pix =QPixmap (path )if path and os .path .exists (path )else None 
        self .q_lbl .hide ();self .q_img .hide ();self .expl_panel .hide ();self .ans_container .hide ()
        # Показать финальную картинку (или градиент если не задана)
        self ._bg_widget .set_pix (self ._end_pix )


        # ====================== ХОСТ ======================
class HostWindow (QMainWindow ):
    def __init__ (self ,controller ):
        super ().__init__ ()
        self .controller =controller 
        self .setWindowTitle ("QuizShow - Host")
        self .setMinimumSize (1050 ,700 )
        self ._btns =[]
        self .setStyleSheet (get_global_style ())

        central =QWidget ()
        self .setCentralWidget (central )
        ml =QVBoxLayout (central )
        ml .setContentsMargins (16 ,16 ,16 ,16 )
        ml .setSpacing (10 )

        # ── Header ──
        hdr =QWidget ()
        hdr .setStyleSheet (f"""
            QWidget {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 rgba(99,102,241,0.25), stop:1 rgba(139,92,246,0.15));
                border: 1px solid {C ['border2']};
                border-radius: 12px;
            }}
        """)
        hdr_l =QHBoxLayout (hdr )
        hdr_l .setContentsMargins (20 ,12 ,20 ,12 )
        logo =QLabel ("🎮 HOST PANEL")
        logo .setStyleSheet (f"color:{C ['text']}; font-size:18px; font-weight:800; background:transparent; border:none;")
        hdr_l .addWidget (logo )
        hdr_l .addStretch ()
        ml .addWidget (hdr )

        splitter =QSplitter (Qt .Horizontal )
        ml .addWidget (splitter ,1 )

        # ── Левая панель — список вопросов ──
        lw =QWidget ()
        lw .setStyleSheet (f"background: {C ['bg2']}; border-radius: 12px;")
        ll =QVBoxLayout (lw )
        ll .setContentsMargins (12 ,12 ,12 ,12 );ll .setSpacing (8 )
        lbl_q =QLabel ("📋 Questions")
        lbl_q .setStyleSheet (f"color:{C ['subtext']}; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px;")
        ll .addWidget (lbl_q )
        self .q_list =QListWidget ()
        self .q_list .currentRowChanged .connect (self ._nav_to )
        ll .addWidget (self .q_list )
        splitter .addWidget (lw )

        # ── Правая панель ──
        rw =QWidget ()
        rw .setStyleSheet ("background: transparent;")
        rl =QVBoxLayout (rw )
        rl .setContentsMargins (12 ,0 ,0 ,0 );rl .setSpacing (10 )

        self .type_lbl =QLabel ()
        self .type_lbl .setStyleSheet (f"""
            color: {C ['violet']};
            font-size: 12px;
            font-weight: 700;
            background: rgba(139,92,246,0.12);
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid rgba(139,92,246,0.3);
        """)
        rl .addWidget (self .type_lbl ,alignment =Qt .AlignLeft )

        self .q_text =QLabel ()
        self .q_text .setWordWrap (True )
        self .q_text .setStyleSheet (f"""
            font-size: 17px;
            font-weight: 700;
            background: {C ['bg2']};
            color: {C ['text']};
            padding: 14px 18px;
            border-radius: 12px;
            border: 1px solid {C ['border']};
        """)
        rl .addWidget (self .q_text )

        self .ans_grid_widget =QWidget ()
        self .ans_grid_widget .setStyleSheet ("background:transparent;")
        self .ans_grid =QGridLayout (self .ans_grid_widget )
        self .ans_grid .setSpacing (8 )
        rl .addWidget (self .ans_grid_widget ,1 )

        # ── Навигация ──
        nav =QHBoxLayout ()
        prev =QPushButton ("◀ Previous")
        nxt =QPushButton ("Next ▶")
        style_btn (prev ,C ['bg3'],C ['text'])
        style_btn (nxt ,C ['bg3'],C ['text'])
        prev .clicked .connect (lambda :self ._nav (-1 ))
        nxt .clicked .connect (lambda :self ._nav (1 ))
        nav .addWidget (prev );nav .addWidget (nxt )
        rl .addLayout (nav )

        rl .addWidget (make_separator ())

        # ── Действия с ответами ──
        acts =QHBoxLayout ()
        ra =QPushButton ("👁 Open all")
        ha =QPushButton ("🙈 Close all")
        ca =QPushButton ("✅ Only the right one")
        self .expl_btn =QPushButton ("📝 Explanation")
        style_btn (ra ,C ['green'])
        style_btn (ha ,"#7C3AED")
        style_btn (ca ,C ['orange'])
        style_btn (self .expl_btn ,C ['cyan'],C ['bg0'])
        self .expl_btn .setCheckable (True )
        ra .clicked .connect (self ._reveal_all )
        ha .clicked .connect (self ._hide_all )
        ca .clicked .connect (self .controller .toggle_correct_only )
        self .expl_btn .clicked .connect (lambda _ :self .controller .toggle_explanation ())
        acts .addWidget (ra );acts .addWidget (ha );acts .addWidget (ca );acts .addWidget (self .expl_btn )
        rl .addLayout (acts )

        # ── Цвета ──
        color_row =QHBoxLayout ()
        border_btn =QPushButton ("🎨 Cell border color")
        bg_btn =QPushButton ("🎨 Cell background color")
        style_btn (border_btn ,C ['bg3'],C ['subtext'])
        style_btn (bg_btn ,C ['bg3'],C ['subtext'])
        border_btn .clicked .connect (self ._change_border_color )
        bg_btn .clicked .connect (self ._change_bg_color )
        color_row .addWidget (border_btn );color_row .addWidget (bg_btn )
        rl .addLayout (color_row )

        rl .addWidget (make_separator ())

        # ── Нижняя панель ──
        bot =QHBoxLayout ()
        bg_b =QPushButton ("🖼 Change background")
        end_b =QPushButton ("🏁 Game over")
        style_btn (bg_b ,C ['bg3'],C ['subtext'])
        style_btn (end_b ,C ['red'])
        bg_b .clicked .connect (self ._chg_bg )
        end_b .clicked .connect (self .controller .end_game )

        scl =QHBoxLayout ()
        scl .setSpacing (6 )
        for txt ,fn ,col in [
        ("T+",self .controller .increase_font ,C ['indigo']),
        ("T−",self .controller .decrease_font ,C ['bg3']),
        ("I+",self .controller .increase_image ,C ['cyan']),
        ("I−",self .controller .decrease_image ,C ['bg3']),
        ]:
            b =QPushButton (txt )
            b .setFixedSize (42 ,36 )
            style_btn (b ,col ,C ['text'])
            b .clicked .connect (fn )
            scl .addWidget (b )

            # ── Шрифт ──
        font_lbl =QLabel ("🔤")
        font_lbl .setStyleSheet (f"color:{C ['subtext']}; font-size:15px; background:transparent; border:none;")
        self .font_combo =QComboBox ()
        self .font_combo .setFixedWidth (148 )
        for name ,_ ,_ in FONT_OPTIONS :
            self .font_combo .addItem (name )
        cur_name =next ((n for n ,_ ,_ in FONT_OPTIONS if _font_map .get (n ,n )==controller .font_family ),FONT_OPTIONS [0 ][0 ])
        self .font_combo .setCurrentText (cur_name )
        self .font_combo .currentTextChanged .connect (self ._on_font_combo )

        bot .addWidget (bg_b );bot .addWidget (end_b );bot .addStretch ()
        bot .addWidget (font_lbl );bot .addWidget (self .font_combo )
        bot .addLayout (scl )
        rl .addLayout (bot )

        splitter .addWidget (rw )
        splitter .setSizes ([280 ,770 ])

        controller .question_changed .connect (self ._load_q )
        controller .answer_revealed .connect (self ._mark_rev )
        controller .answer_hidden .connect (self ._mark_hid )
        controller .correct_only_toggled .connect (lambda _ :self ._load_q (self .controller .current_q_idx ))
        controller .explanation_toggled .connect (self ._sync_expl_button )
        controller .colors_changed .connect (lambda :self ._load_q (self .controller .current_q_idx ))
        controller .font_family_changed .connect (self ._on_font_signal )

        self ._refresh_list ()
        if self .controller .preset .questions :
            self ._load_q (0 )

    def _on_font_combo (self ,name ):
        family =_font_map .get (name ,name )
        self .controller .set_font_family (family )

    def _on_font_signal (self ,family ):
        self .setStyleSheet (get_global_style (family ))
        self ._load_q (self .controller .current_q_idx )

    def _change_border_color (self ):
        color =QColorDialog .getColor (QColor (self .controller .preset .cell_border_color ),self )
        if color .isValid ():
            self .controller .preset .cell_border_color =color .name ()
            self .controller .colors_changed .emit ()

    def _change_bg_color (self ):
        color =QColorDialog .getColor ()
        if color .isValid ():
            self .controller .preset .cell_bg_color =f"rgba({color .red ()},{color .green ()},{color .blue ()},210)"
            self .controller .colors_changed .emit ()

    def _refresh_list (self ):
        self .q_list .clear ()
        for i ,q in enumerate (self .controller .preset .questions ):
            self .q_list .addItem (f"  {i +1 }.  [T{q .q_type }]  {q .text [:38 ]}")

    def _nav_to (self ,row ):
        if row >=0 :self .controller .go_to_question (row )

    def _load_q (self ,idx =None ):
        if idx is None or isinstance (idx ,bool ):
            idx =self .controller .current_q_idx 
        q =self .controller .current_question 
        if not q :return 

        self .type_lbl .setText (TYPE_NAMES_HOST .get (q .q_type ,""))
        self .q_text .setText (q .text )

        self ._btns .clear ()
        while self .ans_grid .count ():
            item =self .ans_grid .takeAt (0 )
            if item .widget ():item .widget ().deleteLater ()

        cols =max (1 ,min (3 ,len (q .answers )))
        for i ,ans in enumerate (q .answers ):
            btn =QPushButton (f"  {i +1 }.  {ans .text [:38 ]}")
            btn .setMinimumSize (180 ,52 )
            btn .setCheckable (True )

            should_be_checked =(self .controller .show_correct_only and ans .is_correct )or (not self .controller .show_correct_only and (q .q_type in (2 ,4 )or i in self .controller .revealed ))

            btn .setStyleSheet (f"""
                QPushButton {{
                    background: {C ['bg2']};
                    color: {C ['subtext']};
                    border: 1px solid {C ['border']};
                    border-radius: 8px;
                    font-weight: 600;
                    text-align: left;
                    padding: 0 14px;
                }}
                QPushButton:hover {{
                    background: {C ['bg3']};
                    color: {C ['text']};
                    border: 1px solid {C ['border2']};
                }}
                QPushButton:checked {{
                    background: rgba(99,102,241,0.2);
                    color: {C ['text']};
                    border: 1px solid {C ['indigo']};
                }}
            """)
            btn .blockSignals (True )
            btn .setChecked (should_be_checked )
            btn .blockSignals (False )
            btn .toggled .connect (partial (self ._on_toggle ,i ))

            r ,c =divmod (i ,cols )
            self .ans_grid .addWidget (btn ,r ,c )
            self ._btns .append (btn )

        has_expl =self .controller .question_has_explanation ()
        can_show_expl =self .controller .can_show_explanation ()
        self .expl_btn .setEnabled (has_expl and can_show_expl )
        self ._sync_expl_button (self .controller .show_explanation )
        self .expl_btn .setToolTip ("Shows the full explanation"if has_expl else "No explanation is set for this question")

        self .q_list .blockSignals (True )
        self .q_list .setCurrentRow (idx )
        self .q_list .blockSignals (False )

    def _on_toggle (self ,idx ,checked ):
        btn =self ._btns [idx ];btn .blockSignals (True )
        try :
            if checked :
                self .controller .revealed .add (idx );self .controller .answer_revealed .emit (idx )
            else :
                self .controller .revealed .discard (idx );self .controller .answer_hidden .emit (idx )
            self .controller .refresh_explanation_state ()
            self .expl_btn .setEnabled (self .controller .question_has_explanation ()and self .controller .can_show_explanation ())
        finally :
            btn .blockSignals (False )

    def _mark_rev (self ,idx ):
        if 0 <=idx <len (self ._btns ):
            b =self ._btns [idx ];b .blockSignals (True );b .setChecked (True );b .blockSignals (False )
        self .expl_btn .setEnabled (self .controller .question_has_explanation ()and self .controller .can_show_explanation ())

    def _mark_hid (self ,idx ):
        if 0 <=idx <len (self ._btns ):
            b =self ._btns [idx ];b .blockSignals (True );b .setChecked (False );b .blockSignals (False )
        self .expl_btn .setEnabled (self .controller .question_has_explanation ()and self .controller .can_show_explanation ())

    def _sync_expl_button (self ,visible ):
        self .expl_btn .blockSignals (True )
        self .expl_btn .setChecked (visible )
        self .expl_btn .blockSignals (False )

    def _nav (self ,delta ):
        ni =self .controller .current_q_idx +delta 
        if 0 <=ni <len (self .controller .preset .questions ):
            self .controller .go_to_question (ni )

    def _reveal_all (self ):
        q =self .controller .current_question 
        if q :
            for i in range (len (q .answers )):
                self .controller .revealed .add (i );self .controller .answer_revealed .emit (i )
            self .controller .refresh_explanation_state ()
            self .expl_btn .setEnabled (self .controller .question_has_explanation ()and self .controller .can_show_explanation ())

    def _hide_all (self ):
        q =self .controller .current_question 
        if q :
            self .controller .revealed .clear ()
            self .controller .show_explanation =False 
            for i in range (len (q .answers )):
                self .controller .answer_hidden .emit (i )
            self .controller .refresh_explanation_state ()
            self .expl_btn .setEnabled (self .controller .question_has_explanation ()and self .controller .can_show_explanation ())

    def _chg_bg (self ):
        p ,_ =QFileDialog .getOpenFileName (self ,"Background","","Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if p :self .controller .set_background (p )


        # ====================== ВИДЖЕТ ОТВЕТА ======================
class AnswerEditWidget (QWidget ):
    def __init__ (self ,answer ,parent =None ):
        super ().__init__ (parent )
        self ._media_path =answer .media_path 
        layout =QHBoxLayout (self )
        layout .setContentsMargins (0 ,0 ,0 ,0 );layout .setSpacing (6 )

        self .text_edit =QLineEdit (answer .text )
        self .text_edit .setPlaceholderText ("Answer text...")
        layout .addWidget (self .text_edit ,3 )

        self .correct_cb =QCheckBox ("✓ Correct")
        self .correct_cb .setChecked (answer .is_correct )
        layout .addWidget (self .correct_cb )

        self .media_type_cb =QComboBox ()
        self .media_type_cb .addItems (["none","image","video"])
        mt_idx =["none","image","video"].index (answer .media_type )if answer .media_type in ["none","image","video"]else 0 
        self .media_type_cb .setCurrentIndex (mt_idx )
        self .media_type_cb .setFixedWidth (80 )
        self .media_type_cb .currentIndexChanged .connect (self ._on_type_changed )
        layout .addWidget (self .media_type_cb )

        self .media_mode_cb =QComboBox ()
        self .media_mode_cb .addItems (["inline","background"])
        self .media_mode_cb .setCurrentIndex (0 if answer .media_mode !="background"else 1 )
        self .media_mode_cb .setFixedWidth (100 )
        layout .addWidget (self .media_mode_cb )

        self .file_lbl =QLabel (os .path .basename (answer .media_path )if answer .media_path else "—")
        self .file_lbl .setStyleSheet (f"color:{C ['muted']}; min-width:70px;")
        self .file_lbl .setMaximumWidth (130 )
        layout .addWidget (self .file_lbl ,1 )

        self .pick_btn =QPushButton ("📎")
        self .pick_btn .setFixedWidth (36 )
        self .pick_btn .setToolTip ("Choose file")
        self .pick_btn .clicked .connect (self ._pick_file )
        layout .addWidget (self .pick_btn )

        self ._on_type_changed ()

    def _on_type_changed (self ):
        mt =self .media_type_cb .currentText ()
        self .file_lbl .setVisible (mt !="none")
        self .pick_btn .setVisible (mt !="none")
        self .media_mode_cb .setVisible (mt =="image")

    def _pick_file (self ):
        mt =self .media_type_cb .currentText ()
        if mt =="image":
            p ,_ =QFileDialog .getOpenFileName (self ,"Image","","Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)")
        elif mt =="video":
            p ,_ =QFileDialog .getOpenFileName (self ,"Video","","Video (*.mp4 *.avi *.mov *.mkv)")
        else :return 
        if p :
            self ._media_path =p 
            self .file_lbl .setText (os .path .basename (p ))

    def get_answer (self ):
        a =AnswerData ()
        a .text =self .text_edit .text ().strip ()
        a .is_correct =self .correct_cb .isChecked ()
        a .media_type =self .media_type_cb .currentText ()
        a .media_mode =self .media_mode_cb .currentText ()
        a .media_path =self ._media_path if a .media_type !="none"else ""
        return a 


        # ====================== РЕДАКТОР ВОПРОСА ======================
class QuestionEditDialog (QDialog ):
    def __init__ (self ,question =None ,parent =None ):
        super ().__init__ (parent )
        self .q =copy .deepcopy (question )if question else QuestionData ()
        if not self .q .answers :
            self .q .answers =[AnswerData ()for _ in range (4 )]
        self .setWindowTitle ("Question Editor")
        self .setMinimumSize (1000 ,820 )
        self ._editors =[]
        self .setStyleSheet (get_global_style ())
        self ._build ()

    def _build (self ):
        l =QVBoxLayout (self )
        l .setSpacing (10 )

        # Тип вопроса
        tr =QHBoxLayout ()
        lbl =QLabel ("Question type")
        lbl .setStyleSheet (f"color:{C ['subtext']}; font-weight:700;")
        tr .addWidget (lbl )
        self .type_cb =QComboBox ()
        for k ,v in TYPE_NAMES_HOST .items ():
            self .type_cb .addItem (v ,k )
        self .type_cb .setCurrentIndex (self .q .q_type -1 )
        self .type_cb .currentIndexChanged .connect (self ._type_change )
        tr .addWidget (self .type_cb ,1 )
        l .addLayout (tr )

        # Текст вопроса
        lbl2 =QLabel ("Question text")
        lbl2 .setStyleSheet (f"color:{C ['subtext']}; font-weight:700;")
        l .addWidget (lbl2 )
        self .q_txt =QTextEdit (self .q .text )
        self .q_txt .setMaximumHeight (80 )
        l .addWidget (self .q_txt )

        # ── Слайдеры в сетке ──
        sliders_row =QHBoxLayout ()
        sliders_row .setSpacing (8 )

        def make_slider_group (title ,min_v ,max_v ,val ):
            gb =QGroupBox (title )
            gh =QHBoxLayout (gb )
            gh .setContentsMargins (8 ,6 ,8 ,6 )
            sl =QSlider (Qt .Horizontal )
            sl .setRange (min_v ,max_v )
            sl .setValue (val )
            vl =QLabel (f"{val }%")
            vl .setFixedWidth (42 )
            vl .setStyleSheet (f"color:{C ['indigo']}; font-weight:700;")
            sl .valueChanged .connect (lambda v ,lb =vl :lb .setText (f"{v }%"))
            gh .addWidget (sl );gh .addWidget (vl )
            return gb ,sl 

        tg ,self .text_slider =make_slider_group ("Question text",50 ,200 ,int (self .q .text_scale *100 ))
        atg ,self .ans_text_slider =make_slider_group ("Answer text",50 ,500 ,int (self .q .answer_text_scale *100 ))
        ig ,self .img_slider =make_slider_group ("Answer images",50 ,300 ,int (self .q .answer_image_scale *100 ))

        self .text_slider .valueChanged .connect (lambda v :setattr (self .q ,'text_scale',v /100 ))
        self .ans_text_slider .valueChanged .connect (lambda v :setattr (self .q ,'answer_text_scale',v /100 ))
        self .img_slider .valueChanged .connect (lambda v :setattr (self .q ,'answer_image_scale',v /100 ))

        sliders_row .addWidget (tg );sliders_row .addWidget (atg );sliders_row .addWidget (ig )
        l .addLayout (sliders_row )

        # Картинка вопроса (тип 3/4)
        self .q_img_group ,self .q_img_slider =make_slider_group (
        "Picture of the question (above the answers)",20 ,200 ,int (getattr (self .q ,'q_image_scale',1.0 )*100 )
        )
        self .q_img_slider .valueChanged .connect (lambda v :setattr (self .q ,'q_image_scale',v /100 ))
        l .addWidget (self .q_img_group )
        self .q_img_group .setVisible (self .q .q_type in (3 ,4 ))

        self .img_row =QWidget ()
        ir =QHBoxLayout (self .img_row )
        ir .setContentsMargins (0 ,0 ,0 ,0 )
        lbl_img =QLabel ("Question picture:")
        lbl_img .setStyleSheet (f"color:{C ['subtext']}; font-weight:700;")
        ir .addWidget (lbl_img )
        self .img_lbl =QLabel (os .path .basename (self .q .image_path )if self .q .image_path else "- not selected -")
        self .img_lbl .setStyleSheet (f"color:{C ['muted']};")
        ir .addWidget (self .img_lbl ,1 )
        pick =QPushButton ("📂 Select");style_btn (pick ,C ['bg3'],C ['subtext']);pick .clicked .connect (self ._pick_img )
        ir .addWidget (pick )
        l .addWidget (self .img_row )
        self .img_row .setVisible (self .q .q_type in (3 ,4 ))

        l .addWidget (make_separator ())

        lbl_expl =QLabel ("Full answer:")
        lbl_expl .setStyleSheet (f"color:{C ['subtext']}; font-weight:700;")
        l .addWidget (lbl_expl )

        self .expl_txt =QTextEdit (getattr (self .q ,'explanation_text',''))
        self .expl_txt .setPlaceholderText ("The text that will appear after opening the correct answer...")
        self .expl_txt .setMaximumHeight (120 )
        l .addWidget (self .expl_txt )

        self .expl_text_group ,self .expl_text_slider =make_slider_group (
        "Explanation text size",50 ,300 ,int (getattr (self .q ,'explanation_text_scale',1.0 )*100 )
        )
        self .expl_text_slider .valueChanged .connect (lambda v :setattr (self .q ,'explanation_text_scale',v /100 ))
        l .addWidget (self .expl_text_group )

        self .expl_img_group ,self .expl_img_slider =make_slider_group (
        "Explanation image",20 ,250 ,int (getattr (self .q ,'explanation_image_scale',1.0 )*100 )
        )
        self .expl_img_slider .valueChanged .connect (lambda v :setattr (self .q ,'explanation_image_scale',v /100 ))
        l .addWidget (self .expl_img_group )

        self .expl_row =QWidget ()
        er =QHBoxLayout (self .expl_row )
        er .setContentsMargins (0 ,0 ,0 ,0 )
        lbl_expl_img =QLabel ("Picture explanation:")
        lbl_expl_img .setStyleSheet (f"color:{C ['subtext']}; font-weight:700;")
        er .addWidget (lbl_expl_img )
        self .expl_img_lbl =QLabel (os .path .basename (getattr (self .q ,'explanation_image_path',''))if getattr (self .q ,'explanation_image_path','')else "- not selected -")
        self .expl_img_lbl .setStyleSheet (f"color:{C ['muted']};")
        er .addWidget (self .expl_img_lbl ,1 )
        pick_expl =QPushButton ("📂 Select")
        style_btn (pick_expl ,C ['bg3'],C ['subtext'])
        pick_expl .clicked .connect (self ._pick_expl_img )
        er .addWidget (pick_expl )
        l .addWidget (self .expl_row )

        l .addWidget (make_separator ())

        lbl3 =QLabel ("Answer options")
        lbl3 .setStyleSheet (f"color:{C ['subtext']}; font-weight:700;")
        l .addWidget (lbl3 )

        scroll =QScrollArea ()
        scroll .setWidgetResizable (True )
        cont =QWidget ()
        self .ans_lay =QVBoxLayout (cont )
        self .ans_lay .setSpacing (4 )
        scroll .setWidget (cont )
        l .addWidget (scroll ,1 )

        for a in self .q .answers :
            self ._add_ans_row (a )

        btn_row =QHBoxLayout ();btn_row .setSpacing (8 )
        add =QPushButton ("＋ Add a reply");style_btn (add ,C ['green'])
        rem =QPushButton ("－ Delete the last one");style_btn (rem ,C ['red'])
        add .clicked .connect (lambda _ :self ._add_ans_row ())
        rem .clicked .connect (self ._rem_last )
        btn_row .addWidget (add );btn_row .addWidget (rem );btn_row .addStretch ()
        l .addLayout (btn_row )

        preview_btn =QPushButton ("👀 Question preview")
        preview_btn .setMinimumHeight (42 )
        style_btn (preview_btn ,f"qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {C ['indigo']},stop:1 {C ['violet']})")
        preview_btn .clicked .connect (self .show_preview )
        l .addWidget (preview_btn )

        db =QDialogButtonBox (QDialogButtonBox .Ok |QDialogButtonBox .Cancel )
        db .accepted .connect (self .accept );db .rejected .connect (self .reject )
        l .addWidget (db )

    def _type_change (self ):
        self .q .q_type =self .type_cb .currentData ()
        v =self .q .q_type in (3 ,4 )
        self .img_row .setVisible (v );self .q_img_group .setVisible (v )

    def _pick_img (self ):
        p ,_ =QFileDialog .getOpenFileName (self ,"Picture","","Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if p :self .q .image_path =p ;self .img_lbl .setText (os .path .basename (p ))

    def _pick_expl_img (self ):
        p ,_ =QFileDialog .getOpenFileName (self ,"Explanation image","","Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)")
        if p :
            self .q .explanation_image_path =p 
            self .expl_img_lbl .setText (os .path .basename (p ))

    def _add_ans_row (self ,ans =None ):
        if ans is None :
            ans =AnswerData ();self .q .answers .append (ans )
        row =QWidget ()
        row .setStyleSheet (f"background:{C ['bg2']}; border-radius:8px;")
        rl =QHBoxLayout (row );rl .setContentsMargins (8 ,4 ,8 ,4 )
        n =QLabel (f"{len (self ._editors )+1 }.")
        n .setFixedWidth (28 )
        n .setStyleSheet (f"color:{C ['muted']}; font-weight:700; background:transparent;")
        rl .addWidget (n )
        ed =AnswerEditWidget (ans )
        rl .addWidget (ed ,1 )
        self .ans_lay .addWidget (row )
        self ._editors .append (ed )

    def _rem_last (self ):
        if len (self ._editors )>1 :
            self ._editors .pop ();self .q .answers .pop ()
            item =self .ans_lay .takeAt (self .ans_lay .count ()-1 )
            if item and item .widget ():item .widget ().deleteLater ()

    def get_question (self ):
        self .q .text =self .q_txt .toPlainText ().strip ()
        self .q .q_type =self .type_cb .currentData ()
        self .q .answers =[e .get_answer ()for e in self ._editors ]
        self .q .explanation_text =self .expl_txt .toPlainText ().strip ()
        return self .q 

    def show_preview (self ):
        preview =PreviewDialog (self .get_question (),self )
        preview .exec_ ()


        # ====================== ПРЕВЬЮ ======================
class PreviewDialog (QDialog ):
    def __init__ (self ,question ,parent =None ):
        super ().__init__ (parent )
        self .setWindowTitle ("Preview")
        self .resize (1200 ,820 )
        self .setStyleSheet (get_global_style ()+f"QDialog{{background:{C ['bg0']};}}")

        layout =QVBoxLayout (self );layout .setSpacing (16 )

        q_lbl =QLabel (question .text or "(question text not asked)")
        q_lbl .setAlignment (Qt .AlignCenter );q_lbl .setWordWrap (True )
        q_lbl .setStyleSheet (f"""
            color:{C ['text']}; font-size:28px; font-weight:800;
            background:rgba(5,8,15,200); border-radius:14px;
            padding:16px 24px; border:1px solid {C ['border2']};
        """)
        layout .addWidget (q_lbl )

        if question .q_type in (3 ,4 )and question .image_path and os .path .exists (question .image_path ):
            scale =getattr (question ,'q_image_scale',1.0 )
            pix =QPixmap (question .image_path ).scaled (int (820 *scale ),int (480 *scale ),Qt .KeepAspectRatio ,Qt .SmoothTransformation )
            img_lbl =QLabel ();img_lbl .setPixmap (pix );img_lbl .setAlignment (Qt .AlignCenter )
            layout .addWidget (img_lbl ,alignment =Qt .AlignCenter )

        if (question .explanation_text or '').strip ()or getattr (question ,'explanation_image_path',''):
            expl_box =QWidget ()
            expl_box .setStyleSheet (f"background: rgba(5,8,15,215); border:1px solid {C ['border2']}; border-radius:14px;")
            expl_l =QVBoxLayout (expl_box )
            expl_l .setContentsMargins (18 ,16 ,18 ,16 )
            expl_l .setSpacing (10 )
            title =QLabel ("Full answer:")
            title .setAlignment (Qt .AlignCenter )
            title .setStyleSheet (f"color:{C ['gold']}; font-size:16px; font-weight:900; background:transparent; border:none;")
            expl_l .addWidget (title )
            if (question .explanation_text or '').strip ():
                expl_text =QLabel (question .explanation_text .strip ())
                expl_text .setAlignment (Qt .AlignCenter )
                expl_text .setWordWrap (True )
                expl_text_scale =getattr (question ,'explanation_text_scale',1.0 )
                expl_text .setStyleSheet (f"color:{C ['text']}; font-size:{int (20 *expl_text_scale )}px; font-weight:600; background:transparent; border:none;")
                expl_l .addWidget (expl_text )
            if getattr (question ,'explanation_image_path','')and os .path .exists (question .explanation_image_path ):
                scale =getattr (question ,'explanation_image_scale',1.0 )
                pix =QPixmap (question .explanation_image_path ).scaled (int (680 *scale ),int (380 *scale ),Qt .KeepAspectRatio ,Qt .SmoothTransformation )
                expl_img =QLabel ()
                expl_img .setPixmap (pix )
                expl_img .setAlignment (Qt .AlignCenter )
                expl_l .addWidget (expl_img ,alignment =Qt .AlignCenter )
            layout .addWidget (expl_box )

        container =QWidget ();container .setStyleSheet ("background:transparent;")
        grid =QGridLayout (container );grid .setSpacing (16 )
        cols =2 
        for i ,ans in enumerate (question .answers ):
            cell =AnswerCell (i +1 ,ans ,revealed =True ,
            font_scale =question .answer_text_scale ,
            image_scale =question .answer_image_scale )
            r ,c =divmod (i ,cols )
            grid .addWidget (cell ,r ,c )

        scroll =QScrollArea ();scroll .setWidgetResizable (True );scroll .setWidget (container )
        scroll .setStyleSheet ("QScrollArea{border:none; background:transparent;}")
        layout .addWidget (scroll ,1 )


        # ====================== ГЛАВНОЕ ОКНО ======================
class EditorWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle (f"{APP_TITLE }")
        self .setMinimumSize (1020 ,720 )
        self .preset =PresetData ()
        self .game_wins =[]
        self .setStyleSheet (get_global_style ())
        self ._build_ui ()

    def _build_ui (self ):
        cw =QWidget ();self .setCentralWidget (cw )
        ml =QVBoxLayout (cw )
        ml .setContentsMargins (28 ,24 ,28 ,24 )
        ml .setSpacing (14 )

        # ── Hero header ──
        hero =QWidget ()
        hero .setStyleSheet (f"""
            QWidget {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 rgba(99,102,241,0.18), stop:0.5 rgba(139,92,246,0.12), stop:1 rgba(34,211,238,0.08));
                border: 1px solid {C ['border2']};
                border-radius: 16px;
            }}
        """)
        hero_l =QVBoxLayout (hero );hero_l .setContentsMargins (24 ,20 ,24 ,20 )
        title =QLabel ("🎮  QuizShow")
        title .setAlignment (Qt .AlignCenter )
        title .setStyleSheet (f"""
            font-size: 34px; font-weight: 900;
            background: transparent; border: none;
            color: {C ['text']};
        """)
        sub =QLabel ("Quiz editor")
        sub .setAlignment (Qt .AlignCenter )
        sub .setStyleSheet (f"color:{C ['muted']}; font-size:13px; background:transparent; border:none;")
        hero_l .addWidget (title );hero_l .addWidget (sub )
        ml .addWidget (hero )

        # ── Пресет ──
        preset_card =QWidget ()
        preset_card .setStyleSheet (f"background:{C ['bg2']}; border:1px solid {C ['border']}; border-radius:12px;")
        pc_l =QHBoxLayout (preset_card );pc_l .setContentsMargins (16 ,12 ,16 ,12 );pc_l .setSpacing (10 )
        lbl_n =QLabel ("Preset")
        lbl_n .setStyleSheet (f"color:{C ['muted']}; font-weight:700; font-size:12px;")
        pc_l .addWidget (lbl_n )
        self .name_edit =QLineEdit (self .preset .name )
        pc_l .addWidget (self .name_edit ,1 )
        for txt ,col ,fn in [
        ("💾 Save",C ['green'],self ._save ),
        ("📂 Download",C ['indigo'],self ._load ),
        ("🆕 New",C ['bg3'],self ._new ),
        ]:
            b =QPushButton (txt );style_btn (b ,col );b .clicked .connect (fn );pc_l .addWidget (b )

            # ── Шрифт ──
        pc_l .addWidget (make_separator ())
        lbl_font =QLabel ("🔤 Font")
        lbl_font .setStyleSheet (f"color:{C ['muted']}; font-weight:700; font-size:12px;")
        pc_l .addWidget (lbl_font )
        self .editor_font_cb =QComboBox ()
        self .editor_font_cb .setFixedWidth (152 )
        for name ,_ ,_ in FONT_OPTIONS :
            self .editor_font_cb .addItem (name )
        self .editor_font_cb .currentTextChanged .connect (self ._on_font_changed )
        pc_l .addWidget (self .editor_font_cb )
        ml .addWidget (preset_card )

        # ── Фон / Финал ──
        media_card =QWidget ()
        media_card .setStyleSheet (f"background:{C ['bg2']}; border:1px solid {C ['border']}; border-radius:12px;")
        mc_l =QHBoxLayout (media_card );mc_l .setContentsMargins (16 ,10 ,16 ,10 );mc_l .setSpacing (12 )

        for attr ,lbl_attr ,icon ,title_t ,pick_fn in [
        ("bg_image","bg_lbl","🖼","Background image",self ._pick_bg ),
        ("end_image","end_lbl","🏁","Final picture",self ._pick_end ),
        ]:
            lbl_t =QLabel (title_t )
            lbl_t .setStyleSheet (f"color:{C ['muted']}; font-size:12px; font-weight:700;")
            mc_l .addWidget (lbl_t )
            val =getattr (self .preset ,attr )
            disp =QLabel (os .path .basename (val )if val else "- not selected -")
            disp .setStyleSheet (f"color:{C ['subtext']};")
            setattr (self ,lbl_attr ,disp )
            mc_l .addWidget (disp ,1 )
            btn =QPushButton (f"{icon }  Choose");style_btn (btn ,C ['bg3'],C ['subtext'])
            btn .clicked .connect (pick_fn );mc_l .addWidget (btn )
            if attr =="bg_image":mc_l .addWidget (make_separator ())

        ml .addWidget (media_card )

        # ── Вопросы ──
        qh =QHBoxLayout ()
        lbl_q =QLabel ("Questions")
        lbl_q .setStyleSheet (f"color:{C ['subtext']}; font-weight:700; font-size:13px;")
        qh .addWidget (lbl_q );qh .addStretch ()

        btn_specs =[
        ("➕Add",C ['green'],self ._add_q ),
        ("✏️ Edit",C ['orange'],self ._edit_q ),
        ("🗑 Delete",C ['red'],self ._del_q ),
        ("⬆",C ['bg3'],lambda :self ._move (-1 )),
        ("⬇",C ['bg3'],lambda :self ._move (1 )),
        ]
        for txt ,col ,fn in btn_specs :
            b =QPushButton (txt );style_btn (b ,col );b .clicked .connect (fn );qh .addWidget (b )
        ml .addLayout (qh )

        self .q_list =QListWidget ()
        self .q_list .setMinimumHeight (260 )
        self .q_list .itemDoubleClicked .connect (self ._edit_q )
        ml .addWidget (self .q_list ,1 )

        # ── Launch ──
        launch =QPushButton ("🚀 LAUNCH GAME")
        launch .setMinimumHeight (58 )
        launch .setStyleSheet (f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C ['indigo']}, stop:1 {C ['violet']});
                color: white;
                font-size: 20px;
                font-weight: 900;
                border-radius: 14px;
                border: none;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #818CF8, stop:1 #A78BFA);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C ['indigo']}, stop:1 {C ['violet']});
                opacity: 0.85;
            }}
        """)
        launch .clicked .connect (self ._launch )
        ml .addWidget (launch )

        self ._refresh_qlist ()

    def _refresh_qlist (self ):
        self .q_list .clear ()
        for i ,q in enumerate (self .preset .questions ):
            txt =q .text [:55 ].replace ("\n"," ")
            self .q_list .addItem (f"  {i +1 }.   [T{q .q_type }]   {txt }   —   {len (q .answers )} ans.")

    def _add_q (self ):
        d =QuestionEditDialog (parent =self )
        if d .exec_ ()==QDialog .Accepted :
            q =d .get_question ()
            if q .text .strip ()or q .answers :
                self .preset .questions .append (q );self ._refresh_qlist ()

    def _edit_q (self ):
        r =self .q_list .currentRow ()
        if r <0 :QMessageBox .information (self ,"","Select a question");return 
        d =QuestionEditDialog (self .preset .questions [r ],self )
        if d .exec_ ()==QDialog .Accepted :
            self .preset .questions [r ]=d .get_question ();self ._refresh_qlist ()

    def _del_q (self ):
        r =self .q_list .currentRow ()
        if r <0 :return 
        if QMessageBox .question (self ,"Delete","Delete question?")==QMessageBox .Yes :
            self .preset .questions .pop (r );self ._refresh_qlist ()

    def _move (self ,d ):
        r =self .q_list .currentRow ();nr =r +d ;qs =self .preset .questions 
        if 0 <=r <len (qs )and 0 <=nr <len (qs ):
            qs [r ],qs [nr ]=qs [nr ],qs [r ];self ._refresh_qlist ();self .q_list .setCurrentRow (nr )

    def _on_font_changed (self ,name ):
        family =_font_map .get (name ,name )
        _app_font [0 ]=family 
        QApplication .instance ().setFont (QFont (family ))
        self .setStyleSheet (get_global_style (family ))

    def _save (self ):
        n =self .name_edit .text ().strip ()
        if not n :QMessageBox .warning (self ,"","Enter a name");return 
        self .preset .name =n 
        QMessageBox .information (self ,"Saved",f"Сохранено:\n{self .preset .save ()}")

    def _load (self ):
        p ,_ =QFileDialog .getOpenFileName (self ,"Download",PRESETS_DIR ,"JSON (*.json)")
        if p :
            try :
                self .preset =PresetData .load (p )
                self .name_edit .setText (self .preset .name )
                self .bg_lbl .setText (os .path .basename (self .preset .bg_image )if self .preset .bg_image else "- not selected -")
                self .end_lbl .setText (os .path .basename (self .preset .end_image )if self .preset .end_image else "- not selected -")
                self ._refresh_qlist ()
            except Exception as e :QMessageBox .critical (self ,"Error",str (e ))

    def _new (self ):
        self .preset =PresetData ()
        self .name_edit .setText ("New preset")
        self .bg_lbl .setText ("- not selected -");self .end_lbl .setText ("- not selected -")
        self ._refresh_qlist ()

    def _pick_bg (self ):
        p ,_ =QFileDialog .getOpenFileName (self ,"Background","","Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if p :self .preset .bg_image =p ;self .bg_lbl .setText (os .path .basename (p ))

    def _pick_end (self ):
        p ,_ =QFileDialog .getOpenFileName (self ,"Final","","Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if p :self .preset .end_image =p ;self .end_lbl .setText (os .path .basename (p ))

    def _launch (self ):
        if not self .preset .questions :QMessageBox .warning (self ,"","Add questions");return 
        pc =copy .deepcopy (self .preset )
        ctrl =GameController (pc ,_app_font [0 ])
        aw =AudienceWindow (ctrl );hw =HostWindow (ctrl )
        screens =QApplication .screens ()
        if len (screens )>=2 :aw .setGeometry (screens [1 ].geometry ());aw .showFullScreen ()
        else :aw .resize (1400 ,900 );aw .show ()
        hw .show ();hw .activateWindow ();hw .raise_ ()
        self .game_wins =[aw ,hw ]


def main ():
    app =QApplication (sys .argv )
    app .setApplicationName (APP_TITLE )
    app .setStyle ("Fusion")
    init_fonts ()# Загрузить/скачать шрифты

    pal =QPalette ()
    pal .setColor (QPalette .Window ,QColor (5 ,8 ,15 ))
    pal .setColor (QPalette .WindowText ,QColor (241 ,245 ,249 ))
    pal .setColor (QPalette .Base ,QColor (15 ,21 ,37 ))
    pal .setColor (QPalette .AlternateBase ,QColor (22 ,30 ,50 ))
    pal .setColor (QPalette .Text ,QColor (241 ,245 ,249 ))
    pal .setColor (QPalette .Button ,QColor (15 ,21 ,37 ))
    pal .setColor (QPalette .ButtonText ,QColor (241 ,245 ,249 ))
    pal .setColor (QPalette .Highlight ,QColor (99 ,102 ,241 ))
    pal .setColor (QPalette .HighlightedText ,QColor (255 ,255 ,255 ))
    pal .setColor (QPalette .ToolTipBase ,QColor (15 ,21 ,37 ))
    pal .setColor (QPalette .ToolTipText ,QColor (241 ,245 ,249 ))
    app .setPalette (pal )

    w =EditorWindow ()
    w .show ()
    sys .exit (app .exec_ ())


if __name__ =="__main__":
    main ()
