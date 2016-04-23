Feature: Validate BGP

    Scenario: Check BGP Neighbors
    Given BGP is enabled
    when neighbors are configured
    then the neighbors should be up