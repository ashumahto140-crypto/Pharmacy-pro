# ============================================================
# 💊 PHARMACY PRO
# PROFESSIONAL KIVY + SQLITE MOBILE PHARMACY APP
# SINGLE FILE VERSION
#
# FEATURES
# ------------------------------------------------------------
# 🔐 Admin Login
# 🏠 Dashboard + Bottom Navigation
# 💊 Medicine & Category Management
# 📦 Stock-In History
# ⚠️ Low Stock / Expiry Alerts
# 🧾 Billing
# ✏️ Edit/Delete Bill Items
# 💰 Discount + GST
# 👤 Customer Database
# 🧾 Professional Invoice Numbers
# 📚 Bill History
# 📊 Sales / Profit Reports
# 📄 PDF Invoice Generation
# 📤 Android Share / Print helper
# 💾 Database Backup / Restore
# 📷 Barcode field / scanner-ready
# 🔎 Medicine Autocomplete
#
# DEFAULT LOGIN
# Username: admin
# Password: admin123
#
# INSTALL:
# pip install kivy reportlab
#
# OPTIONAL ANDROID:
# pip install pyjnius
# ============================================================

import os
import sqlite3
import shutil
from datetime import datetime, date
from difflib import get_close_matches

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.graphics import Color, RoundedRectangle

from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox


# ============================================================
# APP PATH
# ============================================================

APP_DIR = os.path.join(
    os.path.expanduser("~"),
    ".pharmacy_pro"
)

os.makedirs(APP_DIR, exist_ok=True)

DB_NAME = os.path.join(
    APP_DIR,
    "pharmacy.db"
)

BACKUP_DIR = os.path.join(
    APP_DIR,
    "backups"
)

INVOICE_DIR = os.path.join(
    APP_DIR,
    "invoices"
)

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(INVOICE_DIR, exist_ok=True)


# ============================================================
# COLORS
# ============================================================

BG = (0.025, 0.04, 0.07, 1)
CARD = (0.065, 0.09, 0.14, 1)
CARD_LIGHT = (0.09, 0.12, 0.18, 1)

PRIMARY = (0.05, 0.62, 0.67, 1)
PRIMARY_DARK = (0.03, 0.40, 0.44, 1)

ACCENT = (0.25, 0.75, 0.78, 1)

WHITE = (0.96, 0.98, 1, 1)
TEXT = (0.82, 0.87, 0.93, 1)
MUTED = (0.50, 0.57, 0.67, 1)

SUCCESS = (0.12, 0.68, 0.42, 1)
DANGER = (0.86, 0.20, 0.24, 1)
WARNING = (0.92, 0.62, 0.15, 1)

BLACK = (0.01, 0.015, 0.025, 1)


# ============================================================
# DATABASE
# ============================================================

def connect_db():
    return sqlite3.connect(DB_NAME)


def create_database():

    con = connect_db()
    cur = con.cursor()

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin'
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO users
        (username, password, role)
        VALUES ('admin', 'admin123', 'admin')
    """)

    # --------------------------------------------------------
    # CATEGORIES
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # --------------------------------------------------------
    # MEDICINES
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT,
            barcode TEXT,
            batch TEXT,
            expiry TEXT,
            quantity INTEGER DEFAULT 0,
            purchase_price REAL DEFAULT 0,
            selling_price REAL DEFAULT 0,
            low_stock INTEGER DEFAULT 10,
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # INVOICES
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT UNIQUE NOT NULL,
            customer_name TEXT,
            customer_phone TEXT,
            subtotal REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            gst_percent REAL DEFAULT 0,
            gst_amount REAL DEFAULT 0,
            grand_total REAL DEFAULT 0,
            profit REAL DEFAULT 0,
            created_at TEXT
        )
    """)

    # --------------------------------------------------------
    # INVOICE ITEMS
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            medicine_id INTEGER,
            medicine_name TEXT,
            quantity INTEGER,
            purchase_price REAL,
            selling_price REAL,
            amount REAL,
            profit REAL,
            FOREIGN KEY(invoice_id)
                REFERENCES invoices(id)
        )
    """)

    # --------------------------------------------------------
    # STOCK HISTORY
    # --------------------------------------------------------

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            medicine_name TEXT,
            change_type TEXT,
            quantity INTEGER,
            previous_stock INTEGER,
            new_stock INTEGER,
            note TEXT,
            created_at TEXT
        )
    """)

    # Default categories
    categories = [
        "Tablet",
        "Capsule",
        "Syrup",
        "Injection",
        "Cream",
        "Drops",
        "Other"
    ]

    for category in categories:
        cur.execute(
            "INSERT OR IGNORE INTO categories(name) VALUES (?)",
            (category,)
        )

    con.commit()
    con.close()


# ============================================================
# DATABASE HELPERS
# ============================================================

def get_medicines():

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        SELECT *
        FROM medicines
        ORDER BY name COLLATE NOCASE
    """)

    rows = cur.fetchall()

    con.close()

    return rows


def get_categories():

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        SELECT name
        FROM categories
        ORDER BY name
    """)

    rows = [
        r[0]
        for r in cur.fetchall()
    ]

    con.close()

    return rows


def get_customers():

    con = connect_db()
    cur = con.cursor()

    cur.execute("""
        SELECT *
        FROM customers
        ORDER BY name COLLATE NOCASE
    """)

    rows = cur.fetchall()

    con.close()

    return rows


def money(value):

    return f"Rs. {float(value):,.2f}"


# ============================================================
# UI HELPERS
# ============================================================

class RoundedBox(BoxLayout):

    def __init__(
        self,
        bg_color=CARD,
        radius=18,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.bg_color_value = bg_color
        self.radius_value = dp(radius)

        with self.canvas.before:

            Color(
                *bg_color
            )

            self.rectangle = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[
                    (
                        self.radius_value,
                        self.radius_value
                    )
                ]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *args):

        self.rectangle.pos = self.pos
        self.rectangle.size = self.size


def make_button(
    text,
    color=PRIMARY,
    height=48,
    font_size=14
):

    return Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        background_normal="",
        background_color=color,
        color=WHITE,
        font_size=dp(font_size),
        bold=True
    )


def make_input(
    hint="",
    height=46
):

    return TextInput(
        hint_text=hint,
        size_hint_y=None,
        height=dp(height),
        multiline=False,
        padding=[
            dp(12),
            dp(10)
        ],
        font_size=dp(14),
        foreground_color=WHITE,
        hint_text_color=MUTED,
        background_normal="",
        background_color=CARD_LIGHT
    )


def make_label(
    text,
    size=14,
    color=TEXT,
    bold=False
):

    return Label(
        text=text,
        color=color,
        font_size=dp(size),
        bold=bold
    )


# ============================================================
# MESSAGE POPUP
# ============================================================

