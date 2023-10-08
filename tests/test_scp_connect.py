from unittest.mock import call, patch

from ..scp_connect import check_files, check_space, format_size, set_permissions


@patch("scp_connect.subprocess.run")
def test_set_permissions(mock_run):
    """
    Test the set_permissions function.

    This function tests that the set_permissions function correctly calls the subprocess
    run function with the expected arguments.

    Args:
        mock_run (Mock): The mock subprocess run function.
    """
    set_permissions("/path/to/destination")
    mock_run.assert_called_once_with(
        ["ssh", "dvitto@totoro", 'chmod -R 755 "/path/to/destination"']
    )


@patch("scp_connect.subprocess.run")
def test_check_files(mock_run):
    """
    Test the check_files function.

    This function tests that the check_files function correctly calls the subprocess
    run function with the expected arguments to check the files in the destination folder.

    Args:
        mock_run (Mock): The mock subprocess run function.
    """
    check_files([{"/path/to/origin": ["file1", "file2"]}], "/path/to/destination/")
    calls = [
        call(["ssh", "dvitto@totoro", 'ls -alh "/path/to/destination/file1"']),
        call(["ssh", "dvitto@totoro", 'ls -alh "/path/to/destination/file2"']),
    ]
    mock_run.assert_has_calls(calls)


@patch("scp_connect.subprocess.check_output")
def test_check_space(mock_check_output):
    mock_check_output.return_value = b"100G\n"
    check_space()
    mock_check_output.assert_called_once_with(
        ["ssh", "dvitto@totoro", "df -h /opt/mounts/media/ | awk 'NR>1{print $4}'"]
    )


def test_format_size():
    assert format_size(500) == "500.00 B"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1048576) == "1.00 MB"
    assert format_size(1073741824) == "1.00 GB"
    assert format_size(1099511627776) == "1.00 TB"
