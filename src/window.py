from gi.repository import Gtk


@Gtk.Template(resource_path="./window.ui")
class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = "Window"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(200, 200)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
