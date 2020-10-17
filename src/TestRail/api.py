# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .base import APIBase
from . import log
from . import objectBuilder
from typing import Sequence, NamedTuple, Dict
import urllib2
import json
import base64


class APIClient:
    """
    TestRail API binding for Python 2.x (API v2, available since
    TestRail 3.0)

    Variables:

    """
    def __init__(self, base_url):
        """
        Initialize the APUClient Instance

        Arguments:
            base_url {string} -- protocal plus hostname or address ie. http://hostnet.net
        """
        log.trace("APIClient.__init__   '%s'" % (base_url))
        self.user = ''
        self.password = ''
        if not base_url.endswith('/'):
            base_url += '/'
        self.__url = base_url + 'index.php?/api/v2/'

    def send_get(self, uri):
        """
        Issues a GET request (read) against the API and returns the result
        (as Python dict).

        Arguments:
            uri {string} -- The API method to call including parameters
                             (e.g. get_case/1)

        Returns:
            dict -- Server response data
        """
        log.trace("send_get  '%s'" % uri)
        return self.__send_request('GET', uri, None)

    def send_post(self, uri, data):
        """
         Send POST

        Issues a POST request (write) against the API and returns the result
        (as Python dict).

        Arguments:
            uri {string} -- The API method to call including parameters
                            (e.g. add_case/1)
            data {dict} --  The data to submit as part of the request (as
                            Python dict, strings must be UTF-8 encoded)

        Returns:
            dict -- response data
        """
        log.trace("send_post '%s', '%s'" % (uri, data))
        return self.__send_request('POST', uri, data)

    def __send_request(self, method, uri, data):
        """
        Do the heavy lifting for requests

        Arguments:
            method {String} -- HTTP method name
            uri {string} -- full URL
            data {dict} -- Any request data

        Returns:
            dict -- The response data

        Raises:
            APIError -- Any error responses get raised as exceptions
        """
        log.trace("__send_request  '%s', '%s', '%s'" % (method, uri, data))
        url = self.__url + uri
        request = urllib2.Request(url)
        if (method == 'POST'):
            request.add_data(json.dumps(data))
        log.debug("username = '%s', apikey = '%s'" % (self.user, self.password))
        auth = base64.b64encode('%s:%s' % (self.user, self.password))
        log.debug("auth = '%s'" % auth)
        request.add_header('Authorization', 'Basic %s' % auth)
        request.add_header('Content-Type', 'application/json')

        e = None
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError as e:
            response = e.read()

        if response:
            result = json.loads(response)
        else:
            result = {}

        if e != None:
            if result and 'error' in result:
                error = '"' + result['error'] + '"'
            else:
                error = 'No additional error message received'
            raise APIError('TestRail API returned HTTP %s (%s)' % (e.code, error))
        return result


class APIError(Exception):
    pass



class APIBase:
    """
    Base class for classes accessing the Test Rail API
    """

    def __init__(self, baseurl, uname, apikey):
        self.__baseurl = baseurl
        self.client = APIClient(self.__baseurl)
        self.client.user = uname
        self.client.password = apikey
        return


