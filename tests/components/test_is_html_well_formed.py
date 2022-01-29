from django_unicorn.components.unicorn_template_response import is_html_well_formed


def test_is_html_well_formed():
    html = """
<div>
    something
</div>
    """
    actual = is_html_well_formed(html)

    assert actual is True


def test_is_html_well_formed_comment():
    html = """

<!-- some comment here -->

<div>
    something
</div>
    """
    actual = is_html_well_formed(html)

    assert actual is True


def test_is_html_well_formed_p():
    html = """

<p>
    something
    <br />
</p>
    """
    actual = is_html_well_formed(html)

    assert actual is True


def test_is_html_well_formed_missing_internal():
    html = """
<p>
<div>
    something
    <br />
</p>
    """
    actual = is_html_well_formed(html)

    assert actual is False


def test_is_html_well_formed_multiple():
    html = """
<div>
    <div>something</div>
</div>
    """
    actual = is_html_well_formed(html)

    assert actual is True


def test_is_html_well_formed_missing():
    html = """
<div>
    something

    """
    actual = is_html_well_formed(html)

    assert actual is False


def test_is_html_well_formed_invalid():
    html = """
<div>
    something
</di>

    """
    actual = is_html_well_formed(html)

    assert actual is False


def test_is_html_well_formed_no_slash():
    html = """
<div>
    something
<div>

    """
    actual = is_html_well_formed(html)

    assert actual is False


def test_is_well_formed_more():
    html = """
<div>
  <button unicorn:click="$reset">Reset the component</button>
  <button onclick="document.getElementById('name').value = 'asdf';">Plain JS set value on key1</button>
  <button onclick="Unicorn.trigger('unicorn.components.hello_world.HelloWorldView', 'key1')">Trigger key1</button>
  <br />
  <br />

  <label></label>
  <input unicorn:model="name" type="text" id="name" unicorn:key="key1">

  Hello, {{ name|default:'World' }}!

  <div>
    Request path context variable: '{{ request.path }}'
  </div>
</div>
    """

    actual = is_html_well_formed(html)

    assert actual is True
