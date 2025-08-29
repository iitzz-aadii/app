import React from 'react';

type Assessment = {
  id: number;
  student_id: number;
  overall_risk: 'green' | 'yellow' | 'red';
  created_at?: string;
  dropout_probability?: number | null;
};

const RecentAlerts: React.FC<{ assessments: Assessment[] }> = ({ assessments }) => {
  return (
    <div className="bg-white rounded-lg shadow-soft p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Alerts</h3>
      <div className="space-y-3">
        {assessments.slice(0, 5).map((a) => (
          <div key={a.id} className="flex items-center justify-between p-3 rounded border">
            <div className="text-sm text-gray-700">Assessment #{a.id}</div>
            <div className="text-xs text-gray-500">
              {a.dropout_probability != null ? `${(a.dropout_probability * 100).toFixed(1)}%` : '—'}
            </div>
          </div>
        ))}
        {assessments.length === 0 && (
          <div className="text-sm text-gray-500">No recent alerts</div>
        )}
      </div>
    </div>
  );
};

export default RecentAlerts;


