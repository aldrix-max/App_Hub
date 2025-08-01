import flet as ft
from pages.login import login_view
from pages.admin_dashboard import admindashboard
from pages.agent_dashboard import agentdashboard
from pages.vision_dashboard import visiondashboard


def main(page: ft.Page):
    
    page.window_title = "Financial Flow"  # Titre de la fenêtre
    page.window_window_icon = "assets/logo.png"  # Chemin vers votre icône
    
    def route_change(e):
        page.views.clear()
        if page.route == "/admin-dashboard":
            page.views.append(admindashboard(page))
        elif page.route == "/agent-dashboard":
            page.views.append(agentdashboard(page))
        elif page.route == "/vision_dashboard":
            page.views.append(visiondashboard(page))
        
        else:
            page.views.append(login_view(page))
        page.update()


    page.on_route_change = route_change
    page.go(page.route)

ft.app(target=main, assets_dir="assets", port=8080, view=ft.WEB_BROWSER)
