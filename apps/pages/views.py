from django.shortcuts import render


def privacy_policy(request):
    return render(request, "pages/privacy.html", {"meta_title": "Política de Privacidade — Sandra Ellen Modas"})


def cookie_policy(request):
    return render(request, "pages/cookies.html", {"meta_title": "Política de Cookies — Sandra Ellen Modas"})


def terms_of_use(request):
    return render(request, "pages/terms.html", {"meta_title": "Termos de Uso — Sandra Ellen Modas"})


def robots_txt(request):
    from django.http import HttpResponse
    from django.conf import settings

    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: https://{settings.SITE_DOMAIN}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