def show_message(
    title,
    message,
    height=0.45
):

    content = RoundedBox(
        orientation="vertical",
        padding=dp(15),
        spacing=dp(10),
        bg_color=CARD
    )

    scroll = ScrollView()

    msg = Label(
        text=message,
        color=TEXT,
        font_size=dp(14),
        halign="center",
        valign="top",
        size_hint_y=None
    )

    msg.bind(
        texture_size=lambda obj, size:
        setattr(
            obj,
            "height",
            max(size[1], dp(60))
        )
    )

    scroll.add_widget(msg)

    content.add_widget(scroll)

    close = make_button(
        "CLOSE",
        PRIMARY
    )

    content.add_widget(close)

    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.92, height),
        separator_color=PRIMARY
    )

    close.bind(
        on_press=popup.dismiss
    )

    popup.open()

    return popup


# ============================================================
# LOGIN SCREEN
# ============================================================

class LoginScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = FloatLayout()

        card = RoundedBox(
            orientation="vertical",
            padding=dp(22),
            spacing=dp(14),
            size_hint=(0.88, None),
            height=dp(380),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.5
            },
            bg_color=CARD
        )

        card.add_widget(
            Label(
                text="💊",
                color=ACCENT,
                font_size=dp(40),
                size_hint_y=None,
                height=dp(55)
            )
        )

        card.add_widget(
            Label(
                text="PHARMACY PRO",
                color=WHITE,
                font_size=dp(24),
                bold=True,
                size_hint_y=None,
                height=dp(42)
            )
        )

        card.add_widget(
            Label(
                text="ADMIN LOGIN",
                color=ACCENT,
                font_size=dp(11),
                size_hint_y=None,
                height=dp(25)
            )
        )

        self.username = make_input(
            "Username"
        )

        self.password = make_input(
            "Password"
        )

        self.password.password = True

        card.add_widget(
            self.username
        )

        card.add_widget(
            self.password
        )

        login = make_button(
            "LOGIN",
            PRIMARY,
            52,
            15
        )

        login.bind(
            on_press=self.login
        )

        card.add_widget(login)

        card.add_widget(
            Label(
                text="Default: admin / admin123",
                color=MUTED,
                font_size=dp(11)
            )
        )

        root.add_widget(card)

        self.add_widget(root)

    def login(self, instance):

        username = self.username.text.strip()
        password = self.password.text.strip()

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT id, role
            FROM users
            WHERE username=?
            AND password=?
        """, (
            username,
            password
        ))

        user = cur.fetchone()

        con.close()

        if user:

            self.manager.current = "main"

        else:

            show_message(
                "LOGIN FAILED",
                "Invalid username or password."
            )


# ============================================================
# BOTTOM NAVIGATION
# ============================================================

class BottomNavigation(BoxLayout):

    def __init__(self, manager, **kwargs):

        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(62),
            spacing=dp(4),
            padding=dp(4),
            **kwargs
        )

        self.manager_ref = manager

        buttons = [
            ("HOME", "dashboard"),
            ("BILL", "billing"),
            ("STOCK", "stock"),
            ("REPORTS", "reports"),
            ("MORE", "more")
        ]

        for text, screen in buttons:

            btn = Button(
                text=text,
                background_normal="",
                background_color=CARD_LIGHT,
                color=TEXT,
                font_size=dp(11),
                bold=True
            )

            btn.bind(
                on_press=lambda x,
                s=screen:
                self.go(s)
            )

            self.add_widget(btn)

    def go(self, screen):

        self.manager_ref.current = screen


# ============================================================
# MAIN SCREEN
# ============================================================

class MainScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical"
        )

        self.content = ScreenManager()

        self.content.add_widget(
            DashboardScreen(
                name="dashboard"
            )
        )

        self.content.add_widget(
            BillingScreen(
                name="billing"
            )
        )

        self.content.add_widget(
            StockScreen(
                name="stock"
            )
        )

        self.content.add_widget(
            ReportsScreen(
                name="reports"
            )
        )

        self.content.add_widget(
            MoreScreen(
                name="more"
            )
        )

        root.add_widget(
            self.content
        )

        root.add_widget(
            BottomNavigation(
                self.content
            )
        )

        self.add_widget(root)


# ============================================================
# DASHBOARD
# ============================================================

class DashboardScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.root_box = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        self.root_box.add_widget(
            Label(
                text="DASHBOARD",
                color=WHITE,
                font_size=dp(24),
                bold=True,
                size_hint_y=None,
                height=dp(48),
                halign="left"
            )
        )

        scroll = ScrollView()

        self.container = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )

        self.container.bind(
            minimum_height=
            self.container.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.container
        )

        self.root_box.add_widget(scroll)

        self.add_widget(
            self.root_box
        )

    def on_enter(self):

        self.refresh()

    def stat_card(
        self,
        title,
        value,
        color=PRIMARY
    ):

        card = RoundedBox(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(3),
            size_hint_y=None,
            height=dp(105),
            bg_color=CARD
        )

        card.add_widget(
            Label(
                text=title,
                color=MUTED,
                font_size=dp(11)
            )
        )

        card.add_widget(
            Label(
                text=value,
                color=color,
                font_size=dp(25),
                bold=True
            )
        )

        return card

    def refresh(self):

        self.container.clear_widgets()

        con = connect_db()
        cur = con.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM medicines"
        )

        medicine_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COALESCE(SUM(quantity),0) FROM medicines"
        )

        stock = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM medicines
            WHERE quantity <= low_stock
        """)

        low_stock = cur.fetchone()[0]

        today = date.today().strftime(
            "%Y-%m-%d"
        )

        cur.execute("""
            SELECT
                COALESCE(SUM(grand_total),0),
                COALESCE(SUM(profit),0),
                COUNT(*)
            FROM invoices
            WHERE substr(created_at,1,10)=?
        """, (
            today,
        ))

        sales, profit, invoices = cur.fetchone()

        cur.execute("""
            SELECT COUNT(*)
            FROM medicines
            WHERE expiry != ''
            AND date(
                substr(expiry,4,4) || '-' ||
                substr(expiry,1,2) || '-01'
            ) <= date('now','+60 day')
        """)

        expiry_count = cur.fetchone()[0]

        con.close()

        self.container.add_widget(
            self.stat_card(
                "TOTAL MEDICINES",
                str(medicine_count)
            )
        )

        self.container.add_widget(
            self.stat_card(
                "STOCK UNITS",
                str(stock),
                ACCENT
            )
        )

        self.container.add_widget(
            self.stat_card(
                "LOW STOCK",
                str(low_stock),
                DANGER if low_stock else SUCCESS
            )
        )

        self.container.add_widget(
            self.stat_card(
                "EXPIRING SOON",
                str(expiry_count),
                WARNING if expiry_count else SUCCESS
            )
        )

        self.container.add_widget(
            self.stat_card(
                "TODAY SALES",
                money(sales),
                SUCCESS
            )
        )

        self.container.add_widget(
            self.stat_card(
                "TODAY PROFIT",
                money(profit),
                ACCENT
            )
        )

        self.container.add_widget(
            self.stat_card(
                "TODAY INVOICES",
                str(invoices)
            )
        )


