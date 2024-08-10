import os
import platform
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

from entities.weather import Weather

class ConsoleFormatter:
    def __init__(self, weather_data: Weather):
        self.console = Console()
        self.weather_data = weather_data

    def print_console_weather(self):
        self.clear_console()

        load_text = Text("Loading...! 🤔", justify="center")
        self.console.print(Panel(load_text, expand=True, padding=(1, 2)))

        self.print_weather_info(self.weather_data())

        self.print_main_menu()

        self.handle_menu_selection()

    def clear_console(self):
        """Очистка консоли в зависимости от операционной системы."""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    def print_header(self):
        welcome_text = Text("Welcome! 😊", justify="center")
        self.console.print(Panel(welcome_text, expand=True, padding=(1, 2)))

    def print_weather_info(self, weather_data: Weather):
        self.clear_console()
        self.print_header()

        city_name = weather_data.city
        temp = weather_data.temperature
        sunrise = weather_data.sunrise
        sunset = weather_data.sunset
        description = weather_data.weather_type

        temperature_panel = (
            f"🌡️  Temperature:       {temp}°C\n"
        )

        sunrise_sunset_panel = (
            f"🌅  Sunrise:    {sunrise}\n"
            f"🌇  Sunset:     {sunset}"
        )

        description_panel = (
            f"Weather conditions:    {description}"
        )

        main_panel_content = (
            f"[bold]Temperature:[/bold]\n{temperature_panel}\n\n"
            f"[bold]Sunrise and sunset:[/bold]\n{sunrise_sunset_panel}\n\n"
            f"[bold]General conditions:[/bold]\n{description_panel}"
        )

        self.console.print(Panel(main_panel_content, title=f"Weather for the city of {city_name}", title_align="center", padding=(1, 2)))

    def print_main_menu(self):
        menu_text = Text(
            "[1] Refresh data  [2] Exit",
            justify="center"
        )
        self.console.print(Panel(menu_text, expand=True, padding=(1, 2)))

    def handle_menu_selection(self):
        while True:
            choice = input("Select an option: ").strip()

            if choice == "1":
                self.console.print("\n[blue]Updating data...[/blue]\n")
                self.print_console_weather()
                pass
            elif choice == "2":
                self.console.print("\n[green]Exiting the program...[/green]\n")
                exit()
            else:
                self.console.print("\n[red]Invalid choice. Please select a valid option.[/red]\n")