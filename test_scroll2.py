import ipywidgets as widgets
print('Widget methods:', [m for m in dir(widgets.Widget) if 'scroll' in m])
print('HTML methods:', [m for m in dir(widgets.HTML) if 'scroll' in m])
print('VBox methods:', [m for m in dir(widgets.VBox) if 'scroll' in m])
# check if scroll_to exists
w = widgets.HTML()
print('hasattr scroll_to?', hasattr(w, 'scroll_to'))
v = widgets.VBox([])
print('VBox hasattr scroll_to?', hasattr(v, 'scroll_to'))