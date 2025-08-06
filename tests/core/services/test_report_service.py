"""Tests for report service functionality."""

import pytest
from datetime import date, datetime
from unittest.mock import patch

from smart_nippo.core.database import init_database, reset_database
from smart_nippo.core.services.report_service import ReportService
from smart_nippo.core.services.template_service import TemplateService
from smart_nippo.core.models import Template, TemplateField, FieldType


class TestReportService:
    """Test cases for ReportService."""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """テスト用データベースのセットアップ."""
        reset_database()
        init_database()
        yield

    def test_create_report(self):
        """Test creating a new report."""
        # Create a template first
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="date",
                    label="Date",
                    field_type=FieldType.DATE,
                    required=True,
                    order=1
                ),
                TemplateField(
                    name="content",
                    label="Content", 
                    field_type=FieldType.MEMO,
                    required=True,
                    order=2
                )
            ]
        )
        
        # Create a report
        test_data = {
            "date": "2025-08-06",
            "content": "Test content"
        }
        
        report = ReportService.create_report(
            template_id=template.id,
            data=test_data,
            report_date=date(2025, 8, 6)
        )
        
        assert report is not None
        assert report.id is not None
        assert report.template_id == template.id
        assert report.template.name == "Test Template"
        assert report.get_date() == "2025-08-06"
        assert report.get_field_value("content") == "Test content"
        assert report.created_at is not None

    def test_create_report_duplicate_date(self):
        """Test creating a report with duplicate date fails."""
        # Create a template first
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="date",
                    label="Date",
                    field_type=FieldType.DATE,
                    required=True,
                    order=1
                )
            ]
        )
        
        test_data = {"date": "2025-08-06"}
        
        # Create first report
        ReportService.create_report(
            template_id=template.id,
            data=test_data,
            report_date=date(2025, 8, 6)
        )
        
        # Try to create another report for the same date
        with pytest.raises(ValueError, match="の日報は既に存在します"):
            ReportService.create_report(
                template_id=template.id,
                data=test_data,
                report_date=date(2025, 8, 6)
            )

    def test_get_report_by_id(self):
        """Test getting a report by ID."""
        # Create a template and report
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="date",
                    label="Date",
                    field_type=FieldType.DATE,
                    required=True,
                    order=1
                )
            ]
        )
        
        created_report = ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-08-06"}
        )
        
        # Get the report by ID
        retrieved_report = ReportService.get_report(report_id=created_report.id)
        
        assert retrieved_report is not None
        assert retrieved_report.id == created_report.id
        assert retrieved_report.template_id == template.id

    def test_get_report_by_date(self):
        """Test getting a report by date."""
        # Create a template and report
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="date",
                    label="Date",
                    field_type=FieldType.DATE,
                    required=True,
                    order=1
                )
            ]
        )
        
        test_date = date(2025, 8, 6)
        ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-08-06"},
            report_date=test_date
        )
        
        # Get the report by date
        retrieved_report = ReportService.get_report(
            report_date=test_date,
            template_id=template.id
        )
        
        assert retrieved_report is not None
        assert retrieved_report.get_date() == "2025-08-06"

    def test_update_report(self):
        """Test updating a report."""
        # Create a template and report
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="content",
                    label="Content",
                    field_type=FieldType.MEMO,
                    required=True,
                    order=1
                )
            ]
        )
        
        created_report = ReportService.create_report(
            template_id=template.id,
            data={"content": "Original content"}
        )
        
        # Update the report
        updated_report = ReportService.update_report(
            report_id=created_report.id,
            data={"content": "Updated content"}
        )
        
        assert updated_report.get_field_value("content") == "Updated content"
        assert updated_report.updated_at > created_report.created_at

    def test_delete_report(self):
        """Test deleting a report."""
        # Create a template and report
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="date",
                    label="Date",
                    field_type=FieldType.DATE,
                    required=True,
                    order=1
                )
            ]
        )
        
        created_report = ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-08-06"}
        )
        
        # Delete the report
        success = ReportService.delete_report(created_report.id)
        assert success is True
        
        # Verify it's deleted
        deleted_report = ReportService.get_report(report_id=created_report.id)
        assert deleted_report is None

    def test_list_reports(self):
        """Test listing reports."""
        # Create a template
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="date",
                    label="Date",
                    field_type=FieldType.DATE,
                    required=True,
                    order=1
                ),
                TemplateField(
                    name="project",
                    label="Project",
                    field_type=FieldType.TEXT,
                    required=False,
                    order=2
                )
            ]
        )
        
        # Create multiple reports
        ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-08-06", "project": "Project A"}
        )
        ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-08-07", "project": "Project B"}
        )
        
        # List all reports
        reports = ReportService.list_reports()
        assert len(reports) >= 2
        
        # List reports by date range
        reports_in_range = ReportService.list_reports(
            start_date=date(2025, 8, 6),
            end_date=date(2025, 8, 6)
        )
        assert len(reports_in_range) == 1
        assert reports_in_range[0].get_date() == "2025-08-06"

    def test_search_reports(self):
        """Test searching reports by keyword."""
        # Create a template
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="content",
                    label="Content",
                    field_type=FieldType.MEMO,
                    required=True,
                    order=1
                )
            ]
        )
        
        # Create reports with different content
        ReportService.create_report(
            template_id=template.id,
            data={"content": "Python development work"}
        )
        ReportService.create_report(
            template_id=template.id,
            data={"content": "React frontend implementation"}
        )
        
        # Search for specific keyword
        python_reports = ReportService.search_reports("Python")
        assert len(python_reports) >= 1
        assert "Python" in python_reports[0].get_field_value("content")

    def test_get_monthly_reports(self):
        """Test getting monthly reports."""
        # Create a template
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="date",
                    label="Date",
                    field_type=FieldType.DATE,
                    required=True,
                    order=1
                )
            ]
        )
        
        # Create reports for August 2025
        ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-08-01"}
        )
        ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-08-15"}
        )
        # Create a report for different month
        ReportService.create_report(
            template_id=template.id,
            data={"date": "2025-07-30"}
        )
        
        # Get monthly reports
        august_reports = ReportService.get_monthly_reports(2025, 8)
        august_dates = [report.get_date() for report in august_reports]
        
        assert "2025-08-01" in august_dates
        assert "2025-08-15" in august_dates
        assert "2025-07-30" not in august_dates

    def test_get_statistics(self):
        """Test getting report statistics."""
        # Create a template
        template = TemplateService.create_template(
            name="Test Template",
            description="Test template",
            fields=[
                TemplateField(
                    name="project",
                    label="Project",
                    field_type=FieldType.TEXT,
                    required=False,
                    order=1
                )
            ]
        )
        
        # Create multiple reports
        ReportService.create_report(
            template_id=template.id,
            data={"project": "Project A"}
        )
        ReportService.create_report(
            template_id=template.id,
            data={"project": "Project A"}
        )
        ReportService.create_report(
            template_id=template.id,
            data={"project": "Project B"}
        )
        
        # Get statistics
        stats = ReportService.get_statistics()
        
        assert stats["total_reports"] >= 3
        assert "Test Template" in stats["templates_used"]
        assert stats["projects"]["Project A"] >= 2
        assert stats["projects"]["Project B"] >= 1

    def test_invalid_template_id(self):
        """Test creating a report with invalid template ID."""
        with pytest.raises(ValueError, match="テンプレートID .* が見つかりません"):
            ReportService.create_report(
                template_id=999,
                data={"date": "2025-08-06"}
            )

    def test_update_nonexistent_report(self):
        """Test updating a nonexistent report."""
        with pytest.raises(ValueError, match="日報ID .* が見つかりません"):
            ReportService.update_report(
                report_id=999,
                data={"content": "New content"}
            )

    def test_delete_nonexistent_report(self):
        """Test deleting a nonexistent report."""
        success = ReportService.delete_report(999)
        assert success is False