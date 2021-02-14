owl-template
============

owl-template is a simple python template engine implementation

## why owl

¯\_(ツ)_/¯

## Documentation

### Variables

```html
<p>{{ var }}</p>
```

### For

```html
{% for i in items %}
    <div>{{ i }}</div>
{% endfor %}
```

### If

if block doesn't support any operators

```html
{% if var %}
    <div>{{ var }}</div>
{% else %}
    <div>var is false</div>
{% endif %}
```
