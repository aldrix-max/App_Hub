import flet as ft
from flet import *

def main(page: ft.Page):
    page.title = "Connexion Professionnelle"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#667eea"

    # Create the main container
    main_container = Container(
        width=400,
        bgcolor=Colors.WHITE,
        border_radius=border_radius.all(20),
        padding=padding.all(30),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.Colors.BLUE_GREY_300,
            offset=ft.Offset(0, 0),
        ),
    )

    # Create form elements
    email_field = TextField(
        label="Adresse Email",
        prefix_icon=Icons.EMAIL,
        hint_text="votre@email.com",
        border_radius=border_radius.all(10),
    )

    password_field = TextField(
        label="Mot de passe",
        prefix_icon=Icons.LOCK,
        hint_text="••••••••",
        password=True,
        can_reveal_password=True,
        border_radius=border_radius.all(10),
    )

    def login_click(e):
        # Show loading state
        login_button.text = "Connexion en cours..."
        login_button.disabled = True
        page.update()

        # Simulate API call
        import time
        time.sleep(1.5)

        # Check fields
        if email_field.value and password_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("Connexion réussie! Bienvenue."))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Veuillez remplir tous les champs."))
            page.snack_bar.open = True

        # Reset button
        login_button.text = "Se connecter"
        login_button.disabled = False
        page.update()

    login_button.on_click = login_click

    remember_me = ft.Checkbox(label="Se souvenir de moi")
    forgot_password = ft.TextButton(text="Mot de passe oublié?")

    login_button = ft.ElevatedButton(
        text="Se connecter",
        width=400,
        height=45,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
    )

    signup_text = ft.Text("Pas encore de compte? ")
    signup_link = ft.TextButton(text="S'inscrire")

    # Social buttons
    facebook_button = ft.IconButton(
        icon=Icons.FACEBOOK,
        icon_color=Colors.WHITE,
        bgcolor=Colors.BLUE_600,
        tooltip="Connect with Facebook",
    )

    google_button = ft.IconButton(
        icon=Icons.GMAIL,
        icon_color=Colors.WHITE,
        bgcolor=Colors.RED_600,
        tooltip="Connect with Google",
    )

    twitter_button = ft.IconButton(
        icon=Icons.TWITTER,
        icon_color=Colors.WHITE,
        bgcolor=Colors.BLUE_400,
        tooltip="Connect with Twitter",
    )

    # Assemble the form
    form_column = ft.Column(
        [
            ft.Row(
                [ft.Icon(Icons.LOCK, color=Colors.INDIGO_600, size=40)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Text("Connexion", size=24, weight="bold", text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Accédez à votre espace professionnel",
                size=14,
                color=Colors.GREY_600,
                text_align=ft.TextAlign.CENTER,
            ),
            email_field,
            password_field,
            ft.Row(
                [remember_me, forgot_password],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            login_button,
            ft.Row(
                [signup_text, signup_link],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
        spacing=20,
    )

    # Social buttons row
    social_row = ft.Row(
        [facebook_button, google_button, twitter_button],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
    )

    # Add everything to the main container
    main_container.content = ft.Column(
        [form_column, social_row],
        spacing=30,
    )

    page.add(main_container)

ft.app(target=main)