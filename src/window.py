from gi.repository import Adw, Gtk, Gio, GLib
from pathlib import Path


@Gtk.Template(filename=str(Path("ui/window.ui").resolve()))
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    image_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        open_image_action = Gio.SimpleAction(name="open_image")
        open_image_action.connect("activate", self.open_file_dialog)
        self.add_action(open_image_action)

    def set_image(self, source, result, *args):
        try:
            file = self.file_dialog.open_finish(result)

            if file is not None:
                print(file.get_path())

        except GLib.Error:
            print("Operation was cancelled.")

    def open_file_dialog(self, *args):
        self.file_dialog = Gtk.FileDialog(
            title="Open Image",
            default_filter=Gtk.FileFilter(name="images", mime_types=["image/*"]),
            modal=True,
        )
        self.file_dialog.open(self, None, self.set_image)
