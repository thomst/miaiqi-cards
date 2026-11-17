from django.template import Context, Engine
from django.test import SimpleTestCase


class MenuTagTests(SimpleTestCase):
    def test_menu_renders_with_current_context(self):
        engine = Engine(
            libraries={'menu': 'miaiqi_cards.welcome.templatetags.menu'},
            loaders=[
                ('django.template.loaders.locmem.Loader', {
                    'menu.html': '{{ page }}|{{ nested }}',
                }),
            ],
        )
        template = engine.from_string('{% load menu %}{% menu %}')
        context = Context({'page': 'outer'})
        with context.push(page='inner', nested='value'):
            self.assertEqual(template.render(context), 'inner|value')
