from gi.repository import Adw, Gtk, Gio, GLib, Gdk
from pathlib import Path


def margin_setter(widget: Gtk.Widget, value):
    widget.set_margin_top(value)
    widget.set_margin_bottom(value)
    widget.set_margin_start(value)
    widget.set_margin_end(value)
    return widget


@Gtk.Template(filename=str(Path("src/ui/window.ui").resolve()))
class MainWindow(Adw.ApplicationWindow):
    __gtype_name__ = "MainWindow"

    image_bin = Gtk.Template.Child()

    css_provider = Gtk.CssProvider()
    css_provider.load_from_file(
        Gio.File.new_for_path(str(Path("data/resources/style.css").resolve()))
    )

    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.label = self.image_bin.get_child()

        self.click_controller = Gtk.GestureClick()
        self.file_dialog_event_handler = self.click_controller.connect(
            "released", self.on_open_file_dialog
        )
        self.image_bin.add_controller(self.click_controller)

    def get_overlay(self, file):
        image = Gtk.Picture.new_for_file(file)
        close_icon = Gtk.Image()
        close_icon.set_from_icon_name("window-close-symbolic")
        close_button = Gtk.Button()
        close_button.set_child(close_icon)
        close_button.set_css_classes(["osd", "circular"])
        margin_setter(close_button, 8)
        close_button.set_halign(Gtk.Align.END)
        close_button.set_valign(Gtk.Align.START)
        close_button.connect("clicked", self.set_image_bin_empty)
        overlay = Gtk.Overlay()
        overlay.set_child(image)
        overlay.add_overlay(close_button)
        return overlay

    def set_image_bin_empty(self, *args):
        self.image_bin.add_css_class("activatable")
        self.image_bin.set_child(self.label)
        self.file_dialog_event_handler = self.click_controller.connect(
            "released", self.on_open_file_dialog
        )

    def set_image_bin_propagated(self, file, *args):
        self.click_controller.disconnect(self.file_dialog_event_handler)
        self.image_bin.remove_css_class("activatable")
        overlay = self.get_overlay(file)
        self.image_bin.set_child(overlay)

    def on_close_file_dialog(self, source, result, *args):
        try:
            file = self.file_dialog.open_finish(result)

            if file is not None:
                print(file.get_path())
                self.file = file.get_path()
                self.set_image_bin_propagated(file)

        except GLib.Error:
            print("Operation was cancelled.")

    def on_open_file_dialog(self, *args):
        self.file_dialog = Gtk.FileDialog(
            title="Open Image",
            default_filter=Gtk.FileFilter(name="images", mime_types=["image/*"]),
            modal=True,
        )
        self.file_dialog.open(self, None, self.on_close_file_dialog)
