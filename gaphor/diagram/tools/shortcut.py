from gaphas.view import GtkView
from gi.repository import Gdk, Gtk

from gaphor.core import Transaction
from gaphor.core.modeling import Presentation, self_and_owners
from gaphor.diagram.presentation import LinePresentation


def shortcut_tool(event_manager):
    ctrl = Gtk.EventControllerKey.new()
    ctrl.connect("key-pressed", key_pressed, event_manager)
    return ctrl


def key_pressed(ctrl, keyval, keycode, state, event_manager):
    """Handle the 'Delete' key.

    This can not be handled directly (through GTK's accelerators),
    otherwise this key will confuse the text edit stuff.
    """
    view: GtkView = ctrl.get_widget()
    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace):
        delete_selected_items(view, event_manager)
        return True
    if keyval == Gdk.KEY_Escape:
        unselect(view, event_manager)
    return False


def delete_selected_items(view: GtkView, event_manager):
    with Transaction(event_manager):
        items = view.selection.selected_items
        for i in list(items):
            assert isinstance(i, Presentation)
            if i.subject and i.subject in self_and_owners(i.diagram):
                del i.diagram.element
            i.unlink()


def unselect(view: GtkView, event_manager):
    items = view.selection.selected_items
    with Transaction(event_manager):
        for i in list(items):
            if isinstance(i, LinePresentation):
                if (
                    i._has_been_dropped
                    and i._lastHandleMoved
                    and not i._lastHandleMoved.glued
                    and i._connections.get_connection(i._lastHandleMoved)
                ):
                    i._connections.disconnect_item(i, i._lastHandleMoved)
                    i._lastHandleMoved = None
        view.selection.unselect_all()
        view.selection.grayed_out_items = set()
