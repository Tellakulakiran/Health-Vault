import sys
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    with open('crash.log', 'w', encoding='utf-8') as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

sys.excepthook = handle_exception

import api.index
print('SUCCESS')