# ============================================================
# MEDICINE AUTOCOMPLETE
# ============================================================

def find_medicine(text):

    text = text.strip()

    if not text:
        return None, False

    medicines = get_medicines()

    names = [
        row[1]
        for row in medicines
    ]

    for name in names:

        if name.lower() == text.lower():

            return name, False

    matches = get_close_matches(
        text,
        names,
        n=1,
        cutoff=0.55
    )

    if matches:

        return matches[0], True

    for name in names:

        if text.lower() in name.lower():

            return name, True

    return text, False


# ============================================================
# BILLING SCREEN
# ============================================================

class BillingScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.bill = []

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(7)
        )

        root.add_widget(
            Label(
                text="NEW INVOICE",
                color=WHITE,
                font_size=dp(23),
                bold=True,
                size_hint_y=None,
                height=dp(42)
            )
        )

        self.customer_name = make_input(
            "Customer Name"
        )

        self.customer_phone = make_input(
            "Customer Phone"
        )

        root.add_widget(
            self.customer_name
        )

        root.add_widget(
            self.customer_phone
        )

        row = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(5)
        )

        self.medicine_input = make_input(
            "Medicine / Barcode"
        )

        self.qty_input = make_input(
            "Qty"
        )

        self.qty_input.input_filter = "int"

        row.add_widget(
            self.medicine_input
        )

        row.add_widget(
            self.qty_input
        )

        root.add_widget(row)

        self.suggestions = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(2)
        )

        self.suggestions.bind(
            minimum_height=
            self.suggestions.setter(
                "height"
            )
        )

        root.add_widget(
            self.suggestions
        )

        self.medicine_input.bind(
            text=self.autocomplete
        )

        add = make_button(
            "ADD TO BILL",
            SUCCESS
        )

        add.bind(
            on_press=self.add_item
        )

        root.add_widget(add)

        scroll = ScrollView()

        self.items_box = GridLayout(
            cols=1,
            spacing=dp(6),
            size_hint_y=None
        )

        self.items_box.bind(
            minimum_height=
            self.items_box.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.items_box
        )

        root.add_widget(scroll)

        totals = RoundedBox(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(3),
            size_hint_y=None,
            height=dp(125),
            bg_color=CARD
        )

        self.subtotal_label = make_label(
            "Subtotal: Rs. 0.00"
        )

        self.discount_input = make_input(
            "Discount (%)"
        )

        self.discount_input.text = "0"

        self.gst_input = make_input(
            "GST (%)"
        )

        self.gst_input.text = "0"

        self.total_label = make_label(
            "TOTAL: Rs. 0.00",
            19,
            WHITE,
            True
        )

        totals.add_widget(
            self.subtotal_label
        )

        totals.add_widget(
            self.discount_input
        )

        totals.add_widget(
            self.gst_input
        )

        totals.add_widget(
            self.total_label
        )

        root.add_widget(totals)

        generate = make_button(
            "GENERATE INVOICE",
            PRIMARY,
            54,
            15
        )

        generate.bind(
            on_press=self.generate_invoice
        )

        root.add_widget(generate)

        clear = make_button(
            "CLEAR BILL",
            CARD_LIGHT
        )

        clear.bind(
            on_press=lambda x:
            self.clear_bill()
        )

        root.add_widget(clear)

        self.add_widget(root)

    def on_enter(self):

        self.refresh_items()

    def autocomplete(self, instance, value):

        self.suggestions.clear_widgets()

        value = value.strip()

        if len(value) < 2:
            return

        medicines = get_medicines()

        matches = [
            row
            for row in medicines
            if value.lower() in row[1].lower()
        ][:5]

        for row in matches:

            btn = Button(
                text=(
                    f"{row[1]}   "
                    f"Stock: {row[6]}"
                ),
                size_hint_y=None,
                height=dp(38),
                background_normal="",
                background_color=CARD_LIGHT,
                color=WHITE
            )

            btn.bind(
                on_press=lambda x,
                name=row[1]:
                self.select_medicine(name)
            )

            self.suggestions.add_widget(btn)

    def select_medicine(self, name):

        self.medicine_input.text = name
        self.suggestions.clear_widgets()

    def add_item(self, instance):

        text = self.medicine_input.text.strip()

        if not text:

            show_message(
                "ERROR",
                "Enter medicine name or barcode."
            )

            return

        try:

            qty = int(
                self.qty_input.text
            )

            if qty <= 0:
                raise ValueError

        except ValueError:

            show_message(
                "ERROR",
                "Enter a valid quantity."
            )

            return

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT
                id,
                name,
                batch,
                expiry,
                quantity,
                purchase_price,
                selling_price
            FROM medicines
            WHERE LOWER(name)=LOWER(?)
               OR barcode=?
        """, (
            text,
            text
        ))

        medicine = cur.fetchone()

        con.close()

        corrected = False

        if not medicine:

            name, corrected = find_medicine(text)

            con = connect_db()
            cur = con.cursor()

            cur.execute("""
                SELECT
                    id,
                    name,
                    batch,
                    expiry,
                    quantity,
                    purchase_price,
                    selling_price
                FROM medicines
                WHERE LOWER(name)=LOWER(?)
            """, (
                name,
            ))

            medicine = cur.fetchone()

            con.close()

        if not medicine:

            show_message(
                "NOT FOUND",
                "Medicine was not found."
            )

            return

        med_id = medicine[0]
        name = medicine[1]
        batch = medicine[2]
        expiry = medicine[3]
        stock = medicine[4]
        purchase = medicine[5]
        selling = medicine[6]

        existing_qty = sum(
            item["quantity"]
            for item in self.bill
            if item["medicine_id"] == med_id
        )

        if existing_qty + qty > stock:

            show_message(
                "INSUFFICIENT STOCK",
                f"Available stock: {stock}\n"
                f"Already in bill: {existing_qty}"
            )

            return

        for item in self.bill:

            if item["medicine_id"] == med_id:

                item["quantity"] += qty

                item["amount"] = (
                    item["quantity"] *
                    item["selling_price"]
                )

                item["profit"] = (
                    item["quantity"] *
                    (
                        item["selling_price"] -
                        item["purchase_price"]
                    )
                )

                self.medicine_input.text = ""
                self.qty_input.text = ""

                self.refresh_items()

                return

        self.bill.append({
            "medicine_id": med_id,
            "name": name,
            "batch": batch,
            "expiry": expiry,
            "quantity": qty,
            "purchase_price": purchase,
            "selling_price": selling,
            "amount": qty * selling,
            "profit": qty * (selling - purchase)
        })

        self.medicine_input.text = ""
        self.qty_input.text = ""

        self.refresh_items()

        if corrected:

            show_message(
                "AUTO CORRECTION",
                f"Using: {name}"
            )

    def refresh_items(self):

        self.items_box.clear_widgets()

        for index, item in enumerate(self.bill):

            card = RoundedBox(
                orientation="horizontal",
                padding=dp(8),
                spacing=dp(5),
                size_hint_y=None,
                height=dp(70),
                bg_color=CARD
            )

            info = BoxLayout(
                orientation="vertical"
            )

            info.add_widget(
                Label(
                    text=item["name"],
                    color=WHITE,
                    font_size=dp(14),
                    bold=True,
                    halign="left"
                )
            )

            info.add_widget(
                Label(
                    text=(
                        f"Qty {item['quantity']} × "
                        f"{money(item['selling_price'])}"
                        f" = "
                        f"{money(item['amount'])}"
                    ),
                    color=TEXT,
                    font_size=dp(11),
                    halign="left"
                )
            )

            card.add_widget(info)

            edit = Button(
                text="EDIT",
                size_hint_x=None,
                width=dp(55),
                background_normal="",
                background_color=PRIMARY,
                color=WHITE
            )

            delete = Button(
                text="×",
                size_hint_x=None,
                width=dp(45),
                background_normal="",
                background_color=DANGER,
                color=WHITE,
                font_size=dp(18)
            )

            edit.bind(
                on_press=lambda x,
                i=index:
                self.edit_item(i)
            )

            delete.bind(
                on_press=lambda x,
                i=index:
                self.delete_item(i)
            )

            card.add_widget(edit)
            card.add_widget(delete)

            self.items_box.add_widget(card)

        self.update_total()

    def edit_item(self, index):

        if index >= len(self.bill):
            return

        item = self.bill[index]

        content = RoundedBox(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        content.add_widget(
            make_label(
                item["name"],
                17,
                WHITE,
                True
            )
        )

        qty = make_input(
            "Quantity"
        )

        qty.text = str(
            item["quantity"]
        )

        content.add_widget(qty)

        save = make_button(
            "UPDATE",
            SUCCESS
        )

        cancel = make_button(
            "CANCEL",
            CARD_LIGHT
        )

        content.add_widget(save)
        content.add_widget(cancel)

        popup = Popup(
            title="EDIT BILL ITEM",
            content=content,
            size_hint=(0.90, 0.48)
        )

        save.bind(
            on_press=lambda x:
            self.save_item_edit(
                popup,
                index,
                qty
            )
        )

        cancel.bind(
            on_press=popup.dismiss
        )

        popup.open()

    def save_item_edit(
        self,
        popup,
        index,
        qty
    ):

        try:
            new_qty = int(qty.text)

            if new_qty <= 0:
                raise ValueError

        except ValueError:

            show_message(
                "ERROR",
                "Invalid quantity."
            )

            return

        item = self.bill[index]

        con = connect_db()
        cur = con.cursor()

        cur.execute(
            "SELECT quantity FROM medicines WHERE id=?",
            (item["medicine_id"],)
        )

        stock = cur.fetchone()[0]

        con.close()

        if new_qty > stock:

            show_message(
                "ERROR",
                f"Available stock: {stock}"
            )

            return

        item["quantity"] = new_qty

        item["amount"] = (
            new_qty *
            item["selling_price"]
        )

        item["profit"] = (
            new_qty *
            (
                item["selling_price"] -
                item["purchase_price"]
            )
        )

        popup.dismiss()

        self.refresh_items()

    def delete_item(self, index):

        if 0 <= index < len(self.bill):

            self.bill.pop(index)

            self.refresh_items()

    def update_total(self):

        subtotal = sum(
            item["amount"]
            for item in self.bill
        )

        try:
            discount_percent = float(
                self.discount_input.text or 0
            )
        except ValueError:
            discount_percent = 0

        try:
            gst_percent = float(
                self.gst_input.text or 0
            )
        except ValueError:
            gst_percent = 0

        discount = (
            subtotal *
            discount_percent /
            100
        )

        taxable = subtotal - discount

        gst = (
            taxable *
            gst_percent /
            100
        )

        total = taxable + gst

        self.subtotal_label.text = (
            f"Subtotal: {money(subtotal)}"
        )

        self.total_label.text = (
            f"TOTAL: {money(total)}"
        )

    def generate_invoice(self, instance):

        if not self.bill:

            show_message(
                "EMPTY BILL",
                "Add medicines first."
            )

            return

        customer = (
            self.customer_name.text.strip()
            or "Walk-in Customer"
        )

        phone = (
            self.customer_phone.text.strip()
        )

        try:

            discount_percent = float(
                self.discount_input.text or 0
            )

            gst_percent = float(
                self.gst_input.text or 0
            )

            if discount_percent < 0 or \
               gst_percent < 0:

                raise ValueError

        except ValueError:

            show_message(
                "ERROR",
                "Invalid discount or GST."
            )

            return

        subtotal = sum(
            item["amount"]
            for item in self.bill
        )

        discount = (
            subtotal *
            discount_percent /
            100
        )

        taxable = subtotal - discount

        gst_amount = (
            taxable *
            gst_percent /
            100
        )

        grand_total = (
            taxable +
            gst_amount
        )

        profit = sum(
            item["profit"]
            for item in self.bill
        )

        # Discount reduces effective profit
        profit -= discount

        now = datetime.now()

        invoice_no = (
            "INV-"
            + now.strftime("%Y%m%d")
            + "-"
            + now.strftime("%H%M%S%f")[:8]
        )

        con = connect_db()
        cur = con.cursor()

        try:

            # --------------------------------------------
            # VERIFY STOCK BEFORE TRANSACTION
            # --------------------------------------------

            for item in self.bill:

                cur.execute(
                    "SELECT quantity FROM medicines WHERE id=?",
                    (item["medicine_id"],)
                )

                row = cur.fetchone()

                if not row or \
                   row[0] < item["quantity"]:

                    raise ValueError(
                        f"Insufficient stock for "
                        f"{item['name']}"
                    )

            # --------------------------------------------
            # CUSTOMER
            # --------------------------------------------

            cur.execute("""
                SELECT id
                FROM customers
                WHERE name=?
                AND phone=?
            """, (
                customer,
                phone
            ))

            customer_exists = cur.fetchone()

            if not customer_exists:

                cur.execute("""
                    INSERT INTO customers
                    (name, phone, address, created_at)
                    VALUES (?, ?, ?, ?)
                """, (
                    customer,
                    phone,
                    "",
                    now.strftime("%Y-%m-%d %H:%M:%S")
                ))

            # --------------------------------------------
            # INVOICE
            # --------------------------------------------

            cur.execute("""
                INSERT INTO invoices
                (
                    invoice_no,
                    customer_name,
                    customer_phone,
                    subtotal,
                    discount,
                    gst_percent,
                    gst_amount,
                    grand_total,
                    profit,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_no,
                customer,
                phone,
                subtotal,
                discount,
                gst_percent,
                gst_amount,
                grand_total,
                profit,
                now.strftime("%Y-%m-%d %H:%M:%S")
            ))

            invoice_id = cur.lastrowid

            # --------------------------------------------
            # ITEMS + STOCK DEDUCTION
            # --------------------------------------------

            for item in self.bill:

                cur.execute("""
                    INSERT INTO invoice_items
                    (
                        invoice_id,
                        medicine_id,
                        medicine_name,
                        quantity,
                        purchase_price,
                        selling_price,
                        amount,
                        profit
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    item["medicine_id"],
                    item["name"],
                    item["quantity"],
                    item["purchase_price"],
                    item["selling_price"],
                    item["amount"],
                    item["profit"]
                ))

                cur.execute("""
                    UPDATE medicines
                    SET quantity=quantity-?
                    WHERE id=?
                """, (
                    item["quantity"],
                    item["medicine_id"]
                ))

                cur.execute("""
                    INSERT INTO stock_history
                    (
                        medicine_id,
                        medicine_name,
                        change_type,
                        quantity,
                        previous_stock,
                        new_stock,
                        note,
                        created_at
                    )
                    SELECT
                        ?,
                        ?,
                        'SALE',
                        ?,
                        quantity + ?,
                        quantity,
                        ?,
                        ?
                    FROM medicines
                    WHERE id=?
                """, (
                    item["medicine_id"],
                    item["name"],
                    item["quantity"],
                    item["quantity"],
                    invoice_no,
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    item["medicine_id"]
                ))

            con.commit()

        except Exception as e:

            con.rollback()
            con.close()

            show_message(
                "INVOICE ERROR",
                str(e)
            )

            return

        con.close()

        # --------------------------------------------
        # PDF
        # --------------------------------------------

        pdf_path = create_pdf_invoice(
            invoice_no,
            customer,
            phone,
            self.bill,
            subtotal,
            discount,
            gst_percent,
            gst_amount,
            grand_total
        )

        self.bill = []
        self.customer_name.text = ""
        self.customer_phone.text = ""
        self.discount_input.text = "0"
        self.gst_input.text = "0"

        self.refresh_items()

        message = (
            f"Invoice: {invoice_no}\n\n"
            f"Customer: {customer}\n"
            f"Subtotal: {money(subtotal)}\n"
            f"Discount: {money(discount)}\n"
            f"GST: {money(gst_amount)}\n"
            f"Grand Total: {money(grand_total)}"
        )

        popup = show_message(
            "INVOICE GENERATED",
            message,
            0.60
        )

        # PDF action buttons cannot easily be added
        # to the generic popup, so show PDF path.
        if pdf_path:
            message += (
                "\n\nPDF saved successfully."
            )


    def clear_bill(self):

        self.bill = []

        self.customer_name.text = ""
        self.customer_phone.text = ""
        self.medicine_input.text = ""
        self.qty_input.text = ""
        self.discount_input.text = "0"
        self.gst_input.text = "0"

        self.refresh_items()


# ============================================================
# STOCK SCREEN
# ============================================================

class StockScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        root.add_widget(
            Label(
                text="STOCK MANAGEMENT",
                color=WHITE,
                font_size=dp(22),
                bold=True,
                size_hint_y=None,
                height=dp(42)
            )
        )

        actions = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(5)
        )

        add = make_button(
            "ADD MEDICINE",
            SUCCESS
        )

        stock_in = make_button(
            "STOCK IN",
            PRIMARY
        )

        actions.add_widget(add)
        actions.add_widget(stock_in)

        root.add_widget(actions)

        self.search = make_input(
            "Search medicine..."
        )

        self.search.bind(
            text=lambda x:
            self.refresh()
        )

        root.add_widget(
            self.search
        )

        scroll = ScrollView()

        self.list_box = GridLayout(
            cols=1,
            spacing=dp(7),
            size_hint_y=None
        )

        self.list_box.bind(
            minimum_height=
            self.list_box.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.list_box
        )

        root.add_widget(scroll)

        self.add_widget(root)

        add.bind(
            on_press=lambda x:
            self.medicine_popup()
        )

        stock_in.bind(
            on_press=lambda x:
            self.stock_in_popup()
        )

    def on_enter(self):

        self.refresh()

    def refresh(self):

        self.list_box.clear_widgets()

        search = self.search.text.lower()

        for row in get_medicines():

            med_id = row[0]
            name = row[1]
            category = row[2]
            barcode = row[3]
            batch = row[4]
            expiry = row[5]
            qty = row[6]
            purchase = row[7]
            selling = row[8]
            low = row[9]

            if search and \
               search not in name.lower():

                continue

            is_low = qty <= low

            card = RoundedBox(
                orientation="vertical",
                padding=dp(9),
                spacing=dp(3),
                size_hint_y=None,
                height=dp(105),
                bg_color=CARD
            )

            card.add_widget(
                Label(
                    text=name,
                    color=WHITE,
                    font_size=dp(15),
                    bold=True,
                    halign="left"
                )
            )

            card.add_widget(
                Label(
                    text=(
                        f"Category: {category}   "
                        f"Stock: {qty}\n"
                        f"Batch: {batch}   "
                        f"Expiry: {expiry}\n"
                        f"Buy: {money(purchase)}   "
                        f"Sell: {money(selling)}"
                    ),
                    color=TEXT,
                    font_size=dp(10),
                    halign="left"
                )
            )

            status = (
                "⚠ LOW STOCK"
                if is_low
                else "✓ IN STOCK"
            )

            card.add_widget(
                Label(
                    text=status,
                    color=
                    DANGER if is_low else SUCCESS,
                    font_size=dp(10),
                    bold=True,
                    halign="left"
                )
            )

            card.bind(
                on_touch_down=lambda obj,
                touch,
                mid=med_id:
                self.touch_card(
                    obj,
                    touch,
                    mid
                )
            )

            self.list_box.add_widget(card)

    def touch_card(
        self,
        card,
        touch,
        med_id
    ):

        if card.collide_point(
            *touch.pos
        ) and touch.is_double_tap:

            self.medicine_popup(
                med_id
            )

            return True

        return False

    def medicine_popup(
        self,
        medicine_id=None
    ):

        content = RoundedBox(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(7),
            bg_color=CARD
        )

        name = make_input(
            "Medicine Name"
        )

        category = Spinner(
            text="Tablet",
            values=get_categories(),
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=CARD_LIGHT,
            color=WHITE
        )

        barcode = make_input(
            "Barcode"
        )

        batch = make_input(
            "Batch Number"
        )

        expiry = make_input(
            "Expiry MM/YYYY"
        )

        quantity = make_input(
            "Opening Stock"
        )

        purchase = make_input(
            "Purchase Price"
        )

        selling = make_input(
            "Selling Price"
        )

        low = make_input(
            "Low Stock Limit"
        )

        low.text = "10"

        fields = [
            name,
            category,
            barcode,
            batch,
            expiry,
            quantity,
            purchase,
            selling,
            low
        ]

        for field in fields:
            content.add_widget(field)

        save = make_button(
            "SAVE",
            SUCCESS
        )

        content.add_widget(save)

        popup = Popup(
            title=(
                "EDIT MEDICINE"
                if medicine_id
                else "ADD MEDICINE"
            ),
            content=content,
            size_hint=(0.94, 0.94),
            separator_color=PRIMARY
        )

        if medicine_id:

            con = connect_db()
            cur = con.cursor()

            cur.execute(
                "SELECT * FROM medicines WHERE id=?",
                (medicine_id,)
            )

            row = cur.fetchone()

            con.close()

            if row:

                name.text = row[1]
                category.text = row[2] or "Tablet"
                barcode.text = row[3] or ""
                batch.text = row[4] or ""
                expiry.text = row[5] or ""
                quantity.text = str(row[6])
                purchase.text = str(row[7])
                selling.text = str(row[8])
                low.text = str(row[9])

        save.bind(
            on_press=lambda x:
            self.save_medicine(
                popup,
                medicine_id,
                name,
                category,
                barcode,
                batch,
                expiry,
                quantity,
                purchase,
                selling,
                low
            )
        )

        popup.open()

    def save_medicine(
        self,
        popup,
        medicine_id,
        name,
        category,
        barcode,
        batch,
        expiry,
        quantity,
        purchase,
        selling,
        low
    ):

        if not name.text.strip():

            show_message(
                "ERROR",
                "Medicine name required."
            )

            return

        try:

            qty = int(
                quantity.text or 0
            )

            purchase_price = float(
                purchase.text or 0
            )

            selling_price = float(
                selling.text or 0
            )

            low_stock = int(
                low.text or 10
            )

            if qty < 0 or \
               purchase_price < 0 or \
               selling_price < 0:

                raise ValueError

        except ValueError:

            show_message(
                "ERROR",
                "Enter valid numeric values."
            )

            return

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        con = connect_db()
        cur = con.cursor()

        try:

            if medicine_id:

                cur.execute("""
                    UPDATE medicines
                    SET name=?,
                        category=?,
                        barcode=?,
                        batch=?,
                        expiry=?,
                        quantity=?,
                        purchase_price=?,
                        selling_price=?,
                        low_stock=?
                    WHERE id=?
                """, (
                    name.text.strip(),
                    category.text,
                    barcode.text.strip(),
                    batch.text.strip(),
                    expiry.text.strip(),
                    qty,
                    purchase_price,
                    selling_price,
                    low_stock,
                    medicine_id
                ))

                message = "Medicine updated."

            else:

                cur.execute("""
                    INSERT INTO medicines
                    (
                        name,
                        category,
                        barcode,
                        batch,
                        expiry,
                        quantity,
                        purchase_price,
                        selling_price,
                        low_stock,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name.text.strip(),
                    category.text,
                    barcode.text.strip(),
                    batch.text.strip(),
                    expiry.text.strip(),
                    qty,
                    purchase_price,
                    selling_price,
                    low_stock,
                    now
                ))

                medicine_id = cur.lastrowid

                cur.execute("""
                    INSERT INTO stock_history
                    (
                        medicine_id,
                        medicine_name,
                        change_type,
                        quantity,
                        previous_stock,
                        new_stock,
                        note,
                        created_at
                    )
                    VALUES (?, ?, 'OPENING', ?, 0, ?, ?, ?)
                """, (
                    medicine_id,
                    name.text.strip(),
                    qty,
                    qty,
                    "Opening stock",
                    now
                ))

                message = "Medicine added."

            con.commit()

        except sqlite3.IntegrityError:

            con.rollback()

            show_message(
                "ERROR",
                "Medicine name or barcode already exists."
            )

            con.close()

            return

        con.close()

        popup.dismiss()

        self.refresh()

        show_message(
            "SUCCESS",
            message
        )

    def stock_in_popup(self):

        content = RoundedBox(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        medicine = make_input(
            "Medicine Name"
        )

        quantity = make_input(
            "Stock Quantity"
        )

        quantity.input_filter = "int"

        note = make_input(
            "Note / Supplier"
        )

        content.add_widget(medicine)
        content.add_widget(quantity)
        content.add_widget(note)

        save = make_button(
            "ADD STOCK",
            SUCCESS
        )

        content.add_widget(save)

        popup = Popup(
            title="STOCK IN",
            content=content,
            size_hint=(0.90, 0.52)
        )

        save.bind(
            on_press=lambda x:
            self.add_stock(
                popup,
                medicine,
                quantity,
                note
            )
        )

        popup.open()

    def add_stock(
        self,
        popup,
        medicine,
        quantity,
        note
    ):

        try:
            qty = int(quantity.text)

            if qty <= 0:
                raise ValueError

        except ValueError:

            show_message(
                "ERROR",
                "Enter valid stock quantity."
            )

            return

        name, corrected = find_medicine(
            medicine.text
        )

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT id, quantity
            FROM medicines
            WHERE LOWER(name)=LOWER(?)
        """, (
            name,
        ))

        row = cur.fetchone()

        if not row:

            con.close()

            show_message(
                "ERROR",
                "Medicine not found."
            )

            return

        med_id = row[0]
        previous = row[1]
        new_stock = previous + qty

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cur.execute("""
            UPDATE medicines
            SET quantity=?
            WHERE id=?
        """, (
            new_stock,
            med_id
        ))

        cur.execute("""
            INSERT INTO stock_history
            (
                medicine_id,
                medicine_name,
                change_type,
                quantity,
                previous_stock,
                new_stock,
                note,
                created_at
            )
            VALUES (?, ?, 'STOCK IN', ?, ?, ?, ?, ?)
        """, (
            med_id,
            name,
            qty,
            previous,
            new_stock,
            note.text.strip(),
            now
        ))

        con.commit()
        con.close()

        popup.dismiss()

        self.refresh()

        show_message(
            "STOCK UPDATED",
            f"{name}\n"
            f"Previous: {previous}\n"
            f"Added: {qty}\n"
            f"New Stock: {new_stock}"
        )


# ============================================================
# REPORTS SCREEN
# ============================================================

class ReportsScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        root.add_widget(
            Label(
                text="REPORTS",
                color=WHITE,
                font_size=dp(23),
                bold=True,
                size_hint_y=None,
                height=dp(42)
            )
        )

        buttons = [
            ("TODAY REPORT", self.today),
            ("THIS MONTH", self.month),
            ("BILL HISTORY", self.history),
            ("STOCK HISTORY", self.stock_history),
            ("EXPIRY ALERTS", self.expiry_alerts),
            ("LOW STOCK", self.low_stock)
        ]

        scroll = ScrollView()

        box = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )

        box.bind(
            minimum_height=
            box.setter("height")
        )

        for text, callback in buttons:

            btn = make_button(
                text,
                CARD_LIGHT,
                54
            )

            btn.bind(
                on_press=callback
            )

            box.add_widget(btn)

        scroll.add_widget(box)

        root.add_widget(scroll)

        self.add_widget(root)

    def today(self, instance):

        self.sales_report(
            date.today().strftime(
                "%Y-%m-%d"
            ),
            "TODAY SALES REPORT"
        )

    def month(self, instance):

        prefix = date.today().strftime(
            "%Y-%m"
        )

        self.month_report(
            prefix
        )

    def sales_report(
        self,
        day,
        title
    ):

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(grand_total),0),
                COALESCE(SUM(profit),0)
            FROM invoices
            WHERE substr(created_at,1,10)=?
        """, (
            day,
        ))

        count, sales, profit = cur.fetchone()

        cur.execute("""
            SELECT
                invoice_no,
                customer_name,
                grand_total,
                profit,
                created_at
            FROM invoices
            WHERE substr(created_at,1,10)=?
            ORDER BY id DESC
        """, (
            day,
        ))

        rows = cur.fetchall()

        con.close()

        text = (
            f"Date: {day}\n\n"
            f"Invoices: {count}\n"
            f"Sales: {money(sales)}\n"
            f"Profit: {money(profit)}\n\n"
            "--------------------------------\n"
        )

        for row in rows:

            text += (
                f"{row[0]}\n"
                f"{row[1]}  |  "
                f"{money(row[2])}\n"
                f"Profit: {money(row[3])}\n"
                f"{row[4]}\n\n"
            )

        show_message(
            title,
            text,
            0.85
        )

    def month_report(self, prefix):

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(grand_total),0),
                COALESCE(SUM(profit),0)
            FROM invoices
            WHERE substr(created_at,1,7)=?
        """, (
            prefix,
        ))

        count, sales, profit = cur.fetchone()

        con.close()

        show_message(
            "MONTHLY REPORT",
            f"Month: {prefix}\n\n"
            f"Invoices: {count}\n"
            f"Sales: {money(sales)}\n"
            f"Profit: {money(profit)}"
        )

    def history(self, instance):

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT
                id,
                invoice_no,
                customer_name,
                grand_total,
                created_at
            FROM invoices
            ORDER BY id DESC
            LIMIT 100
        """)

        rows = cur.fetchall()

        con.close()

        text = ""

        for row in rows:

            text += (
                f"{row[1]}\n"
                f"Customer: {row[2]}\n"
                f"Total: {money(row[3])}\n"
                f"{row[4]}\n"
                "--------------------------------\n"
            )

        if not text:
            text = "No invoices found."

        show_message(
            "BILL HISTORY",
            text,
            0.88
        )

    def stock_history(self, instance):

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT
                medicine_name,
                change_type,
                quantity,
                previous_stock,
                new_stock,
                note,
                created_at
            FROM stock_history
            ORDER BY id DESC
            LIMIT 100
        """)

        rows = cur.fetchall()

        con.close()

        text = ""

        for row in rows:

            text += (
                f"{row[0]}\n"
                f"{row[1]}: {row[2]}\n"
                f"Stock: {row[3]} → {row[4]}\n"
                f"{row[5]}\n"
                f"{row[6]}\n"
                "--------------------------------\n"
            )

        show_message(
            "STOCK HISTORY",
            text or "No stock history.",
            0.88
        )

    def expiry_alerts(self, instance):

        con = connect_db()
        cur = con.cursor()

        cur.execute("""
            SELECT name, expiry, quantity
            FROM medicines
            WHERE expiry != ''
            ORDER BY expiry
        """)

        rows = cur.fetchall()

        con.close()

        today = date.today()

        alert = []

        for name, expiry, qty in rows:

            try:

                d = datetime.strptime(
                    expiry,
                    "%m/%Y"
                ).date()

                d = d.replace(day=1)

                months = (
                    (d.year - today.year) * 12
                    + d.month - today.month
                )

                if months <= 2:

                    alert.append(
                        f"{name}\n"
                        f"Expiry: {expiry}\n"
                        f"Stock: {qty}"
                    )

            except ValueError:

                continue

        show_message(
            "EXPIRY ALERTS",
            "\n\n".join(alert)
            if alert
            else "No medicines expiring within approximately 2 months.",
            0.75
        )

    def low_stock(self, instance):

        medicines = [
            row
            for row in get_medicines()
            if row[6] <= row[9]
        ]

        text = ""

        for row in medicines:

            text += (
                f"{row[1]}\n"
                f"Stock: {row[6]}\n"
                f"Minimum: {row[9]}\n\n"
            )

        show_message(
            "LOW STOCK",
            text or "No low-stock medicines.",
            0.65
        )


# ============================================================
# MORE SCREEN
# ============================================================

class MoreScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(8)
        )

        root.add_widget(
            Label(
                text="MORE",
                color=WHITE,
                font_size=dp(23),
                bold=True,
                size_hint_y=None,
                height=dp(45)
            )
        )

        buttons = [
            ("CUSTOMERS", self.customers),
            ("CATEGORIES", self.categories),
            ("BACKUP DATABASE", self.backup),
            ("RESTORE DATABASE", self.restore),
            ("APP INFORMATION", self.info),
            ("LOGOUT", self.logout)
        ]

        scroll = ScrollView()

        box = GridLayout(
            cols=1,
            spacing=dp(9),
            size_hint_y=None
        )

        box.bind(
            minimum_height=
            box.setter("height")
        )

        for text, callback in buttons:

            btn = make_button(
                text,
                CARD_LIGHT if text != "LOGOUT"
                else DANGER,
                54
            )

            btn.bind(
                on_press=callback
            )

            box.add_widget(btn)

        scroll.add_widget(box)

        root.add_widget(scroll)

        self.add_widget(root)

    def customers(self, instance):

        rows = get_customers()

        text = ""

        for row in rows:

            text += (
                f"{row[1]}\n"
                f"Phone: {row[2]}\n"
                f"Address: {row[3]}\n"
                "--------------------------------\n"
            )

        show_message(
            "CUSTOMERS",
            text or "No customers saved.",
            0.85
        )

    def categories(self, instance):

        content = RoundedBox(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(8)
        )

        name = make_input(
            "New Category"
        )

        add = make_button(
            "ADD CATEGORY",
            SUCCESS
        )

        content.add_widget(name)
        content.add_widget(add)

        popup = Popup(
            title="CATEGORIES",
            content=content,
            size_hint=(0.88, 0.48)
        )

        add.bind(
            on_press=lambda x:
            self.add_category(
                popup,
                name
            )
        )

        popup.open()

    def add_category(
        self,
        popup,
        name
    ):

        value = name.text.strip()

        if not value:
            return

        con = connect_db()
        cur = con.cursor()

        cur.execute(
            "INSERT OR IGNORE INTO categories(name) VALUES (?)",
            (value,)
        )

        con.commit()
        con.close()

        popup.dismiss()

        show_message(
            "SUCCESS",
            "Category added."
        )

    def backup(self, instance):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        destination = os.path.join(
            BACKUP_DIR,
            f"pharmacy_backup_{timestamp}.db"
        )

        try:

            shutil.copy2(
                DB_NAME,
                destination
            )

            show_message(
                "BACKUP COMPLETE",
                f"Database backup created:\n\n"
                f"{destination}"
            )

        except Exception as e:

            show_message(
                "BACKUP ERROR",
                str(e)
            )

    def restore(self, instance):

        backups = sorted(
            [
                f
                for f in os.listdir(BACKUP_DIR)
                if f.endswith(".db")
            ],
            reverse=True
        )

        if not backups:

            show_message(
                "RESTORE",
                "No backup files found."
            )

            return

        latest = os.path.join(
            BACKUP_DIR,
            backups[0]
        )

        try:

            # Validate SQLite backup
            test = sqlite3.connect(latest)
            test.execute(
                "SELECT name FROM sqlite_master LIMIT 1"
            )
            test.close()

            shutil.copy2(
                latest,
                DB_NAME
            )

            show_message(
                "RESTORE COMPLETE",
                f"Restored backup:\n{backups[0]}\n\n"
                "Restart the application."
            )

        except Exception as e:

            show_message(
                "RESTORE ERROR",
                str(e)
            )

    def info(self, instance):

        show_message(
            "PHARMACY PRO",
            "Professional Pharmacy Billing & "
            "Stock Management\n\n"
            "Kivy + SQLite\n\n"
            "Features:\n"
            "• Billing\n"
            "• Inventory\n"
            "• Customers\n"
            "• Reports\n"
            "• GST\n"
            "• PDF invoices\n"
            "• Backup / Restore\n"
            "• Stock history"
        )

    def logout(self, instance):

        self.manager.parent.parent.current = "login"


# ============================================================
# PDF GENERATOR
# ============================================================

def create_pdf_invoice(
    invoice_no,
    customer,
    phone,
    items,
    subtotal,
    discount,
    gst_percent,
    gst_amount,
    total
):

    try:

        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm

    except ImportError:

        return None

    filename = (
        invoice_no.replace("/", "_")
        + ".pdf"
    )

    path = os.path.join(
        INVOICE_DIR,
        filename
    )

    c = canvas.Canvas(
        path,
        pagesize=A4
    )

    width, height = A4

    y = height - 25 * mm

    c.setFont(
        "Helvetica-Bold",
        20
    )

    c.drawString(
        20 * mm,
        y,
        "PHARMACY PRO"
    )

    y -= 8 * mm

    c.setFont(
        "Helvetica",
        9
    )

    c.drawString(
        20 * mm,
        y,
        "PHARMACY BILL / TAX INVOICE"
    )

    y -= 12 * mm

    c.drawString(
        20 * mm,
        y,
        f"Invoice No: {invoice_no}"
    )

    c.drawRightString(
        width - 20 * mm,
        y,
        datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )
    )

    y -= 7 * mm

    c.drawString(
        20 * mm,
        y,
        f"Customer: {customer}"
    )

    y -= 5 * mm

    c.drawString(
        20 * mm,
        y,
        f"Phone: {phone}"
    )

    y -= 10 * mm

    # Table header
    c.setFont(
        "Helvetica-Bold",
        9
    )

    c.drawString(
        20 * mm,
        y,
        "Medicine"
    )

    c.drawString(
        105 * mm,
        y,
        "Qty"
    )

    c.drawString(
        125 * mm,
        y,
        "Rate"
    )

    c.drawString(
        160 * mm,
        y,
        "Amount"
    )

    y -= 5 * mm

    c.line(
        20 * mm,
        y,
        width - 20 * mm,
        y
    )

    y -= 7 * mm

    c.setFont(
        "Helvetica",
        9
    )

    for item in items:

        if y < 35 * mm:

            c.showPage()

            y = height - 25 * mm

        c.drawString(
            20 * mm,
            y,
            item["name"][:35]
        )

        c.drawString(
            105 * mm,
            y,
            str(item["quantity"])
        )

        c.drawString(
            125 * mm,
            y,
            f"{item['selling_price']:.2f}"
        )

        c.drawRightString(
            width - 20 * mm,
            y,
            f"{item['amount']:.2f}"
        )

        y -= 6 * mm

    y -= 5 * mm

    c.line(
        110 * mm,
        y,
        width - 20 * mm,
        y
    )

    y -= 7 * mm

    c.drawString(
        110 * mm,
        y,
        "Subtotal:"
    )

    c.drawRightString(
        width - 20 * mm,
        y,
        f"Rs. {subtotal:.2f}"
    )

    y -= 6 * mm

    c.drawString(
        110 * mm,
        y,
        "Discount:"
    )

    c.drawRightString(
        width - 20 * mm,
        y,
        f"Rs. {discount:.2f}"
    )

    y -= 6 * mm

    c.drawString(
        110 * mm,
        y,
        f"GST ({gst_percent:.2f}%):"
    )

    c.drawRightString(
        width - 20 * mm,
        y,
        f"Rs. {gst_amount:.2f}"
    )

    y -= 8 * mm

    c.setFont(
        "Helvetica-Bold",
        13
    )

    c.drawString(
        110 * mm,
        y,
        "TOTAL:"
    )

    c.drawRightString(
        width - 20 * mm,
        y,
        f"Rs. {total:.2f}"
    )

    y -= 18 * mm

    c.setFont(
        "Helvetica",
        9
    )

    c.drawCentredString(
        width / 2,
        y,
        "Thank you for visiting our pharmacy."
    )

    c.save()

    return path


# ============================================================
# ANDROID SHARE / PRINT HELPER
# ============================================================

def share_file(path):

    if not path:
        return False

    try:

        from jnius import autoclass

        PythonActivity = autoclass(
            "org.kivy.android.PythonActivity"
        )

        Intent = autoclass(
            "android.content.Intent"
        )

        Uri = autoclass(
            "android.net.Uri"
        )

        activity = PythonActivity.mActivity

        intent = Intent(
            Intent.ACTION_SEND
        )

        intent.setType(
            "application/pdf"
        )

        intent.putExtra(
            Intent.EXTRA_STREAM,
            Uri.parse(
                "file://" + path
            )
        )

        chooser = Intent.createChooser(
            intent,
            "Share Invoice"
        )

        activity.startActivity(chooser)

        return True

    except Exception:

        return False


# ============================================================
# MAIN APP
# ============================================================

class PharmacyProApp(App):

    def build(self):

        Window.clearcolor = BG

        create_database()

        manager = ScreenManager()

        manager.add_widget(
            LoginScreen(
                name="login"
            )
        )

        manager.add_widget(
            MainScreen(
                name="main"
            )
        )

        return manager


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    PharmacyProApp().run()
