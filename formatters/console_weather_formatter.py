import os
import platform
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from entities.dto.weather_dto import WeatherDTO

class ConsoleFormatter:
    def __init__(self, weather_data: WeatherDTO):
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

    def _format_optional_fields(self, value, metric: str="", placeholder="N/A"):
        if value is None:
            return placeholder
        return f"{value}{metric}"

    def print_weather_info(self, weather_data: WeatherDTO):
        self.clear_console()
        self.print_header()

        city_name = weather_data.city_name
        temp = weather_data.temp
        feels_like = weather_data.feels_like
        temp_min = weather_data.temp_min
        temp_max = weather_data.temp_max
        pressure = weather_data.pressure
        wind_speed = self._format_optional_fields(weather_data.wind_speed, " м/с")
        wind_dir = self._format_optional_fields(weather_data.wind_dir)
        visibility = self._format_optional_fields(weather_data.visibility_km, " км")
        clouds = self._format_optional_fields(weather_data.clouds, "%")
        humidity = weather_data.humidity
        sunrise = self._format_optional_fields(weather_data.sunrise)
        sunset = self._format_optional_fields(weather_data.sunset)
        description = weather_data.description

        # Панель для температуры
        temperature_panel = (
            f"🌡️  Температура:       {temp}°C\n"
            f"🌬️  Ощущается как:    {feels_like}°C\n"
            f"🌡️  Минимальная:      {temp_min}°C\n"
            f"🌡️  Максимальная:     {temp_max}°C"
        )

        # Панель для ветра
        wind_panel = (
            f"💨  Ветер:            {wind_speed}, {wind_dir}\n"
            f"🌫️  Видимость:        {visibility}\n"
            f"☁️  Облачность:       {clouds}"
        )

        # Панель для влажности и давления
        air_conditions_panel = (
            f"💧  Влажность:        {humidity}%\n"
            f"🧭  Давление:         {pressure} гПа"
        )

        # Панель для восхода и заката
        sunrise_sunset_panel = (
            f"🌅  Восход солнца:    {sunrise}\n"
            f"🌇  Закат солнца:     {sunset}"
        )

        # Панель для описания погоды
        description_panel = (
            f"Погодные условия:    {description} 🌞"
        )

        # Общий блок для всех панелей
        main_panel_content = (
            f"[bold]Температура:[/bold]\n{temperature_panel}\n\n"
            f"[bold]Ветер и видимость:[/bold]\n{wind_panel}\n\n"
            f"[bold]Воздух и давление:[/bold]\n{air_conditions_panel}\n\n"
            f"[bold]Восход и закат солнца:[/bold]\n{sunrise_sunset_panel}\n\n"
            f"[bold]Общие условия:[/bold]\n{description_panel}"
        )

        # Вывод главного блока
        self.console.print(Panel(main_panel_content, title=f"Погода для города {city_name}", title_align="center", padding=(1, 2)))

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