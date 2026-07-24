import ast, traceback
s=open('main.py',encoding='utf-8').read()
try:
    ast.parse(s)
    print('AST parse OK')
except Exception as e:
    traceback.print_exc()
    print('Error type:', type(e))
    try:
        print('lineno, offset:', e.lineno, e.offset)
    except Exception:
        pass
