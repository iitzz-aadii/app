import React from 'react';
import { Icon as LucideIcon } from 'lucide-react';

type Props = {
  title: string;
  value: number | string;
  icon: LucideIcon;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
};

const colorMap: Record<NonNullable<Props['color']>, string> = {
  blue: 'text-blue-600 bg-blue-100',
  green: 'text-green-600 bg-green-100',
  yellow: 'text-yellow-600 bg-yellow-100',
  red: 'text-red-600 bg-red-100',
  purple: 'text-purple-600 bg-purple-100',
};

const StatCard: React.FC<Props> = ({ title, value, icon: Icon, color = 'blue', change, changeType = 'neutral' }) => {
  const colorCls = colorMap[color];
  const changeCls = changeType === 'positive' ? 'text-green-600' : changeType === 'negative' ? 'text-red-600' : 'text-gray-600';

  return (
    <div className="bg-white rounded-lg shadow-soft p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorCls}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      {change && (
        <div className={`text-xs mt-3 ${changeCls}`}>{change} from last period</div>
      )}
    </div>
  );
};

export default StatCard;


