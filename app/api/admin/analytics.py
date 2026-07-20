"""
Admin Analytics API
Endpoints for analytics and reporting
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models import AdminUser
from app.api.dependencies import get_current_admin
from app.services.analytics_service import AnalyticsService

router = APIRouter()


class OverviewMetrics(BaseModel):
    """Overview metrics response"""
    total_leads: int
    status_breakdown: Dict[str, int]
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    delivery_success_rate: float
    active_clients: int
    total_credits_used: float
    stored_leads_count: int
    pending_batches: int


class TimeSeriesDataPoint(BaseModel):
    """Time series data point"""
    date: str
    leads_count: int


class ClientPerformance(BaseModel):
    """Client performance metrics"""
    client_id: str
    client_name: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float
    credits_used: float
    credits_balance: float


class DeliveryMethodStats(BaseModel):
    """Delivery method statistics"""
    delivery_method: str
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float


class LeadSourceStats(BaseModel):
    """Lead source statistics"""
    source_type: str
    source_name: str
    source_slug: str
    leads_count: int


class ConversionFunnel(BaseModel):
    """Conversion funnel metrics"""
    total_leads: int
    assigned_leads: int
    delivered_leads: int
    failed_leads: int
    stored_leads: int
    assignment_rate: float
    delivery_rate: float


class HourlyDistribution(BaseModel):
    """Hourly distribution data"""
    hour: int
    leads_count: int


class RevenueMetrics(BaseModel):
    """Revenue metrics"""
    total_credits_used: float
    total_credits_available: float
    credits_by_client: List[Dict[str, Any]]


@router.get("/overview", response_model=OverviewMetrics)
def get_overview_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get overview metrics
    
    Returns high-level metrics including:
    - Total leads and status breakdown
    - Delivery statistics
    - Active clients
    - Credits usage
    - Stored leads and pending batches
    """
    metrics = AnalyticsService.get_overview_metrics(db, start_date, end_date)
    return OverviewMetrics(**metrics)


@router.get("/time-series", response_model=List[TimeSeriesDataPoint])
def get_time_series_data(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    granularity: str = Query("day", regex="^(day|hour)$", description="Time granularity"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get time series data for leads
    
    Returns daily or hourly lead counts for the specified period
    """
    data = AnalyticsService.get_time_series_data(db, days, granularity)
    return data


@router.get("/client-performance", response_model=List[ClientPerformance])
def get_client_performance(
    limit: int = Query(10, ge=1, le=100, description="Number of top clients to return"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get client performance metrics
    
    Returns performance data for top clients including:
    - Total and successful deliveries
    - Success rate
    - Credits used and balance
    """
    performance = AnalyticsService.get_client_performance(db, limit)
    return performance


@router.get("/delivery-methods", response_model=List[DeliveryMethodStats])
def get_delivery_method_stats(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get delivery method statistics
    
    Returns statistics for each delivery method (webhook, email, etc.)
    """
    stats = AnalyticsService.get_delivery_method_stats(db)
    return stats


@router.get("/lead-sources", response_model=List[LeadSourceStats])
def get_lead_source_stats(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get lead source statistics
    
    Returns statistics by landing page and campaign
    """
    stats = AnalyticsService.get_lead_source_stats(db)
    return stats


@router.get("/conversion-funnel", response_model=ConversionFunnel)
def get_conversion_funnel(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get conversion funnel metrics

    Returns funnel data showing lead progression through the system
    """
    funnel = AnalyticsService.get_conversion_funnel(db)
    return ConversionFunnel(**funnel)


@router.get("/hourly-distribution", response_model=List[HourlyDistribution])
def get_hourly_distribution(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get hourly distribution of leads

    Returns lead counts by hour of day
    """
    distribution = AnalyticsService.get_hourly_distribution(db, days)
    return distribution


@router.get("/revenue", response_model=RevenueMetrics)
def get_revenue_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get revenue metrics (credits)

    Returns credit usage and availability data
    """
    metrics = AnalyticsService.get_revenue_metrics(db, start_date, end_date)
    return RevenueMetrics(**metrics)

