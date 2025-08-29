#!/bin/bash

# AI-Driven Dropout Prediction System Setup Script
# This script will help you set up the complete system

set -e

echo "🎓 Setting up AI-Driven Dropout Prediction System..."
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/app/ml/models
mkdir -p data
mkdir -p logs

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://dropout_user:dropout_password@localhost:5432/dropout_db
DATABASE_TEST_URL=postgresql://dropout_user:dropout_password@localhost:5432/dropout_test_db

# Security
SECRET_KEY=your-secret-key-change-in-production-$(openssl rand -hex 32)

# ML Model Configuration
MODEL_PATH=app/ml/models
MODEL_VERSION=v1.0

# Risk Thresholds
ATTENDANCE_SAFE_THRESHOLD=75.0
ATTENDANCE_WARNING_THRESHOLD=60.0
SCORE_SAFE_THRESHOLD=60.0
SCORE_WARNING_THRESHOLD=40.0
MAX_ATTEMPTS_THRESHOLD=2

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=[".csv", ".xlsx", ".xls"]

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Create sample data directory
echo "📊 Creating sample data directory..."
mkdir -p sample_data

# Create sample CSV files
echo "📝 Creating sample data files..."

# Sample students data
cat > sample_data/students.csv << EOF
student_id,first_name,last_name,email,phone,class_name,section,academic_year,enrollment_date,guardian_name,guardian_phone
ST001,John,Doe,john.doe@email.com,+1234567890,10th,A,2024-25,2024-01-15,Jane Doe,+1234567891
ST002,Jane,Smith,jane.smith@email.com,+1234567892,10th,A,2024-25,2024-01-15,John Smith,+1234567893
ST003,Mike,Johnson,mike.johnson@email.com,+1234567894,10th,B,2024-25,2024-01-15,Sarah Johnson,+1234567895
ST004,Emily,Brown,emily.brown@email.com,+1234567896,11th,A,2024-25,2024-01-15,David Brown,+1234567897
ST005,David,Wilson,david.wilson@email.com,+1234567898,11th,B,2024-25,2024-01-15,Lisa Wilson,+1234567899
EOF

# Sample attendance data
cat > sample_data/attendance.csv << EOF
student_id,date,subject,is_present,remarks
ST001,2024-01-15,Mathematics,true,
ST001,2024-01-15,English,true,
ST001,2024-01-16,Mathematics,false,Medical leave
ST001,2024-01-16,English,true,
ST002,2024-01-15,Mathematics,true,
ST002,2024-01-15,English,true,
ST002,2024-01-16,Mathematics,true,
ST002,2024-01-16,English,true,
ST003,2024-01-15,Mathematics,false,Personal reason
ST003,2024-01-15,English,true,
ST003,2024-01-16,Mathematics,true,
ST003,2024-01-16,English,false,Family emergency
EOF

# Sample exam scores data
cat > sample_data/exam_scores.csv << EOF
student_id,exam_name,subject,marks_obtained,total_marks,exam_date,remarks
ST001,Midterm 1,Mathematics,85,100,2024-01-20,Good performance
ST001,Midterm 1,English,78,100,2024-01-20,Good performance
ST002,Midterm 1,Mathematics,92,100,2024-01-20,Excellent performance
ST002,Midterm 1,English,88,100,2024-01-20,Good performance
ST003,Midterm 1,Mathematics,65,100,2024-01-20,Needs improvement
ST003,Midterm 1,English,72,100,2024-01-20,Average performance
ST004,Midterm 1,Mathematics,95,100,2024-01-20,Outstanding performance
ST004,Midterm 1,English,90,100,2024-01-20,Excellent performance
ST005,Midterm 1,Mathematics,58,100,2024-01-20,Needs significant improvement
ST005,Midterm 1,English,68,100,2024-01-20,Below average
EOF

# Sample fees data
cat > sample_data/fees.csv << EOF
student_id,fee_type,amount_due,amount_paid,due_date,payment_date,status,is_overdue,remarks
ST001,Tuition,500.00,500.00,2024-01-31,2024-01-25,paid,false,Paid on time
ST001,Library,50.00,50.00,2024-01-31,2024-01-25,paid,false,Paid on time
ST002,Tuition,500.00,300.00,2024-01-31,2024-01-25,partial,false,Partial payment
ST002,Library,50.00,0.00,2024-01-31,,unpaid,false,Not paid yet
ST003,Tuition,500.00,0.00,2024-01-31,,unpaid,true,Overdue
ST003,Library,50.00,0.00,2024-01-31,,unpaid,true,Overdue
ST004,Tuition,500.00,500.00,2024-01-31,2024-01-20,paid,false,Paid early
ST004,Library,50.00,50.00,2024-01-31,2024-01-20,paid,false,Paid early
ST005,Tuition,500.00,0.00,2024-01-31,,unpaid,true,Overdue
ST005,Library,50.00,0.00,2024-01-31,,unpaid,true,Overdue
EOF

echo "✅ Sample data files created"

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Create initial admin user
echo "👤 Creating initial admin user..."
docker-compose exec backend python -c "
from app.core.database import SessionLocal, engine
from app.models import Base, User
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

# Create admin user
db = SessionLocal()
try:
    admin_user = User(
        email='admin@dropout-system.com',
        username='admin',
        full_name='System Administrator',
        hashed_password=get_password_hash('admin123'),
        role='admin',
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    print('✅ Admin user created successfully')
    print('   Email: admin@dropout-system.com')
    print('   Password: admin123')
except Exception as e:
    print(f'⚠️  Admin user creation failed: {e}')
finally:
    db.close()
"

# Train initial ML models
echo "🤖 Training initial ML models..."
docker-compose run --rm ml_training

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================================="
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔐 Default login credentials:"
echo "   Email: admin@dropout-system.com"
echo "   Password: admin123"
echo ""
echo "📊 Sample data has been created in the sample_data/ directory"
echo "   You can import this data using the Data Import feature"
echo ""
echo "📚 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Log in with the admin credentials"
echo "   3. Import sample data from the Data Import page"
echo "   4. Explore the dashboard and features"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"
echo ""
echo "📖 For more information, check the README.md file"
echo ""
echo "Happy coding! 🚀"