class TestSuites(APIBase):
    """
    Deal with test suites

    Extends:
        APIBase

    Variables:
        __projects {TestProjects} -- Used to get project information
    """

    def __init__(self, baseURI: str, uname: str, apiKey: str):
        """

        Arguments:
            baseURI {str} -- Base url for the server. https://hostname:port/
            uname {str} -- The Test Rail username to use
            apiKey {str} -- The Test Rail API key for the user
        """
        APIBase.__init__(self, baseURI, uname, apiKey)
        self.__projects = TestProjects(baseURI, uname, apiKey)

    def getTestSuites(self, projectName: str) -> dict:
        """
        Return a list of suites

        Arguments:
            projectName {str} -- The project name we are working with

        Returns:
            dict -- The server response
                    {
                        "description": "..",
                        "id": 1,
                        "name": "Setup & Installation",
                        "project_id": 1,
                        "url": "http://<server>/testrail/index.php?/suites/view/1"
                    }
        """

        log.trace("getTestSuites %s" % projectName)
        projID = self.__projects.projectIDFromName(projectName)
        path = "get_suites/%s" % projID
        log.debug("End point: '%s'" % path)
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt

    def getTestSuite(self, suiteID: int) -> dict:
        """
        Return details on a specific suite

        Arguments:
            suiteID {int} -- The test suite we want information on

        Returns:
            Dict -- The server response
            {
                "description": "..",
                "id": 1,
                "name": "Setup & Installation",
                "project_id": 1,
                "url": "http://<server>/testrail/index.php?/suites/view/1"
            }
        """
        log.trace("getTestSuite '%d'" % suiteID)
        path = "get_suite/%d" % suiteID
        log.debug("Path = '%s'" % path)
        rslt =  self.client.send_get(path)
        log.debug(rslt)
        return rslt

    def addTestSuite(self, projectName, name, description):
        """
        Add a new test suite

        Arguments:
            projectName {string} -- Name of the project
            name {string} -- Name of the test suite
            description {string} -- Test suite description

        Returns:
            dict -- server response
            {
                "description": "..",
                "id": 1,
                "name": "Setup & Installation",
                "project_id": 1,
                "url": "http://<server>/testrail/index.php?/suites/view/1"
            }
        """
        log.trace("addTestSuite '%s', '%s', '%s'" % (projectName, name, description))
        path = "add_suite/%s" % projectName
        log.debug("Path='%s'" % path)
        rslt = self.client.send_post(path, {"name": name, "description": description})
        log.debug(rslt)
        return rslt

    def updateTestSuite(self, suiteID: str, name: str, description: str):
        """
         update an existing test suite

        Arguments:
            suiteID {string} -- The suite ID that we are updating
            name {string} -- updated name
            description {string} -- updated description

        Returns:
            dict -- The server response
        """
        log.trace("updateTestSuite '%s', '%s', '%s'" % (suiteID, name, description))
        path = "update_suite/%s" % suiteID
        log.debug("Path = '%s'" % path)
        rslt = self.client.send_post(path, {"name": name, "description": description})
        log.debug(rslt)
        return rslt

    def suiteNameFromID(self, projectName, suiteID):
        """
        Derive a suite name from a suite ID.

        Arguments:
            projectName {string} -- The name of the project where the suite is located
            suiteID {String} -- The ID of the suite we want the name of

        Returns:
            string -- The name of the suite
            {
                "description": "..",
                "id": 1,
                "name": "Setup & Installation",
                "project_id": 1,
                "url": "http://<server>/testrail/index.php?/suites/view/1"
            }
        """
        log.trace("suiteNameFromID %s, %s" % (projectName, suiteID))
        suites = self.getTestSuites(projectName)
        rslt = None
        log.debug(suites)
        for s in suites:
            if s["id"] == suiteID:
                rslt = s["name"]
                break
        log.debug("Suite Name: '%s'" % rslt)
        return rslt

    def getSectionFromID(self, sectionID):
        """
        get the section info for this section

        Arguments:
            sectionID {string} -- section we want

        Returns:
            dict -- section info
            {
                "depth": 0,
                "description": null,
                "display_order": 1,
                "id": 1,
                "name": "Prerequisites",
                "parent_id": null,
                "suite_id": 1
            }
        """
        log.trace("getSectionByID '%s'" % sectionID)
        path = "get_section/%s" % sectionID
        log.debug("Path = %s" % path)
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt

    def getSections(self, projID, suiteID):
        """
        get the sections for this suite and project

        Arguments:
            projID {string} -- The project ID for the suite
            suiteID {string} -- The suite ID for these sections

        Returns:
            List of Dict -- server response
            [
                {
                    "depth": 0,
                    "display_order": 1,
                    "id": 1,
                    "name": "Prerequisites",
                    "parent_id": null,
                    "suite_id": 1
                },
                {
                    "depth": 0,
                    "display_order": 2,
                    "id": 2,
                    "name": "Documentation & Help",
                    "parent_id": null,
                    "suite_id": 1
                },
                {
                    "depth": 1, // A child section
                    "display_order": 3,
                    "id": 3,
                    "name": "Licensing & Terms",
                    "parent_id": 2, // Points to the parent section
                    "suite_id": 1
                },
                ..
            ]
        """
        log.trace("getSections '%s', '%s'" % (projID, suiteID))
        path = "get_sections/%s&suite_id=%s" % (projID, suiteID)
        log.debug("Path = %s" % path)
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt

