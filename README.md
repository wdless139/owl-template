# owl-template

### Причем здесь совы?

¯\\_(ツ)_/¯

### Простой пример

```html
from template import Template

result = Template('Hello, {{ name }}').render({
            'name': 'John'
        })
```

### Переменные

```html
<p>{{ var }}</p>
```

### Циклы

```html
{% for i in items %}
    <div>{{ i }}</div>
{% endfor %}
```

### Условия

На данный момент блок if не поддерживает операторы сравнения

```html
{% if var %}
    <div>{{ var }}</div>
{% else %}
    <div>var is false</div>
{% endif %}
```
