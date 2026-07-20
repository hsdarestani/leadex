"""
Analytics Service
Provides comprehensive analytics and reporting functionality
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.models import Asset, Delivery, Client, Campaign, LandingPage, BatchQueue, StoredLead


class AnalyticsService:
    """Service for analytics calculations and aggregations"""
    
    @staticmethod
    def get_overview_metrics(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """
        Get high-level overview metrics
        
        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with overview metrics
        """
        # Build date filter
        date_filter = []
        if start_date:
            date_filter.append(Asset.created_at >= start_date)
        if end_date:
            date_filter.append(Asset.created_at <= end_date)
        
        # Total leads
        total_leads_query = db.query(func.count(Asset.id))
        if date_filter:
            total_leads_query = total_leads_query.filter(and_(*date_filter))
        total_leads = total_leads_query.scalar() or 0
        
        # Leads by status
        status_counts = db.query(
            Asset.status,
            func.count(Asset.id)
        ).group_by(Asset.status).all()
        
        status_breakdown = {status: count for status, count in status_counts}
        
        # Delivery success rate
        total_deliveries = db.query(func.count(Delivery.id)).scalar() or 0
        successful_deliveries = db.query(func.count(Delivery.id)).filter(
            Delivery.success == True
        ).scalar() or 0
        
        delivery_success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Active clients
        active_clients = db.query(func.count(Client.id)).filter(
            Client.status == "active"
        ).scalar() or 0
        
        # Total credits distributed
        total_credits_used = db.query(func.sum(Delivery.credit_charged)).scalar() or 0
        
        # Stored leads (waiting for credits)
        stored_leads_count = db.query(func.count(StoredLead.id)).scalar() or 0
        
        # Pending batches
        pending_batches = db.query(func.count(BatchQueue.id)).scalar() or 0
        
        return {
            "total_leads": total_leads,
            "status_breakdown": status_breakdown,
            "total_deliveries": total_deliveries,
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": total_deliveries - successful_deliveries,
            "delivery_success_rate": round(delivery_success_rate, 2),
            "active_clients": active_clients,
            "total_credits_used": float(total_credits_used),
            "stored_leads_count": stored_leads_count,
            "pending_batches": pending_batches
        }
    
    @staticmethod
    def get_time_series_data(db: Session, days: int = 30, granularity: str = "day") -> List[Dict]:
        """
        Get time series data for leads and deliveries
        
        Args:
            db: Database session
            days: Number of days to look back
            granularity: Time granularity (day, hour)
            
        Returns:
            List of time series data points
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        if granularity == "day":
            # Group by day
            time_series = db.query(
                func.date(Asset.created_at).label('date'),
                func.count(Asset.id).label('leads_count')
            ).filter(
                Asset.created_at >= start_date
            ).group_by(
                func.date(Asset.created_at)
            ).order_by('date').all()
            
            return [
                {
                    "date": str(date),
                    "leads_count": count
                }
                for date, count in time_series
            ]
        
        return []
    
    @staticmethod
    def get_client_performance(db: Session, limit: int = 10) -> List[Dict]:
        """
        Get client performance metrics
        
        Args:
            db: Database session
            limit: Number of top clients to return
            
        Returns:
            List of client performance data
        """
        client_stats = db.query(
            Client.id,
            Client.name,
            func.count(Delivery.id).label('total_deliveries'),
            func.sum(case((Delivery.success == True, 1), else_=0)).label('successful_deliveries'),
            func.sum(Delivery.credit_charged).label('credits_used'),
            Client.credits_balance
        ).join(
            Delivery, Client.id == Delivery.client_id
        ).group_by(
            Client.id, Client.name, Client.credits_balance
        ).order_by(
            func.count(Delivery.id).desc()
        ).limit(limit).all()
        
        results = []
        for client_id, name, total, successful, credits_used, credits_balance in client_stats:
            success_rate = (successful / total * 100) if total > 0 else 0
            results.append({
                "client_id": str(client_id),
                "client_name": name,
                "total_deliveries": total,
                "successful_deliveries": successful,
                "failed_deliveries": total - successful,
                "success_rate": round(success_rate, 2),
                "credits_used": float(credits_used or 0),
                "credits_balance": float(credits_balance)
            })
        
        return results

    @staticmethod
    def get_delivery_method_stats(db: Session) -> List[Dict]:
        """
        Get statistics by delivery method

        Args:
            db: Database session

        Returns:
            List of delivery method statistics
        """
        method_stats = db.query(
            Delivery.delivery_method,
            func.count(Delivery.id).label('total'),
            func.sum(case((Delivery.success == True, 1), else_=0)).label('successful'),
            func.sum(case((Delivery.success == False, 1), else_=0)).label('failed')
        ).group_by(
            Delivery.delivery_method
        ).all()

        results = []
        for method, total, successful, failed in method_stats:
            success_rate = (successful / total * 100) if total > 0 else 0
            results.append({
                "delivery_method": method,
                "total_deliveries": total,
                "successful_deliveries": successful,
                "failed_deliveries": failed,
                "success_rate": round(success_rate, 2)
            })

        return results

    @staticmethod
    def get_lead_source_stats(db: Session) -> List[Dict]:
        """
        Get statistics by lead source (landing page/campaign)

        Args:
            db: Database session

        Returns:
            List of lead source statistics
        """
        # Stats by landing page
        landing_stats = db.query(
            LandingPage.name,
            LandingPage.slug,
            func.count(Asset.id).label('leads_count')
        ).join(
            Asset, LandingPage.id == Asset.landing_id
        ).group_by(
            LandingPage.id, LandingPage.name, LandingPage.slug
        ).all()

        results = []
        for name, slug, count in landing_stats:
            results.append({
                "source_type": "landing_page",
                "source_name": name,
                "source_slug": slug,
                "leads_count": count
            })

        return results

    @staticmethod
    def get_conversion_funnel(db: Session) -> Dict:
        """
        Get conversion funnel metrics

        Args:
            db: Database session

        Returns:
            Dictionary with funnel metrics
        """
        # Total leads captured
        total_leads = db.query(func.count(Asset.id)).scalar() or 0

        # Leads assigned (ASSIGNED status)
        assigned_leads = db.query(func.count(Asset.id)).filter(
            Asset.status.in_(["ASSIGNED", "DELIVERED"])
        ).scalar() or 0

        # Leads delivered successfully
        delivered_leads = db.query(func.count(Asset.id)).filter(
            Asset.status == "DELIVERED"
        ).scalar() or 0

        # Leads failed
        failed_leads = db.query(func.count(Asset.id)).filter(
            Asset.status == "FAILED"
        ).scalar() or 0

        # Leads stored (waiting for credits)
        stored_leads = db.query(func.count(StoredLead.id)).scalar() or 0

        # Calculate conversion rates
        assignment_rate = (assigned_leads / total_leads * 100) if total_leads > 0 else 0
        delivery_rate = (delivered_leads / total_leads * 100) if total_leads > 0 else 0

        return {
            "total_leads": total_leads,
            "assigned_leads": assigned_leads,
            "delivered_leads": delivered_leads,
            "failed_leads": failed_leads,
            "stored_leads": stored_leads,
            "assignment_rate": round(assignment_rate, 2),
            "delivery_rate": round(delivery_rate, 2)
        }

    @staticmethod
    def get_hourly_distribution(db: Session, days: int = 7) -> List[Dict]:
        """
        Get hourly distribution of leads

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            List of hourly distribution data
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        hourly_data = db.query(
            extract('hour', Asset.created_at).label('hour'),
            func.count(Asset.id).label('leads_count')
        ).filter(
            Asset.created_at >= start_date
        ).group_by(
            extract('hour', Asset.created_at)
        ).order_by('hour').all()

        return [
            {
                "hour": int(hour),
                "leads_count": count
            }
            for hour, count in hourly_data
        ]

    @staticmethod
    def get_geo_distribution(db: Session, limit: int = 10) -> List[Dict]:
        """
        Get geographic distribution of leads

        Args:
            db: Database session
            limit: Number of top locations to return

        Returns:
            List of geographic distribution data
        """
        # This requires parsing the geo JSON field
        # For now, return a placeholder
        # In production, you'd parse the geo field and aggregate by country/city

        return []

    @staticmethod
    def get_revenue_metrics(db: Session, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """
        Get revenue-related metrics (credits)

        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary with revenue metrics
        """
        # Build date filter
        date_filter = []
        if start_date:
            date_filter.append(Delivery.timestamp >= start_date)
        if end_date:
            date_filter.append(Delivery.timestamp <= end_date)

        # Total credits used
        credits_query = db.query(func.sum(Delivery.credit_charged))
        if date_filter:
            credits_query = credits_query.filter(and_(*date_filter))
        total_credits_used = credits_query.scalar() or 0

        # Total credits available (sum of all client balances)
        total_credits_available = db.query(func.sum(Client.credits_balance)).scalar() or 0

        # Credits by client
        client_credits = db.query(
            Client.name,
            func.sum(Delivery.credit_charged).label('credits_used')
        ).join(
            Delivery, Client.id == Delivery.client_id
        ).group_by(
            Client.name
        ).all()

        credits_by_client = [
            {
                "client_name": name,
                "credits_used": float(credits or 0)
            }
            for name, credits in client_credits
        ]

        return {
            "total_credits_used": float(total_credits_used),
            "total_credits_available": float(total_credits_available),
            "credits_by_client": credits_by_client
        }