class TestRun(APIBase):
    """
    Work with testruns

    Extends:
        APIBase

    Variables:
        __testProjects {TestProjects} -- for getting project information
    """
    __testProjects = TestProjects()

    def __init__(self, *args, **kwargs):
        log.trace("TestRun.__init__")
        APIBase.__init__(self, *args, **kwargs)
        return

    def getTestRuns(self, projectName):
        """
        return a list of test runs for the project.
        """
        log.trace("getTestRuns '%s'" % projectName)
        projectID = self.__testProjects.projectIDFromName(projectName)
        path = "/get_runs/%s" % projectID
        log.debug("Path = %s" % path)
        rslt = self.client(path)
        log.debug(rslt)
        return rslt

    def addTestRun(self, projectName, **kwargs):
        """
        Add a test run to the project for the suite
        suite_id    int The ID of the test suite for the test run (optional if the project is operating in single suite mode, required otherwise)
        name    string  The name of the test run
        description string  The description of the test run
        milestone_id    int The ID of the milestone to link to the test run
        assignedto_id   int The ID of the user the test run should be assigned to
        include_all bool    True for including all test cases of the test suite and false for a custom case selection (default: true)
        case_ids    array   An array of case IDs for the custom case selection
        """
        log.trace("""addTestRun '%s'""" % dict(projectName=projectName, **kwargs))
        projectID = self.__testProjects.projectIDFromName(projectName)
        path = "add_run/%s" % projectID
        log.debug("path = '%s'" % path)
        rslt = self.client.send_post(path, kwargs)
        log.debug(rslt)
        return rslt

    def updateTestRun(self, runID, **details):
        """
        Update and existing test run.
        name    string  The name of the test run
        description string  The description of the test run
        milestone_id    int The ID of the milestone to link to the test run
        include_all bool    True for including all test cases of the test suite and false for a custom case selection (default: true)
        case_ids    array   An array of case IDs for the custom case selection
        project_id  The ID of the project the test run should be added to
        """
        log.trace("""updateTestRun '%s'""" % dict(runID=runID, **details))
        path = "update_run/%s" % runID
        log.debug("path='%s'" % path)
        rslt = self.client.send_post(path, details)
        log.debug(rslt)
        return rslt

    def closeTestRun(self, runID):
        """
        Close an existing test run.
        Please note: Closing a test run cannot be undone.
        """
        log.trace("closeTestRun '%s'" % runID)
        path = "close_run/%s" % runID
        log.debug(path)
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt

    def delete_run(self, runID):
        """
        delete an existing test run
        Please note: Deleting a test run cannot be undone and also permanently deletes all tests & results of the test run.
        """
        log.debug("delete_run '%s'" % runID)
        path = "/delete_run/%s" % runID
        log.debug(path)
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt


ResultList = Sequence[NamedTuple]


