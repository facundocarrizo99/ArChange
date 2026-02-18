"""Tests for job execution and exchange rate fetching."""
import pytest
from unittest.mock import patch, MagicMock
from app.job import run_job, scheduled_task


class TestJobExecution:
    """Test suite for job execution functions."""

    @patch('app.job.fetch_and_store_exchange_rates')
    def test_run_job_success(self, mock_fetch):
        """Test run_job executes successfully and returns expected result."""
        # Mock successful fetch response
        mock_fetch.return_value = {
            "status": "ok",
            "inserted": 7,
            "total": 7,
            "exchanges": [],
            "errors": None
        }
        
        result = run_job()
        
        assert result["status"] == "ok"
        assert result["inserted"] == 7
        assert result["total"] == 7
        mock_fetch.assert_called_once()

    @patch('app.job.fetch_and_store_exchange_rates')
    def test_run_job_with_errors(self, mock_fetch):
        """Test run_job handles errors from fetch function."""
        mock_fetch.return_value = {
            "status": "ok",
            "inserted": 5,
            "total": 7,
            "errors": ["Error 1", "Error 2"]
        }
        
        result = run_job()
        
        assert result["status"] == "ok"
        assert result["inserted"] == 5
        assert len(result["errors"]) == 2

    @patch('app.job.fetch_and_store_exchange_rates')
    def test_run_job_exception(self, mock_fetch):
        """Test run_job handles exceptions gracefully."""
        mock_fetch.side_effect = Exception("Connection error")
        
        result = run_job()
        
        assert result["status"] == "error"
        assert "Connection error" in result["message"]

    @patch('app.job.fetch_and_store_exchange_rates')
    def test_run_job_when_function_unavailable(self, mock_fetch):
        """Test run_job when fetch function raises an exception."""
        mock_fetch.side_effect = RuntimeError("DB pool not initialized")
        result = run_job()
        assert result["status"] == "error"
        assert "DB pool not initialized" in result["message"]

    @patch('app.job.run_job')
    def test_scheduled_task(self, mock_run_job):
        """Test scheduled_task calls run_job correctly."""
        mock_run_job.return_value = {"status": "ok", "inserted": 7}
        
        result = scheduled_task()
        
        mock_run_job.assert_called_once_with("scheduled")
        assert result["status"] == "ok"
