import flet as ft
from flet import *

def stat_card(title, value, color="blue", icon=Icons.INSIGHTS):
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=30, color="white"),
                    ft.Text(title, size=16, color="white", weight="bold", expand=True, text_align="end")
                ]),
                ft.Text(str(value), size=24, weight="bold", color="white")
            ], spacing=10),
            padding=20,
            bgcolor=color,
            border_radius=10,
            width=200,
            height=100
        )
    )
