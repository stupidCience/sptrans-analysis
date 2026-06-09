from src.controllers.main_controller import MainController
from src.views.dashboard_view import DashboardView

if __name__ == "__main__":
    controller = MainController()
    view = DashboardView(controller)
    view.render()