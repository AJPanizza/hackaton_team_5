# Static code checks

Perform checks on python files using ruff and mypy.

## Steps

1. Ask the user:
   - Which projects should be reviewed? (provide paths or describe the scope)

2. uv sync

3. Run ruff check on that folder
   `ruff check {folder}`

4. Run mypy check on that folder
   `mypy {folder}`

5. Solve issues if there are any. Repeat steps 3 and 4.
