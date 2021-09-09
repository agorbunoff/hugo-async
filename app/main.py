from hugo.main import Hugo

hugo = Hugo()


@hugo.handler("/")
async def home(request):
    return "<html>hello</html>"
