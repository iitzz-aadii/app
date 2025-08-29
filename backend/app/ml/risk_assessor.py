import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import Student, Attendance, ExamScore, Fee, RiskAssessment
from ..core.config import settings


class RiskAssessor:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.model_path = settings.MODEL_PATH
        self.load_models()

    def load_models(self):
        """Load trained ML models from disk"""
        try:
            if os.path.exists(f"{self.model_path}/logistic_regression.joblib"):
                self.models["logistic"] = joblib.load(
                    f"{self.model_path}/logistic_regression.joblib"
                )
            if os.path.exists(f"{self.model_path}/random_forest.joblib"):
                self.models["random_forest"] = joblib.load(
                    f"{self.model_path}/random_forest.joblib"
                )
            if os.path.exists(f"{self.model_path}/scaler.joblib"):
                self.scaler = joblib.load(f"{self.model_path}/scaler.joblib")
        except Exception as e:
            print(f"Error loading models: {e}")

    def save_models(self):
        """Save trained models to disk"""
        os.makedirs(self.model_path, exist_ok=True)
        for name, model in self.models.items():
            joblib.dump(model, f"{self.model_path}/{name}.joblib")
        joblib.dump(self.scaler, f"{self.model_path}/scaler.joblib")

    def extract_features(self, student: Student, db: Session) -> Dict[str, float]:
        """Extract features for risk assessment from student data"""
        features = {}

        # Attendance features
        attendance_records = (
            db.query(Attendance).filter(Attendance.student_id == student.id).all()
        )

        if attendance_records:
            total_sessions = len(attendance_records)
            present_sessions = sum(
                1 for record in attendance_records if record.is_present
            )
            features["attendance_percentage"] = (
                present_sessions / total_sessions
            ) * 100
            features["total_sessions"] = total_sessions
        else:
            features["attendance_percentage"] = 0.0
            features["total_sessions"] = 0

        # Academic features
        exam_scores = (
            db.query(ExamScore).filter(ExamScore.student_id == student.id).all()
        )

        if exam_scores:
            scores = [score.percentage for score in exam_scores]
            features["average_score"] = np.mean(scores)
            features["score_std"] = np.std(scores)
            features["failed_exams"] = sum(1 for score in scores if score < 40)
            features["total_exams"] = len(scores)
        else:
            features["average_score"] = 0.0
            features["score_std"] = 0.0
            features["failed_exams"] = 0
            features["total_exams"] = 0

        # Financial features
        fee_records = db.query(Fee).filter(Fee.student_id == student.id).all()

        if fee_records:
            overdue_fees = sum(1 for fee in fee_records if fee.is_overdue)
            total_fees = len(fee_records)
            features["overdue_fees_count"] = overdue_fees
            features["total_fees"] = total_fees
            features["overdue_fees_ratio"] = (
                overdue_fees / total_fees if total_fees > 0 else 0
            )
        else:
            features["overdue_fees_count"] = 0
            features["total_fees"] = 0
            features["overdue_fees_ratio"] = 0

        # Temporal features
        if student.enrollment_date:
            days_enrolled = (datetime.now().date() - student.enrollment_date).days
            features["days_enrolled"] = days_enrolled

        return features

    def rule_based_assessment(self, features: Dict[str, float]) -> Dict[str, str]:
        """Apply rule-based logic to determine risk levels"""
        risk_levels = {}

        # Attendance risk
        attendance = features.get("attendance_percentage", 0)
        if attendance >= settings.ATTENDANCE_SAFE_THRESHOLD:
            risk_levels["attendance"] = "green"
        elif attendance >= settings.ATTENDANCE_WARNING_THRESHOLD:
            risk_levels["attendance"] = "yellow"
        else:
            risk_levels["attendance"] = "red"

        # Academic risk
        avg_score = features.get("average_score", 0)
        if avg_score >= settings.SCORE_SAFE_THRESHOLD:
            risk_levels["academic"] = "green"
        elif avg_score >= settings.SCORE_WARNING_THRESHOLD:
            risk_levels["academic"] = "yellow"
        else:
            risk_levels["academic"] = "red"

        # Financial risk
        overdue_ratio = features.get("overdue_fees_ratio", 0)
        if overdue_ratio == 0:
            risk_levels["financial"] = "green"
        elif overdue_ratio <= 0.3:
            risk_levels["financial"] = "yellow"
        else:
            risk_levels["financial"] = "red"

        # Overall risk (worst case)
        risk_values = {"green": 1, "yellow": 2, "red": 3}
        max_risk = max(
            risk_values[risk_levels.get(key, "green")]
            for key in ["attendance", "academic", "financial"]
        )

        if max_risk == 1:
            risk_levels["overall"] = "green"
        elif max_risk == 2:
            risk_levels["overall"] = "yellow"
        else:
            risk_levels["overall"] = "red"

        return risk_levels

    def ml_prediction(self, features: Dict[str, float]) -> Dict[str, float]:
        """Get ML predictions for dropout probability"""
        if not self.models:
            return {"dropout_probability": 0.5, "confidence": 0.0}

        # Prepare feature vector
        feature_names = [
            "attendance_percentage",
            "average_score",
            "score_std",
            "failed_exams",
            "overdue_fees_ratio",
            "days_enrolled",
        ]

        feature_vector = []
        for name in feature_names:
            value = features.get(name, 0)
            # Handle missing values
            if pd.isna(value) or value is None:
                value = 0
            feature_vector.append(float(value))

        feature_vector = np.array(feature_vector).reshape(1, -1)

        # Scale features
        try:
            feature_vector_scaled = self.scaler.transform(feature_vector)
        except:
            feature_vector_scaled = feature_vector

        # Get predictions from multiple models
        predictions = {}
        confidences = {}

        for name, model in self.models.items():
            try:
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(feature_vector_scaled)[0]
                    predictions[name] = proba[1] if len(proba) > 1 else proba[0]
                else:
                    pred = model.predict(feature_vector_scaled)[0]
                    predictions[name] = float(pred)
                confidences[name] = 0.8  # Default confidence
            except Exception as e:
                print(f"Error with model {name}: {e}")
                predictions[name] = 0.5
                confidences[name] = 0.0

        # Ensemble prediction
        if predictions:
            avg_probability = np.mean(list(predictions.values()))
            avg_confidence = np.mean(list(confidences.values()))
        else:
            avg_probability = 0.5
            avg_confidence = 0.0

        return {
            "dropout_probability": float(avg_probability),
            "confidence": float(avg_confidence),
            "model_predictions": predictions,
        }

    def assess_student_risk(self, student: Student, db: Session) -> Dict:
        """Complete risk assessment for a student"""
        # Extract features
        features = self.extract_features(student, db)

        # Rule-based assessment
        risk_levels = self.rule_based_assessment(features)

        # ML prediction
        ml_results = self.ml_prediction(features)

        # Determine ML risk level
        dropout_prob = ml_results["dropout_probability"]
        if dropout_prob < 0.3:
            ml_risk_level = "green"
        elif dropout_prob < 0.6:
            ml_risk_level = "yellow"
        else:
            ml_risk_level = "red"

        # Generate recommendations
        recommendations = self.generate_recommendations(
            features, risk_levels, ml_results
        )

        # Create risk assessment result
        assessment = {
            "student_id": student.id,
            "assessment_date": datetime.now().date(),
            "features": features,
            "rule_based_risk": risk_levels,
            "ml_prediction": ml_results,
            "ml_risk_level": ml_risk_level,
            "recommendations": recommendations,
            "overall_risk": risk_levels["overall"],
        }

        return assessment

    def generate_recommendations(
        self, features: Dict[str, float], risk_levels: Dict[str, str], ml_results: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on risk assessment"""
        recommendations = []

        # Attendance recommendations
        if risk_levels.get("attendance") in ["yellow", "red"]:
            attendance = features.get("attendance_percentage", 0)
            if attendance < 60:
                recommendations.append("Immediate intervention required for attendance")
            elif attendance < 75:
                recommendations.append(
                    "Schedule meeting with student and parents about attendance"
                )
            recommendations.append(
                "Implement attendance tracking and early warning system"
            )

        # Academic recommendations
        if risk_levels.get("academic") in ["yellow", "red"]:
            avg_score = features.get("average_score", 0)
            if avg_score < 40:
                recommendations.append("Urgent academic support needed")
            elif avg_score < 60:
                recommendations.append("Schedule extra classes and academic counseling")
            recommendations.append("Assign peer mentor for academic support")

        # Financial recommendations
        if risk_levels.get("financial") in ["yellow", "red"]:
            overdue_ratio = features.get("overdue_fees_ratio", 0)
            if overdue_ratio > 0.5:
                recommendations.append("Immediate financial counseling required")
            elif overdue_ratio > 0.2:
                recommendations.append("Schedule fee payment discussion")
            recommendations.append("Explore financial aid and payment plan options")

        # ML-based recommendations
        dropout_prob = ml_results.get("dropout_probability", 0.5)
        if dropout_prob > 0.7:
            recommendations.append(
                "High dropout risk - implement comprehensive intervention plan"
            )
        elif dropout_prob > 0.5:
            recommendations.append(
                "Moderate dropout risk - monitor closely and provide support"
            )

        # General recommendations
        if risk_levels["overall"] == "red":
            recommendations.append("Schedule comprehensive counseling session")
            recommendations.append("Involve parents/guardians in intervention plan")
            recommendations.append("Weekly progress monitoring required")

        return recommendations

    def train_models(self, training_data: pd.DataFrame, target_column: str):
        """Train ML models with provided data"""
        if training_data.empty:
            print("No training data provided")
            return

        # Prepare features and target
        feature_columns = [col for col in training_data.columns if col != target_column]
        X = training_data[feature_columns]
        y = training_data[target_column]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Logistic Regression
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train_scaled, y_train)
        lr_score = accuracy_score(y_test, lr_model.predict(X_test_scaled))

        # Train Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X_train_scaled, y_train)
        rf_score = accuracy_score(y_test, rf_model.predict(X_test_scaled))

        # Store models
        self.models["logistic"] = lr_model
        self.models["random_forest"] = rf_model

        # Save models
        self.save_models()

        print(f"Models trained successfully!")
        print(f"Logistic Regression accuracy: {lr_score:.3f}")
        print(f"Random Forest accuracy: {rf_score:.3f}")

        return {"logistic_accuracy": lr_score, "random_forest_accuracy": rf_score}
