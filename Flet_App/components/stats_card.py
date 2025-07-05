import flet as ft
from flet import *

def stat_card(title, value, color="blue", icon=Icons.INSIGHTS):
    return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=30, color=Colors.INDIGO),
                    ft.Text(title, size=16,color=Colors.GREY,  expand=True, text_align="start")
                ]),
                ft.Text(str(value), size=24, weight="bold", color="black")
            ], spacing=10),
            padding=20,
            bgcolor="white",
            border_radius=10,
            width=400,
            height=100,
            shadow=BoxShadow(blur_radius=10, color=Colors.GREY_300)
        )
    
