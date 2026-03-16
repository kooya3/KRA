#!/usr/bin/env python3

import sys
import logging
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.logging import RichHandler

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
from src.kra_client import KRAClient
from src.models import ObligationCode
from src.exceptions import KRAAPIError, AuthenticationError, ValidationError


console = Console()

# Setup logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)


def print_obligation_codes():
    """Display available obligation codes in a table"""
    table = Table(title="Available Obligation Codes", show_header=True, header_style="bold magenta")
    table.add_column("Code", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    
    for code, description in settings.get_obligation_codes().items():
        table.add_row(code, description)
    
    console.print(table)


@click.group()
@click.version_option(version="0.1.0", prog_name="KRA Tax Filing CLI")
def cli():
    """KRA Tax Return Filing System - Command Line Interface"""
    pass


@cli.command()
def test_connection():
    """Test connection to KRA API"""
    console.print("\n[bold cyan]Testing KRA API Connection...[/bold cyan]\n")
    
    try:
        settings.validate()
        client = KRAClient(
            client_id=settings.KRA_CLIENT_ID,
            client_secret=settings.KRA_CLIENT_SECRET,
            base_url=settings.KRA_BASE_URL,
        )
        
        if client.check_connection():
            console.print("[bold green]✓[/bold green] Successfully connected to KRA API")
            console.print(f"[dim]Base URL: {settings.KRA_BASE_URL}[/dim]")
        else:
            console.print("[bold red]✗[/bold red] Failed to connect to KRA API")
            
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        console.print("[yellow]Please check your .env file[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.option(
    "--pin",
    default=settings.DEFAULT_TAXPAYER_PIN,
    help="Taxpayer PIN (e.g., A017174812E)",
    prompt="Enter Taxpayer PIN" if not settings.DEFAULT_TAXPAYER_PIN else False,
)
@click.option(
    "--obligation",
    type=click.Choice(["4", "6", "7", "9"]),
    default=settings.DEFAULT_OBLIGATION_CODE,
    help="Obligation code (4=Company, 6=Withholding, 7=PAYE, 9=VAT)",
    prompt="Select obligation code",
)
@click.option(
    "--month",
    type=click.IntRange(1, 12),
    default=int(settings.DEFAULT_MONTH) if settings.DEFAULT_MONTH else datetime.now().month,
    help="Month (1-12)",
    prompt="Enter month",
)
@click.option(
    "--year",
    type=click.IntRange(2000, 2100),
    default=int(settings.DEFAULT_YEAR) if settings.DEFAULT_YEAR else datetime.now().year,
    help="Year",
    prompt="Enter year",
)
@click.option(
    "--confirm",
    is_flag=True,
    default=False,
    help="Skip confirmation prompt",
)
def file_nil(pin, obligation, month, year, confirm):
    """File a NIL return for the specified tax period"""
    
    # Display filing details
    console.print("\n[bold cyan]NIL Return Filing Details[/bold cyan]")
    
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="dim")
    table.add_column("Value", style="white")
    
    table.add_row("Taxpayer PIN:", pin)
    table.add_row("Obligation:", f"{settings.get_obligation_codes()[obligation]} ({obligation})")
    table.add_row("Month:", str(month).zfill(2))
    table.add_row("Year:", str(year))
    
    console.print(table)
    
    if not confirm:
        if not click.confirm("\nDo you want to proceed with filing?"):
            console.print("[yellow]Filing cancelled[/yellow]")
            return
    
    console.print("\n[bold cyan]Filing NIL return...[/bold cyan]\n")
    
    try:
        settings.validate()
        
        client = KRAClient(
            client_id=settings.KRA_CLIENT_ID,
            client_secret=settings.KRA_CLIENT_SECRET,
            base_url=settings.KRA_BASE_URL,
        )
        
        response = client.file_nil_return(
            taxpayer_pin=pin,
            obligation_code=obligation,
            month=str(month),
            year=str(year),
        )
        
        # Success panel
        success_panel = Panel.fit(
            f"[bold green]✓ Successfully Filed NIL Return[/bold green]\n\n"
            f"[white]Message: {response.RESPONSE.Message}[/white]\n"
            f"[dim]Acknowledgment Number: {response.RESPONSE.AckNumber}[/dim]\n"
            f"[dim]Response Code: {response.RESPONSE.ResponseCode}[/dim]",
            border_style="green",
            title="Success",
        )
        console.print(success_panel)
        
        # Save acknowledgment to file
        save_acknowledgment(pin, obligation, month, year, response.RESPONSE.AckNumber)
        
    except ValidationError as e:
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
    except AuthenticationError as e:
        console.print(f"[bold red]Authentication Error:[/bold red] {e}")
        console.print("[yellow]Please check your API credentials in .env file[/yellow]")
    except KRAAPIError as e:
        console.print(f"[bold red]API Error:[/bold red] {e}")
        if "timeout" in str(e).lower() or "504" in str(e):
            console.print("\n[yellow]💡 Suggestion:[/yellow] The KRA sandbox server appears to be slow.")
            console.print("[dim]Try running the command again in a few minutes.[/dim]")
        elif "502" in str(e) or "503" in str(e):
            console.print("\n[yellow]💡 Suggestion:[/yellow] The KRA server is temporarily unavailable.")
            console.print("[dim]This is common with sandbox environments. Try again later.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")
        logger.exception("Unexpected error occurred")


