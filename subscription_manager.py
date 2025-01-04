
from datetime import datetime, timedelta
from models import User, db
import logging

logger = logging.getLogger(__name__)

def check_overdue_subscriptions():
    """Verifica y actualiza suscripciones vencidas"""
    try:
        overdue_users = User.query.filter(
            User.plan_type == 'Premium',
            User.subscription_status == 'active',
            User.subscription_start <= datetime.utcnow() - timedelta(days=60)
        ).all()
        
        for user in overdue_users:
            user.plan_type = 'Free'
            user.subscription_status = 'inactive'
            user.nevin_access = False
            logger.info(f"Downgrading user {user.id} to free plan")
            
        db.session.commit()
    except Exception as e:
        logger.error(f"Error checking overdue subscriptions: {str(e)}")
