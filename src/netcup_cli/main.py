"""
Main CLI entry point for netcup CLI.
"""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .api.client import NetcupAPIClient
from .api.dns import DNSManager, DNSRecord
from .config.manager import ConfigManager
from .utils.exceptions import (
    NetcupError, 
    ConfigurationError, 
    AuthenticationError, 
    APIError
)

console = Console()


def handle_error(error: Exception) -> None:
    """Handle and display errors in a user-friendly way."""
    if isinstance(error, ConfigurationError):
        console.print(f"[red]Configuration Error:[/red] {error}")
        console.print("\n[yellow]Tip:[/yellow] Run 'netcup auth login' to set up your credentials.")
    elif isinstance(error, AuthenticationError):
        console.print(f"[red]Authentication Error:[/red] {error}")
        console.print("\n[yellow]Tip:[/yellow] Check your credentials and try 'netcup auth login' again.")
    elif isinstance(error, APIError):
        console.print(f"[red]API Error:[/red] {error}")
        if hasattr(error, 'status_code') and error.status_code:
            console.print(f"[dim]Status Code: {error.status_code}[/dim]")
            
            # Provide specific help for common errors
            if error.status_code == 4008:
                console.print("\n[yellow]💡 Tip:[/yellow] This error usually means:")
                console.print("  • DNS management is not enabled for this domain in your netcup CCP")
                console.print("  • The domain doesn't use netcup nameservers") 
                console.print("  • Your API key lacks DNS management permissions")
                console.print("  • The domain type may not support DNS API (check if it's 'zusätzlich')")
                console.print("\n[cyan]To fix:[/cyan]")
                console.print("  1. Log into your netcup Customer Control Panel (CCP)")
                console.print("  2. Go to 'Domains' → select your domain")
                console.print("  3. Look for 'DNS' or 'DNS Management' section") 
                console.print("  4. Ensure DNS management is enabled/activated")
                console.print("\nRun '[cyan]netcup dns check[/cyan]' for more information.")
    elif isinstance(error, NetcupError):
        console.print(f"[red]Error:[/red] {error}")
    else:
        console.print(f"[red]Unexpected Error:[/red] {error}")
        console.print("\n[dim]If this persists, please report this issue.[/dim]")