class TestCases(APIBase):
    """
    An interface to test rail for working with test cases

    Extends:
        APIBase

    """

    def __init__(self, baseURI, uname, apiKey):
        APIBase.__init__(self, baseURI, uname, apiKey)

    def getTestCases(self, projectID: int, testSuiteID: int, sectionID: int = 0) -> ResultList:
        """
        Get a list of test cases for the project and suite
        looks similar to below. Fields are customizable so your custom field names will be here
        but using object syntax
        fields are customizable so your custom field names will be here but in object syntax
        Returns:[
            {
                "created_by": 5,
                "created_on": 1392300984,
                "custom_expected": "..",
                "custom_preconds": "..",
                "custom_steps": "..",
                "custom_steps_separated": [
                    {
                        "content": "Step 1",
                        "expected": "Expected Result 1"
                    },
                    {
                        "content": "Step 2",
                        "expected": "Expected Result 2"
                    }
                ],
                "estimate": "1m 5s",
                "estimate_forecast": null,
                "id": 1,
                "milestone_id": 7,
                "priority_id": 2,
                "refs": "RF-1, RF-2",
                "section_id": 1,
                "suite_id": 1,
                "title": "Change document attributes (author, title, organization)",
                "type_id": 4,
                "updated_by": 1,
                "updated_on": 1393586511
            }, ...]
        """
        log.trace("getTestCases  '%d', '%d', '%d'" % (projectID, testSuiteID, sectionID))
        path = "get_cases/%s&suite_id=%s" % (projectID, testSuiteID)
        if sectionID:
            path += "&section_id=%d" % sectionID
        log.debug("Path = '%s'" % path)
        TCs = [objectBuilder(x.keys(), **x) for x in self.client.send_get(path) if x]
        log.debug(TCs)
        return TCs

    def getTestCaseTypes(self) -> ResultList:
        """
        The available test case types for the system

        Returns:
            [list of namedtuples] -- The fields look like this but use object syntax
            [
                {
                    "id": 1,
                    "is_default": false,
                    "name": "Automated"
                },
                {
                    "id": 2,
                    "is_default": false,
                    "name": "Functionality"
                },
                {
                    "id": 6,
                    "is_default": true,
                    "name": "Other"
                },
                ..
            ]
        """
        log.trace("getTestCaseTypes")
        path = "get_case_types"
        rslt = [objectBuilder(x.keys(), **x) for x in self.client.send_get(path) if x]
        log.debug(rslt)
        return rslt

    def getTestCasePriorities(self) -> ResultList:
        """
        Get the list of available priority type info

        Returns:
            List of namedtuples -- Fields look like this but using object syntax

            [
                {
                    "id": 1,
                    "is_default": false,
                    "name": "1 - Don't Test",
                    "priority": 1,
                    "short_name": "1 - Don't"
                },
                ..
                {
                    "id": 4,
                    "is_default": true,
                    "name": "4 - Must Test",
                    "priority": 4,
                    "short_name": "4 - Must"
                },
                ..
            ]
        """
        log.trace("getTestCasePriorities")
        path = "get_priorities"
        rslt = [objectBuilder(x.keys(), **x) for x in self.client.send_get(path) if x]
        log.debug(rslt)
        return rslt

    def getCustomFieldDefinitions(self) -> ResultList:
        """
        get the field definitions for the test case fiels.

        Type ID Name
            1   String
            2   Integer
            3   Text
            4   URL
            5   Checkbox
            6   Dropdown
            7   User
            8   Date
            9   Milestone
            10  Steps
            12  Multi-select

        Returns:
            [List of namedtuples] -- Fields look like this but using object syntax
            [
                {
                    "configs": [
                    {
                        "context": {
                            "is_global": true,
                            "project_ids": null
                        },
                        "id": "..",
                        "options": {
                            "default_value": "",
                            "format": "markdown",
                            "is_required": false,
                            "rows": "5"
                        }
                    }
                    ],
                    "description": "The preconditions of this test case. ..",
                    "display_order": 1,
                    "id": 1,
                    "label": "Preconditions",
                    "name": "preconds",
                    "system_name": "custom_preconds",
                    "type_id": 3
                },
                ..
            ]
        """
        log.trace("testCaseFieldDefinitions")
        path = "get_case_fields"
        d = self.client.send_get(path)

        def ofy(obj: Dict) -> NamedTuple:
            def ooffyy(y: Dict) -> NamedTuple:
                y["context"] = objectBuilder(y["context"].keys(), **y["context"])
                y["options"] = objectBuilder(y["options"].keys(), **y["options"])
                return objectBuilder(y.keys(), y)
            obj["configs"] = [ooffyy(b) for b in obj["configs"] if b]
            return objectBuilder(obj.keys(), **obj)

        rslt = [ofy(a) for a in d if a]
        log.debug(rslt)
        return rslt


class TestProjects(APIBase):
    """
    Dealing with projects

    Extends:
        APIBase
    """

    def __init__(self, *args, **kwargs):
        APIBase.__init__(self, *args, **kwargs)
        self.__projIDNameMap = {k: v for k, v in [(x[u"name"], x[u"id"]) for x in self.getProjects()]}

    def getProject(self, projectID):
        """
        get a single project
        """
        log.trace("getProject '%s'" % projectID)
        path = "get_project/%s" % projectID
        log.debug("Path = '%s'" % path)
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt

    def getProjects(self):
        """
        Retrieve a list of projects
        """
        log.trace("getProjects")
        rslt = self.client.send_get("get_projects")
        log.debug(rslt)
        return rslt

    def projectIDFromName(self, name):
        """
        Derive a project ID from a project Name
        """
        log.trace("projectIDFromName '%s'" % name)
        rslt = self.__projIDNameMap[name]
        log.debug("Found project ID: '%s'" % rslt)
        return rslt

    def addProject(self, **details):
        """
        name    string  The name of the project (required)
        announcement    string  The description of the project
        show_announcement   bool  True if the announcement should be
                                  displayed on the project's overview page and false otherwise
        suite_mode  integer       The suite mode of the project (1 for single suite mode,
                                  2 for single suite + baselines, 3 for multiple suites)
                                  (added with TestRail 4.0)
        """
        log.trace("addProject '%s'" % details)
        path = "add_project"
        rslt = self.client.send_post(path, details)
        log.debug(rslt)
        return rslt

    def updateProject(self, projectID, **details):
        """
        Update an existing project
        name    string  The name of the project (required)
        announcement    string  The description of the project
        show_announcement   bool    True if the announcement should be displayed on the project's
        overview page and false otherwise suite_mode  integer The suite mode of the project
        (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)
        (added with TestRail 4.0) is_completed bool  Specifies whether a project is considered
        completed or not
        """
        log.trace("updateProject '%s', '%s'" % (projectID, details))
        path = "update_project/%s" % projectID
        rslt = self.client.send_post(path, details)
        log.debug(rslt)
        return rslt

    def deleteProject(self, projectID):
        """
        Deletes an existing project
           Please note: Deleting a project cannot be undone and also permanently deletes all test
           suites & cases, test runs & results and everything else that is part of the project.
        """

        log.debug("deleteProject '%s'" % projectID)
        path = "/delete_project/%s" % projectID
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt

