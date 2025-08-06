"""Report management service."""

from datetime import datetime, date, timedelta
from typing import Any

from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Session

from ..database import ReportDB, TemplateDB, get_session
from ..models import Report, Template
from .template_service import TemplateService


class ReportService:
    """日報管理サービス."""
    
    @staticmethod
    def create_report(
        template_id: int,
        data: dict[str, Any],
        report_date: date | None = None,
    ) -> Report:
        """
        日報を作成.
        
        Args:
            template_id: 使用するテンプレートのID
            data: 日報データ
            report_date: 日報の日付（省略時は今日）
            
        Returns:
            作成された日報
            
        Raises:
            ValueError: テンプレートが見つからない場合
        """
        with get_session() as session:
            # テンプレートの存在確認
            template_db = session.query(TemplateDB).filter_by(id=template_id).first()
            if not template_db:
                raise ValueError(f"テンプレートID {template_id} が見つかりません")
            
            # 日報の日付を決定
            if report_date is None:
                # データから日付を取得を試行
                if "date" in data and data["date"]:
                    try:
                        report_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        report_date = date.today()
                else:
                    report_date = date.today()
            
            # 同じ日付の日報が既に存在するかチェック
            date_str = report_date.strftime("%Y-%m-%d")
            existing_report = session.query(ReportDB).filter(
                and_(
                    ReportDB.template_id == template_id,
                    ReportDB.data_json.op("->>")("date") == date_str
                )
            ).first()
            
            if existing_report:
                raise ValueError(f"{report_date.strftime('%Y-%m-%d')} の日報は既に存在します")
            
            # 日報を作成
            report_db = ReportDB(
                template_id=template_id,
                data=data,
            )
            session.add(report_db)
            session.commit()
            
            # Pydanticモデルに変換して返す
            return ReportService._db_to_model(report_db, template_db)
    
    @staticmethod
    def get_report(
        report_id: int | None = None,
        report_date: date | None = None,
        template_id: int | None = None,
    ) -> Report | None:
        """
        日報を取得.
        
        Args:
            report_id: 日報ID
            report_date: 日報の日付
            template_id: テンプレートID（日付指定時に使用）
            
        Returns:
            日報（見つからない場合はNone）
        """
        with get_session() as session:
            query = session.query(ReportDB).join(TemplateDB)
            
            if report_id is not None:
                report_db = query.filter(ReportDB.id == report_id).first()
            elif report_date is not None:
                date_str = report_date.strftime("%Y-%m-%d")
                if template_id is not None:
                    report_db = query.filter(
                        and_(
                            ReportDB.template_id == template_id,
                            ReportDB.data_json.op("->>")("date") == date_str
                        )
                    ).first()
                else:
                    # テンプレート指定がない場合は該当日の日報を検索
                    reports = query.filter(ReportDB.data_json.op("->>")("date") == date_str).all()
                    if len(reports) == 1:
                        report_db = reports[0]
                    elif len(reports) > 1:
                        # 複数ある場合はデフォルトテンプレートを優先
                        for r in reports:
                            if r.template.is_default:
                                report_db = r
                                break
                        else:
                            report_db = reports[0]  # デフォルトがない場合は最初の1つ
                    else:
                        report_db = None
            else:
                return None
            
            if report_db:
                return ReportService._db_to_model(report_db, report_db.template)
            return None
    
    @staticmethod
    def update_report(
        report_id: int,
        data: dict[str, Any] | None = None,
    ) -> Report:
        """
        日報を更新.
        
        Args:
            report_id: 日報ID
            data: 新しい日報データ
            
        Returns:
            更新された日報
            
        Raises:
            ValueError: 日報が見つからない場合
        """
        with get_session() as session:
            report_db = session.query(ReportDB).filter_by(id=report_id).first()
            if not report_db:
                raise ValueError(f"日報ID {report_id} が見つかりません")
            
            # データの更新
            if data is not None:
                report_db.data = data
                report_db.updated_at = datetime.now()
            
            session.commit()
            return ReportService._db_to_model(report_db, report_db.template)
    
    @staticmethod
    def delete_report(report_id: int) -> bool:
        """
        日報を削除.
        
        Args:
            report_id: 日報ID
            
        Returns:
            削除に成功した場合True
        """
        with get_session() as session:
            report_db = session.query(ReportDB).filter_by(id=report_id).first()
            if not report_db:
                return False
            
            session.delete(report_db)
            session.commit()
            return True
    
    @staticmethod
    def list_reports(
        start_date: date | None = None,
        end_date: date | None = None,
        template_id: int | None = None,
        project_name: str | None = None,
        keyword: str | None = None,
        limit: int | None = None,
        order_by: str = "date_desc",
    ) -> list[Report]:
        """
        日報一覧を取得.
        
        Args:
            start_date: 開始日（含む）
            end_date: 終了日（含む）
            template_id: テンプレートID
            project_name: プロジェクト名での絞り込み
            keyword: キーワード検索
            limit: 取得件数制限
            order_by: ソート順 ("date_asc", "date_desc", "created_asc", "created_desc")
            
        Returns:
            日報リスト
        """
        with get_session() as session:
            query = session.query(ReportDB).join(TemplateDB)
            
            # 日付範囲フィルタ
            if start_date:
                start_str = start_date.strftime("%Y-%m-%d")
                query = query.filter(ReportDB.data_json.op("->>")("date") >= start_str)
            
            if end_date:
                end_str = end_date.strftime("%Y-%m-%d")
                query = query.filter(ReportDB.data_json.op("->>")("date") <= end_str)
            
            # テンプレートフィルタ
            if template_id:
                query = query.filter(ReportDB.template_id == template_id)
            
            # プロジェクト名フィルタ
            if project_name:
                query = query.filter(
                    ReportDB.data_json.op("->>")("project").ilike(f"%{project_name}%")
                )
            
            # キーワード検索
            if keyword:
                # データ内のテキストを検索
                search_conditions = []
                for key in ["content", "issues", "tomorrow_plan", "notes"]:
                    search_conditions.append(
                        ReportDB.data_json.op("->>")(key).ilike(f"%{keyword}%")
                    )
                query = query.filter(or_(*search_conditions))
            
            # ソート
            if order_by == "date_asc":
                query = query.order_by(asc(ReportDB.data_json.op("->>")("date")))
            elif order_by == "date_desc":
                query = query.order_by(desc(ReportDB.data_json.op("->>")("date")))
            elif order_by == "created_asc":
                query = query.order_by(asc(ReportDB.created_at))
            elif order_by == "created_desc":
                query = query.order_by(desc(ReportDB.created_at))
            
            # 件数制限
            if limit:
                query = query.limit(limit)
            
            reports_db = query.all()
            return [
                ReportService._db_to_model(report_db, report_db.template)
                for report_db in reports_db
            ]
    
    @staticmethod
    def get_report_by_date_range(
        start_date: date,
        end_date: date,
        template_id: int | None = None,
    ) -> list[Report]:
        """
        日付範囲で日報を取得.
        
        Args:
            start_date: 開始日
            end_date: 終了日
            template_id: テンプレートID（省略可）
            
        Returns:
            日報リスト（日付順）
        """
        return ReportService.list_reports(
            start_date=start_date,
            end_date=end_date,
            template_id=template_id,
            order_by="date_asc"
        )
    
    @staticmethod
    def search_reports(keyword: str, limit: int = 50) -> list[Report]:
        """
        日報をキーワード検索.
        
        Args:
            keyword: 検索キーワード
            limit: 取得件数制限
            
        Returns:
            検索結果の日報リスト（更新日時順）
        """
        return ReportService.list_reports(
            keyword=keyword,
            limit=limit,
            order_by="created_desc"
        )
    
    @staticmethod
    def _db_to_model(report_db: ReportDB, template_db: TemplateDB) -> Report:
        """データベースモデルをPydanticモデルに変換."""
        # テンプレートを変換
        template = TemplateService._db_to_model(template_db)
        
        return Report(
            id=report_db.id,
            template_id=report_db.template_id,
            template=template,
            data=report_db.data,
            created_at=report_db.created_at,
            updated_at=report_db.updated_at,
        )
    
    @staticmethod
    def validate_report_data(template: Template, data: dict[str, Any]) -> list[str]:
        """
        日報データを検証.
        
        Args:
            template: テンプレート定義
            data: 検証する日報データ
            
        Returns:
            エラーメッセージのリスト（エラーがない場合は空リスト）
        """
        from ..validators import validate_report_data
        return validate_report_data(template, data)
    
    @staticmethod
    def get_monthly_reports(year: int, month: int) -> list[Report]:
        """
        月次日報を取得.
        
        Args:
            year: 年
            month: 月
            
        Returns:
            該当月の日報リスト
        """
        # 月の最初と最後の日を計算
        start_date = date(year, month, 1)
        
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        return ReportService.get_report_by_date_range(start_date, end_date)
    
    @staticmethod
    def get_statistics(
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, Any]:
        """
        日報統計を取得.
        
        Args:
            start_date: 開始日
            end_date: 終了日
            
        Returns:
            統計情報辞書
        """
        reports = ReportService.list_reports(
            start_date=start_date,
            end_date=end_date
        )
        
        if not reports:
            return {
                "total_reports": 0,
                "date_range": {
                    "start": start_date,
                    "end": end_date,
                },
                "templates_used": {},
                "projects": {},
            }
        
        # 基本統計
        templates_used = {}
        projects = {}
        
        for report in reports:
            # テンプレート使用統計
            template_name = report.template.name
            templates_used[template_name] = templates_used.get(template_name, 0) + 1
            
            # プロジェクト統計
            project_name = report.get_project_name() or "未分類"
            projects[project_name] = projects.get(project_name, 0) + 1
        
        return {
            "total_reports": len(reports),
            "date_range": {
                "start": start_date,
                "end": end_date,
            },
            "templates_used": templates_used,
            "projects": projects,
        }