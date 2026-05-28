"""Email templates"""

from pathlib import Path

from fastapi.templating import Jinja2Templates

email_templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
