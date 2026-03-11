try:
    from api.index import app
    print('SUCCESS')
except Exception as e:
    import traceback
    traceback.print_exc()
