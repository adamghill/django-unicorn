# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adamghill/django-unicorn/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| conftest.py                                                          |       21 |        2 |        4 |        2 |     84% |    83, 93 |
| example/apps/\_\_init\_\_.py                                         |        0 |        0 |        0 |        0 |    100% |           |
| example/apps/main/\_\_init\_\_.py                                    |        0 |        0 |        0 |        0 |    100% |           |
| example/books/\_\_init\_\_.py                                        |        1 |        0 |        0 |        0 |    100% |           |
| example/books/apps.py                                                |        3 |        0 |        0 |        0 |    100% |           |
| example/books/models.py                                              |        9 |        0 |        0 |        0 |    100% |           |
| example/coffee/\_\_init\_\_.py                                       |        1 |        0 |        0 |        0 |    100% |           |
| example/coffee/apps.py                                               |        3 |        0 |        0 |        0 |    100% |           |
| example/coffee/models.py                                             |       26 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/cacher.py                                        |       92 |        3 |       34 |        1 |     97% | 50, 82-88 |
| src/django\_unicorn/call\_method\_parser.py                          |       80 |        1 |       24 |        2 |     97% |31->49, 47 |
| src/django\_unicorn/components/\_\_init\_\_.py                       |        5 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/components/fields.py                             |        3 |        1 |        0 |        0 |     67% |         7 |
| src/django\_unicorn/components/mixins.py                             |        7 |        1 |        2 |        1 |     78% |        15 |
| src/django\_unicorn/components/unicorn\_template\_response.py        |      136 |        5 |       48 |        4 |     95% |85, 175, 184, 205-206, 287->290 |
| src/django\_unicorn/components/unicorn\_view.py                      |      438 |       48 |      160 |       12 |     88% |103->106, 204, 244-245, 275-287, 323, 382->385, 394-397, 425-426, 442->457, 461->460, 502-503, 533, 562-571, 576, 636->639, 659-660, 712->707, 715-717, 825, 827, 864-865, 958-969 |
| src/django\_unicorn/components/updaters.py                           |       18 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/decorators.py                                    |       25 |        0 |       10 |        1 |     97% |    35->38 |
| src/django\_unicorn/errors.py                                        |       24 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/management/commands/startunicorn.py              |      102 |        8 |       36 |        7 |     89% |40-41, 80, 99, 102, 117, 129, 173->177, 187 |
| src/django\_unicorn/serializer.py                                    |      205 |        9 |      110 |        7 |     95% |31-32, 59->63, 84, 144->140, 184-186, 222, 251-255, 330->exit, 455->454 |
| src/django\_unicorn/settings.py                                      |       57 |        7 |       16 |        3 |     86% |25->28, 52-56, 59, 107-112 |
| src/django\_unicorn/templatetags/\_\_init\_\_.py                     |        0 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/templatetags/unicorn.py                          |      120 |        8 |       44 |        4 |     93% |23->26, 40, 47-48, 119, 126-129, 141->146, 170->173 |
| src/django\_unicorn/typer.py                                         |      168 |       33 |       88 |        9 |     78% |9-10, 21-24, 39-49, 126->135, 157-158, 183->190, 200-206, 221-222, 231, 276-283, 287->293, 289->293, 294, 313->312 |
| src/django\_unicorn/typing.py                                        |        5 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/urls.py                                          |        4 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/utils.py                                         |       67 |        8 |       18 |        3 |     87% |66-70, 137->136, 140-143 |
| src/django\_unicorn/views/\_\_init\_\_.py                            |      255 |       47 |      128 |       18 |     79% |103, 147, 150->117, 153, 158, 162, 172->178, 174->173, 180->178, 195, 208-209, 218-219, 242->245, 246, 256->226, 332-380, 431-432, 470, 486->494, 496-524 |
| src/django\_unicorn/views/action\_parsers/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| src/django\_unicorn/views/action\_parsers/call\_method.py            |      127 |       17 |       62 |       10 |     84% |5-6, 24-29, 39, 46-51, 83, 112, 160, 183->149, 210, 216->exit, 222->216, 226 |
| src/django\_unicorn/views/action\_parsers/sync\_input.py             |       13 |        0 |        4 |        0 |    100% |           |
| src/django\_unicorn/views/action\_parsers/utils.py                   |       74 |        9 |       50 |        9 |     85% |30, 32, 55, 79, 85->108, 112, 115, 133-134, 139 |
| src/django\_unicorn/views/objects.py                                 |       92 |       12 |       32 |        2 |     85% |25, 29-35, 57, 61, 82, 158-161 |
| src/django\_unicorn/views/utils.py                                   |       71 |        8 |       34 |        5 |     88% |20-21, 39-43, 55->exit, 71, 75-77, 123->128, 124->123 |
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
| tests/components/test\_get\_locations.py                             |       74 |        0 |        4 |        2 |     97% |15->19, 21->exit |
| tests/components/test\_is\_html\_well\_formed.py                     |       37 |        0 |        0 |        0 |    100% |           |
| tests/components/test\_unicorn\_template\_response.py                |       81 |        1 |        0 |        0 |     99% |        56 |
| tests/components/test\_unicorn\_template\_response\_recursion.py     |       30 |        0 |        0 |        0 |    100% |           |
| tests/management/\_\_init\_\_.py                                     |        0 |        0 |        0 |        0 |    100% |           |
| tests/management/commands/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| tests/management/commands/startunicorn/\_\_init\_\_.py               |        0 |        0 |        0 |        0 |    100% |           |
| tests/management/commands/startunicorn/test\_handle.py               |      130 |        0 |        0 |        0 |    100% |           |
| tests/serializer/test\_dumps.py                                      |      328 |        0 |        0 |        0 |    100% |           |
| tests/serializer/test\_exclude\_field\_attributes.py                 |       24 |        0 |        0 |        0 |    100% |           |
| tests/serializer/test\_model\_value.py                               |       32 |        0 |        0 |        0 |    100% |           |
| tests/templatetags/test\_unicorn.py                                  |       15 |        0 |        0 |        0 |    100% |           |
| tests/templatetags/test\_unicorn\_render.py                          |      287 |        0 |        8 |        4 |     99% |52->exit, 61->exit, 70->exit, 79->exit |
| tests/templatetags/test\_unicorn\_scripts.py                         |       30 |        0 |        0 |        0 |    100% |           |
| tests/test\_cacher.py                                                |      113 |        2 |       10 |        0 |     98% |  129, 132 |
| tests/test\_model\_lifecycle.py                                      |       64 |        0 |        0 |        0 |    100% |           |
| tests/test\_settings.py                                              |       49 |        0 |        4 |        2 |     96% |69->72, 90->exit |
| tests/test\_typer.py                                                 |      102 |        2 |        0 |        0 |     98% |    14, 23 |
| tests/test\_utils.py                                                 |       60 |        2 |        0 |        0 |     97% |    52, 63 |
| tests/urls.py                                                        |        8 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/\_\_init\_\_.py                          |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/call\_method/\_\_init\_\_.py             |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/call\_method/test\_call\_method\_name.py |      147 |        1 |        4 |        0 |     99% |        68 |
| tests/views/action\_parsers/utils/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/action\_parsers/utils/test\_set\_property\_value.py      |       86 |        0 |        0 |        0 |    100% |           |
| tests/views/fake\_components.py                                      |      126 |        5 |        4 |        2 |     95% |94, 121, 137, 174, 183 |
| tests/views/message/test\_call\_method.py                            |      175 |        0 |        2 |        0 |    100% |           |
| tests/views/message/test\_call\_method\_multiple.py                  |      170 |      136 |        6 |        0 |     19% |20-23, 32-41, 50-61, 66-90, 95-122, 127-154, 159-187, 197-231, 236-263, 268-295, 300-327, 333-360 |
| tests/views/message/test\_calls.py                                   |       23 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_get\_property\_value.py                    |       18 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_hash.py                                    |       98 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_message.py                                 |       73 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_set\_property.py                           |       39 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_sync\_input.py                             |       13 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_target.py                                  |       72 |        0 |        4 |        2 |     97% |50->exit, 51->50 |
| tests/views/message/test\_toggle.py                                  |       20 |        0 |        0 |        0 |    100% |           |
| tests/views/message/test\_type\_hints.py                             |       48 |        0 |        0 |        0 |    100% |           |
| tests/views/message/utils.py                                         |       18 |        1 |        8 |        1 |     92% |        21 |
| tests/views/test\_is\_component\_field\_model\_or\_unicorn\_field.py |       21 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_process\_component\_request.py                     |       24 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_dict.py                                   |       15 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_field.py                                  |       22 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_model.py                                  |       15 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_set\_property\_value.py                   |       38 |        0 |        0 |        0 |    100% |           |
| tests/views/test\_unicorn\_view\_init.py                             |       36 |        0 |        0 |        0 |    100% |           |
| tests/views/utils/\_\_init\_\_.py                                    |        0 |        0 |        0 |        0 |    100% |           |
| tests/views/utils/test\_construct\_model.py                          |       47 |       10 |        0 |        0 |     79% |     44-60 |
| tests/views/utils/test\_set\_property\_from\_data.py                 |      139 |        2 |        0 |        0 |     99% |     29-30 |
| **TOTAL**                                                            | **5646** |  **408** |  **958** |  **113** | **91%** |           |


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