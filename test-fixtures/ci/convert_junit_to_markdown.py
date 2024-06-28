import getopt, sys
import xml.etree.ElementTree as ET

# Modified from junit_to_markdown
# https://github.com/stevengoossensB/junit_to_markdown/tree/main

def parse_junit_xml(file_path):
    """
    Parses a JUnit XML file and extracts test suite data.

    Args:
        file_path (str): Path to the JUnit XML file.

    Returns:
        list of dict: A list of dictionaries, each representing a test case.
    """
    test_suites = []
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    for testsuite in root.iter('testsuite'):
        suite = {
            'name': testsuite.get('name', ''),
            'tests': testsuite.get('tests', ''),
            'failures': testsuite.get('failures', ''),
            'test_cases': []
        }
        
        for testcase in testsuite.iter('testcase'):
            case = {
                'name': testcase.get('name', ''),
                'classname': testcase.get('classname', ''),
                'time': testcase.get('time', ''),
                'status': '✅'
            }

            failure = testcase.find('failure')
            error = testcase.find('error')
            if failure is not None:
                case['status'] = '❌'
                case['message'] = failure.get('message','')
            if error is not None:
                case['status'] = '🛑'
                case['message'] = error.get('message', '')

            suite['test_cases'].append(case)
            
        test_suites.append(suite)

    return test_suites

def count_test_retry_failure(test_name, test_cases):
    count = 0
    for test_case in test_cases:
        if test_case.get('name', '') == test_name and not test_case.get('status') == '✅':
            count += 1
    return count

def convert_to_github_markdown(test_suites):
    markdown = "# Test Results\n\n"

    for test_suite in test_suites:
        markdown += "## {name}\n\n".format(name = test_suite.get('name', '').replace('XCUITest.' ,''))
        markdown += "* Number of tests: {tests}\n".format(tests = test_suite['tests'])
        markdown += "* Number of failures: {failures}\n\n".format(failures = test_suite['failures'])
        markdown += convert_test_cases_to_github_markdown(test_suite['test_cases'])
    return markdown

def convert_to_slack_markdown(test_suites):
    markdown = ""
    for test_suite in test_suites:
        if int(test_suite.get('failures')):
            markdown += "{test_suite_name}\\n".format(test_suite_name = test_suite.get('name', '').replace('XCUITest.' ,''))
            markdown += "```\\n"
            test_cases = test_suite.get('test_cases', [])
            done = []
            for test_case in test_cases:
                if not test_case.get('status') == '✅' and not test_case.get('name','') in done:
                    fail_count = count_test_retry_failure(test_case.get('name', ''), test_cases)
                    # flaky test?
                    if fail_count < 3:
                        test_case['status'] = '⚠️'
                    markdown += "{status} {test_case_name}\\n".format(test_case_name=test_case.get("name"), status=test_case.get('status'))
                    done.append(test_case.get('name', ''))
                    markdown += "```\\n"
    if markdown == "":
        markdown += "🎉 No test failures 🎉"
    else:
        markdown += "\n\n⚠️-Flaky ❌-Failed"
    return markdown    

def convert_to_github_markdown_failures_only(test_suites):
    markdown = ""
    for test_suite in test_suites:
        if int(test_suite['failures']):
            markdown += "## {name}\n\n".format(name = test_suite.get('name', '').replace('XCUITest.' ,''))
            markdown += convert_test_cases_to_github_markdown_failures_only(test_suite.get('test_cases', []))
    if markdown == "":
        markdown += "## 🎉 No test failures 🎉"
    else:
        markdown += "\n\n⚠️-Flaky ❌-Failed"
    return markdown

def convert_test_cases_to_github_markdown(test_cases):
    markdown = ""
    markdown += "| Test Name | Time (s) | Status | Message |\n"
    markdown += "|-----------|----------|--------|---------|\n"

    for test_case in test_cases:
        message = test_case.get('message', '')
        message = ('```{message}```'.format(message = message) if message != '' else '')
        markdown += "| {name} | {time} | {status} | {message} |\n".format(
            name = test_case.get('name', ''),
            time = test_case.get('time', ''),
            status = test_case.get('status'),
            message = message
        )
    markdown += "\n"
    
    return markdown

def convert_test_cases_to_github_markdown_failures_only(test_cases):
    markdown = ""
    markdown += "| Test Name | Status | Message |\n"
    markdown += "|-----------|--------|---------|\n"
    
    done = []
    
    for test_case in test_cases:
        if not test_case.get('status') == '✅' and not test_case.get('name', '') in done:
            fail_count = count_test_retry_failure(test_case.get('name'), test_cases)
            # flaky test?
            if fail_count < 3:
                test_case['status'] = '⚠️'
            message = test_case.get('message', '')
            message = message = ('```{message}```'.format(message = message) if message != '' else '')
            markdown += "| {name} | {status} | {message} |".format(
                name = test_case.get('name', ''),
                status = test_case.get('status'),
                message = message
            )
            done.append(test_case.get('name'))
            markdown += "\n"
    
    return markdown

def convert_file_github(input_file, output_file, failures_only = False):
    test_cases = parse_junit_xml(input_file)
    markdown = ""
    if failures_only:
        markdown = convert_to_github_markdown_failures_only(test_cases)
    else:
        markdown = convert_to_github_markdown(test_cases)
    with open(output_file, 'w') as md_file:
        md_file.write(markdown)

def convert_file_slack(input_file, output_file):
    test_cases = parse_junit_xml(input_file)
    markdown = convert_to_slack_markdown(test_cases)
    with open(output_file, 'w') as md_file:
        md_file.write(markdown)

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "fgs", ["failures-only", "github", "slack"])
    failures_only = False
    github_markdown = True
    for opt, arg in opts:
        if opt == "-f" or opt == "--failures-only":
            failures_only = True
        if opt == "-s" or opt == "--slack":
            github_markdown = False
    if github_markdown:
        convert_file_github(args[0], args[1], failures_only=failures_only)
    else:
        convert_file_slack(args[0], args[1])