class TestResults(APIBase):
    """
    TestRail interface for posting test results from python

    Extends:
        APIBase
    """

    def __init__(self, *args, **kwargs):
        APIBase.__init__(self, *args, **kwargs)

    def getTestResults(self, testID):
        """
        Get the results for a specific test case

        Arguments:
            testID {string} -- get the test results a test run

        Returns:
            list of dict -- The server response
        """
        log.trace("getTestResults %s" % testID)
        path = "get_results/%s" % testID
        log.debug(path)
        rslt = self.client.send_get(path)
        log.debug(rslt)
        return rslt

    def getResultsForTestRun(self, runID):
        """
        Get the results for a test run

        Arguments:
            runID {string} -- The test run

        Returns:
            List of dict -- The test run info for this test run
        """
        log.trace("getResultsForTestRun %s, %s" % runID)
        path = "get_results_for_run/%s" % runID
        log.debug(path)
        rslts = self.client.send_get(path)
        log.debug(rslts)
        return rslts

    def postTestResult(self, testID, **details):
        """
        Add a result to the given test.

        Arguments:
            testID {string} -- The ID os the test we want to post details againse
            **details {dict} -- status_id: int
                    passed = 1
                    blocked = 2
                    untested = 3
                    retest = 4
                    failed = 5

                comment: free form string
                version: version or build tested
                elapsed: execution time
                defects: defect ID's
                assignedto_id: who executed the test

        Returns:
            dict -- Server response
        """
        log.trace("postTestResult '%s', '%s'" % (testID, details))
        path = "add_result/%s" % testID
        log.debug(path)
        rslt = self.client.send_post(path, details)
        log.debug(rslt)
        return rslt

    def postTestResultsForRun(self, runID, *details):
        """
        add test results for a given run. details contains a list of
        dictionaries where testID is a required field. All tests must be part of the same test run

        Arguments:
            runID {string} -- The run that we are posting results for
            *details {var args of dictionaries} -- var args for the additional parameters
                                                    Each dictionary must have these fields:
                                                    test_id: Int. ID of the test
                                                    status_id: int
                                                                passed = 1
                                                                blocked = 2
                                                                untested = 3
                                                                retest = 4
                                                                failed = 5

                                                    comment: free form string
                                                    version: version or build tested
                                                    elapsed: execution time
                                                    defects: defect ID's
                                                    assignedto_id: who executed the test
                                                    Optional fields:
                                                        Custom field ID's and values

        Returns:
            dict -- server response
        """
        log.debug("postTestResultsForRun '%s', '%s'" % (runID, details))
        path = "add_results/%s" % runID
        log.debug(path)
        rslt = self.client.send_post(path, details)
        log.debug(rslt)
        return rslt

    def postResults(self, runID, *details):
        """
        add test results for the given test cases in the given test run. Each result dictionary
        must contain a test case ID instead of a test ID. Details is a list of dictionaries
        with the result details.


        Arguments:
            runID {string} -- The run ID to post results to
            *details {var args of dicts} -- The results to post
                                            Mandatory Fields:
                                            Test Case ID
                                            status_id: int
                                                        passed = 1
                                                        blocked = 2
                                                        untested = 3
                                                        retest = 4
                                                        failed = 5

                                            comment: free form string
                                            version: version or build tested
                                            elapsed: execution time
                                            defects: defect ID's
                                            assignedto_id: who executed the test
                                        Optional fields:
                                            Custom field ID's and values

        Returns:
            dict -- The server response
        """

        log.debug("postResults '%s', '%s'" % (runID, details))
        path = "add_results_for_cases/%s" % runID
        log.debug(path)
        rslt = self.client.send_post(path, details)
        log.debug(rslt)
        return rslt
