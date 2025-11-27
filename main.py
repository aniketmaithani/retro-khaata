import argparse
import json
import os
import shlex
import sys
import time
from datetime import datetime

from fpdf import FPDF
from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

# --- CONFIGURATION ---
DATA_FILE_CLIENTS = "clients.json"
DATA_FILE_INVOICES = "invoices.json"
DATA_FILE_CONFIG = "config.json"
INVOICE_DIR = "invoices"

# Initialize Rich Console
console = Console()

# --- DEFAULT CONFIGURATION ---
DEFAULT_CONFIG = {
    "name": "RANDOM NAME",
    "pan": "SOME NUMBER",
    "address": "OKAY",
    "bank_name": "BANKBANK",
    "branch": "DDSD",
    "branch_address": "ADSADSD",
    "account_name": "RANDOM NAME",
    "account_number": "82838388282388128381283",
    "ifsc": "asdjalskjdoqij",
    "swift_bic": "klsadjaslkdj",
    "branch_code": "aslkdalksjdaslkjd",
}

# --- UTILITY CLASSES ---


class RetroUI:
    """Handles the Retro Gaming / Terminal UI aesthetics."""

    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def print_banner():
        RetroUI.clear_screen()
        title = """
        /$$$$$$$  /$$$$$$$$ /$$$$$$$$ /$$$$$$$   /$$$$$$        /$$   /$$ /$$   /$$  /$$$$$$   /$$$$$$  /$$$$$$$$ /$$$$$$
       | $$__  $$| $$_____/|__  $$__/| $$__  $$ /$$__  $$      | $$  /$$/| $$  | $$ /$$__  $$ /$$__  $$|__  $$__//$$__  $$
       | $$  \ $$| $$         | $$   | $$  \ $$| $$  \ $$      | $$ /$$/ | $$  | $$| $$  \ $$| $$  \ $$   | $$  | $$  \ $$
       | $$$$$$$/| $$$$$      | $$   | $$$$$$$/| $$  | $$      | $$$$$/  | $$$$$$$$| $$$$$$$$| $$$$$$$$   | $$  | $$$$$$$$
       | $$__  $$| $$__/      | $$   | $$__  $$| $$  | $$      | $$  $$  | $$__  $$| $$__  $$| $$__  $$   | $$  | $$__  $$
       | $$  \ $$| $$         | $$   | $$  \ $$| $$  | $$      | $$\  $$ | $$  | $$| $$  | $$| $$  | $$   | $$  | $$  | $$
       | $$  | $$| $$$$$$$$   | $$   | $$  | $$|  $$$$$$/      | $$ \  $$| $$  | $$| $$  | $$| $$  | $$   | $$  | $$  | $$
       |__/  |__/|________/   |__/   |__/  |__/ \______/       |__/  \__/|__/  |__/|__/  |__/|__/  |__/   |__/  |__/  |__/
        >>> RETRO KHAATA v1.0 <<<
        """
        console.print(
            Panel(
                Align.center(title),
                style="bold green",
                border_style="green",
                box=box.DOUBLE,
            )
        )

    @staticmethod
    def boot_sequence():
        RetroUI.clear_screen()
        steps = [
            "Initializing Memory...",
            "Mounting File System...",
            "Loading Configuration...",
            "Checking Peripherals...",
            "System Ready.",
        ]
        with Live(console=console, refresh_per_second=10) as live:
            for step in steps:
                time.sleep(0.1)
                live.update(Text(f">>> {step} [OK]", style="bold green"))
        time.sleep(0.5)

    @staticmethod
    def success(msg):
        console.print(f"[bold green]>> SUCCESS: {msg}[/bold green]")

    @staticmethod
    def error(msg):
        console.print(f"[bold red]>> ERROR: {msg}[/bold red]")

    @staticmethod
    def info(msg):
        console.print(f"[bold cyan]>> INFO: {msg}[/bold cyan]")


