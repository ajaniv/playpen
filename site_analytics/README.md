The driver for this effort was to explore how to use Django rest framework for solving real time page analytics
implementation issues.  The context is a real time site page analytics application, where clients (embedded javascript) 
report page visits, and reporting tools provide real time analytics on most visited, pages whose visitation statistics
changed most significantly from the last snapshot, etc.
Other implementation alternatives for REST API within the space of Django included TastyPie and Django views.
Implementation aspects focused include:
* Integration of urls
* Listing of end points
* Serialization/de-serialization
* Control on the request/response pay load
* Error handling
*  Unit testing


## Key Messages
* Scale horizontally and vertically with page visit POST event  nodes (Apache, Django)
* Page visit event  stored in distributed cache which may not require persistent store (i.e. memcached,  redis).  Data is validated balancing speed vs data quality requirements
*Multiple nodes host collector processes which are triggered by timed messages (i.e. celery)  collect the data,  perform second level validation, generate exception reports, store the  statistics in persistent backed distributed cache
* Agent requests for top pages, page hit delta  fetch  the  data from the distributed cache 
* Ability to handle raw page visit data processing  in real time is questionable, requiring a level of event data  consolidation.   

## Discussion points
* The PageVisit event data may be discarded  unless there are requirements for historical data analysis at the granularity of the event
* Page statistics capture frequency needs to be balanced with data analysis requirements.  Are there any requirements to view the data at 1 second intervals?  60 seconds?  Feels more likely that a number of 5 seconds which create a technical scalability challenge
* Page view activity change requests should allow a from, to period  parameters, and not only be limited to the last two snapshots
* Authentication token used within get params and not within HTTP header.

## Physical Architecture
Note: missing load balancers, processes running on each node,  process interaction, database replication,  WAN replication for  global data distribution
See diagram in docs/PhysicalArchitecture.jpg.

## Simplified  Analytics Data Work Flow
See diagram in docs/DataWorkflow.jpg
* N number of agents produce concurrent PageVisit event data
* N number of collector process instances:
    -Create new Page object instances for newly used pages
    -Update Page  visit totals per domain and page
    -Generate  PageStatistics  instances  snapshots  with per domain and page change data
    
## High Level Business Object Model
See diagram in docs/BusinessObjectModel.jpg
* All business classes inherit from  the abstract base class AppBaseModel which captures creation time, creation user, and objet id
* Domain: Top level abstraction for organizing pages
* Page: captures total page hits for a page associated with a domain, subject, path
* PageVisit: raw event data captured from  agent including ip address,  path, user agent, domain,  subject, apikey.  Has no foreign keys for simple validation and rapid capture
* PageStatistics:  time based snapshot of  PageVisit activity per domain.  Captures page events from t to t+1


## Implementation notes
* Focused on building the minimal scaffold for finding the page activity differences
* Unit test proves that handling of page activity changes for a domain between two time periods or last two time periods works
* Unit test uses factories to create page statistics data for consumption by web services


## Installation

Software was developed on a MacBook Pro under Python 2.7.6, using Django, Django Rest Framework, sqlite, and virtualenv
Steps to install locally, using bash:
```
    > cp analytics-0.1.0.tar.gz /tmp
    > cd /tmp
    > tar -xf analytics-0.1.0.tar.gz
    > cd analytics-0.1.0
    > virtualenv pyenv/analytics
    > source pyenv/analytics/bin/activate
    > pip install –r requirements.txt
    > manage.py  syncdb (no need to create admin account)
    > scripts/loaddata.sh
```

## Runing unit testing
```
    >./manage.py test
        Creating test database for alias 'default'...
        DEBUG api_root elapsed time: 78.507000 ms
        ..WARNING missing underlying statistics
        DEBUG page_diffs elapsed time: 7.241000 ms
        .DEBUG page_diffs elapsed time: 4.831000 ms
        .DEBUG visit_list elapsed time: 6.397000 ms
        ..WARNING missing underlying statistics
        DEBUG page_diffs elapsed time: 4.862000 ms
        .
        ----------------------------------------------------------------------
        Ran 7 tests in 0.716s

        OK
```
        
## Running integration tests
*   start server
```
    > ./manage.py runserver
        Validating models...

        0 errors found
        March 24, 2014 - 18:22:05
        Django version 1.6.2, using settings 'analytics.settings'
        Starting development server at http://127.0.0.1:8000/
        Quit the server with CONTROL-C.
```
* Show end points
```
> curl -H 'Accept: application/json; indent=4'  'http://127.0.0.1:8000/api/' -uadmin:admin

{
    "domains": "http://127.0.0.1:8000/api/domains/", 
    "pagediffs": "http://127.0.0.1:8000/api/pagediffs/", 
    "users": "http://127.0.0.1:8000/api/users/", 
    "visits": "http://127.0.0.1:8000/api/visits/"
}
```
* Show domains
```
> curl -H 'Accept: application/json; indent=4'  'http://127.0.0.1:8000/api/domains/?apikey=99b792d59799b05a35ce4ff8bd41f35c72992a32'

{
    "count": 3, 
    "next": null, 
    "previous": null, 
    "results": [
        {
            "id": 1, 
            "creation_time": "2014-03-22T18:13:44.927Z", 
            "name": "gizmodo.com"
        }, 
        {
            "id": 2, 
            "creation_time": "2014-03-22T18:14:33.663Z", 
            "name": "avc.com"
        }, 
        {
            "id": 3, 
            "creation_time": "2014-03-22T18:15:03.215Z", 
            "name": "someecards.com"
        }
    ]
}
```
* Show pagediffs
```
> curl -H 'Accept: application/json; indent=4'  'http://127.0.0.1:8000/api/pagediffs/?apikey=99b792d59799b05a35ce4ff8bd41f35c72992a32&domain=gizmodo.com'

{
    "count": 1, 
    "next": null, 
    "previous": null, 
    "results": [
        {
            "path": "http://gismodo.com/page/1", 
            "subject": "First Subject", 
            "change": 200
        }
    ]
}
```
   
## Code and Design Review

Key modules and classes, in suggested priority order:
- analytics_api.api.tests.PageDiffTestCase
- analytics__api.views. PageDiffView   
- analytics__api.models. PageStatistics


## Key Findings
- Further analysis required on validation of request.  Not yet clear how it stacks vs typical Django form validation
- Further analysis required for efficient attribute level serialization override.
- Ability to quickly test the API using forms similar to the Django admin facilities
- Clean code
- Good documentation