@click.group()
@click.version_option(version="0.1.0", prog_name="netcup")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--debug', is_flag=True, help='Enable debug output')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, debug: bool) -> None:
    """netcup CLI - Manage your netcup DNS records from the command line."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    
    # Set debug environment variable for other modules
    if debug:
        import os
        os.environ['NETCUP_DEBUG'] = '1'


@cli.group()
def auth() -> None:
    """Authentication commands."""
    pass


@auth.command()
@click.option('--customer-number', prompt='Customer Number', help='Your netcup customer number')
@click.option('--api-key', prompt='API Key', help='Your netcup API key')
@click.option('--api-password', prompt='API Password', hide_input=True, help='Your netcup API password')
def login(customer_number: str, api_key: str, api_password: str) -> None:
    """Set up authentication credentials."""
    try:
        config_manager = ConfigManager()
        
        # Save credentials
        config_manager.save_credentials(customer_number, api_key, api_password)
        
        # Test the credentials by logging in
        api_client = NetcupAPIClient(config_manager)
        session_id = api_client.login()
        
        console.print("[green]✓[/green] Authentication successful!")
        console.print(f"[dim]Session ID: {session_id[:8]}...[/dim]")
        console.print("\n[yellow]Credentials have been securely stored in your system keyring.[/yellow]")
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@auth.command()
def logout() -> None:
    """Clear stored credentials and end session."""
    try:
        config_manager = ConfigManager()
        
        # Try to logout from API if we have a session
        try:
            api_client = NetcupAPIClient(config_manager)
            api_client.logout()
        except ConfigurationError:
            # No credentials stored, that's fine
            pass
        except Exception:
            # Logout failed, but we'll still clear local credentials
            pass
        
        # Clear stored credentials
        config_manager.clear_credentials()
        console.print("[green]✓[/green] Logged out and credentials cleared.")
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@auth.command()
def status() -> None:
    """Check authentication status."""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.has_credentials():
            console.print("[yellow]No credentials stored.[/yellow]")
            console.print("Run 'netcup auth login' to authenticate.")
            return
        
        # Try to make an authenticated request to verify credentials
        api_client = NetcupAPIClient(config_manager)
        api_client.login()  # This will test the credentials
        
        config = config_manager.get_config()
        console.print("[green]✓[/green] Authenticated")
        console.print(f"Customer Number: [cyan]{config.customer_number}[/cyan]")
        console.print(f"API Key: [cyan]{config.api_key[:8]}...[/cyan]")
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@cli.group()
def dns() -> None:
    """DNS management commands."""
    pass


@dns.command()
def check() -> None:
    """Check if DNS API is working and list requirements."""
    try:
        config_manager = ConfigManager()
        api_client = NetcupAPIClient(config_manager)
        
        # Test authentication first
        session_id = api_client.login()
        console.print("[green]✓[/green] Authentication successful")
        
        console.print("\n[bold]DNS API Requirements:[/bold]")
        console.print("To use the DNS API, you need domains that:")
        console.print("  1. Are registered through your netcup account, OR")
        console.print("  2. Have netcup nameservers configured")
        console.print("  3. Are set up for DNS management in your netcup CCP")
        
        console.print("\n[bold]netcup Nameservers:[/bold]")
        console.print("  • root-dns.netcup.net")
        console.print("  • second-dns.netcup.net") 
        console.print("  • third-dns.netcup.net")
        
        console.print("\n[yellow]If you're getting 'Input value in invalid format' errors,[/yellow]")
        console.print("[yellow]your domain may not be configured for netcup DNS management.[/yellow]")
        
        api_client.logout()
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@dns.group()
def zone() -> None:
    """DNS zone commands."""
    pass


@zone.command()
@click.argument('domain')
def info(domain: str) -> None:
    """Get information about a DNS zone."""
    try:
        config_manager = ConfigManager()
        api_client = NetcupAPIClient(config_manager)
        dns_manager = DNSManager(api_client)
        
        zone_info = dns_manager.get_zone_info(domain)
        
        console.print(f"\n[bold]DNS Zone Information for {domain}[/bold]")
        console.print(f"Name: [cyan]{zone_info.name}[/cyan]")
        if zone_info.ttl:
            console.print(f"TTL: [cyan]{zone_info.ttl}[/cyan]")
        if zone_info.serial:
            console.print(f"Serial: [cyan]{zone_info.serial}[/cyan]")
        if zone_info.dnssecstatus is not None:
            status = "Enabled" if zone_info.dnssecstatus else "Disabled"
            console.print(f"DNSSEC: [cyan]{status}[/cyan]")
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@dns.group()
def records() -> None:
    """DNS records commands."""
    pass


@records.command()
@click.argument('domain')
def list(domain: str) -> None:
    """List all DNS records for a domain."""
    try:
        config_manager = ConfigManager()
        api_client = NetcupAPIClient(config_manager)
        dns_manager = DNSManager(api_client)
        
        records = dns_manager.get_records(domain)
        
        if not records:
            console.print(f"[yellow]No DNS records found for {domain}[/yellow]")
            return
        
        table = Table(title=f"DNS Records for {domain}")
        table.add_column("ID", style="dim")
        table.add_column("Hostname", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Destination", style="yellow")
        table.add_column("Priority", style="magenta")
        table.add_column("State", style="dim")
        
        for record in records:
            table.add_row(
                record.id or "N/A",
                record.hostname,
                record.type,
                record.destination,
                record.priority or "N/A",
                record.state or "N/A"
            )
        
        console.print(table)
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@dns.group()
def record() -> None:
    """Individual DNS record commands."""
    pass


@record.command()
@click.argument('domain')
@click.argument('hostname')
@click.argument('record_type')
@click.argument('destination')
@click.option('--priority', help='Priority for MX records')
def add(domain: str, hostname: str, record_type: str, destination: str, priority: Optional[str]) -> None:
    """Add a new DNS record."""
    try:
        config_manager = ConfigManager()
        api_client = NetcupAPIClient(config_manager)
        dns_manager = DNSManager(api_client)
        
        success = dns_manager.add_record(domain, hostname, record_type.upper(), destination, priority)
        
        if success:
            console.print(f"[green]✓[/green] Added {record_type.upper()} record for {hostname}.{domain}")
        else:
            console.print(f"[red]✗[/red] Failed to add DNS record")
            sys.exit(1)
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@record.command()
@click.argument('domain')
@click.argument('record_id')
def delete(domain: str, record_id: str) -> None:
    """Delete a DNS record."""
    try:
        config_manager = ConfigManager()
        api_client = NetcupAPIClient(config_manager)
        dns_manager = DNSManager(api_client)
        
        success = dns_manager.delete_record(domain, record_id)
        
        if success:
            console.print(f"[green]✓[/green] Deleted DNS record {record_id}")
        else:
            console.print(f"[red]✗[/red] Failed to delete DNS record")
            sys.exit(1)
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@record.command()
@click.argument('domain')
@click.argument('record_id')
@click.option('--hostname', help='New hostname')
@click.option('--destination', help='New destination')
@click.option('--priority', help='New priority')
def update(domain: str, record_id: str, hostname: Optional[str], destination: Optional[str], priority: Optional[str]) -> None:
    """Update a DNS record."""
    if not any([hostname, destination, priority]):
        console.print("[red]Error:[/red] At least one of --hostname, --destination, or --priority must be provided")
        sys.exit(1)
    
    try:
        config_manager = ConfigManager()
        api_client = NetcupAPIClient(config_manager)
        dns_manager = DNSManager(api_client)
        
        success = dns_manager.update_record(domain, record_id, hostname, destination, priority)
        
        if success:
            console.print(f"[green]✓[/green] Updated DNS record {record_id}")
        else:
            console.print(f"[red]✗[/red] Failed to update DNS record")
            sys.exit(1)
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


@cli.group()
def config() -> None:
    """Configuration commands."""
    pass


@config.command()
def show() -> None:
    """Show current configuration (without sensitive data)."""
    try:
        config_manager = ConfigManager()
        
        if not config_manager.has_credentials():
            console.print("[yellow]No configuration found.[/yellow]")
            console.print("Run 'netcup auth login' to set up your credentials.")
            return
        
        config_obj = config_manager.get_config()
        
        table = Table(title="Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Customer Number", config_obj.customer_number)
        table.add_row("API Key", f"{config_obj.api_key[:8]}..." if len(config_obj.api_key) > 8 else config_obj.api_key)
        table.add_row("API Password", "*" * 8)
        table.add_row("API Endpoint", config_obj.api_endpoint)
        table.add_row("Session Timeout", f"{config_obj.session_timeout}s")
        
        console.print(table)
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    cli() 