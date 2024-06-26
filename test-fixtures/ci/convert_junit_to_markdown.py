import sys
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
            'name': testsuite.get('name'),
            'tests': testsuite.get('tests'),
            'failures': testsuite.get('failures'),
            'test_cases': []
        }
        
        for testcase in testsuite.iter('testcase'):
            case = {
                'name': testcase.get('name'),
                'classname': testcase.get('classname'),
                'time': testcase.get('time'),
                'status': '✅'
            }

            failure = testcase.find('failure')
            error = testcase.find('error')
            if failure is not None:
                case['status'] = '❌'
                case['message'] = failure.get('message')
            elif error is not None:
                case['status'] = '⚠️'
                case['message'] = error.get('message')

            suite['test_cases'].append(case)
            
        test_suites.append(suite)

    return test_suites

def convert_to_markdown(test_suites):
    """
    Converts a test suite data into Markdown format with the suite's name as heading
    
    Args:
        test_suites (a dict): Test suite data.
        
    Returns:
        str: A string in Markdown format.
    """
    markdown = "# Test Results\n\n"

    for test_suite in test_suites:
        markdown += "## {name}\n\n".format(name = test_suite['name'].replace('XCUITest.' ,''))
        markdown += "* Number of tests: {tests}\n".format(tests = test_suite['tests'])
        markdown += "* Number of failures: {failures}\n\n".format(failures = test_suite['failures'])
        markdown += convert_test_cases_to_markdown(test_suite['test_cases'])
    return markdown

def convert_test_cases_to_markdown(test_cases):
    """
    Converts test case data into Markdown format using a table.

    Args:
        test_cases (list of dict): List of test case data from a test suite

    Returns:
        str: A string in Markdown format.
    """
    markdown = ""
    markdown += "| Test Name | Time (s) | Status | Message |\n"
    markdown += "|-----------|----------|--------|---------|\n"

    for case in test_cases:
        message = case.get('message', '')
        message = ('`{message}`'.format(message = message) if message != '' else '')
        markdown += "| {name} | {time} | {status} | {message} |\n".format(
            name = case['name'],
            time = case['time'],
            status = case['status'],
            message = message
        )
    markdown += "\n"
    
    return markdown

def convert_file(input_file, output_file):
    """
    Converts a JUnit XML file to a Markdown file.

    Args:
        input_file (str): Path to the JUnit XML file.
        output_file (str): Path to the output Markdown file.
    """
    test_cases = parse_junit_xml(input_file)
    markdown = convert_to_markdown(test_cases)
    with open(output_file, 'w') as md_file:
        md_file.write(markdown)

if __name__ == "__main__":
    convert_file(sys.argv[1], "output.md")