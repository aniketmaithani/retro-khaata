## RETRO KHAATA v1.0

Retro Khaata is a Python-based command-line invoicing system designed with a retro gaming console aesthetic. It allows freelancers and small business owners to manage clients, generate professional PDF invoices, and track billing history directly from the terminal.

### Features

- Retro Terminal UI: Green-on-black aesthetic with simulated boot sequences and boxy menus.

- Client Management: Support for both Domestic (Indian) and International (Foreign) clients.

- Currency Support: Handles multiple currencies (USD, EUR, GBP, JPY, INR, etc.) for international billing.

- Invoice Generation: Create professional PDF invoices with automatic tax ID handling (GSTIN/VAT).

- Data Persistence: Automatically saves clients and invoices to JSON files.

- Configuration: Customizable business details (Bank info, Address, PAN, etc.).

### Prerequisites

- Python 3.6 or higher

### Installation

- Clone the repository or download the source code.

- Install the required dependencies using the requirements file.

- pip install -r requirements.txt

### Usage

- Run the application using Python:

`python main.py`

- Make sure to setup your DEFAULT_CONFIG in `main.py`

### Command Reference

Once inside the application, use the following commands:

### Client Management


add-client: Add a new client (starts a wizard).

list-clients: View all stored clients.

update-client: Modify existing client details.

delete-client: Remove a client from the database.

### Invoicing

create-invoice [Client Name]: Start the invoice creation wizard.

list-invoices [Client Name]: View invoice history.

view-invoice [Invoice ID]: View raw data of a specific invoice.

delete-invoice [Invoice ID]: Delete a specific invoice.

generate-pdf [Invoice ID]: Regenerate the PDF for an existing invoice.

### System and Config

config: View current business/bank configuration.

update-config: Update your business details (Name, Bank Account, Swift Code, etc.).

clear: Clear the terminal screen.

exit: Close the application.

help: Display the help menu.

### Configuration

The system initializes with default configuration values. You should run the 'update-config' command upon first launch to set your own Name, Address, PAN, and Bank Details. These details will appear on all generated PDFs.

File Structure

main.py: Main application script.

clients.json: Database for client information (created automatically).

invoices.json: Database for invoice history (created automatically).

config.json: Stores user configuration (created automatically).

invoices/: Directory where generated PDFs are saved.
