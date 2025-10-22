"""Textual TUI for installing instructions from library."""

from typing import Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Select, Static

from instructionkit.core.models import InstallationScope, LibraryInstruction
from instructionkit.storage.library import LibraryManager


class InstructionInstallerScreen(Screen):
    """Main screen for selecting and installing instructions."""

    CSS = """
    Screen {
        background: $background;
    }

    #search-container {
        height: 3;
        padding: 0 1;
    }

    #filter-container {
        height: 3;
        padding: 0 1;
    }

    #instructions-table {
        height: 1fr;
    }

    #status-bar {
        height: 3;
        padding: 1;
        background: $panel;
    }

    #actions-container {
        height: 3;
        padding: 0 1;
    }

    Button {
        margin: 0 1;
    }

    .selected-row {
        background: $accent;
    }
    """

    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("ctrl+a", "select_all", "Select All"),
        ("ctrl+d", "deselect_all", "Deselect All"),
        ("ctrl+l", "clear_search", "Clear Search"),
        ("/", "focus_search", "Search"),
    ]

    def __init__(
        self,
        library: LibraryManager,
        scope: InstallationScope = InstallationScope.GLOBAL,
        tool: Optional[str] = None,
    ):
        """
        Initialize installer screen.

        Args:
            library: Library manager instance
            scope: Installation scope (global or project)
            tool: AI tool to install to (None = all)
        """
        super().__init__()
        self.library = library
        self.scope = scope
        self.tool = tool
        self.instructions = library.list_instructions()
        self.filtered_instructions = self.instructions.copy()
        self.selected_ids: set[str] = set()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        # Search container
        with Container(id="search-container"):
            yield Input(
                placeholder="Search instructions...",
                id="search-input"
            )

        # Filter container
        with Horizontal(id="filter-container"):
            # Repository filter
            repo_options = [("All Repositories", "")]
            repos = {inst.repo_namespace: inst.repo_name for inst in self.instructions}
            repo_options.extend([(name, namespace) for namespace, name in repos.items()])

            yield Label("Repo:")
            yield Select(
                options=repo_options,
                value="",
                id="repo-filter",
            )

            # Tool filter (if not already specified)
            if not self.tool:
                tool_options = [
                    ("All Tools", ""),
                    ("Cursor", "cursor"),
                    ("GitHub Copilot", "copilot"),
                    ("Windsurf", "windsurf"),
                    ("Claude Code", "claude"),
                ]
                yield Label("Tool:")
                yield Select(
                    options=tool_options,
                    value="",
                    id="tool-filter",
                )

            # Scope selector
            scope_options = [
                ("Global", "global"),
                ("Project", "project"),
            ]
            yield Label("Scope:")
            yield Select(
                options=scope_options,
                value=self.scope.value,
                id="scope-select",
            )

        # Instructions table
        yield DataTable(id="instructions-table")

        # Status bar
        with Container(id="status-bar"):
            yield Static("", id="status-text")

        # Action buttons
        with Horizontal(id="actions-container"):
            yield Button("Cancel", variant="default", id="cancel-btn")
            yield Button("Select All", variant="primary", id="select-all-btn")
            yield Button("Deselect All", variant="default", id="deselect-all-btn")
            yield Button("Install", variant="success", id="install-btn")

        yield Footer()

    def on_mount(self) -> None:
        """Set up the table when mounted."""
        table = self.query_one("#instructions-table", DataTable)

        # Add columns
        table.add_column("☑", key="selected", width=3)
        table.add_column("Name", key="name", width=25)
        table.add_column("Description", key="description", width=40)
        table.add_column("Repository", key="repo", width=20)
        table.add_column("Author", key="author", width=15)
        table.add_column("Ver", key="version", width=8)
        table.add_column("Tags", key="tags", width=20)

        # Populate table
        self.refresh_table()
        self.update_status()

    def refresh_table(self) -> None:
        """Refresh the table with filtered instructions."""
        table = self.query_one("#instructions-table", DataTable)
        table.clear()

        for inst in self.filtered_instructions:
            is_selected = inst.id in self.selected_ids
            checkbox = "[✓]" if is_selected else "[ ]"

            # Truncate long text
            name = inst.name[:23] + "..." if len(inst.name) > 23 else inst.name
            desc = inst.description[:38] + "..." if len(inst.description) > 38 else inst.description
            repo = inst.repo_name[:18] + "..." if len(inst.repo_name) > 18 else inst.repo_name
            author = inst.author[:13] + "..." if len(inst.author) > 13 else inst.author
            tags = ", ".join(inst.tags[:2]) if inst.tags else "-"
            if len(inst.tags) > 2:
                tags += f" +{len(inst.tags) - 2}"

            table.add_row(
                checkbox,
                name,
                desc,
                repo,
                author,
                inst.version,
                tags,
                key=inst.id,
            )

    def update_status(self) -> None:
        """Update the status bar."""
        status = self.query_one("#status-text", Static)
        total = len(self.filtered_instructions)
        selected = len(self.selected_ids)

        scope_text = self.scope.value.capitalize()
        tool_text = self.tool.capitalize() if self.tool else "All tools"

        status.update(
            f"Selected: {selected} | Showing: {total} instructions | "
            f"Scope: {scope_text} | Tool: {tool_text}"
        )

    def filter_instructions(
        self,
        search: str = "",
        repo_namespace: str = "",
    ) -> None:
        """
        Filter instructions based on criteria.

        Args:
            search: Search query
            repo_namespace: Repository namespace filter
        """
        self.filtered_instructions = self.instructions.copy()

        # Apply search filter
        if search:
            query = search.lower()
            self.filtered_instructions = [
                inst for inst in self.filtered_instructions
                if query in inst.name.lower() or query in inst.description.lower()
            ]

        # Apply repo filter
        if repo_namespace:
            self.filtered_instructions = [
                inst for inst in self.filtered_instructions
                if inst.repo_namespace == repo_namespace
            ]

        self.refresh_table()
        self.update_status()

    @on(Input.Changed, "#search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        repo_filter = self.query_one("#repo-filter", Select).value
        self.filter_instructions(search=event.value, repo_namespace=repo_filter)

    @on(Select.Changed, "#repo-filter")
    def on_repo_filter_changed(self, event: Select.Changed) -> None:
        """Handle repository filter changes."""
        search = self.query_one("#search-input", Input).value
        self.filter_instructions(search=search, repo_namespace=str(event.value))

    @on(Select.Changed, "#scope-select")
    def on_scope_changed(self, event: Select.Changed) -> None:
        """Handle scope selection changes."""
        self.scope = InstallationScope(event.value)
        self.update_status()

    @on(Select.Changed, "#tool-filter")
    def on_tool_changed(self, event: Select.Changed) -> None:
        """Handle tool filter changes."""
        self.tool = str(event.value) if event.value else None
        self.update_status()

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Toggle selection when row is clicked."""
        if event.row_key:
            instruction_id = str(event.row_key.value)

            if instruction_id in self.selected_ids:
                self.selected_ids.remove(instruction_id)
            else:
                self.selected_ids.add(instruction_id)

            self.refresh_table()
            self.update_status()

    @on(Button.Pressed, "#select-all-btn")
    def action_select_all(self) -> None:
        """Select all filtered instructions."""
        self.selected_ids.update(inst.id for inst in self.filtered_instructions)
        self.refresh_table()
        self.update_status()

    @on(Button.Pressed, "#deselect-all-btn")
    def action_deselect_all(self) -> None:
        """Deselect all instructions."""
        self.selected_ids.clear()
        self.refresh_table()
        self.update_status()

    def action_clear_search(self) -> None:
        """Clear search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        search_input.focus()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    @on(Button.Pressed, "#cancel-btn")
    def action_quit(self) -> None:
        """Cancel and exit."""
        self.dismiss(None)

    @on(Button.Pressed, "#install-btn")
    def on_install_pressed(self) -> None:
        """Handle install button press."""
        if not self.selected_ids:
            # TODO: Show error message
            return

        # Get selected instructions
        selected_instructions = [
            inst for inst in self.instructions
            if inst.id in self.selected_ids
        ]

        # Return result
        self.dismiss({
            "instructions": selected_instructions,
            "scope": self.scope,
            "tool": self.tool,
        })


class InstructionInstallerApp(App):
    """Application for installing instructions."""

    def __init__(
        self,
        library: LibraryManager,
        scope: InstallationScope = InstallationScope.GLOBAL,
        tool: Optional[str] = None,
    ):
        """
        Initialize installer app.

        Args:
            library: Library manager instance
            scope: Default installation scope
            tool: AI tool to install to (None = all)
        """
        super().__init__()
        self.library = library
        self.scope = scope
        self.tool = tool
        self.result = None

    def on_mount(self) -> None:
        """Push the installer screen when app mounts."""
        screen = InstructionInstallerScreen(
            library=self.library,
            scope=self.scope,
            tool=self.tool,
        )
        self.push_screen(screen, self.handle_result)

    def handle_result(self, result: Optional[dict]) -> None:
        """Handle result from installer screen."""
        self.result = result
        self.exit()


def show_installer_tui(
    library: LibraryManager,
    scope: InstallationScope = InstallationScope.GLOBAL,
    tool: Optional[str] = None,
) -> Optional[dict]:
    """
    Show the instruction installer TUI.

    Args:
        library: Library manager instance
        scope: Default installation scope
        tool: AI tool to install to (None = all)

    Returns:
        Dictionary with selected instructions and settings, or None if cancelled
    """
    app = InstructionInstallerApp(library=library, scope=scope, tool=tool)
    app.run()
    return app.result
