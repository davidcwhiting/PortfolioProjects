import dash
from dash import html
import dash_bootstrap_components as dbc  # pip install dash-bootstrap-components
import dash_auth


VALID_USERNAME_PASSWORD_PAIRS = {"NaplesWard": "ISCOOL"}

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True
)

auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)


navbar = dbc.NavbarSimple(
    dbc.DropdownMenu(
        [
            dbc.DropdownMenuItem(page["name"], href=page["path"])
            for page in dash.page_registry.values()
            if page["module"] != "pages.not_found_404"
        ],
        nav=True,
        label="Explore Pages",
    ),
    color="secondary",
    dark=True,
    className="mb-2",
)

app.layout = dbc.Container(
    [navbar, dash.page_container],
    fluid=True,
)

app.server.secret_key = "BYU2025!"
if __name__ == "__main__":
    app.run( debug=True)