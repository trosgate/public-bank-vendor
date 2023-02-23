from .models import WebsiteSetting


def website(request):
    if WebsiteSetting.objects.count():
        website = WebsiteSetting.objects.get_or_create(pk=1)[0]
        return {'website': website}
    return {'website': None}
