1. link vs. button
    - link: navigates to a new page
    - button: performs an action on the current page
    - use button for actions that change the state of the application or perform an operation
    - use link for navigation to a different page or section of the application
1. ok, but what about updating the session state of a thoughtswap course/session thing
    * ideally the request wouldn't be a GET request, but rather POST or PUT or PATCH or DELETE
        * so need a form priobably revisit https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django/Forms 
1. add a datamigration to create a teacher group and only users in the teacher group will have the create course options?