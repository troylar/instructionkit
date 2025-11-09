"""Template management commands."""

import typer

# Create template subcommand group
template_app = typer.Typer(
    name="template",
    help="Manage template repositories for consistent project standards",
    add_completion=False,
)


@template_app.callback(invoke_without_command=True)
def template_callback(ctx: typer.Context) -> None:
    """Manage template repositories."""
    # If no subcommand was provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)
