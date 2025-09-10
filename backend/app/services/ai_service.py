import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.merchant import Merchant
from app.core.config import settings
import joblib
import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AIRecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Corrected path: now relative to the backend directory
        self.models_path = "backend/app/ml_models" 
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Ensure models directory exists
        os.makedirs(self.models_path, exist_ok=True)

    async def analyze_customer_behavior(self, customer_id: int) -> Dict[str, Any]:
        """Comprehensive customer behavior analysis"""
        customer = await self._get_customer_with_transactions(customer_id)
        if not customer:
            return {"error": "Customer not found"}
        
        transactions = customer.transactions
        if not transactions:
            return {"error": "No transaction history"}
        
        # Calculate behavioral metrics
        behavior_metrics = await self._calculate_behavior_metrics(transactions)
        
        # Predict churn risk
        churn_risk = await self.predict_churn_risk(customer_id)
        
        # Predict next purchase
        next_purchase = await self.predict_next_purchase(customer_id)
        
        # Generate personalized recommendations
        recommendations = await self.generate_personalized_offers(customer_id)
        
        return {
            "customer_id": customer_id,
            "behavior_metrics": behavior_metrics,
            "churn_risk": churn_risk,
            "next_purchase_prediction": next_purchase,
            "personalized_offers": recommendations,
            "analysis_date": datetime.utcnow().isoformat()
        }

    async def _get_customer_with_transactions(self, customer_id: int) -> Optional[Customer]:
        """Get customer with transaction history"""
        from sqlalchemy.orm import selectinload
        
        result = await self.db.execute(
            select(Customer)
            .options(selectinload(Customer.transactions))
            .where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def _calculate_behavior_metrics(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate detailed customer behavior metrics"""
        if not transactions:
            return {}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([{
            'amount': t.amount,
            'date': t.transaction_date,
            'day_of_week': t.transaction_date.weekday(),
            'hour': t.transaction_date.hour,
            'month': t.transaction_date.month
        } for t in transactions])
        
        # Time-based patterns
        purchase_intervals = df['date'].diff().dt.days.dropna()
        
        # Spending patterns
        spending_trend = self._calculate_spending_trend(df)
        
        # Frequency patterns
        frequency_pattern = self._analyze_frequency_patterns(df)
        
        # Seasonal patterns
        seasonal_pattern = self._analyze_seasonal_patterns(df)
        
        return {
            "total_transactions": len(transactions),
            "average_amount": float(df['amount'].mean()),
            "spending_volatility": float(df['amount'].std()),
            "average_days_between_purchases": float(purchase_intervals.mean()) if len(purchase_intervals) > 0 else None,
            "purchase_frequency_trend": spending_trend,
            "preferred_days": frequency_pattern["preferred_days"],
            "preferred_hours": frequency_pattern["preferred_hours"],
            "seasonal_preferences": seasonal_pattern,
            "spending_acceleration": self._calculate_spending_acceleration(df),
            "loyalty_score": self._calculate_loyalty_score(df)
        }

    def _calculate_spending_trend(self, df: pd.DataFrame) -> str:
        """Calculate if customer spending is increasing, decreasing, or stable"""
        if len(df) < 3:
            return "insufficient_data"
        
        # Calculate trend using linear regression on recent transactions
        recent_transactions = df.tail(10)  # Last 10 transactions
        x = np.arange(len(recent_transactions))
        y = recent_transactions['amount'].values
        
        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 5:  # Threshold for increasing trend
            return "increasing"
        elif slope < -5:  # Threshold for decreasing trend
            return "decreasing"
        else:
            return "stable"

    def _analyze_frequency_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze when customer prefers to make purchases"""
        day_counts = df['day_of_week'].value_counts()
        hour_counts = df['hour'].value_counts()
        
        # Convert day numbers to names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        preferred_days = [day_names[day] for day in day_counts.head(2).index]
        
        return {
            "preferred_days": preferred_days,
            "preferred_hours": hour_counts.head(2).index.tolist()
        }

    def _analyze_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze seasonal spending patterns"""
        monthly_spending = df.groupby('month')['amount'].agg(['mean', 'count'])
        
        # Find peak spending months
        peak_months = monthly_spending['mean'].nlargest(2).index.tolist()
        
        return {
            "peak_spending_months": peak_months,
            "seasonal_variance": float(monthly_spending['mean'].std())
        }

    def _calculate_spending_acceleration(self, df: pd.DataFrame) -> float:
        """Calculate if customer is accelerating or decelerating spending"""
        if len(df) < 6:
            return 0.0
        
        # Compare recent vs older spending
        recent_avg = df.tail(3)['amount'].mean()
        older_avg = df.head(3)['amount'].mean()
        
        if older_avg == 0:
            return 0.0
        
        return float((recent_avg - older_avg) / older_avg)

    def _calculate_loyalty_score(self, df: pd.DataFrame) -> float:
        """Calculate customer loyalty score based on consistency"""
        if len(df) < 2:
            return 0.0
        
        # Factors: frequency, consistency, recency
        frequency_score = min(len(df) / 10, 1.0)  # Max score at 10+ transactions
        
        # Consistency score based on purchase intervals
        intervals = df['date'].diff().dt.days.dropna()
        if len(intervals) > 0:
            consistency_score = 1.0 / (1.0 + intervals.std() / intervals.mean())
        else:
            consistency_score = 0.0
        
        # Recency score
        days_since_last = (datetime.utcnow() - df['date'].max()).days
        recency_score = max(0, 1.0 - days_since_last / 90)  # Decay over 90 days
        
        return float((frequency_score + consistency_score + recency_score) / 3)

    async def predict_churn_risk(self, customer_id: int) -> Dict[str, Any]:
        """Predict customer churn risk using ML model"""
        try:
            # Get customer features
            features = await self._extract_customer_features(customer_id)
            if not features:
                return {"error": "Insufficient data for prediction"}
            
            # Load or train churn model
            model = await self._get_or_train_churn_model()
            
            # Make prediction
            risk_score = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._predict_churn_score, model, features
            )
            
            # Update customer record
            await self._update_customer_churn_score(customer_id, risk_score)
            
            return {
                "churn_risk_score": risk_score,
                "risk_level": self._categorize_risk(risk_score),
                "recommendation": self._get_churn_recommendation(risk_score)
            }
            
        except Exception as e:
            logger.error(f"Churn prediction error for customer {customer_id}: {str(e)}")
            return {"error": "Prediction failed"}

    def _predict_churn_score(self, model, features: np.ndarray) -> float:
        """Predict churn score using trained model"""
        if hasattr(model, 'predict_proba'):
            # For classification models, return probability of churn
            return float(model.predict_proba(features.reshape(1, -1))[0][1])
        else:
            # For regression models, return direct prediction
            return float(max(0, min(1, model.predict(features.reshape(1, -1))[0])))

    async def _extract_customer_features(self, customer_id: int) -> Optional[np.ndarray]:
        """Extract features for ML models"""
        # Get customer and transaction data
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
        
        # Get transaction statistics
        transaction_stats = await self.db.execute(
            select(
                func.count(Transaction.id).label('transaction_count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.sum(Transaction.amount).label('total_spent'),
                func.max(Transaction.transaction_date).label('last_transaction'),
                func.min(Transaction.transaction_date).label('first_transaction')
            ).where(Transaction.customer_id == customer_id)
        )
        stats = transaction_stats.first()
        
        if not stats or stats.transaction_count == 0:
            return None
        
        # Calculate features
        days_since_last = (datetime.utcnow() - stats.last_transaction).days if stats.last_transaction else 999
        customer_lifetime_days = (stats.last_transaction - stats.first_transaction).days if stats.first_transaction and stats.last_transaction else 1
        
        features = np.array([
            stats.transaction_count or 0,
            float(stats.avg_amount or 0),
            float(stats.total_spent or 0),
            days_since_last,
            customer_lifetime_days,
            customer.loyalty_points,
            customer.churn_risk_score,  # Previous score as feature
            1 if customer.customer_segment == "vip" else 0,
            1 if customer.customer_segment == "regular" else 0,
            1 if customer.customer_segment == "at_risk" else 0
        ])
        
        return features

    async def _get_or_train_churn_model(self):
        """Get existing churn model or train a new one"""
        model_path = os.path.join(self.models_path, "churn_model.joblib")
        
        if os.path.exists(model_path):
            try:
                return joblib.load(model_path)
            except Exception as e:
                logger.warning(f"Failed to load churn model: {str(e)}")
        
        # Train new model
        return await self._train_churn_model()

    async def _train_churn_model(self):
        """Train churn prediction model"""
        logger.info("Training new churn prediction model")
        
        # Get training data
        training_data = await self._get_churn_training_data()
        
        if len(training_data) < 50:  # Minimum data requirement
            logger.warning("Insufficient data for churn model training")
            # Return a simple rule-based model
            return self._create_rule_based_churn_model()
        
        X, y = training_data
        
        # Train model in executor to avoid blocking
        model = await asyncio.get_event_loop().run_in_executor(
            self.executor, self._train_churn_model_sync, X, y
        )
        
        # Save model
        model_path = os.path.join(self.models_path, "churn_model.joblib")
        joblib.dump(model, model_path)
        
        return model

    def _train_churn_model_sync(self, X: np.ndarray, y: np.ndarray):
        """Synchronous model training"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Churn model trained with accuracy: {accuracy:.3f}")
        
        # Return model with scaler
        return {"model": model, "scaler": scaler}

    async def _get_churn_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get training data for churn model"""
        # Get customers with sufficient history
        result = await self.db.execute(
            select(Customer).where(
                and_(
                    Customer.total_transactions >= 3,
                    Customer.first_purchase_date.isnot(None)
                )
            )
        )
        customers = result.scalars().all()
        
        features_list = []
        labels_list = []
        
        for customer in customers:
            features = await self._extract_customer_features(customer.id)
            if features is not None:
                features_list.append(features)
                
                # Label as churned if no purchase in 60+ days
                days_since_last = (datetime.utcnow() - customer.last_purchase_date).days if customer.last_purchase_date else 999
                is_churned = 1 if days_since_last > 60 else 0
                labels_list.append(is_churned)
        
        if not features_list:
            return np.array([]), np.array([])
        
        return np.array(features_list), np.array(labels_list)

    def _create_rule_based_churn_model(self):
        """Create simple rule-based churn model when insufficient data"""
        class RuleBasedChurnModel:
            def predict_proba(self, X):
                # Simple rule: high churn risk if days_since_last > 30
                days_since_last = X[:, 3]  # Feature index for days_since_last
                churn_probs = np.minimum(days_since_last / 60.0, 1.0)  # Max at 60 days
                return np.column_stack([1 - churn_probs, churn_probs])
        
        return {"model": RuleBasedChurnModel(), "scaler": None}

    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize churn risk score"""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _get_churn_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on churn risk"""
        if risk_score >= 0.7:
            return "Send immediate retention offer with high-value discount"
        elif risk_score >= 0.4:
            return "Engage with personalized offer or loyalty bonus"
        else:
            return "Continue regular engagement, customer is stable"

    async def _update_customer_churn_score(self, customer_id: int, risk_score: float):
        """Update customer's churn risk score"""
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        
        if customer:
            customer.churn_risk_score = risk_score
            await self.db.commit()

    async def predict_next_purchase(self, customer_id: int) -> Dict[str, Any]:
        """Predict when customer will make next purchase"""
        try:
            # Get customer transaction history
            result = await self.db.execute(
                select(Transaction)
                .where(Transaction.customer_id == customer_id)
                .order_by(Transaction.transaction_date.desc())
                .limit(10)
            )
            transactions = result.scalars().all()
            
            if len(transactions) < 2:
                return {"error": "Insufficient transaction history"}
            
            # Calculate purchase intervals
            intervals = []
            for i in range(1, len(transactions)):
                interval = (transactions[i-1].transaction_date - transactions[i].transaction_date).days
                intervals.append(interval)
            
            # Predict next purchase date
            avg_interval = np.mean(intervals)
            std_interval = np.std(intervals) if len(intervals) > 1 else avg_interval * 0.3
            
            # Use weighted average favoring recent intervals
            weights = np.exp(np.linspace(-1, 0, len(intervals)))
            weighted_avg = np.average(intervals, weights=weights)
            
            # Predict next purchase date
            last_purchase = transactions[0].transaction_date
            predicted_date = last_purchase + timedelta(days=int(weighted_avg))
            
            # Calculate confidence based on consistency
            confidence = max(0.1, 1.0 - (std_interval / avg_interval)) if avg_interval > 0 else 0.1
            
            return {
                "predicted_date": predicted_date.isoformat(),
                "confidence": float(confidence),
                "average_interval_days": float(avg_interval),
                "recommendation": self._get_timing_recommendation(predicted_date, confidence)
            }
            
        except Exception as e:
            logger.error(f"Next purchase prediction error for customer {customer_id}: {str(e)}")
            return {"error": "Prediction failed"}

    def _get_timing_recommendation(self, predicted_date: datetime, confidence: float) -> str:
        """Get recommendation for campaign timing"""
        days_until = (predicted_date - datetime.utcnow()).days
        
        if confidence > 0.7:
            if days_until <= 2:
                return "Send offer now - customer likely to purchase soon"
            elif days_until <= 7:
                return f"Send offer in {days_until-2} days for optimal timing"
            else:
                return f"Schedule offer for {days_until-3} days from now"
        else:
            return "Low confidence prediction - use general engagement strategy"

    async def generate_personalized_offers(self, customer_id: int) -> List[Dict[str, Any]]:
        """Generate personalized offers for customer"""
        try:
            # Get customer behavior analysis
            customer = await self._get_customer_with_transactions(customer_id)
            if not customer or not customer.transactions:
                return []
            
            offers = []
            
            # Analyze spending patterns
            transactions = customer.transactions
            avg_amount = np.mean([t.amount for t in transactions])
            recent_amount = np.mean([t.amount for t in transactions[-3:]]) if len(transactions) >= 3 else avg_amount
            
            # Offer 1: Spend-based discount
            if recent_amount < avg_amount * 0.8:  # Recent spending is down
                offers.append({
                    "type": "discount",
                    "title": "Welcome Back Offer",
                    "description": f"Get 15% off your next purchase of {avg_amount:.0f} or more",
                    "discount_percentage": 15,
                    "minimum_spend": avg_amount,
                    "reasoning": "Customer's recent spending is below average"
                })
            
            # Offer 2: Frequency-based reward
            if len(transactions) >= 5:
                offers.append({
                    "type": "loyalty_bonus",
                    "title": "Loyalty Bonus Points",
                    "description": "Earn double points on your next 3 purchases",
                    "points_multiplier": 2.0,
                    "usage_limit": 3,
                    "reasoning": "Reward loyal customer with bonus points"
                })
            
            # Offer 3: Time-based offer
            last_purchase = max(t.transaction_date for t in transactions)
            days_since_last = (datetime.utcnow() - last_purchase).days
            
            if days_since_last > 14:  # Haven't purchased in 2+ weeks
                offers.append({
                    "type": "comeback",
                    "title": "We Miss You!",
                    "description": "Get 20% off your next purchase - no minimum spend",
                    "discount_percentage": 20,
                    "minimum_spend": 0,
                    "reasoning": "Re-engage customer who hasn't purchased recently"
                })
            
            # Offer 4: Tier-based offer
            if customer.loyalty_tier in ["gold", "platinum"]:
                offers.append({
                    "type": "vip_exclusive",
                    "title": f"{customer.loyalty_tier.title()} Member Exclusive",
                    "description": "Exclusive early access to new products + 10% off",
                    "discount_percentage": 10,
                    "reasoning": f"Exclusive offer for {customer.loyalty_tier} tier member"
                })
            
            return offers[:3]  # Return top 3 offers
            
        except Exception as e:
            logger.error(f"Offer generation error for customer {customer_id}: {str(e)}")
            return []

    async def get_optimal_campaign_timing(self, merchant_id: int) -> Dict[str, Any]:
        """Analyze optimal timing for campaigns"""
        try:
            # Get merchant's transaction data
            result = await self.db.execute(
                select(Transaction)
                .where(Transaction.merchant_id == merchant_id)
                .order_by(Transaction.transaction_date.desc())
                .limit(1000)  # Analyze recent transactions
            )
            transactions = result.scalars().all()
            
            if len(transactions) < 50:
                return {"error": "Insufficient transaction data"}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame([{
                'date': t.transaction_date,
                'amount': t.amount,
                'day_of_week': t.transaction_date.weekday(),
                'hour': t.transaction_date.hour,
                'day_of_month': t.transaction_date.day
            } for t in transactions])
            
            # Analyze patterns
            daily_patterns = df.groupby('day_of_week')['amount'].agg(['count', 'mean'])
            hourly_patterns = df.groupby('hour')['amount'].agg(['count', 'mean'])
            monthly_patterns = df.groupby('day_of_month')['amount'].agg(['count', 'mean'])
            
            # Find optimal times
            best_days = daily_patterns['count'].nlargest(3).index.tolist()
            best_hours = hourly_patterns['count'].nlargest(3).index.tolist()
            best_days_of_month = monthly_patterns['count'].nlargest(5).index.tolist()
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            return {
                "optimal_days": [day_names[day] for day in best_days],
                "optimal_hours": best_hours,
                "optimal_days_of_month": best_days_of_month,
                "peak_transaction_day": day_names[daily_patterns['count'].idxmax()],
                "peak_revenue_day": day_names[daily_patterns['mean'].idxmax()],
                "recommendations": {
                    "best_campaign_day": day_names[best_days[0]],
                    "best_campaign_time": f"{best_hours[0]:02d}:00",
                    "avoid_days": [day_names[day] for day in daily_patterns['count'].nsmallest(2).index]
                }
            }
            
        except Exception as e:
            logger.error(f"Campaign timing analysis error for merchant {merchant_id}: {str(e)}")
            return {"error": "Analysis failed"}

    async def predict_customer_lifetime_value(self, customer_id: int) -> Dict[str, Any]:
        """Predict customer lifetime value"""
        try:
            customer = await self._get_customer_with_transactions(customer_id)
            if not customer or len(customer.transactions) < 3:
                return {"error": "Insufficient transaction history"}
            
            transactions = customer.transactions
            
            # Calculate historical CLV metrics
            total_spent = sum(t.amount for t in transactions)
            avg_order_value = total_spent / len(transactions)
            
            # Calculate purchase frequency (purchases per month)
            first_purchase = min(t.transaction_date for t in transactions)
            last_purchase = max(t.transaction_date for t in transactions)
            months_active = max(1, (last_purchase - first_purchase).days / 30.44)
            purchase_frequency = len(transactions) / months_active
            
            # Predict future behavior
            # Simple model: assume current patterns continue with some decay
            churn_risk = customer.churn_risk_score
            retention_probability = 1 - churn_risk
            
            # Predict CLV for next 12 months
            monthly_value = avg_order_value * purchase_frequency
            predicted_clv = monthly_value * 12 * retention_probability
            
            # Update customer record
            customer.lifetime_value_prediction = predicted_clv
            await self.db.commit()
            
            return {
                "customer_id": customer_id,
                "predicted_clv_12_months": float(predicted_clv),
                "current_total_spent": float(total_spent),
                "average_order_value": float(avg_order_value),
                "purchase_frequency_per_month": float(purchase_frequency),
                "retention_probability": float(retention_probability),
                "clv_category": self._categorize_clv(predicted_clv),
                "recommendations": self._get_clv_recommendations(predicted_clv)
            }
            
        except Exception as e:
            logger.error(f"CLV prediction error for customer {customer_id}: {str(e)}")
            return {"error": "Prediction failed"}

    def _categorize_clv(self, clv: float) -> str:
        """Categorize customer lifetime value"""
        if clv >= 5000:
            return "high_value"
        elif clv >= 2000:
            return "medium_value"
        elif clv >= 500:
            return "low_value"
        else:
            return "minimal_value"

    def _get_clv_recommendations(self, clv: float) -> List[str]:
        """Get recommendations based on CLV"""
        if clv >= 5000:
            return [
                "Prioritize retention with VIP treatment",
                "Offer premium services and exclusive access",
                "Assign dedicated account management"
            ]
        elif clv >= 2000:
            return [
                "Focus on upselling and cross-selling",
                "Provide excellent customer service",
                "Send personalized offers regularly"
            ]
        elif clv >= 500:
            return [
                "Encourage increased purchase frequency",
                "Offer loyalty program benefits",
                "Send targeted promotions"
            ]
        else:
            return [
                "Focus on basic retention",
                "Provide value-focused offers",
                "Monitor for improvement potential"
            ]

    async def generate_merchant_insights(self, merchant_id: int) -> Dict[str, Any]:
        """Generate comprehensive AI insights for merchant"""
        try:
            insights = {}
            
            # Customer segmentation insights
            insights["customer_segments"] = await self._analyze_customer_segments(merchant_id)
            
            # Revenue optimization insights
            insights["revenue_optimization"] = await self._analyze_revenue_optimization(merchant_id)
            
            # Campaign timing insights
            insights["optimal_timing"] = await self.get_optimal_campaign_timing(merchant_id)
            
            # Churn risk summary
            insights["churn_analysis"] = await self._analyze_merchant_churn_risk(merchant_id)
            
            # Growth opportunities
            insights["growth_opportunities"] = await self._identify_growth_opportunities(merchant_id)
            
            return insights
            
        except Exception as e:
            logger.error(f"Merchant insights error for {merchant_id}: {str(e)}")
            return {"error": "Analysis failed"}

    async def _analyze_customer_segments(self, merchant_id: int) -> Dict[str, Any]:
        """Analyze customer segments for merchant"""
        result = await self.db.execute(
            select(
                Customer.customer_segment,
                func.count(Customer.id).label('count'),
                func.avg(Customer.total_spent).label('avg_spent'),
                func.avg(Customer.churn_risk_score).label('avg_churn_risk')
            )
            .where(Customer.merchant_id == merchant_id)
            .group_by(Customer.customer_segment)
        )
        
        segments = {}
        for row in result:
            segments[row.customer_segment] = {
                "count": row.count,
                "average_spent": float(row.avg_spent or 0),
                "average_churn_risk": float(row.avg_churn_risk or 0)
            }
        
        return segments

    async def _analyze_revenue_optimization(self, merchant_id: int) -> Dict[str, Any]:
        """Analyze revenue optimization opportunities"""
        # Get transaction patterns
        result = await self.db.execute(
            select(
                func.avg(Transaction.amount).label('avg_transaction'),
                func.count(Transaction.id).label('total_transactions'),
                func.sum(Transaction.amount).label('total_revenue')
            )
            .where(Transaction.merchant_id == merchant_id)
        )
        stats = result.first()
        
        return {
            "current_avg_transaction": float(stats.avg_transaction or 0),
            "total_transactions": stats.total_transactions or 0,
            "total_revenue": float(stats.total_revenue or 0),
            "recommendations": [
                "Focus on increasing average order value",
                "Implement upselling strategies",
                "Create bundle offers for popular items"
            ]
        }

    async def _analyze_merchant_churn_risk(self, merchant_id: int) -> Dict[str, Any]:
        """Analyze overall churn risk for merchant's customers"""
        result = await self.db.execute(
            select(
                func.avg(Customer.churn_risk_score).label('avg_churn_risk'),
                func.count(Customer.id).filter(Customer.churn_risk_score >= 0.7).label('high_risk_count'),
                func.count(Customer.id).filter(Customer.churn_risk_score >= 0.4).label('medium_risk_count'),
                func.count(Customer.id).label('total_customers')
            )
            .where(Customer.merchant_id == merchant_id)
        )
        stats = result.first()
        
        return {
            "average_churn_risk": float(stats.avg_churn_risk or 0),
            "high_risk_customers": stats.high_risk_count or 0,
            "medium_risk_customers": stats.medium_risk_count or 0,
            "total_customers": stats.total_customers or 0,
            "churn_risk_percentage": (stats.high_risk_count or 0) / max(1, stats.total_customers or 1) * 100
        }

    async def _identify_growth_opportunities(self, merchant_id: int) -> List[Dict[str, Any]]:
        """Identify growth opportunities for merchant"""
        opportunities = []
        
        # Analyze customer segments for opportunities
        segments = await self._analyze_customer_segments(merchant_id)
        
        if segments.get("new", {}).get("count", 0) > segments.get("regular", {}).get("count", 0):
            opportunities.append({
                "type": "customer_retention",
                "priority": "high",
                "description": "High number of new customers - focus on retention strategies",
                "action": "Implement onboarding campaign for new customers"
            })
        
        if segments.get("at_risk", {}).get("count", 0) > 0:
            opportunities.append({
                "type": "churn_prevention",
                "priority": "high",
                "description": "Customers at risk of churning detected",
                "action": "Launch retention campaign for at-risk customers"
            })
        
        # Add more opportunity identification logic here
        
        return opportunities