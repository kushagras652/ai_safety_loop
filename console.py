import re


try:
    from rich import print as _rich_print



    def rprint(*args,**kwargs):
        _rich_print(*args,**kwargs)

except Exception:
    _TAG= re.complie(r"\[/?[a-zA-Z0-9_ #]+\]")

    def rprint(*args,**kwargs):
        cleaned=tuple(
            _TAG.sub("",a) if isinstance(a,str) else a for a in args
        )
        print(*cleaned,**kwargs)