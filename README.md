# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adamghill/django-unicorn/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| conftest.py                                                          |       21 |        2 |        4 |        2 |     84% |    83, 93 |
| django\_unicorn/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/cacher.py                                            |       92 |        3 |       32 |        1 |     97% | 48, 80-86 |
| django\_unicorn/call\_method\_parser.py                              |       79 |        1 |       24 |        2 |     97% |30->48, 46 |
| django\_unicorn/components/\_\_init\_\_.py                           |        5 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/components/fields.py                                 |        3 |        1 |        0 |        0 |     67% |         7 |
| django\_unicorn/components/mixins.py                                 |        4 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/components/unicorn\_template\_response.py            |      134 |        5 |       46 |        5 |     94% |81, 172->176, 174, 183, 204-205, 279->282 |
| django\_unicorn/components/unicorn\_view.py                          |      436 |       48 |      160 |       12 |     88% |102->105, 203, 243-244, 274-286, 322, 381->384, 393-396, 424-425, 441->456, 460->459, 501-502, 532, 561-570, 575, 635->638, 658-659, 711->706, 714-716, 822, 824, 861-862, 955-966 |
| django\_unicorn/components/updaters.py                               |       19 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/decorators.py                                        |       25 |        0 |       10 |        1 |     97% |    35->38 |
| django\_unicorn/errors.py                                            |       24 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/management/commands/startunicorn.py                  |      103 |        8 |       36 |        7 |     89% |41-42, 81, 100, 103, 118, 130, 174->178, 188 |
| django\_unicorn/serializer.py                                        |      202 |        7 |      110 |        7 |     96% |31-32, 59->63, 84, 144->140, 218, 247-251, 326->exit, 451->450 |
| django\_unicorn/settings.py                                          |       57 |        7 |       16 |        3 |     86% |25->28, 52-56, 59, 107-112 |
| django\_unicorn/templatetags/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/templatetags/unicorn.py                              |      121 |        8 |       44 |        4 |     93% |25->28, 42, 49-50, 121, 128-131, 143->148, 172->175 |
| django\_unicorn/typer.py                                             |      145 |       23 |       66 |        5 |     84% |15-18, 33-43, 120->129, 151-152, 180-182, 194-200, 218, 264->269, 270, 289->288 |
| django\_unicorn/typing.py                                            |        6 |        1 |        0 |        0 |     83% |        18 |
| django\_unicorn/urls.py                                              |        4 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/utils.py                                             |       68 |        8 |       18 |        3 |     87% |67-71, 138->137, 141-144 |
| django\_unicorn/views/\_\_init\_\_.py                                |      252 |       50 |      126 |       19 |     78% |94, 98, 144, 147->114, 150, 155, 159, 169->175, 171->170, 177->175, 192, 205-206, 215-216, 239->242, 243, 253->223, 329-377, 428-429, 467, 475-477, 483->491, 493-521 |
| django\_unicorn/views/action\_parsers/\_\_init\_\_.py                |        0 |        0 |        0 |        0 |    100% |           |
| django\_unicorn/views/action\_parsers/call\_method.py                |      121 |       14 |       60 |        9 |     85% |19-24, 33, 40-45, 104, 149, 172->141, 199, 205->exit, 211->205, 215 |
| django\_unicorn/views/action\_parsers/sync\_input.py                 |       14 |        0 |        4 |        0 |    100% |           |
| django\_unicorn/views/action\_parsers/utils.py                       |       71 |        8 |       46 |        8 |     86% |30, 32, 76, 82->105, 109, 112, 130-131, 136 |
| django\_unicorn/views/objects.py                                     |       92 |       11 |       32 |        2 |     86% |25, 29-35, 57, 61, 158-161 |
| django\_unicorn/views/utils.py                                       |       61 |        5 |       28 |        2 |     92% |26-30, 42->exit, 62-64 |
| example/apps/\_\_init\_\_.py                                         |        0 |        0 |        0 |        0 |    100% |           |
| example/apps/main/\_\_init\_\_.py                                    |        0 |        0 |        0 |        0 |    100% |           |
| example/books/\_\_init\_\_.py                                        |        1 |        0 |        0 |        0 |    100% |           |
| example/books/apps.py                                                |        3 |        0 |        0 |        0 |    100% |           |
| example/books/models.py                                              |        9 |        0 |        0 |        0 |    100% |           |
| example/coffee/\_\_init\_\_.py                                       |        1 |        0 |        0 |        0 |    100% |           |
| example/coffee/apps.py                                               |        3 |        0 |        0 |        0 |    100% |           |
| example/coffee/models.py                                             |       26 |        0 |        0 |        0 |    100% |           |
| tests/\_\_init\_\_.py                                                |        0 |        0 |        0 |        0 |    100% |           |
| tests/benchmarks/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| tests/benchmarks/serializer/\_\_init\_\_.py                          |        0 |        0 |        0 |        0 |    100% |           |
| tests/benchmarks/serializer/test\_dumps.py                           |       53 |       19 |        0 |        0 |     64% |48-53, 57-79, 83-88, 92-118 |
| tests/call\_method\_parser/test\_parse\_args.py                      |       96 |        0 |        0 |        0 |    100% |           |
| tests/call\_method\_parser/test\_parse\_call\_method\_name.py        |       43 |        0 |        0 |        0 |    100% |           |
| tests/call\_method\_parser/test\_parse\_kwarg.py                     |       44 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_component.py                                  |      183 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_convert\_to\_dash\_case.py                    |        5 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_convert\_to\_pascal\_case.py                  |        5 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_convert\_to\_snake\_case.py                   |        5 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_create.py                                     |       13 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_get\_locations.py                             |       70 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_is\_html\_well\_formed.py                     |       37 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_unicorn\_template\_response.py                |       81 |        1 |        0 |        0 |     99% |        56 |
| tests/management/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| tests/management/commands/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| tests/management/commands/startunicorn/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| tests/management/commands/startunicorn/test\_handle.py               |      130 |        0 |        0 |        0 |    100% |           |
| tests/serializer/test\_dumps.py                                      |      329 |        0 |        0 |        0 |    100% |           |
| tests/serializer/test\_exclude\_field\_attributes.py                 |       24 |        0 |        0 |        0 |    100% |           |
| tests/serializer/test\_model\_value.py                               |       32 |        0 |        0 |        0 |    100% |           |
| tests/templatetags/test\_unicorn.py                                  |       15 |        0 |        0 |        0 |    100% |           |
| tests/templatetags/test\_unicorn\_render.py                          |      283 |        0 |        0 |        0 |    100% |           |
| tests/templatetags/test\_unicorn\_scripts.py                         |       30 |        0 |        0 |        0 |    100% |           |
| tests/test\_cacher.py                                                |      113 |        2 |       10 |        0 |     98% |  129, 132 |
| tests/test\_model\_lifecycle.py                                      |       64 |        0 |        0 |        0 |    100% |           |
| tests/test\_settings.py                                              |       46 |        0 |        0 |        0 |    100% |           |
| tests/test\_typer.py                                                 |      114 |        2 |        0 |        0 |     98% |    15, 24 |
| tests/test\_utils.py                                                 |       60 |        2 |        0 |        0 |     97% |    52, 63 |
| tests/urls.py                                                        |        8 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/\_\_init\_\_.py                          |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/call\_method/\_\_init\_\_.py             |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/call\_method/test\_call\_method\_name.py |      148 |        1 |        4 |        0 |     99% |        69 |
| tests/views/action\_parsers/utils/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/utils/test\_set\_property\_value.py      |       87 |        0 |        0 |        0 |    100% |           |
| tests/views/fake\_components.py                                      |      127 |        5 |        4 |        2 |     95% |95, 122, 138, 175, 184 |
| tests/views/message/test\_call\_method.py                            |      175 |        0 |        2 |        0 |    100% |           |
| tests/views/message/test\_call\_method\_multiple.py                  |      172 |      138 |        6 |        0 |     19% |20-23, 32-35, 39-50, 55-79, 84-111, 116-143, 148-176, 186-220, 225-252, 257-284, 289-316, 322-349 |
| tests/views/message/test\_calls.py                                   |       23 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_get\_property\_value.py                    |       18 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_hash.py                                    |       98 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_message.py                                 |       73 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_set\_property.py                           |       39 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_sync\_input.py                             |       13 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_target.py                                  |       72 |        0 |        4 |        2 |     97% |50->exit, 51->50 |
| tests/views/message/test\_toggle.py                                  |       20 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_type\_hints.py                             |       47 |        0 |        0 |        0 |    100% |           |
| tests/views/message/utils.py                                         |       18 |        1 |        8 |        1 |     92% |        21 |
| tests/views/test\_is\_component\_field\_model\_or\_unicorn\_field.py |       21 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_process\_component\_request.py                     |       24 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_dict.py                                   |       15 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_field.py                                  |       22 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_model.py                                  |       15 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_set\_property\_value.py                   |       40 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_view\_init.py                             |       36 |        0 |        0 |        0 |    100% |           |
| tests/views/utils/\_\_init\_\_.py                                    |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/utils/test\_construct\_model.py                          |       47 |       10 |        0 |        0 |     79% |     44-60 |
| tests/views/utils/test\_set\_property\_from\_data.py                 |      139 |        2 |        0 |        0 |     99% |     29-30 |
|                                                            **TOTAL** | **5574** |  **393** |  **900** |   **97** | **92%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/adamghill/django-unicorn/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/adamghill/django-unicorn/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/adamghill/django-unicorn/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/adamghill/django-unicorn/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fadamghill%2Fdjango-unicorn%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/adamghill/django-unicorn/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.