@cli.command()
def list_obligations():
    """List available tax obligation codes"""
    print_obligation_codes()


@cli.command()
def check_config():
    """Check configuration and display current settings"""
    console.print("\n[bold cyan]Current Configuration[/bold cyan]\n")
    
    table = Table(show_header=False, box=None)
    table.add_column("Setting", style="dim")
    table.add_column("Value", style="white")
    
    # Check if credentials are set
    client_id_status = "✓ Set" if settings.KRA_CLIENT_ID else "✗ Not set"
    client_secret_status = "✓ Set" if settings.KRA_CLIENT_SECRET else "✗ Not set"
    
    table.add_row("KRA Client ID:", client_id_status)
    table.add_row("KRA Client Secret:", client_secret_status)
    table.add_row("KRA Base URL:", settings.KRA_BASE_URL)
    table.add_row("", "")
    table.add_row("Default PIN:", settings.DEFAULT_TAXPAYER_PIN or "Not set")
    table.add_row("Default Obligation:", settings.DEFAULT_OBLIGATION_CODE)
    table.add_row("Default Month:", settings.DEFAULT_MONTH or "Current month")
    table.add_row("Default Year:", settings.DEFAULT_YEAR or "Current year")
    
    console.print(table)
    
    try:
        settings.validate()
        console.print("\n[bold green]✓[/bold green] Configuration is valid")
    except ValueError as e:
        console.print(f"\n[bold red]✗[/bold red] Configuration error: {e}")
        console.print("[yellow]Please update your .env file[/yellow]")


def save_acknowledgment(pin, obligation, month, year, ack_number):
    """Save acknowledgment number to a file"""
    try:
        ack_dir = Path("acknowledgments")
        ack_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = ack_dir / f"NIL_{pin}_{year}{str(month).zfill(2)}_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(f"NIL Return Acknowledgment\n")
            f.write(f"========================\n\n")
            f.write(f"Taxpayer PIN: {pin}\n")
            f.write(f"Obligation Code: {obligation}\n")
            f.write(f"Period: {str(month).zfill(2)}/{year}\n")
            f.write(f"Filed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Acknowledgment Number: {ack_number}\n")
        
        console.print(f"\n[dim]Acknowledgment saved to: {filename}[/dim]")
        
    except Exception as e:
        logger.error(f"Failed to save acknowledgment: {e}")


if __name__ == "__main__":
    cli()