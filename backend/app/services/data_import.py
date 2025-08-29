import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, date
import logging
from ..models import Student, Attendance, Exam, ExamScore, Fee
from ..core.config import settings

logger = logging.getLogger(__name__)


class DataImportService:
    def __init__(self):
        self.supported_formats = [".csv", ".xlsx", ".xls"]
        self.required_student_columns = [
            "student_id",
            "first_name",
            "last_name",
            "class_name",
            "academic_year",
        ]
        self.required_attendance_columns = [
            "student_id",
            "date",
            "subject",
            "is_present",
        ]
        self.required_exam_columns = [
            "student_id",
            "exam_name",
            "subject",
            "marks_obtained",
            "total_marks",
        ]
        self.required_fee_columns = ["student_id", "fee_type", "amount_due", "due_date"]

    def validate_file_format(self, filename: str) -> bool:
        """Validate if the uploaded file format is supported"""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)

    def read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Read file and return DataFrame"""
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return None

            logger.info(f"Successfully read file: {file_path}, shape: {df.shape}")
            return df

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the DataFrame"""
        if df is None or df.empty:
            return df

        # Remove duplicate rows
        initial_rows = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_rows:
            logger.info(f"Removed {initial_rows - len(df)} duplicate rows")

        # Handle missing values
        df = self.handle_missing_values(df)

        # Standardize column names
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Clean string columns
        string_columns = df.select_dtypes(include=["object"]).columns
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the DataFrame"""
        # For numeric columns, fill with 0 or mean
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if df[col].isnull().sum() > 0:
                if col in ["marks_obtained", "total_marks", "amount_due"]:
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(df[col].mean())

        # For categorical columns, fill with mode or 'Unknown'
        categorical_columns = df.select_dtypes(include=["object"]).columns
        for col in categorical_columns:
            if df[col].isnull().sum() > 0:
                if col in ["student_id", "first_name", "last_name"]:
                    # Remove rows with missing critical information
                    df = df.dropna(subset=[col])
                else:
                    mode_value = (
                        df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                    )
                    df[col] = df[col].fillna(mode_value)

        return df

    def validate_student_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate student data format and content"""
        errors = []

        # Check required columns
        missing_columns = set(self.required_student_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        # Check data types and content
        if "student_id" in df.columns:
            if df["student_id"].duplicated().any():
                errors.append("Duplicate student IDs found")

            if df["student_id"].isnull().any():
                errors.append("Student ID cannot be null")

        if "class_name" in df.columns:
            if df["class_name"].isnull().any():
                errors.append("Class name cannot be null")

        if "academic_year" in df.columns:
            if df["academic_year"].isnull().any():
                errors.append("Academic year cannot be null")

        return len(errors) == 0, errors

    def validate_attendance_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate attendance data format and content"""
        errors = []

        # Check required columns
        missing_columns = set(self.required_attendance_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        # Check data types and content
        if "student_id" in df.columns:
            if df["student_id"].isnull().any():
                errors.append("Student ID cannot be null")

        if "date" in df.columns:
            try:
                df["date"] = pd.to_datetime(df["date"]).dt.date
            except:
                errors.append("Invalid date format in date column")

        if "is_present" in df.columns:
            # Convert various present/absent formats to boolean
            df["is_present"] = df["is_present"].astype(str).str.lower()
            df["is_present"] = df["is_present"].map(
                {
                    "present": True,
                    "p": True,
                    "1": True,
                    "yes": True,
                    "true": True,
                    "absent": False,
                    "a": False,
                    "0": False,
                    "no": False,
                    "false": False,
                }
            )

            if df["is_present"].isnull().any():
                errors.append("Invalid values in is_present column")

        return len(errors) == 0, errors

    def validate_exam_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate exam data format and content"""
        errors = []

        # Check required columns
        missing_columns = set(self.required_exam_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        # Check data types and content
        if "marks_obtained" in df.columns and "total_marks" in df.columns:
            df["marks_obtained"] = pd.to_numeric(df["marks_obtained"], errors="coerce")
            df["total_marks"] = pd.to_numeric(df["total_marks"], errors="coerce")

            # Validate marks
            invalid_marks = df[
                (df["marks_obtained"] < 0)
                | (df["total_marks"] <= 0)
                | (df["marks_obtained"] > df["total_marks"])
            ]

            if not invalid_marks.empty:
                errors.append(
                    "Invalid marks found (negative marks, zero total marks, or marks exceeding total)"
                )

        return len(errors) == 0, errors

    def validate_fee_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate fee data format and content"""
        errors = []

        # Check required columns
        missing_columns = set(self.required_fee_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        # Check data types and content
        if "amount_due" in df.columns:
            df["amount_due"] = pd.to_numeric(df["amount_due"], errors="coerce")
            if (df["amount_due"] < 0).any():
                errors.append("Negative amounts found in amount_due")

        if "due_date" in df.columns:
            try:
                df["due_date"] = pd.to_datetime(df["due_date"]).dt.date
            except:
                errors.append("Invalid date format in due_date column")

        return len(errors) == 0, errors

    def import_students(self, df: pd.DataFrame, db: Session) -> Dict[str, int]:
        """Import student data into database"""
        if df is None or df.empty:
            return {"imported": 0, "errors": 0, "skipped": 0}

        imported = 0
        errors = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                # Check if student already exists
                existing_student = (
                    db.query(Student)
                    .filter(Student.student_id == str(row["student_id"]))
                    .first()
                )

                if existing_student:
                    skipped += 1
                    continue

                # Create new student
                student = Student(
                    student_id=str(row["student_id"]),
                    first_name=str(row["first_name"]),
                    last_name=str(row["last_name"]),
                    email=row.get("email"),
                    phone=row.get("phone"),
                    date_of_birth=self.parse_date(row.get("date_of_birth")),
                    gender=row.get("gender"),
                    address=row.get("address"),
                    class_name=str(row["class_name"]),
                    section=row.get("section"),
                    academic_year=str(row["academic_year"]),
                    enrollment_date=self.parse_date(row.get("enrollment_date"))
                    or date.today(),
                    guardian_name=row.get("guardian_name"),
                    guardian_phone=row.get("guardian_phone"),
                    guardian_email=row.get("guardian_email"),
                    guardian_relationship=row.get("guardian_relationship"),
                )

                db.add(student)
                imported += 1

            except Exception as e:
                logger.error(
                    f"Error importing student {row.get('student_id', 'Unknown')}: {e}"
                )
                errors += 1

        try:
            db.commit()
            logger.info(f"Successfully imported {imported} students")
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing student import: {e}")
            return {"imported": 0, "errors": errors, "skipped": skipped}

        return {"imported": imported, "errors": errors, "skipped": skipped}

    def import_attendance(self, df: pd.DataFrame, db: Session) -> Dict[str, int]:
        """Import attendance data into database"""
        if df is None or df.empty:
            return {"imported": 0, "errors": 0, "skipped": 0}

        imported = 0
        errors = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                # Check if student exists
                student = (
                    db.query(Student)
                    .filter(Student.student_id == str(row["student_id"]))
                    .first()
                )

                if not student:
                    skipped += 1
                    continue

                # Check if attendance record already exists
                existing_attendance = (
                    db.query(Attendance)
                    .filter(
                        Attendance.student_id == student.id,
                        Attendance.date == row["date"],
                        Attendance.subject == str(row["subject"]),
                    )
                    .first()
                )

                if existing_attendance:
                    skipped += 1
                    continue

                # Create new attendance record
                attendance = Attendance(
                    student_id=student.id,
                    date=row["date"],
                    subject=str(row["subject"]),
                    is_present=bool(row["is_present"]),
                    remarks=row.get("remarks"),
                )

                db.add(attendance)
                imported += 1

            except Exception as e:
                logger.error(
                    f"Error importing attendance for student {row.get('student_id', 'Unknown')}: {e}"
                )
                errors += 1

        try:
            db.commit()
            logger.info(f"Successfully imported {imported} attendance records")
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing attendance import: {e}")
            return {"imported": 0, "errors": errors, "skipped": skipped}

        return {"imported": imported, "errors": errors, "skipped": skipped}

    def import_exam_scores(self, df: pd.DataFrame, db: Session) -> Dict[str, int]:
        """Import exam scores into database"""
        if df is None or df.empty:
            return {"imported": 0, "errors": 0, "skipped": 0}

        imported = 0
        errors = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                # Check if student exists
                student = (
                    db.query(Student)
                    .filter(Student.student_id == str(row["student_id"]))
                    .first()
                )

                if not student:
                    skipped += 1
                    continue

                # Check if exam exists, create if not
                exam_name = str(row.get("exam_name", "Unknown"))
                subject = str(row.get("subject", "Unknown"))

                exam = (
                    db.query(Exam)
                    .filter(Exam.exam_name == exam_name, Exam.subject == subject)
                    .first()
                )

                if not exam:
                    exam = Exam(
                        exam_name=exam_name,
                        exam_type=row.get("exam_type", "quiz"),
                        subject=subject,
                        class_name=student.class_name,
                        exam_date=row.get("exam_date", date.today()),
                        total_marks=float(row["total_marks"]),
                        passing_marks=float(
                            row.get("passing_marks", row["total_marks"] * 0.4)
                        ),
                    )
                    db.add(exam)
                    db.flush()  # Get the exam ID

                # Check if score already exists
                existing_score = (
                    db.query(ExamScore)
                    .filter(
                        ExamScore.student_id == student.id, ExamScore.exam_id == exam.id
                    )
                    .first()
                )

                if existing_score:
                    skipped += 1
                    continue

                # Create new exam score
                exam_score = ExamScore(
                    student_id=student.id,
                    exam_id=exam.id,
                    marks_obtained=float(row["marks_obtained"]),
                    remarks=row.get("remarks"),
                )

                db.add(exam_score)
                imported += 1

            except Exception as e:
                logger.error(
                    f"Error importing exam score for student {row.get('student_id', 'Unknown')}: {e}"
                )
                errors += 1

        try:
            db.commit()
            logger.info(f"Successfully imported {imported} exam scores")
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing exam score import: {e}")
            return {"imported": 0, "errors": errors, "skipped": skipped}

        return {"imported": imported, "errors": errors, "skipped": skipped}

    def import_fees(self, df: pd.DataFrame, db: Session) -> Dict[str, int]:
        """Import fee data into database"""
        if df is None or df.empty:
            return {"imported": 0, "errors": 0, "skipped": 0}

        imported = 0
        errors = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                # Check if student exists
                student = (
                    db.query(Student)
                    .filter(Student.student_id == str(row["student_id"]))
                    .first()
                )

                if not student:
                    skipped += 1
                    continue

                # Check if fee record already exists
                existing_fee = (
                    db.query(Fee)
                    .filter(
                        Fee.student_id == student.id,
                        Fee.fee_type == str(row["fee_type"]),
                        Fee.due_date == row["due_date"],
                    )
                    .first()
                )

                if existing_fee:
                    skipped += 1
                    continue

                # Create new fee record
                fee = Fee(
                    student_id=student.id,
                    fee_type=str(row["fee_type"]),
                    amount_due=float(row["amount_due"]),
                    amount_paid=float(row.get("amount_paid", 0)),
                    due_date=row["due_date"],
                    payment_date=self.parse_date(row.get("payment_date")),
                    status=row.get("status", "unpaid"),
                    is_overdue=row.get("is_overdue", False),
                    remarks=row.get("remarks"),
                )

                db.add(fee)
                imported += 1

            except Exception as e:
                logger.error(
                    f"Error importing fee for student {row.get('student_id', 'Unknown')}: {e}"
                )
                errors += 1

        try:
            db.commit()
            logger.info(f"Successfully imported {imported} fee records")
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing fee import: {e}")
            return {"imported": 0, "errors": errors, "skipped": skipped}

        return {"imported": imported, "errors": errors, "skipped": skipped}

    def parse_date(self, date_value) -> Optional[date]:
        """Parse date from various formats"""
        if pd.isna(date_value) or date_value is None:
            return None

        try:
            if isinstance(date_value, str):
                return pd.to_datetime(date_value).date()
            elif isinstance(date_value, (datetime, pd.Timestamp)):
                return date_value.date()
            else:
                return None
        except:
            return None

    def get_import_summary(self, file_path: str, data_type: str) -> Dict:
        """Get summary of data import process"""
        df = self.read_file(file_path)
        if df is None:
            return {"error": "Could not read file"}

        df_cleaned = self.clean_dataframe(df)

        summary = {
            "file_path": file_path,
            "data_type": data_type,
            "original_rows": len(df),
            "cleaned_rows": len(df_cleaned),
            "columns": list(df_cleaned.columns),
            "missing_values": df_cleaned.isnull().sum().to_dict(),
            "duplicates_removed": len(df) - len(df_cleaned),
        }

        return summary
