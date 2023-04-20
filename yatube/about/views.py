from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = "about/author.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Страница об авторе проекта."
        context["text"] = "Пока это пробный текст"
        return context


class AboutTechView(TemplateView):
    template_name = "about/tech.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Страница о примененных технологиях."
        return context
