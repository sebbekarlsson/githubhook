from githubhook.app import app

from mock import patch


@patch('githubhook.app.deploy_app')
@patch('githubhook.app.download_file')
def test_endpoint_success(
    mock_deploy_app,
    mock_download_file,
    github_push_payload
):
    with app.test_client() as client:
        response = client.post('/', json=github_push_payload)

        assert response.status_code == 200
        mock_download_file.assert_called_once()


@patch('githubhook.app.deploy_app')
@patch('githubhook.app.download_file')
def test_endpoint_fail(
    mock_deploy_app,
    mock_download_file,
    github_push_payload
):
    del github_push_payload['commits']

    with app.test_client() as client:
        response = client.post('/', json=github_push_payload)

        assert response.status_code == 400
        mock_download_file.assert_not_called()
