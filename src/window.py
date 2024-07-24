import time
from gi.repository import Adw, Gtk, Gio, GLib, Gdk
from pathlib import Path
from logic import RemoveBackground


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
    destroy_button = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()

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

        self.image_bin_click_controller = Gtk.GestureClick()
        self.file_dialog_event_handler = self.image_bin_click_controller.connect(
            "released", self.open_file_dialog
        )
        self.image_bin.add_controller(self.image_bin_click_controller)

        self.destroy_button_click_controller = Gtk.GestureClick()
        self.destroy_button.add_controller(self.destroy_button_click_controller)

        self.image_bin_drop_controller = Gtk.DropTarget(actions=Gdk.DragAction.COPY)
        self.image_bin_drop_controller.set_gtypes([Gio.File])
        self.image_bin_drop_controller.connect("drop", self.on_drop)
        self.image_bin.add_controller(self.image_bin_drop_controller)

    def get_overlay(self):
        image = Gtk.Picture.new_for_file(self.file)
        close_icon = Gtk.Image()
        close_icon.set_from_icon_name("window-close-symbolic")
        self.close_button = Gtk.Button()
        self.close_button.set_child(close_icon)
        self.close_button.set_css_classes(["osd", "circular"])
        margin_setter(self.close_button, 8)
        self.close_button.set_halign(Gtk.Align.END)
        self.close_button.set_valign(Gtk.Align.START)
        self.close_button.connect("clicked", self.set_image_bin_empty)
        overlay = Gtk.Overlay()
        overlay.set_child(image)
        overlay.add_overlay(self.close_button)
        return overlay

    def set_image_bin_empty(self, *args):
        self.image_bin.add_css_class("activatable")
        self.image_bin.set_child(self.label)
        self.file_dialog_event_handler = self.image_bin_click_controller.connect(
            "released", self.open_file_dialog
        )
        self.remove_background = None
        self.destroy_button.set_sensitive(False)

    def set_image_bin_propagated(self, *args):
        self.image_bin_click_controller.disconnect(self.file_dialog_event_handler)
        self.image_bin.remove_css_class("activatable")
        overlay = self.get_overlay()
        self.image_bin.set_child(overlay)
        self.remove_background = RemoveBackground(self.file.get_path())
        self.destroy_button.set_sensitive(True)
        self.destroy_button_click_controller.connect(
            "pressed", self.remove_background.remove_background
        )
        self.destroy_button.connect("clicked", self.open_save_file_dialog)

    def close_save_file_dialog(self, source, result, *args):
        try:
            self.save_location = self.save_dialog.save_finish(result)
            self.remove_background.save_image(self.save_location.get_path())
            self.toast_overlay.add_toast(Adw.Toast(title="Image saved successfully!"))
            self.set_image_bin_empty()
        except GLib.Error:
            print("Operation was cancelled.")

    def open_save_file_dialog(self, *args):
        if self.file is not None:
            self.save_dialog = Gtk.FileDialog(
                title="Save Image",
                initial_file=self.file,
                modal=True,
            )
            self.destroy_button.set_sensitive(False)
            self.close_button.set_sensitive(False)
            self.save_dialog.save(self, None, self.close_save_file_dialog)
        else:
            raise ValueError("No image given. WHICH SHOULD NOT HAPPENED!")

    def close_file_dialog(self, source, result, *args):
        try:
            self.file = self.file_dialog.open_finish(result)

            if self.file is not None:
                print(self.file.get_path())
                self.set_image_bin_propagated()

        except GLib.Error:
            print("Operation was cancelled.")

    def open_file_dialog(self, *args):
        self.file_dialog = Gtk.FileDialog(
            title="Open Image",
            default_filter=Gtk.FileFilter(name="images", mime_types=["image/*"]),
            modal=True,
        )
        self.file_dialog.open(self, None, self.close_file_dialog)

    def on_drop(self, _ctrl, value, _x, _y):
        self.file = value

        if value is not None:
            print(value.get_path())
            self.set_image_bin_propagated()