class InvoicePDF(FPDF):
    """Custom PDF Generator handling Invoice Layout."""

    def __init__(self, client, invoice_data, config):
        super().__init__()
        self.client = client
        self.invoice_data = invoice_data
        self.config = config
        self.currency_code = client.get("currency", "INR")
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        # Header
        self.set_font("Courier", "B", 20)
        self.cell(0, 10, "INVOICE", 0, 1, "R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Courier", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def generate(self):
        self.add_page()

        # --- SENDER DETAILS (From Config) ---
        self.set_font("Courier", "B", 12)
        self.cell(0, 5, self.config.get("name", "Unknown"), 0, 1)
        self.set_font("Courier", "", 10)

        # Handle multi-line address
        addr_lines = self.config.get("address", "").split("\n")
        for line in addr_lines:
            self.cell(0, 5, line, 0, 1)

        self.cell(0, 5, f"PAN: {self.config.get('pan', 'N/A')}", 0, 1)
        self.ln(10)

        # --- BILL TO & INFO ---
        y_start = self.get_y()

        # Left side: Client
        self.set_font("Courier", "B", 11)
        self.cell(100, 5, "BILL TO:", 0, 1)
        self.set_font("Courier", "", 10)
        self.cell(100, 5, self.client["name"], 0, 1)
        self.cell(100, 5, self.client["address"], 0, 1)
        self.cell(100, 5, f"{self.client['country']}", 0, 1)

        if self.client["type"] == "Foreign":
            self.cell(100, 5, f"VAT ID: {self.client.get('vat_id', 'N/A')}", 0, 1)
        else:
            self.cell(100, 5, f"GSTIN: {self.client.get('gst_id', 'N/A')}", 0, 1)

        # Right side: Invoice Meta
        self.set_xy(120, y_start)
        self.cell(0, 5, f"Invoice #: {self.invoice_data['id']}", 0, 1, "R")
        self.set_x(120)
        self.cell(0, 5, f"Date: {self.invoice_data['date']}", 0, 1, "R")
        self.set_x(120)
        self.cell(0, 5, f"Currency: {self.currency_code}", 0, 1, "R")

        self.ln(20)

        # --- TABLE HEADERS ---
        self._draw_table_header()

        # --- ITEMS ---
        total = 0
        services = self.invoice_data.get("services", [])
        reimbursements = self.invoice_data.get("reimbursements", [])

        # Services
        if services:
            self.set_font("Courier", "B", 10)
            self.cell(0, 10, "Professional Services", 0, 1)
            self.set_font("Courier", "", 10)

            for item in services:
                line_total = item["rate"] * item["qty"]
                total += line_total
                desc = f"{item['desc']} ({item['qty']} hrs @ {item['rate']})"
                self.cell(110, 8, desc, 1)
                self.cell(30, 8, str(item["qty"]), 1, 0, "C")
                self.cell(50, 8, f"{line_total:.2f}", 1, 0, "R")
                self.ln()

        # Reimbursements
        if reimbursements:
            self.set_font("Courier", "B", 10)
            self.cell(0, 10, "Reimbursements", 0, 1)
            self.set_font("Courier", "", 10)

            for item in reimbursements:
                line_total = item["rate"] * item["qty"]
                total += line_total
                self.cell(110, 8, item["desc"], 1)
                self.cell(30, 8, "-", 1, 0, "C")
                self.cell(50, 8, f"{line_total:.2f}", 1, 0, "R")
                self.ln()

        # --- TOTAL ---
        self.ln(5)
        self.set_font("Courier", "B", 12)
        self.set_fill_color(220, 220, 220)
        self.cell(140, 12, "TOTAL AMOUNT DUE:", 1, 0, "R", True)
        self.cell(50, 12, f"{self.currency_code} {total:.2f}", 1, 1, "R", True)

        # --- BANK DETAILS ---
        self.ln(20)
        self.set_font("Courier", "B", 10)
        self.cell(0, 5, "Payment Information:", 0, 1)
        self.set_font("Courier", "", 10)
        self.cell(0, 5, f"Beneficiary: {self.config.get('account_name', '')}", 0, 1)
        self.cell(0, 5, f"Bank: {self.config.get('bank_name', '')}", 0, 1)
        self.cell(0, 5, f"Account No: {self.config.get('account_number', '')}", 0, 1)

        if self.client["type"] == "Foreign":
            self.cell(0, 5, f"SWIFT/BIC: {self.config.get('swift_bic', '')}", 0, 1)
        else:
            self.cell(0, 5, f"IFSC: {self.config.get('ifsc', '')}", 0, 1)

        self.cell(
            0, 5, f"Branch Address: {self.config.get('branch_address', '')}", 0, 1
        )

    def _draw_table_header(self):
        self.set_font("Courier", "B", 10)
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.cell(110, 8, "Description", 1, 0, "C", True)
        self.cell(30, 8, "Qty/Hrs", 1, 0, "C", True)
        self.cell(50, 8, "Amount", 1, 1, "C", True)
        self.set_text_color(0, 0, 0)


# --- DATA MANAGERS ---


class DataManager:
    @staticmethod
    def load(filename, default=None):
        if default is None:
            default = []
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    return json.load(f)
            except:
                return default
        return default

    @staticmethod
    def save(filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)


# --- COMMAND PROCESSOR ---


class RetroShell:
    def __init__(self):
        self.clients = DataManager.load(DATA_FILE_CLIENTS, [])
        self.invoices = DataManager.load(DATA_FILE_INVOICES, [])
        self.config = DataManager.load(DATA_FILE_CONFIG, DEFAULT_CONFIG)
        if not os.path.exists(INVOICE_DIR):
            os.makedirs(INVOICE_DIR)

    # --- CLIENT COMMANDS ---

    def do_add_client(self):
        console.print("[bold green]>> ADD NEW CLIENT <<[/bold green]")
        name = Prompt.ask("[green]Company Name[/green]")
        address = Prompt.ask("[green]Address[/green]")

        console.print("1. Indian (Domestic)\n2. Foreign (International)")
        choice = IntPrompt.ask("[green]Select Type[/green]", choices=["1", "2"])
        client_type = "Indian" if choice == 1 else "Foreign"

        extra_data = {}
        if client_type == "Indian":
            extra_data["gst_id"] = Prompt.ask("[green]GSTIN/PAN[/green]")
            extra_data["currency"] = "INR"
            extra_data["country"] = "India"
        else:
            extra_data["country"] = Prompt.ask("[green]Country[/green]")
            extra_data["vat_id"] = Prompt.ask("[green]VAT ID[/green]")
            currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
            for idx, c in enumerate(currencies, 1):
                console.print(f"{idx}. {c}")
            c_choice = IntPrompt.ask(
                "[green]Currency[/green]",
                choices=[str(i) for i in range(1, len(currencies) + 1)],
            )
            extra_data["currency"] = currencies[c_choice - 1]

        client = {
            "id": int(time.time()),  # Unique ID based on timestamp
            "name": name,
            "address": address,
            "type": client_type,
            **extra_data,
        }
        self.clients.append(client)
        DataManager.save(DATA_FILE_CLIENTS, self.clients)
        RetroUI.success(f"Client '{name}' added.")

    def do_list_clients(self):
        table = Table(title="CLIENT DATABASE", border_style="green", box=box.SIMPLE)
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Currency", style="yellow")

        for c in self.clients:
            table.add_row(str(c["id"]), c["name"], c["type"], c["currency"])
        console.print(table)

    def do_update_client(self):
        self.do_list_clients()
        c_id = IntPrompt.ask("[green]Enter Client ID to update[/green]")
        client = next((c for c in self.clients if c["id"] == c_id), None)
        if not client:
            RetroUI.error("Client not found.")
            return

        console.print(f"Updating: [bold]{client['name']}[/bold]")
        if Confirm.ask("Update Name?"):
            client["name"] = Prompt.ask("New Name", default=client["name"])
        if Confirm.ask("Update Address?"):
            client["address"] = Prompt.ask("New Address", default=client["address"])

        # Specific fields
        if client["type"] == "Foreign":
            if Confirm.ask("Update VAT ID?"):
                client["vat_id"] = Prompt.ask(
                    "New VAT ID", default=client.get("vat_id", "")
                )
        else:
            if Confirm.ask("Update GSTIN?"):
                client["gst_id"] = Prompt.ask(
                    "New GSTIN", default=client.get("gst_id", "")
                )

        DataManager.save(DATA_FILE_CLIENTS, self.clients)
        RetroUI.success("Client updated.")

    def do_delete_client(self):
        self.do_list_clients()
        c_id = IntPrompt.ask("[green]Enter Client ID to delete[/green]")
        client = next((c for c in self.clients if c["id"] == c_id), None)
        if not client:
            RetroUI.error("Client not found.")
            return

        if Confirm.ask(f"[red]Are you sure you want to delete {client['name']}?[/red]"):
            self.clients.remove(client)
            DataManager.save(DATA_FILE_CLIENTS, self.clients)
            RetroUI.success("Client deleted.")

    # --- INVOICE COMMANDS ---

    def do_create_invoice(self, args):
        # Parse args manually or simple logic
        if not self.clients:
            RetroUI.error("No clients found. Add a client first.")
            return

        # Find client (fuzzy match or list)
        target_client_name = args[0] if args else None
        client = None

        if target_client_name:
            # Simple fuzzy search
            client = next(
                (
                    c
                    for c in self.clients
                    if target_client_name.lower() in c["name"].lower()
                ),
                None,
            )

        if not client:
            self.do_list_clients()
            c_id = IntPrompt.ask("\n[green]Enter Client ID from list[/green]")
            client = next((c for c in self.clients if c["id"] == c_id), None)

        if not client:
            RetroUI.error("Invalid Client.")
            return

        # Generate Invoice
        console.print(
            f"\n[bold green]>> NEW INVOICE FOR: {client['name']} <<[/bold green]"
        )

        items_service = []
        items_reimburse = []

        # Interactive Item Entry
        while True:
            console.print("\n[cyan]--- Add Service ---[/cyan]")
            desc = Prompt.ask("[green]Description (or 'done')[/green]")
            if desc.lower() == "done":
                break

            # Simple wizard
            is_hourly = Confirm.ask("Is this Hourly?")
            rate = FloatPrompt.ask(f"Rate ({client['currency']})")
            qty = FloatPrompt.ask("Hours" if is_hourly else "Quantity", default=1.0)

            items_service.append({"desc": desc, "rate": rate, "qty": qty})

        if Confirm.ask("\n[yellow]Add Reimbursements?[/yellow]"):
            while True:
                console.print("\n[cyan]--- Add Expense ---[/cyan]")
                desc = Prompt.ask("[green]Description (or 'done')[/green]")
                if desc.lower() == "done":
                    break
                amt = FloatPrompt.ask(f"Amount ({client['currency']})")
                items_reimburse.append({"desc": desc, "rate": amt, "qty": 1.0})

        if not items_service and not items_reimburse:
            RetroUI.error("Empty invoice cancelled.")
            return

        # Create Invoice Object
        inv_number = f"INV-{int(time.time())}"
        invoice_data = {
            "id": inv_number,
            "client_id": client["id"],
            "client_name": client["name"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "services": items_service,
            "reimbursements": items_reimburse,
            "total": sum(i["rate"] * i["qty"] for i in items_service + items_reimburse),
        }

        self.invoices.append(invoice_data)
        DataManager.save(DATA_FILE_INVOICES, self.invoices)

        # Generate PDF
        self._generate_pdf_file(client, invoice_data)

    def _generate_pdf_file(self, client, invoice_data):
        try:
            pdf = InvoicePDF(client, invoice_data, self.config)
            pdf.generate()
            filename = f"{INVOICE_DIR}/{client['name'].replace(' ', '_')}_{invoice_data['id']}.pdf"
            pdf.output(filename)
            RetroUI.success(f"Invoice Saved & PDF Generated: {filename}")
        except Exception as e:
            RetroUI.error(f"PDF Generation Failed: {e}")

    def do_list_invoices(self, args):
        table = Table(title="INVOICE HISTORY", border_style="green", box=box.SIMPLE)
        table.add_column("INV #", style="cyan")
        table.add_column("Date", style="dim")
        table.add_column("Client", style="green")
        table.add_column("Total", justify="right", style="bold yellow")

        # Filter by client if arg provided
        filter_name = args[0].lower() if args else None

        for inv in self.invoices:
            if filter_name and filter_name not in inv["client_name"].lower():
                continue
            table.add_row(
                inv["id"], inv["date"], inv["client_name"], f"{inv['total']:.2f}"
            )

        console.print(table)

    def do_view_invoice(self, args):
        if not args:
            RetroUI.error("Usage: view-invoice <INV_NUM>")
            return

        inv_id = args[0]
        inv = next((i for i in self.invoices if i["id"] == inv_id), None)
        if not inv:
            RetroUI.error("Invoice not found.")
            return

        console.print(
            Panel(
                json.dumps(inv, indent=2),
                title=f"INVOICE {inv_id}",
                border_style="green",
            )
        )

    def do_delete_invoice(self, args):
        if not args:
            RetroUI.error("Usage: delete-invoice <INV_NUM>")
            return

        inv_id = args[0]
        inv = next((i for i in self.invoices if i["id"] == inv_id), None)

        if inv:
            if Confirm.ask(f"[red]Delete invoice {inv_id}?[/red]"):
                self.invoices.remove(inv)
                DataManager.save(DATA_FILE_INVOICES, self.invoices)
                RetroUI.success("Invoice deleted.")
        else:
            RetroUI.error("Invoice not found.")

    def do_generate_pdf(self, args):
        if not args:
            RetroUI.error("Usage: generate-pdf <INV_NUM>")
            return

        inv_id = args[0]
        inv = next((i for i in self.invoices if i["id"] == inv_id), None)
        if not inv:
            RetroUI.error("Invoice not found.")
            return

        client = next((c for c in self.clients if c["id"] == inv["client_id"]), None)
        if not client:
            RetroUI.error("Client associated with invoice no longer exists.")
            return

        self._generate_pdf_file(client, inv)

    # --- CONFIG COMMANDS ---

    def do_config(self):
        table = Table(
            title="SYSTEM CONFIGURATION", border_style="blue", box=box.ROUNDED
        )
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        for k, v in self.config.items():
            table.add_row(k.replace("_", " ").title(), str(v))
        console.print(table)

    def do_update_config(self):
        console.print(
            "[bold yellow]Update Configuration (Press Enter to keep current)[/bold yellow]"
        )
        for k in self.config.keys():
            new_val = Prompt.ask(
                f"{k.replace('_', ' ').title()}", default=str(self.config[k])
            )
            self.config[k] = new_val
        DataManager.save(DATA_FILE_CONFIG, self.config)
        RetroUI.success("Configuration updated.")

    def do_help(self):
        table = Table(
            box=box.DOUBLE,
            border_style="bold green",
            show_header=True,
            header_style="bold black on green",
            expand=True,
        )
        table.add_column("COMMAND", style="bold cyan", width=20)
        table.add_column("PARAMETERS", style="yellow", width=20)
        table.add_column("FUNCTION", style="green")

        table.add_section()
        table.add_row("[bold white]CLIENTS[/]", "", "")
        table.add_row("add-client", "", "Initialize new client entity")
        table.add_row("list-clients", "", "Display client database")
        table.add_row("update-client", "", "Modify client registry")
        table.add_row("delete-client", "", "Purge client from memory")

        table.add_section()
        table.add_row("[bold white]INVOICING[/]", "", "")
        table.add_row("create-invoice", "<CLIENT>", "Execute billing protocol")
        table.add_row("list-invoices", "[CLIENT]", "Access transaction logs")
        table.add_row("view-invoice", "<INV_ID>", "Decode invoice data")
        table.add_row("delete-invoice", "<INV_ID>", "Erase transaction record")
        table.add_row("generate-pdf", "<INV_ID>", "Compile PDF artifact")

        table.add_section()
        table.add_row("[bold white]SYSTEM[/]", "", "")
        table.add_row("config", "", "Display bio/bank info")
        table.add_row("update-config", "", "Reconfigure user details")
        table.add_row("clear", "", "Refresh CRT display")
        table.add_row("exit", "", "Power down system")

        console.print(
            Panel(
                table,
                title="[bold green]COMMAND REFERENCE MANUAL v2.1[/bold green]",
                border_style="green",
                box=box.HEAVY,
            )
        )

    # --- MAIN LOOP ---

    def run(self):
        RetroUI.print_banner()
        self.do_help()

        while True:
            try:
                user_input = Prompt.ask("\n[bold green]RETRO-OS >[/bold green]")
                if not user_input.strip():
                    continue

                parts = shlex.split(user_input)
                command = parts[0].lower()
                args = parts[1:]

                if command == "exit":
                    console.print("[bold red]Shutting down system...[/bold red]")
                    sys.exit()
                elif command == "clear":
                    RetroUI.clear_screen()
                    RetroUI.print_banner()
                elif command == "help":
                    self.do_help()

                # Client Mapping
                elif command == "add-client":
                    self.do_add_client()
                elif command == "list-clients":
                    self.do_list_clients()
                elif command == "update-client":
                    self.do_update_client()
                elif command == "delete-client":
                    self.do_delete_client()

                # Invoice Mapping
                elif command == "create-invoice":
                    self.do_create_invoice(args)
                elif command == "list-invoices":
                    self.do_list_invoices(args)
                elif command == "view-invoice":
                    self.do_view_invoice(args)
                elif command == "delete-invoice":
                    self.do_delete_invoice(args)
                elif command == "generate-pdf":
                    self.do_generate_pdf(args)

                # Config Mapping
                elif command == "config":
                    self.do_config()
                elif command == "update-config":
                    self.do_update_config()

                else:
                    RetroUI.error(f"Unknown command: {command}")

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except Exception as e:
                RetroUI.error(f"System Failure: {e}")


if __name__ == "__main__":
    RetroUI.boot_sequence()
    shell = RetroShell()
    shell.run()
