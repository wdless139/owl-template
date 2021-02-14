import unittest
from template import Template, exceptions


class TemplateTest(unittest.TestCase):
    def test_text(self):
        result = Template('Hello World!').render()
        self.assertEqual(result, 'Hello World!')

    def test_var(self):
        result = Template('Hello, {{ name }}').render({
            'name': 'John',
        })
        self.assertEqual(result, 'Hello, John')

    def test_nested_var(self):
        result = Template('Here\'s {{ values.name }}').render({
            'values': {
                'name': 'Johnny'
            }
        })
        self.assertEqual(result, 'Here\'s Johnny')

    def test_var_without_context(self):
        with self.assertRaises(exceptions.TemplateContextError):
            Template('Hello, {{ name }}').render()

    def test_if_true(self):
        result = Template('{% if name %}Hello, {{ name }}{% else %}Hello, people{% endif %}').render({
            'name': 'Chris',
        })
        self.assertEqual(result, 'Hello, Chris')

    def test_if_false(self):
        result = Template('{% if name %}Hello, {{ name }}{% else %}Hello, people{% endif %}').render({
            'name': '',
        })
        self.assertEqual(result, 'Hello, people')

    def test_unclosed_if(self):
        with self.assertRaises(exceptions.TemplateSyntaxError):
            Template('{% if name %}Hello, {{ name }}{% else %}Hello, people').render({
                'name': '',
            })

    def test_for(self):
        result = Template('{% for v in values %}{{ v }}: item\n{% endfor %}').render({
            'values': [1, 2, 3],
        })
        self.assertEqual(result, '1: item\n2: item\n3: item\n')

    def test_unclosed_for(self):
        with self.assertRaises(exceptions.TemplateSyntaxError):
            Template('{% for v in values %}{{ v }}: item\n').render({
                'values': [1, 2, 3],
            })


if __name__ == '__main__':
    unittest.main()