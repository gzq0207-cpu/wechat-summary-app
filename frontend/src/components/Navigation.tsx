import React from 'react'
import { Link } from 'react-router-dom'

export const Navigation: React.FC = () => {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-8">
            <Link to="/" className="text-2xl font-bold text-blue-600">
              📰 WeChat Summary
            </Link>
            <div className="flex gap-4">
              <Link to="/feed" className="text-gray-700 hover:text-blue-600 transition-colors">
                文章流
              </Link>
              <Link to="/accounts" className="text-gray-700 hover:text-blue-600 transition-colors">
                公众号管理
              </Link>
              <Link to="/tasks" className="text-gray-700 hover:text-blue-600 transition-colors">
                任务状态
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
