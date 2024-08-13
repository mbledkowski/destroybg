from transformers import pipeline
import sys
from git import Repo
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gio, Gtk, Adw
from .window import MainWindow


class MainApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(
            application_id="dk.mble.destroybg", flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        self.create_action("quit", lambda *_: self.quit(), ["<primary>q"])
        self.create_action("about", self.on_about_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = MainWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Destroy Background",
            application_icon="org.gnome.Example",
            developer_name="Maciej Błędkowski",
            version=Repo().head.commit.hexsha[:7],  # TODO
            designers=["Maciej Błędkowski"],
            developers=["Maciej Błędkowski"],
            website=Repo().remotes.origin.url.replace(".git", ""),  # Git remote
            issue_url="",  # Git remote
            # license_type="",  # Read from LICENSE file
            license_type=Gtk.License.AGPL_3_0,
            copyright="🄯 2024 Maciej Błędkowski",
        )
        about.present()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main():
    """The application's entry point."""
    app = MainApplication()
    return app.run(sys.argv)
