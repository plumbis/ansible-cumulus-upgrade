Feature: Validate the webservers can be reached. 
This will validate each server has apache2 configured and running.
Then each server will try to reach every other server and fetch the index page

    Scenario: Validate Web Server Access
    Given a webserver is configured
    When apache is running
    Then the website should be accessable