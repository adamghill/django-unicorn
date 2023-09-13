# Architecture

`Unicorn` is made up of multiple pieces which are all integrated tightly together. The following is a summary of how some of it all fits together, although it skips over a lot of the complexity and advanced functionality. However, for all of the details the code is available at https://github.com/adamghill/django-unicorn/.

## Template tags

Starting with the integration with a normal Django template, there are the `unicorn_scripts` and `unicorn` template tags. `unicorn_scripts` renders out the entire JavaScript library and initializes the global `Unicorn` object. The `unicorn` template tag provides the ability to add the component wherever it is needed on the page. Based on the name passed into the `unicorn` template tag, conventions are used to find the correct component view and component template (e.g. if "hello-world" is passed into the template tag, a class of `hello_world.HelloWorldView` and a template named `hello-world.html` will be searched for).

Once the component view and template are found, a serialized version of all of the public attributes of the component view is generated into a JSON object for the page, and the template is rendered with a context of those same public attributes.

## JavaScript initialization

After the template is rendered, the JavaScript library parses the HTML for DOM elements that start with `unicorn:` or `u:` and creates a list of attributes that end with `:model`, `:poll`, or other specific `Unicorn` functionality. For attributes that are left, the assumption is that they are an event type (e.g. `unicorn:click`).

For anything that is a model, the JavaScript sets the value for the element based on the serialized data of the publicly available attributes from the component view. Event listeners are attached for all event types. Then, other custom functionality is setup (e.g. polling).

## Models

For all inputs which have a `model` attribute, an event listener is attached (either `change` or `blur` depending on if the `lazy` modifier is used). The `defer` modifier will store the action to be bundled with an action event that might happen later.

Once a model event is fired it is sent over the wire to the defined AJAX endpoint with a specific JSON structure which tells `Unicorn` what the updated data from the input should be. The component class is re-instantiated and the data is updated from the front-end, then re-rendered and the HTML is returned in the response.

## Actions

Actions follow a similar path as the models above, however there is a different JSON stucture. Also, the method, arguments, and kwargs that are passed from the front-end get parsed with a mix of `ast.parse` and `ast.literal_eval` to convert the strings into the appropriate Python types (i.e. change the string "1" to the integer `1`). After the component is re-initialized, the method is called with the passed-in arguments and kwargs. Once all of the actions have been called, the component view is re-rendered and the HTML is returned in the response.

## HTML Diff

After the AJAX endpoint returns its response, the newly rendered DOM is merged into the old DOM and input values are set again based on the new data in the AJAX response. By default, a library called `morphdom` is used to do the diffing and merging of the DOM. However, this can be overridden by setting the `MORPHER` setting to use a different library.
