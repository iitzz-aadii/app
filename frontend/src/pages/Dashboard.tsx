import React from 'react';
import { useQuery } from 'react-query';
import { 
  Users, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp, 
  Clock,
  Activity
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { format } from 'date-fns';
import { api } from '../services/api';
import StatCard from '../components/Dashboard/StatCard';
import RiskDistributionChart from '../components/Dashboard/RiskDistributionChart';
import RecentAlerts from '../components/Dashboard/RecentAlerts';
import QuickActions from '../components/Dashboard/QuickActions';

const Dashboard: React.FC = () => {
  const { data: riskSummary, isLoading: summaryLoading } = useQuery(
    'riskSummary',
    () => api.get('/risk-assessment/summary').then(res => res.data),
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const { data: highRiskStudents, isLoading: highRiskLoading } = useQuery(
    'highRiskStudents',
    () => api.get('/risk-assessment/high-risk?limit=10').then(res => res.data),
    { refetchInterval: 60000 } // Refresh every minute
  );

  const { data: recentAssessments, isLoading: assessmentsLoading } = useQuery(
    'recentAssessments',
    () => api.get('/risk-assessment/?limit=20').then(res => res.data),
    { refetchInterval: 120000 } // Refresh every 2 minutes
  );

  const isLoading = summaryLoading || highRiskLoading || assessmentsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const totalStudents = riskSummary?.total_assessments || 0;
  const greenCount = riskSummary?.green_count || 0;
  const yellowCount = riskSummary?.yellow_count || 0;
  const redCount = riskSummary?.red_count || 0;

  const riskData = [
    { name: 'Safe', value: greenCount, color: '#22c55e' },
    { name: 'Warning', value: yellowCount, color: '#f59e0b' },
    { name: 'Critical', value: redCount, color: '#ef4444' },
  ];

  const trendData = [
    { date: 'Mon', green: 65, yellow: 20, red: 15 },
    { date: 'Tue', green: 62, yellow: 23, red: 15 },
    { date: 'Wed', green: 60, yellow: 25, red: 15 },
    { date: 'Thu', green: 58, yellow: 27, red: 15 },
    { date: 'Fri', green: 55, yellow: 30, red: 15 },
    { date: 'Sat', green: 52, yellow: 32, red: 16 },
    { date: 'Sun', green: 50, yellow: 35, red: 15 },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back! Here's what's happening with your students today.
          </p>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {format(new Date(), 'MMM dd, yyyy HH:mm')}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Students"
          value={totalStudents}
          icon={Users}
          color="blue"
          change="+2.5%"
          changeType="positive"
        />
        <StatCard
          title="Safe Students"
          value={greenCount}
          icon={CheckCircle}
          color="green"
          change="+1.2%"
          changeType="positive"
        />
        <StatCard
          title="At Risk"
          value={yellowCount + redCount}
          icon={AlertTriangle}
          color="yellow"
          change="+0.8%"
          changeType="negative"
        />
        <StatCard
          title="Critical Risk"
          value={redCount}
          icon={Activity}
          color="red"
          change="+0.3%"
          changeType="negative"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution Chart */}
        <div className="bg-white rounded-lg shadow-soft p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Trend Chart */}
        <div className="bg-white rounded-lg shadow-soft p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="green" stackId="a" fill="#22c55e" />
              <Bar dataKey="yellow" stackId="a" fill="#f59e0b" />
              <Bar dataKey="red" stackId="a" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* High Risk Students */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-soft p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">High Risk Students</h3>
              <span className="text-sm text-gray-500">
                {highRiskStudents?.length || 0} students need attention
              </span>
            </div>
            
            {highRiskStudents && highRiskStudents.length > 0 ? (
              <div className="space-y-3">
                {highRiskStudents.slice(0, 5).map((student: any) => (
                  <div key={student.student.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        student.latest_assessment?.overall_risk === 'red' ? 'bg-red-500' : 'bg-yellow-500'
                      }`} />
                      <div>
                        <p className="font-medium text-gray-900">
                          {student.student.first_name} {student.student.last_name}
                        </p>
                        <p className="text-sm text-gray-600">
                          Class {student.student.class_name} • {student.student.student_id}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-medium ${
                        student.latest_assessment?.overall_risk === 'red' ? 'text-red-600' : 'text-yellow-600'
                      }`}>
                        {student.latest_assessment?.overall_risk === 'red' ? 'Critical' : 'Warning'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {student.latest_assessment?.dropout_probability ? 
                          `${(student.latest_assessment.dropout_probability * 100).toFixed(1)}% dropout risk` : 
                          'Risk assessed'
                        }
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AlertTriangle className="mx-auto h-12 w-12 text-gray-400 mb-3" />
                <p>No high-risk students at the moment</p>
                <p className="text-sm">Great job keeping everyone on track!</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions & Recent Activity */}
        <div className="space-y-6">
          <QuickActions />
          <RecentAlerts assessments={recentAssessments || []} />
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-soft p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Last Assessment</p>
              <p className="text-lg font-semibold text-gray-900">
                {recentAssessments && recentAssessments.length > 0 
                  ? format(new Date(recentAssessments[0].created_at), 'MMM dd, HH:mm')
                  : 'No assessments yet'
                }
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-soft p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Improvement Rate</p>
              <p className="text-lg font-semibold text-gray-900">+12.5%</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-soft p-6">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p className="text-lg font-semibold text-gray-900">8</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
