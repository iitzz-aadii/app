import React from 'react';

const QuickActions: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-soft p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div className="grid grid-cols-2 gap-3">
        <button className="px-3 py-2 rounded bg-blue-600 text-white text-sm">Assess All</button>
        <button className="px-3 py-2 rounded bg-green-600 text-white text-sm">Import Data</button>
        <button className="px-3 py-2 rounded bg-yellow-600 text-white text-sm">Schedule Counseling</button>
        <button className="px-3 py-2 rounded bg-gray-600 text-white text-sm">Export Report</button>
      </div>
    </div>
  );
};

export default QuickActions;


