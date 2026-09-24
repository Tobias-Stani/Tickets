from typing import Annotated

from pydantic import BaseModel, StringConstraints

TagName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
HexColor = Annotated[str, StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$")]


class TagInput(BaseModel):
    name: TagName
    color: HexColor = "#6366f1"
