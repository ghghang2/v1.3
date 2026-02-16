import ipywidgets as widgets
print('Output methods:', [m for m in dir(widgets.Output) if 'scroll' in m])
o = widgets.Output()
print('hasattr scroll_to?', hasattr(o, 'scroll_to'))